#!/usr/bin/env python3
"""
Render every equation used in the defense deck to a high-resolution,
transparent-background PNG (plus a white-text variant for dark slides).

One source of truth: the FORMULAS dict below. Each entry also gets dumped as an
individual standalone `.tex` in src/ so it can be edited or reused directly.

Pipeline:  LaTeX body  ->  standalone .tex  ->  pdflatex  ->  pdftocairo PNG

Usage:
    python3 build_formulas.py            # build everything
    python3 build_formulas.py icfm_path  # build only the named formulas

Outputs:
    src/<name>.tex        standalone LaTeX source (black text)
    png/<name>.png        600-dpi transparent PNG, black text  (light slides)
    png_white/<name>.png  600-dpi transparent PNG, white text  (dark slides)
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
# The equation manifest.  Keys are file stems; values are LaTeX math bodies.
# Grouped by where they appear in the talk.  Everything here matches the
# thesis chapters (contents/chapter0{2,3,4}.tex) verbatim in meaning.
# ---------------------------------------------------------------------------
FORMULAS = {
    # --- Diffusion background (Slides: diffusion primer / EDM) ---
    "forward_noising":
        r"x_\sigma \;=\; x_0 + \sigma\,\varepsilon, \qquad \varepsilon \sim \mathcal{N}(0, I)",
    "pf_ode":
        r"\frac{dx}{d\sigma} \;=\; -\,\sigma\,\nabla_x \log p_\sigma(x)",
    "tweedie":
        r"\nabla_x \log p_\sigma(x) \;=\; \frac{D_\theta(x;\sigma) - x}{\sigma^2}",
    "dsm_loss":
        r"\mathcal{L}_{\mathrm{DSM}} \;=\; \mathbb{E}_{x_0,\varepsilon}\!\left[\,\big\lVert D_\theta(x_0 + \sigma\varepsilon;\,\sigma) - x_0 \big\rVert^2\,\right]",
    "edm_precond":
        r"D_\theta(x_\sigma;\sigma) \;=\; c_{\mathrm{skip}}(\sigma)\,x_\sigma \;+\; c_{\mathrm{out}}(\sigma)\,F_\theta\!\big(c_{\mathrm{in}}(\sigma)\,x_\sigma,\; c_{\mathrm{noise}}(\sigma)\big)",
    "edm_schedule":
        r"\sigma_i \;=\; \left(\sigma_{\max}^{1/\rho} + \frac{i}{N-1}\big(\sigma_{\min}^{1/\rho} - \sigma_{\max}^{1/\rho}\big)\right)^{\!\rho}",
    "edm_params":
        r"\sigma_{\min} = 0.002, \quad \sigma_{\max} = 80, \quad \sigma_{\mathrm{data}} = 0.5, \quad \rho = 7",
    "heun_nfe":
        r"N = 18 \ \text{Heun steps} \;\Longrightarrow\; 2N - 1 = 35 \ \text{NFE / forecast step}",

    # --- The cost problem (motivation) ---
    "cost_blowup":
        r"\underbrace{50}_{\text{members}} \times \underbrace{24}_{\text{hours}} \times \underbrace{35}_{\text{NFE}} \;=\; 42{,}000 \ \text{U\text{-}Net passes / cycle}",

    # --- StormCast two-stage decomposition ---
    "two_stage":
        r"M_t = F_\xi(X_{t-1}, S_t, I), \qquad R_t = X_t - M_t, \qquad \hat{X}_t = M_t + \hat{R}_t",
    "conditioning":
        r"c_t \;=\; \mathrm{concat}\big(X_{t-1},\; M_t,\; I\big)",
    "hr_stats":
        r"\mu_{\mathrm{HR}} = (295.98,\,-1.58,\,-2.65,\,0.182), \quad \sigma_{\mathrm{HR}} = (5.61,\,3.84,\,5.66,\,9.12)",

    # --- Flow matching (FlowCast / I-CFM) ---
    "icfm_path":
        r"x_t \;=\; (1-t)\,x_0 + t\,x_1 + \sigma_{\mathrm{path}}\,\eta, \qquad x_1 = R_t/\sigma_{\mathrm{data}}, \;\; x_0 \sim \mathcal{N}(0,I)",
    "icfm_target":
        r"u_t(x \mid x_0, x_1) \;=\; x_1 - x_0 \qquad (\text{constant: a straight line})",
    "icfm_loss":
        r"\mathcal{L}_{\mathrm{CFM}} \;=\; \mathbb{E}_{t,\,x_0,\,x_1,\,\eta}\!\left[\,\big\lVert v_\theta(x_t, t, c_t) - (x_1 - x_0) \big\rVert_{2,\beta}^2\,\right]",
    "flowcast_precond":
        r"v_\theta(x_t, t, c_t) \;=\; \mathrm{SongUNet}\big(\mathrm{concat}[x_t, c_t],\; t \cdot \tau\big), \qquad \tau = 1000",
    "flowcast_sampler":
        r"x_{t+\Delta t} \;=\; x_t + \Delta t\; v_\theta(x_t, t, c_t), \qquad \Delta t = 1/K, \quad x_0 \sim \mathcal{N}(0, I)",

    # --- MeanFlow (average velocity) ---
    "meanflow_avgvel":
        r"u(z_r, r, t) \;\triangleq\; \frac{1}{t - r}\int_{r}^{t} v(z_\tau, \tau)\, d\tau, \qquad \lim_{t \to r} u = v(z_r, r)",
    "meanflow_displacement":
        r"z_t \;=\; z_r + (t - r)\, u(z_r, r, t) \qquad (\text{one algebraic jump, no solver})",
    "meanflow_identity":
        r"\boxed{\;\; u(z_r, r, t) \;=\; v(z_r, r) \;+\; (t - r)\, \frac{d}{dr}\, u(z_r, r, t) \;\;}",
    "meanflow_jvp":
        r"\frac{d}{dr}\, u \;=\; \underbrace{v\,\partial_z u + \partial_r u}_{\text{one JVP, stop-gradient}}",
    "meanflow_loss":
        r"\mathcal{L}_{\mathrm{MF}} = \mathbb{E}\!\left[\mathrm{sg}(w)\,\big\lVert u_\theta - \mathrm{sg}(u_{\mathrm{tgt}})\big\rVert_{2,\beta}^2\right],\quad u_{\mathrm{tgt}} = v + (t-r)\big(v\,\partial_z u_\theta + \partial_r u_\theta\big)",
    "meanflow_sampler":
        r"z_{(i+1)/K} \;=\; z_{i/K} + \tfrac{1}{K}\, u_\theta\!\big(z_{i/K},\, \tfrac{i}{K},\, \tfrac{i+1}{K},\, c_t\big), \qquad i = 0, \ldots, K-1",

    # --- Precipitation-aware loss design ---
    "channel_l2":
        r"\lVert a \rVert_{2,\beta}^2 \;=\; \sum_{k=1}^{4} \beta_k\, \lVert a_k \rVert^2, \qquad \beta = (1,\,1,\,1,\,w_{\mathrm{pr}}), \;\; w_{\mathrm{pr}} = 2",
    "logpsd":
        r"\mathcal{L}_{\mathrm{spec}} \;=\; \frac{1}{|\mathcal{K}|}\sum_{\kappa \in \mathcal{K}} \big|\log P_{\mathrm{pred}}(\kappa) - \log P_{\mathrm{target}}(\kappa)\big|",
    "log1p":
        r"\texttt{qpepre} \;\longmapsto\; \log(1 + x): \quad \sigma = 9.12\,\text{mm h}^{-1} \;\longrightarrow\; \approx 0.37 \ \text{(log space)}",

    # --- Evaluation metrics ---
    "rmse":
        r"\mathrm{RMSE}_k \;=\; \sqrt{\frac{1}{|\mathcal{T}|\,HW}\sum_{t \in \mathcal{T}}\sum_{i,j}\big(\hat{X}^{(k)}_{t,i,j} - X^{(k)}_{t,i,j}\big)^2}",
    "csi_far":
        r"\mathrm{CSI}(\tau) = \frac{H}{H + M + F}, \qquad \mathrm{FAR}(\tau) = \frac{F}{H + F}",
    "fss":
        r"\mathrm{FSS}(\tau, n) \;=\; 1 - \frac{\sum_{i,j}\big(p^{\mathrm{fc}}_{i,j} - p^{\mathrm{ob}}_{i,j}\big)^2}{\sum_{i,j}\big(p^{\mathrm{fc}}_{i,j}\big)^2 + \sum_{i,j}\big(p^{\mathrm{ob}}_{i,j}\big)^2}",
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
        # pdflatex -> build/<stem>.pdf
        r = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
             "-output-directory", BUILD, tex_path],
            cwd=HERE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        pdf = os.path.join(BUILD, stem + ".pdf")
        if r.returncode != 0 or not os.path.exists(pdf):
            print(f"  [FAIL] pdflatex {stem}")
            ok = False
            continue
        # pdftocairo transparent PNG -> <out_dir>/<name>.png
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
    # tidy aux files
    for f in os.listdir(BUILD):
        if f.endswith((".aux", ".log", ".pdf", ".tex")):
            os.remove(os.path.join(BUILD, f))
    print(f"\nDone: {n_ok}/{len(wanted)} formulas rendered "
          f"(black -> png/, white -> png_white/).")


if __name__ == "__main__":
    main()
