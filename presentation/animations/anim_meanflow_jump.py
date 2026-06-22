"""MeanFlow's idea in one picture. The instantaneous velocity v(x,t) (grey
arrows) is what FlowCast learns: to follow it you take many small steps. The
AVERAGE velocity u(z_r,r,t) over the whole interval is a single arrow whose one
application lands you exactly on the data point: z_t = z_r + (t-r) u.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from _anim_common import save, FLOW, MEAN, INK

S = np.array([0.0, 0.0])
E = np.array([1.0, 0.0])
U = np.linspace(0, 1, 200)
straight = (1 - U)[:, None] * S + U[:, None] * E
# the *marginal* velocity field is curved (avg over crossing paths) -> bow it
path = straight.copy()
path[:, 1] = 0.55 * np.sin(np.pi * U)

F = 150
half = 70

fig, ax = plt.subplots(figsize=(11.4, 5.2))
fig.subplots_adjust(left=0.04, right=0.97, top=0.80, bottom=0.06)
ax.plot(path[:, 0], path[:, 1], color="#cdd2d8", lw=2.5, zorder=1)
ax.plot(*S, "o", ms=13, color="#9AA0A6", mec="white", zorder=6)
ax.plot(*E, "*", ms=24, color=INK, mec="white", zorder=6)
ax.text(S[0], S[1] - 0.18, "noise  $z_0$", ha="center", color="#9AA0A6", fontsize=12)
ax.text(E[0], E[1] - 0.18, "forecast  $z_1$", ha="center", color=INK, fontsize=12)
ax.set_xlim(-0.15, 1.18); ax.set_ylim(-0.45, 0.95)
ax.set_xticks([]); ax.set_yticks([])
for s in ax.spines.values():
    s.set_color("#dddddd")
title = ax.set_title("", fontsize=17, fontweight="bold", pad=14)

dot, = ax.plot([], [], "o", ms=15, color=FLOW, mec="white", zorder=7)
small_arrows = []
big_arrow = [None]
caption = ax.text(0.5, -0.40, "", transform=ax.transData if False else ax.transAxes,
                  ha="center", fontsize=13, color="#555")


def tangent(k):
    k = min(k, len(path) - 2)
    v = path[k + 1] - path[k]
    return v / (np.linalg.norm(v) + 1e-9)


def update(frame):
    for a in small_arrows:
        a.remove()
    small_arrows.clear()
    if big_arrow[0] is not None:
        big_arrow[0].remove(); big_arrow[0] = None

    if frame < half:                       # ACT 1: follow instantaneous velocity
        title.set_text("FlowCast: follow the instantaneous velocity  $v(x,t)$  — many small steps")
        title.set_color(FLOW)
        p = frame / (half - 1)
        k = int(p * (len(path) - 1))
        dot.set_data([path[k, 0]], [path[k, 1]])
        dot.set_color(FLOW)
        for kk in range(0, k + 1, max(1, len(path) // 12)):
            t = tangent(kk) * 0.10
            a = ax.annotate("", xy=path[kk] + t, xytext=path[kk],
                            arrowprops=dict(arrowstyle="->", color="#8a9097", lw=1.6))
            small_arrows.append(a)
        caption.set_text(r"each arrow = one network call along the curved marginal field")
    else:                                  # ACT 2: one average-velocity jump
        title.set_text("MeanFlow: one average-velocity jump   $z_1 = z_0 + (1-0)\\,u(z_0,0,1)$")
        title.set_color(MEAN)
        p = (frame - half) / (F - half - 1)
        pos = (1 - p) * S + p * E
        pos = pos.astype(float)
        pos[1] = 0.0
        dot.set_data([pos[0]], [pos[1]])
        dot.set_color(MEAN)
        big_arrow[0] = ax.annotate("", xy=E, xytext=S,
                                   arrowprops=dict(arrowstyle="-|>", color=MEAN,
                                                   lw=3.6, alpha=0.55 + 0.45 * p))
        caption.set_text("a single arrow — the whole interval in 1 model evaluation")
    return [dot, title, caption]


anim = FuncAnimation(fig, update, frames=F, interval=45, blit=False)
save(anim, "anim_meanflow_jump", fps=24)
plt.close(fig)
