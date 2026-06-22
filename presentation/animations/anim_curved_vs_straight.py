"""Concept centerpiece: same noise -> same forecast, three different routes.

Diffusion follows a CURVED probability-flow ODE and needs ~35 model calls.
FlowCast follows a STRAIGHT-line flow and needs ~10 Euler steps.
MeanFlow learns the AVERAGE velocity and jumps the whole way in 1 call.

A sample dot travels the same start->end journey in all three panels; the
number of stop markers (= network evaluations) is what differs.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from _anim_common import save, DIFF, FLOW, MEAN, NOISE, DATA, MUTED, INK

rng = np.random.default_rng(3)
S = np.array([-0.55, -1.15])          # the chosen prior (noise) sample
E = np.array([0.38, 1.40])            # its target forecast (data) sample
prior = S + 0.42 * rng.standard_normal((140, 2)) + np.array([0.1, 0.05])
targ = np.array([[0.2, 1.45], [0.95, 1.15], [-0.7, 1.25]])
targ_pts = np.vstack([c + 0.16 * rng.standard_normal((45, 2)) for c in targ])

U = np.linspace(0, 1, 400)
straight = (1 - U)[:, None] * S + U[:, None] * E
d = E - S
perp = np.array([-d[1], d[0]]) / np.linalg.norm(d)
curve = straight + perp[None, :] * (0.85 * np.sin(np.pi * U) +
                                    0.22 * np.sin(3 * np.pi * U))[:, None]

NODES = {"diff": 18, "flow": 10, "mean": 1}
F = 150

fig, axes = plt.subplots(1, 3, figsize=(12.6, 4.9))
fig.subplots_adjust(left=0.02, right=0.98, top=0.80, bottom=0.10, wspace=0.10)
panels = [
    (axes[0], curve, DIFF, "Diffusion", "curved PF-ODE  ·  35 model calls", NODES["diff"]),
    (axes[1], straight, FLOW, "FlowCast", "straight-line flow  ·  ~10 calls", NODES["flow"]),
    (axes[2], straight, MEAN, "MeanFlow", "average velocity  ·  1 call", NODES["mean"]),
]
dots, trails, nodescat = [], [], []
for ax, path, col, name, sub, nn in panels:
    ax.scatter(prior[:, 0], prior[:, 1], s=7, c=NOISE, alpha=0.45, lw=0)
    ax.scatter(targ_pts[:, 0], targ_pts[:, 1], s=7, c=MUTED, alpha=0.7, lw=0)
    ax.plot(*S, marker="o", ms=9, color=NOISE, mec="white", zorder=5)
    ax.plot(*E, marker="*", ms=18, color=DATA, mec="white", zorder=5)
    ax.text(S[0], S[1] - 0.42, "noise", ha="center", color=NOISE, fontsize=11)
    ax.text(E[0], E[1] + 0.30, "forecast", ha="center", color=DATA, fontsize=11)
    (trail,) = ax.plot([], [], color=col, lw=3.0, alpha=0.9, zorder=3)
    nodes_u = np.linspace(0, 1, nn + 1)
    nidx = (nodes_u * (len(path) - 1)).astype(int)
    nsc = ax.scatter(path[nidx, 0], path[nidx, 1], s=46, facecolors="white",
                     edgecolors=col, linewidths=1.8, zorder=4)
    (dot,) = ax.plot([], [], marker="o", ms=13, color=col, mec="white", zorder=6)
    dots.append((dot, path))
    trails.append((trail, path))
    nodescat.append((nsc, path, nidx, col))
    ax.set_title(name, color=col, fontsize=16, fontweight="bold", pad=16)
    ax.text(0.5, 1.015, sub, transform=ax.transAxes, ha="center",
            va="bottom", fontsize=11, color="#555")
    ax.set_xlim(-1.7, 1.8)
    ax.set_ylim(-1.9, 1.95)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_color("#dddddd")

fig.suptitle("Same noise, same forecast — the route is the dial",
             fontsize=18, fontweight="bold", y=0.965)


def update(frame):
    p = 0.5 - 0.5 * np.cos(np.pi * frame / (F - 1))  # ease 0->1
    k = int(p * (len(straight) - 1))
    arts = []
    for (dot, path), (trail, _), (nsc, _, nidx, col) in zip(dots, trails, nodescat):
        dot.set_data([path[k, 0]], [path[k, 1]])
        trail.set_data(path[:k + 1, 0], path[:k + 1, 1])
        fc = np.array([[1, 1, 1, 1]] * len(nidx))
        passed = nidx <= k
        from matplotlib.colors import to_rgba
        fc[passed] = to_rgba(col)
        nsc.set_facecolors(fc)
        arts += [dot, trail, nsc]
    return arts


anim = FuncAnimation(fig, update, frames=F, interval=40, blit=False)
save(anim, "anim_curved_vs_straight", fps=25)
plt.close(fig)
