"""Why curvature costs steps. A solver approximates a path by K straight Euler
hops. On a CURVED diffusion ODE, few hops cut the corner badly (big error);
you need many hops to hug the curve. On a STRAIGHT-line flow, ONE hop is already
exact. The animation sweeps K = 1,2,3,4,6,8,12,20 and prints the worst-case gap.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from _anim_common import save, DIFF, FLOW, INK

S = np.array([0.0, 0.0])
E = np.array([1.0, 1.0])
U = np.linspace(0, 1, 400)
straight = (1 - U)[:, None] * S + U[:, None] * E
d = E - S
perp = np.array([-d[1], d[0]]) / np.linalg.norm(d)
curve = straight + perp[None, :] * (0.62 * np.sin(np.pi * U))[:, None]

Ks = [1, 1, 2, 2, 3, 4, 6, 8, 12, 20]   # repeats = hold frames
FRAMES_PER_K = 9


def euler_nodes(path, K):
    idx = (np.linspace(0, 1, K + 1) * (len(path) - 1)).astype(int)
    return path[idx]


def max_gap(path, poly):
    # worst distance from true path samples to the polyline approximation
    seg = poly[1:] - poly[:-1]
    gaps = []
    for pt in path:
        t = np.clip(((pt - poly[:-1]) * seg).sum(1) /
                    (seg ** 2).sum(1).clip(1e-9), 0, 1)
        proj = poly[:-1] + t[:, None] * seg
        gaps.append(np.min(np.linalg.norm(proj - pt, axis=1)))
    return max(gaps)


fig, (axc, axs) = plt.subplots(1, 2, figsize=(11.6, 5.6), sharex=True, sharey=True)
fig.subplots_adjust(left=0.05, right=0.97, top=0.84, bottom=0.08, wspace=0.12)
for ax, path, col, name in [(axc, curve, DIFF, "Diffusion — curved path"),
                            (axs, straight, FLOW, "Flow matching — straight path")]:
    ax.plot(path[:, 0], path[:, 1], color=col, lw=3.5, alpha=0.35, zorder=1)
    ax.plot(*S, "o", ms=11, color="#9AA0A6", mec="white", zorder=5)
    ax.plot(*E, "*", ms=20, color=INK, mec="white", zorder=5)
    ax.set_title(name, color=col, fontsize=15, fontweight="bold", pad=10)
    ax.set_xlim(-0.18, 1.18); ax.set_ylim(-0.18, 1.32)
    ax.set_xticks([]); ax.set_yticks([])

cpoly, = axc.plot([], [], "-o", color=DIFF, lw=2.4, ms=7, mfc="white", zorder=4)
spoly, = axs.plot([], [], "-o", color=FLOW, lw=2.4, ms=7, mfc="white", zorder=4)
ctxt = axc.text(0.04, 1.18, "", fontsize=13, color=DIFF, fontweight="bold")
stxt = axs.text(0.04, 1.18, "", fontsize=13, color=FLOW, fontweight="bold")
sup = fig.suptitle("", fontsize=17, fontweight="bold", y=0.965)


def update(frame):
    K = Ks[(frame // FRAMES_PER_K) % len(Ks)]
    cp, sp = euler_nodes(curve, K), euler_nodes(straight, K)
    cpoly.set_data(cp[:, 0], cp[:, 1])
    spoly.set_data(sp[:, 0], sp[:, 1])
    cg, sg = max_gap(curve, cp), max_gap(straight, sp)
    ctxt.set_text(f"K = {K} steps   ·   error = {cg:.2f}")
    stxt.set_text(f"K = {K} steps   ·   error = {sg:.3f}")
    sup.set_text(f"Approximate the path with K straight hops   (K = {K})")
    return [cpoly, spoly, ctxt, stxt, sup]


anim = FuncAnimation(fig, update, frames=FRAMES_PER_K * len(Ks),
                     interval=110, blit=False)
save(anim, "anim_integration_error", fps=12)
plt.close(fig)
