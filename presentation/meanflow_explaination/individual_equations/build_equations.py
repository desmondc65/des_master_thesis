#!/usr/bin/env python3
"""
Render the "from flow matching to MeanFlow" equation chain to high-resolution,
transparent-background PNGs (plus a white-text variant for dark slides).

This is the focused companion to ../../formulas/build_formulas.py: the same
pipeline, but the manifest below is *only* the ordered derivation that takes the
straight-line flow-matching objective (FlowCast) to the MeanFlow average-velocity
objective. The stems are zero-padded so the directory lists in derivation order,
and the bodies match meanflow_from_flowmatching.tex equation-for-equation.

Pipeline:  LaTeX body  ->  standalone .tex  ->  pdflatex  ->  pdftocairo PNG

Usage:
    python3 build_equations.py                 # build everything
    python3 build_equations.py 08_mf_identity  # build only the named stems

Outputs:
    src/<stem>.tex        standalone LaTeX source (black text)
    png/<stem>.png        600-dpi transparent PNG, black text  (light slides)
    png_white/<stem>.png  600-dpi transparent PNG, white text  (dark slides)
"""
import os
import sys
import shutil
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
BUILD = os.path.join(HERE, "build")
PNG = os.path.join(HERE, "png")
PNG_W = os.path.join(HERE, "png_white")
DPI = 600

# ---------------------------------------------------------------------------
# The derivation manifest, in order. Convention (mirror of Geng et al. 2025):
# flow time tau in [0,1], tau=0 -> noise, tau=1 -> data; the field is evaluated
# at the lower edge z_r and differentiated w.r.t. r at fixed t (tangent (v,1,0)).
# Each entry carries a one-line caption used by the slide deck / README.
# ---------------------------------------------------------------------------
FORMULAS = {
    # === Part A: the flow-matching starting point (FlowCast) =================
    "01_fm_path":            # straight-line interpolant noise -> data
        r"x_t \;=\; (1-t)\,x_0 + t\,x_1 + \sigma_{\mathrm{path}}\,\eta, \qquad x_0 \sim \mathcal{N}(0, I), \;\; x_1 = R_t/\sigma_{\mathrm{data}}",
    "02_fm_velocity":        # instantaneous velocity = constant along the line
        r"v \;=\; \frac{dx_t}{dt} \;=\; x_1 - x_0 \qquad (\text{constant per pair: a straight line})",
    "03_fm_loss":            # conditional flow-matching objective (FlowCast head)
        r"\mathcal{L}_{\mathrm{FC}} \;=\; \mathbb{E}_{t,\,x_0,\,x_1}\!\left[\,\big\lVert v_\theta(x_t, t; c_t) - (x_1 - x_0) \big\rVert_{2,\beta}^2\,\right] \;\;(+\,\lambda_{\mathrm{spec}}\mathcal{L}_{\mathrm{spec}})",
    "04_fm_sampler":         # the cost we want to remove: K Euler steps
        r"x_{t+\Delta t} \;=\; x_t + \Delta t\; v_\theta(x_t, t; c_t), \qquad \Delta t = 1/K, \quad K \approx 10",

    # === Part B: the one idea -- the average velocity =======================
    "05_mf_avgvel":          # average velocity over the interval [r, t]
        r"u(z_r, r, t) \;\triangleq\; \frac{1}{t - r}\int_{r}^{t} v(z_\tau, \tau)\, d\tau, \qquad \lim_{t \to r} u(z_r, r, t) = v(z_r, r)",
    "06_mf_displacement":    # transport becomes a single algebraic jump
        r"z_t \;=\; z_r + (t - r)\, u(z_r, r, t) \qquad (\text{one jump, no solver})",

    # === Part C: making it trainable -- the MeanFlow identity ================
    "07_mf_integral":        # clear the denominator before differentiating
        r"(t - r)\, u(z_r, r, t) \;=\; \int_{r}^{t} v(z_\tau, \tau)\, d\tau",
    "08_mf_identity":        # differentiate w.r.t. r at fixed t -> the identity
        r"\boxed{\;\; u(z_r, r, t) \;=\; v(z_r, r) \;+\; (t - r)\, \frac{d}{dr}\, u(z_r, r, t) \;\;}",
    "09_mf_jvp":             # total derivative = one JVP with tangent (v, 1, 0)
        r"\frac{d}{dr}\, u \;=\; \underbrace{v\,\partial_z u \;+\; \partial_r u}_{\text{one JVP, tangent }(v,\,1,\,0),\; t\text{ fixed}}",
    "10_mf_boundary":        # zero-width interval recovers flow matching exactly
        r"\lim_{r \to t} u(z_r, r, t) \;=\; u(z_t, t, t) \;=\; v \qquad (\text{the diagonal } r=t \text{ is exactly flow matching})",

    # === Part D: the objective and the sampler ==============================
    "11_mf_target":          # stop-gradient bootstrap target
        r"u_{\mathrm{tgt}} \;=\; \mathrm{sg}\!\Big[\, v + (t - r)\big(v\,\partial_z u_\theta + \partial_r u_\theta\big) \Big]",
    "12_mf_loss":            # the MeanFlow training loss (adaptive, channel-weighted)
        r"\mathcal{L}_{\mathrm{MF}} \;=\; \mathbb{E}\!\left[\,\mathrm{sg}(w)\,\big\lVert u_\theta(z_r, r, t; c_t) - u_{\mathrm{tgt}} \big\rVert_{2,\beta}^2\,\right], \qquad w = \big(\lVert \Delta \rVert_{2,\beta}^2 + \varepsilon_w\big)^{-p}",
    "13_mf_sampler":         # one/two-step generation; reconstruct the field
        r"z_{(i+1)/K} \;=\; z_{i/K} + \tfrac{1}{K}\, u_\theta\!\big(z_{i/K},\, \tfrac{i}{K},\, \tfrac{i+1}{K};\, c_t\big), \qquad \widehat{X}_t = M_t + \sigma_{\mathrm{data}}\, z_1",
}

