#!/usr/bin/env bash
# Render every defense animation to out/<name>.{gif,mp4}.
# Run from anywhere; paths are resolved relative to this script.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p out
for f in anim_*.py; do
    echo "=== $f ==="
    python3 "$f"
done
echo
echo "All animations written to: $(pwd)/out"
ls -lh out/*.gif 2>/dev/null || true
