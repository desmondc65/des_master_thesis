#!/usr/bin/env bash
# Render each notation from the StormCast workflow figure as an individual,
# transparent-background PNG via LaTeX (standalone) -> PDF -> PNG.
#
# Usage:  bash build_notations.sh
set -euo pipefail

OUTDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD="$(mktemp -d)"
DENSITY=1200   # rasterization DPI; high so glyphs stay crisp when scaled
trap 'rm -rf "$BUILD"' EXIT

# name  <TAB>  LaTeX math body (rendered inside $...$)
read -r -d '' NOTATIONS <<'EOF' || true
S_t	S_t
M_t	M_t
M_tp1	M_{t+1}
F_theta	F_\theta
mu_tp1	\mu_{t+1}
D_phi	D_\phi
sigma_noise	\sigma\,\mathcal{N}(0, I)
r_tp1	r_{t+1}
residual_def	r_{t+1} = M_{t+1} - \mu_{t+1}
p_residual	p\left( r_{t+1} \,\middle|\, \mu_{t+1},\, M_t \right)
MF_theta	MF_\theta
concatenate	\odot
add	\oplus
EOF

# name  <TAB>  text label body (centered tabular, text mode; use \\ for line breaks)
read -r -d '' TEXT_LABELS <<'EOF' || true
era5	ERA 5 \\ 24 ch
rwrf_qpepre	RWRF + Qpepre \\ 4 ch
regression	Regression
meanflow	MeanFlow
ar	AR
EOF

render() {
    local name="$1" body="$2"
    local tex="$BUILD/$name.tex"
    cat > "$tex" <<TEX
\\documentclass[border=2pt]{standalone}
\\usepackage{amsmath}
\\usepackage{amssymb}
\\begin{document}
\$\\displaystyle $body\$
\\end{document}
TEX
    pdflatex -interaction=batchmode -halt-on-error -output-directory "$BUILD" "$tex" >/dev/null 2>&1
    convert -density "$DENSITY" -background none "$BUILD/$name.pdf" \
            -trim +repage -quality 100 "$OUTDIR/$name.png"
    echo "  ok  $name.png"
}

render_text() {
    local name="$1" body="$2"
    local tex="$BUILD/$name.tex"
    cat > "$tex" <<TEX
\\documentclass[border=4pt]{standalone}
\\begin{document}
\\begin{tabular}{c}
$body
\\end{tabular}
\\end{document}
TEX
    pdflatex -interaction=batchmode -halt-on-error -output-directory "$BUILD" "$tex" >/dev/null 2>&1
    convert -density "$DENSITY" -background none "$BUILD/$name.pdf" \
            -trim +repage -quality 100 "$OUTDIR/$name.png"
    echo "  ok  $name.png"
}

echo "Rendering notations -> $OUTDIR"
while IFS=$'\t' read -r name body; do
    [ -z "$name" ] && continue
    render "$name" "$body"
done <<< "$NOTATIONS"

while IFS=$'\t' read -r name body; do
    [ -z "$name" ] && continue
    render_text "$name" "$body"
done <<< "$TEXT_LABELS"
echo "Done."