# Captions for the README / slide notes (kept here so there is one source).
CAPTIONS = {
    "01_fm_path":         "Straight-line interpolant from noise to the standardized residual.",
    "02_fm_velocity":     "Instantaneous velocity is the constant slope of that line.",
    "03_fm_loss":         "Conditional flow-matching loss = the FlowCast residual head.",
    "04_fm_sampler":      "Knowing only v, the sampler must integrate (about K=10 Euler steps).",
    "05_mf_avgvel":       "Average velocity over the whole interval [r, t] -- the MeanFlow object.",
    "06_mf_displacement": "If you know the average velocity, transport is one algebraic jump.",
    "07_mf_integral":     "Clear the denominator: (t-r) u = the displacement integral of v.",
    "08_mf_identity":     "Differentiate w.r.t. r at fixed t -> the MeanFlow identity.",
    "09_mf_jvp":          "The total derivative is one Jacobian-vector product, tangent (v,1,0).",
    "10_mf_boundary":     "Zero-width interval recovers flow matching: MeanFlow generalises it.",
    "11_mf_target":       "Stop-gradient bootstrap target built from the identity.",
    "12_mf_loss":         "The MeanFlow loss: adaptive weight, precipitation channel weights.",
    "13_mf_sampler":      "One/two-step sampler, then rebuild the field X_t = M_t + sigma_data z_1.",
}

TEX_TEMPLATE = r"""\documentclass[border=10pt,varwidth=\maxdimen]{standalone}
\usepackage{amsmath,amssymb,bm}
\usepackage{xcolor}
%(colorline)s
\begin{document}
\(\displaystyle %(body)s \)
\end{document}
"""


def write_tex(name, body, white=False):
    target_dir = SRC if not white else BUILD
    colorline = r"\color{white}" if white else ""
    tex = TEX_TEMPLATE % {"colorline": colorline, "body": body}
    stem = name if not white else name + "_white"
    path = os.path.join(target_dir, stem + ".tex")
    with open(path, "w") as f:
        f.write(tex)
    return path, stem


def compile_one(name, body):
    ok = True
    for white, out_dir in ((False, PNG), (True, PNG_W)):
        tex_path, stem = write_tex(name, body, white=white)
        r = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
             "-output-directory", BUILD, tex_path],
            cwd=HERE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        pdf = os.path.join(BUILD, stem + ".pdf")
        if r.returncode != 0 or not os.path.exists(pdf):
            print(f"  [FAIL] pdflatex {stem}")
            ok = False
            continue
        out_stem = os.path.join(out_dir, name)
        r2 = subprocess.run(
            ["pdftocairo", "-png", "-transp", "-r", str(DPI),
             "-singlefile", pdf, out_stem],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if r2.returncode != 0 or not os.path.exists(out_stem + ".png"):
            print(f"  [FAIL] pdftocairo {stem}")
            ok = False
    return ok


def main():
    for d in (SRC, BUILD, PNG, PNG_W):
        os.makedirs(d, exist_ok=True)
    if shutil.which("pdflatex") is None or shutil.which("pdftocairo") is None:
        sys.exit("ERROR: need pdflatex and pdftocairo on PATH")

    wanted = sys.argv[1:] or list(FORMULAS)
    n_ok = 0
    for name in wanted:
        if name not in FORMULAS:
            print(f"  [SKIP] unknown formula '{name}'")
            continue
        print(f"building {name} ...")
        if compile_one(name, FORMULAS[name]):
            n_ok += 1
    for f in os.listdir(BUILD):
        if f.endswith((".aux", ".log", ".pdf", ".tex")):
            os.remove(os.path.join(BUILD, f))
    print(f"\nDone: {n_ok}/{len(wanted)} equations rendered "
          f"(black -> png/, white -> png_white/).")


if __name__ == "__main__":
    main()
