"""What 'generate a forecast' means: integrate pure noise into a weather field.

Left: the forward corruption x_sigma = x0 + sigma*eps walks a clean precip
field up to pure Gaussian noise. Right (the generative direction): a learned
model walks noise back down to a sharp field. The clock at the bottom is the
noise level sigma; the loop plays data -> noise -> data so it reads as 'noise
<-> weather'.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.colors import LinearSegmentedColormap
from _anim_common import save, synthetic_precip, INK, FLOW

x0 = synthetic_precip(n=96, seed=7)
rng = np.random.default_rng(1)
eps = rng.standard_normal(x0.shape)

# precip colormap: white(dry) -> blue -> purple(heavy)
precip = LinearSegmentedColormap.from_list(
    "precip", ["#ffffff", "#cfe8ff", "#5aa9e6", "#2e5fa3", "#5c3a99", "#3a1a5c"])

SIG_MAX = 2.4
F = 104
half = F // 2
# sigma schedule: ramp up (corrupt) then down (generate), eased
phase = np.concatenate([np.linspace(0, 1, half), np.linspace(1, 0, F - half)])
sig = SIG_MAX * (0.5 - 0.5 * np.cos(np.pi * phase)) ** 1.0

fig, ax = plt.subplots(figsize=(6.4, 6.8))
fig.subplots_adjust(left=0.04, right=0.96, top=0.88, bottom=0.13)
im = ax.imshow(x0, cmap=precip, vmin=-0.2, vmax=1.1, origin="lower",
               interpolation="bilinear")
ax.set_xticks([]); ax.set_yticks([])
ax.set_title("", fontsize=16, pad=12)
title = ax.set_title("clean forecast field", fontsize=17, fontweight="bold")
# sigma bar
bx = fig.add_axes([0.12, 0.05, 0.76, 0.035])
bx.set_xlim(0, SIG_MAX); bx.set_ylim(0, 1)
bx.set_yticks([]); bx.set_xticks([0, SIG_MAX])
bx.set_xticklabels([r"$\sigma=0$ (data)", r"$\sigma_{\max}$ (pure noise)"])
(bar,) = bx.barh([0.5], [0], height=0.7, color=FLOW)
bx.set_facecolor("#f4f5f7")


def corrupt(s):
    return x0 + s * eps


def update(frame):
    s = sig[frame]
    im.set_data(corrupt(s))
    bar.set_width(s)
    going_up = frame < half
    if s < 0.05:
        title.set_text("clean forecast field")
        title.set_color(INK)
    elif going_up:
        title.set_text("forward process: add noise  →")
        title.set_color("#9AA0A6")
    else:
        title.set_text("← generative model: integrate noise into a forecast")
        title.set_color(FLOW)
    return [im, bar, title]


anim = FuncAnimation(fig, update, frames=F, interval=45, blit=False)
save(anim, "anim_noise_to_field", fps=20, dpi=84)
plt.close(fig)
