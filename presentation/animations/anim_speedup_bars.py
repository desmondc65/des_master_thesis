"""The payoff slide, animated. Wall-clock to generate one ten-member, +12 h
rollout sequence on a single RTX A6000 (Table 4.1 of the thesis). Bars grow
from zero; speedup-over-diffusion labels count up. FlowCast ~3.7x, MeanFlow ~9x.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from _anim_common import save, DIFF, FLOW, MEAN, INK

rows = [
    ("EDM diffusion\n(35 NFE)", 21.78, DIFF, 1.0),
    ("FlowCast\n(K=10)", 5.88, FLOW, 21.78 / 5.88),
    ("MeanFlow\n(K=2)", 2.35, MEAN, 21.78 / 2.35),
]
labels = [r[0] for r in rows]
vals = np.array([r[1] for r in rows])
cols = [r[2] for r in rows]
spd = [r[3] for r in rows]
y = np.arange(len(rows))[::-1]

fig, ax = plt.subplots(figsize=(11.0, 5.2))
fig.subplots_adjust(left=0.20, right=0.96, top=0.82, bottom=0.12)
ax.set_xlim(0, 25); ax.set_ylim(-0.6, len(rows) - 0.4)
ax.set_yticks(y); ax.set_yticklabels(labels, fontsize=13)
ax.set_xlabel("seconds per 10-member, +12 h rollout sequence  (lower = faster)",
              fontsize=12)
ax.set_title("Same skill class, a fraction of the cost — no teacher, single run",
             fontsize=16, fontweight="bold", pad=14)
for s in ["top", "right"]:
    ax.spines[s].set_visible(False)
ax.grid(axis="x", color="#eceef0")

bars = ax.barh(y, [0] * len(rows), color=cols, height=0.55, zorder=3)
vtxt = [ax.text(0, yi, "", va="center", ha="left", fontsize=13,
                fontweight="bold", color=INK) for yi in y]

GROW, HOLD = 40, 30
F = GROW + HOLD


def update(frame):
    p = min(frame / GROW, 1.0)
    e = 1 - (1 - p) ** 3                      # ease-out
    for i, bar in enumerate(bars):
        w = vals[i] * e
        bar.set_width(w)
        s = spd[i] * e if spd[i] > 1 else 1.0
        tag = f"{vals[i]:.2f}s" if i == 0 else f"{vals[i]:.2f}s   ({s:.1f}× faster)"
        vtxt[i].set_text(tag if p > 0.02 else "")
        vtxt[i].set_position((w + 0.4, y[i]))
        vtxt[i].set_color(cols[i] if i > 0 else INK)
    return list(bars) + vtxt


anim = FuncAnimation(fig, update, frames=F, interval=55, blit=False)
save(anim, "anim_speedup_bars", fps=20)
plt.close(fig)
