"""The motivation slide, animated. The diffusion teacher costs 35 NFE per
forecast step; an operational cycle multiplies that by the rollout horizon and
the ensemble size. The three factors light up one by one and the running
product climbs to 42,000 U-Net passes per forecast cycle.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from _anim_common import save, DIFF, INK

factors = [("35", "NFE per step", "EDM Heun sampler"),
           ("24", "hours", "autoregressive rollout"),
           ("50", "members", "ensemble forecast")]
products = [35, 35 * 24, 35 * 24 * 50]

fig, ax = plt.subplots(figsize=(11.2, 5.6))
fig.subplots_adjust(left=0.04, right=0.96, top=0.82, bottom=0.06)
ax.axis("off")
ax.set_xlim(0, 10); ax.set_ylim(0, 10)
fig.suptitle("Why diffusion is too slow to deploy",
             fontsize=19, fontweight="bold", y=0.95)

xs = [1.7, 4.6, 7.5]
boxes, bignum, biglbl = [], [], []
for i, (num, lbl, sub) in enumerate(factors):
    b = plt.Rectangle((xs[i] - 1.0, 5.3), 2.0, 2.8, fc="#fff6ec",
                      ec=DIFF, lw=1.6, alpha=0.0, zorder=1)
    ax.add_patch(b); boxes.append(b)
    n = ax.text(xs[i], 7.0, num, ha="center", va="center", fontsize=34,
                fontweight="bold", color=DIFF, alpha=0.0)
    l = ax.text(xs[i], 6.1, lbl, ha="center", va="center", fontsize=14,
                color=INK, alpha=0.0)
    s = ax.text(xs[i], 5.6, sub, ha="center", va="center", fontsize=10.5,
                color="#777", alpha=0.0)
    bignum.append(n); biglbl.append([l, s])
    if i < 2:
        ax.text(xs[i] + 1.45, 6.7, "×", ha="center", va="center",
                fontsize=26, color="#999")

prod = ax.text(5.0, 2.6, "", ha="center", va="center", fontsize=28,
               fontweight="bold", color=INK)
sub = ax.text(5.0, 1.4, "", ha="center", va="center", fontsize=14, color="#555")

STAGE = 24
HOLD = 34
F = STAGE * 3 + HOLD


def update(frame):
    revealed = min(frame // STAGE + 1, 3)        # how many factors are visible
    for i in range(3):
        a = np.clip((frame - i * STAGE) / 12.0, 0, 1) if i < revealed else 0.0
        boxes[i].set_alpha(0.9 * a)
        bignum[i].set_alpha(a)
        for t in biglbl[i]:
            t.set_alpha(a)
    val = products[revealed - 1]
    if frame >= STAGE * 3 + 6:
        prod.set_text("= 42,000 U-Net passes / forecast cycle")
        prod.set_color(DIFF)
        sub.set_text("far outside the between-radar-volume compute budget")
    else:
        prod.set_text(f"= {val:,} U-Net passes")
        prod.set_color(INK)
        sub.set_text("")
    return boxes + bignum + [prod, sub]


anim = FuncAnimation(fig, update, frames=F, interval=60, blit=False)
save(anim, "anim_cost_problem", fps=18)
plt.close(fig)
