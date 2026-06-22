#!/usr/bin/env bash
# Render the MeanFlow-StormCast workflow TikZ figures to high-res PNG.
# Pipeline:  src/<name>.tex  ->  pdflatex (standalone)  ->  pdftocairo PNG
# Outputs:   <name>.pdf (vector) + <name>.png (600 dpi, white bg) in this dir.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$HERE/src"; BUILD="$HERE/build"; DPI="${DPI:-600}"
mkdir -p "$BUILD"
export TEXINPUTS="$SRC:${TEXINPUTS:-}"
# figures to build: CLI args, else both by default
read -r -a FIGS <<< "${*:-meanflow_training meanflow_inference}"
for name in "${FIGS[@]}"; do
  echo "==> $name"
  pdflatex -interaction=nonstopmode -halt-on-error \
           -output-directory "$BUILD" "$SRC/$name.tex" >/dev/null
  cp "$BUILD/$name.pdf" "$HERE/$name.pdf"
  pdftocairo -png -r "$DPI" -singlefile "$BUILD/$name.pdf" "$HERE/$name"
  echo "    wrote $name.pdf  +  $name.png"
done
echo "done."
