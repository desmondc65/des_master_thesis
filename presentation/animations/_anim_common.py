"""Shared style + save helper for the defense animations.

Colour scheme matches figures/concepts/diffusion_vs_flow_2d_paths.png:
    diffusion = orange,  flow matching = blue,  MeanFlow = green.
Every script writes both a .gif (Pillow, for PowerPoint/Keynote) and an .mp4
(ffmpeg, smaller + smoother, for web/Reveal.js) into out/.
Backgrounds are white to drop straight onto a light slide template.
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import PillowWriter, FFMpegWriter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

# palette
DIFF = "#E8820C"   # diffusion  (curved, 35 NFE)
FLOW = "#1F77B4"   # FlowCast   (straight, ~10 NFE)
MEAN = "#2BA84A"   # MeanFlow   (average velocity, 1-2 NFE)
DATA = "#2A2A2A"   # ground truth / data
NOISE = "#9AA0A6"  # gaussian prior / noise
MUTED = "#C8CDD2"
INK = "#222222"
GRID = "#E6E8EB"

plt.rcParams.update({
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
    "axes.facecolor": "white",
    "font.size": 13,
    "font.family": "DejaVu Sans",
    "axes.edgecolor": "#444444",
    "axes.linewidth": 1.0,
    "text.color": INK,
    "axes.labelcolor": INK,
    "xtick.color": INK,
    "ytick.color": INK,
})


def save(anim, name, fps=25, dpi=120, mp4=True):
    """Write out/<name>.gif and out/<name>.mp4."""
    gif = os.path.join(OUT, name + ".gif")
    anim.save(gif, writer=PillowWriter(fps=fps), dpi=dpi)
    print(f"  wrote {gif}  ({os.path.getsize(gif) / 1e6:.1f} MB)")
    if mp4:
        try:
            mp4p = os.path.join(OUT, name + ".mp4")
            anim.save(mp4p, writer=FFMpegWriter(fps=fps, bitrate=2600), dpi=dpi)
            print(f"  wrote {mp4p}  ({os.path.getsize(mp4p) / 1e6:.1f} MB)")
        except Exception as e:  # ffmpeg missing -> gif is enough
            print(f"  (mp4 skipped: {e})")


def synthetic_precip(n=96, seed=7):
    """A small, Taiwan-ish convective precipitation field: a few heavy cells on
    a sparse dry background, plus a faint orographic band. Returns a [0,1] field.
    """
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:n, 0:n] / n
    field = np.zeros((n, n))
    cells = [(0.35, 0.45, 0.05, 1.0), (0.55, 0.62, 0.07, 0.7),
             (0.62, 0.40, 0.035, 0.9), (0.30, 0.70, 0.045, 0.55),
             (0.72, 0.72, 0.03, 0.8)]
    for cy, cx, s, amp in cells:
        field += amp * np.exp(-((yy - cy) ** 2 + (xx - cx) ** 2) / (2 * s ** 2))
    # faint orographic spine down the middle (terrain forcing)
    field += 0.12 * np.exp(-((xx - 0.5) ** 2) / (2 * 0.06 ** 2))
    field += 0.03 * rng.standard_normal((n, n))
    field = np.clip(field, 0, None)
    return field / field.max()
