#!/usr/bin/env bash
# Build the MeanFlow thesis TikZ figures to high-res PNG.
#   src/<name>.tex (standalone) -> pdflatex -> PDF -> pdftoppm/pdftocairo -> PNG
# Self-contained: shares ./mfstyle.tex (NOT the legacy presentation pipeline).
#
# Usage:
#   ./build.sh                      # build all figures
#   ./build.sh meanflow_network     # build a subset
#   DPI=300 ./build.sh              # override resolution (default 600)
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD="$HERE/build"
DPI="${DPI:-600}"
mkdir -p "$BUILD"
# let \input{mfstyle} resolve from this directory
export TEXINPUTS="$HERE:${TEXINPUTS:-}"

# default = all figures
read -r -a FIGS <<< "${*:-meanflow_overall meanflow_network meanflow_objective regression_network_detail meanflow_network_detail}"

# pick a PDF->PNG rasterizer that is actually installed
if command -v pdftoppm >/dev/null 2>&1; then
  raster() { pdftoppm -png -r "$DPI" -singlefile "$1" "${2%.png}"; }
elif command -v pdftocairo >/dev/null 2>&1; then
  raster() { pdftocairo -png -r "$DPI" -singlefile "$1" "${2%.png}"; }
elif command -v convert >/dev/null 2>&1; then
  raster() { convert -density "$DPI" "$1" -quality 95 "$2"; }
else
  echo "error: need one of pdftoppm / pdftocairo / convert to make PNGs" >&2
  exit 1
fi

for name in "${FIGS[@]}"; do
  echo "==> $name"
  pdflatex -interaction=nonstopmode -halt-on-error \
           -output-directory "$BUILD" "$HERE/$name.tex" >/dev/null
  cp "$BUILD/$name.pdf" "$HERE/$name.pdf"
  raster "$HERE/$name.pdf" "$HERE/$name.png"
  echo "    wrote $name.pdf + $name.png (${DPI} dpi)"
done
echo "done."
