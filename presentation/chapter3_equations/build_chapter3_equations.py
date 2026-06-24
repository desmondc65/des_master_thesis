#!/usr/bin/env python3
"""
Export EVERY displayed equation in thesis Chapter 3 (contents/chapter03.tex) to a
standalone LaTeX source and a high-resolution transparent PNG (black + white).

Unlike ../formulas/ and ../meanflow_explaination/ (hand-curated manifests), this
script *auto-extracts* the equations directly from the chapter, so it stays in
sync with the thesis: re-run it after editing chapter03.tex. Each equation is
named by its thesis \\label (e.g. eq:meanflow-identity -> meanflow_identity) and
prefixed with its document order (01_, 02_, ...), so the directory lists in the
same order the equations appear in the chapter.

The thesis's own math macros (\\Ebb, \\Nbb, \\Freg, \\unet, ... from ntusetup.tex)
are injected into the standalone preamble so every symbol renders identically to
the compiled thesis.

Pipeline:  extract body -> standalone .tex -> pdflatex -> pdftocairo PNG

Usage:
    python3 build_chapter3_equations.py            # extract + build everything
    python3 build_chapter3_equations.py --list     # just print what it found
    python3 build_chapter3_equations.py 08_meanflow_identity   # build a subset

Outputs:
    src/<stem>.tex        standalone LaTeX source (black text)
    png/<stem>.png        600-dpi transparent PNG, black text  (light slides)
    png_white/<stem>.png  600-dpi transparent PNG, white text  (dark slides)
    manifest.txt          stem -> label, one per line (regenerated each run)
"""
import os
import re
import sys
import shutil
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
CHAPTER = os.path.normpath(os.path.join(HERE, "..", "..", "contents", "chapter03.tex"))
SRC = os.path.join(HERE, "src")
BUILD = os.path.join(HERE, "build")
PNG = os.path.join(HERE, "png")
PNG_W = os.path.join(HERE, "png_white")
DPI = 600

# Thesis math macros (verbatim from ntusetup.tex) so every symbol resolves.
THESIS_MACROS = r"""
\DeclareMathOperator*{\argmin}{arg\,min}
\DeclareMathOperator*{\argmax}{arg\,max}
\newcommand{\Ebb}{\mathbb{E}}
\newcommand{\Rbb}{\mathbb{R}}
\newcommand{\Nbb}{\mathcal{N}}
\newcommand{\Dnet}{D_{\theta}}
\newcommand{\Dedm}{D_{\psi}}
\newcommand{\Dteach}{D_{\psi}}
\newcommand{\vnet}{v_{\theta}}
\newcommand{\unet}{u_{\theta}}
\newcommand{\Freg}{F_{\xi}}
"""

TEX_TEMPLATE = r"""\documentclass[border=10pt,varwidth=\maxdimen]{standalone}
\usepackage{amsmath,amssymb,bm}
\usepackage{siunitx}
\usepackage{xcolor}
%(macros)s
%(colorline)s
\begin{document}
\(\displaystyle %(body)s \)
\end{document}
"""

EQ_RE = re.compile(r"\\begin\{equation\}(.*?)\\end\{equation\}", re.DOTALL)
LABEL_RE = re.compile(r"\\label\{([^}]*)\}")


# Friendly names for the chapter's *unlabelled* equations, matched on a unique
# substring of the body (robust to reordering; only used when no \label exists).
FRIENDLY_NAMES = [
    (r"\Freg(X_{t-1}",            "regression_mean"),
    (r"\mathrm{concat}\bigl(X_{t-1}", "conditioning"),
    ("v_{1/2}",                   "heun_step"),
    (r"\sum_{k=1}^{4} \beta_k",   "channel_norm"),
    (r"P_{\text{pred}}",          "logpsd"),
]


def slug(label, body, idx):
    """eq:meanflow-identity -> meanflow_identity ; unlabelled -> friendly/ch3_eqNN."""
    if label:
        name = label.split(":", 1)[-1]      # drop the 'eq:' namespace
        name = re.sub(r"[^0-9A-Za-z]+", "_", name).strip("_").lower()
        if name:
            return name
    for needle, friendly in FRIENDLY_NAMES:
        if needle in body:
            return friendly
    return f"ch3_eq{idx:02d}"


def clean_body(raw):
    """Strip the \\label, comments, and surrounding whitespace from a body."""
    body = LABEL_RE.sub("", raw)
    lines = []
    for ln in body.splitlines():
        s = ln.strip()
        if not s or s.startswith("%"):
            continue
        lines.append(s)
    return " ".join(lines).strip()


def extract():
    with open(CHAPTER, encoding="utf-8") as f:
        text = f.read()
    items = []
    for i, m in enumerate(EQ_RE.finditer(text), start=1):
        raw = m.group(1)
        label_m = LABEL_RE.search(raw)
        label = label_m.group(1) if label_m else ""
        body = clean_body(raw)
        stem = f"{i:02d}_{slug(label, body, i)}"
        items.append((stem, label, body))
    return items


def write_tex(name, body, white=False):
    target_dir = SRC if not white else BUILD
    colorline = r"\color{white}" if white else ""
    tex = TEX_TEMPLATE % {
        "macros": THESIS_MACROS,
        "colorline": colorline,
        "body": body,
    }
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

    items = extract()

    if "--list" in sys.argv[1:]:
        for stem, label, body in items:
            print(f"{stem}\t<- {label or '(no label)'}")
            print(f"    {body}")
        print(f"\n{len(items)} equations found in {os.path.relpath(CHAPTER, HERE)}")
        return

    if shutil.which("pdflatex") is None or shutil.which("pdftocairo") is None:
        sys.exit("ERROR: need pdflatex and pdftocairo on PATH")

    # Always (re)write the manifest so the mapping stem -> label is on disk.
    with open(os.path.join(HERE, "manifest.txt"), "w") as f:
        for stem, label, _ in items:
            f.write(f"{stem}\t{label or '(no label)'}\n")

    wanted = [a for a in sys.argv[1:] if not a.startswith("-")]
    by_stem = {stem: body for stem, _, body in items}
    targets = wanted or list(by_stem)

    n_ok = 0
    for name in targets:
        if name not in by_stem:
            print(f"  [SKIP] unknown stem '{name}'")
            continue
        print(f"building {name} ...")
        if compile_one(name, by_stem[name]):
            n_ok += 1

    for f in os.listdir(BUILD):
        if f.endswith((".aux", ".log", ".pdf", ".tex")):
            os.remove(os.path.join(BUILD, f))
    print(f"\nDone: {n_ok}/{len(targets)} equations rendered "
          f"(black -> png/, white -> png_white/).")


if __name__ == "__main__":
    main()
