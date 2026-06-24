# Chapter 3 equations — every displayed equation as PNG + LaTeX

All **17** displayed equations of the thesis methods chapter
([`../../contents/chapter03.tex`](../../contents/chapter03.tex)), exported as
standalone slide assets. Unlike [`../formulas/`](../formulas/) and
[`../meanflow_explaination/`](../meanflow_explaination/) (hand-curated manifests),
this set is **auto-extracted** straight from the chapter, so it stays in sync —
re-run the builder after editing the chapter and the PNGs/sources regenerate.

The thesis's own math macros (`\Ebb`, `\Nbb`, `\Freg`, `\vnet`, `\unet`, … from
`ntusetup.tex`) are injected into each standalone preamble, so every symbol
renders identically to the compiled thesis (e.g. `\Freg → F_ξ`, `\unet → u_θ`).

## Build

```bash
python3 build_chapter3_equations.py            # extract + build all 17
python3 build_chapter3_equations.py --list     # print stem -> label + body
python3 build_chapter3_equations.py 13_meanflow_loss   # build a subset
```

Outputs (600-dpi, transparent):

- `src/<stem>.tex` — standalone LaTeX source (black text)
- `png/<stem>.png` — black text, for light slides
- `png_white/<stem>.png` — white text, for dark slides
- `manifest.txt` — `stem → thesis \label`, regenerated each run

## Naming

Stems are `NN_<name>` in document order. `<name>` is the thesis `\label`
(`eq:meanflow-identity → meanflow_identity`); the few unlabelled equations get a
content-based friendly name (`regression_mean`, `conditioning`, `heun_step`,
`channel_norm`, `logpsd`).

| # | Stem | Equation (chapter 3) |
|---|---|---|
| 01 | `regression_mean` | `M_t = F_ξ(X_{t-1}, S_t, I)` |
| 02 | `hr_stats` | HighRes per-channel mean / std |
| 03 | `conditioning` | `c_t = concat(X_{t-1}, M_t, I)` |
| 04 | `flowcast_path` | I-CFM straight-line interpolant |
| 05 | `flowcast_precond` | FlowCast velocity / SongUNet preconditioner |
| 06 | `flowcast_loss` | FlowCast CFM loss + spectral term |
| 07 | `flowcast_sampler` | FlowCast Euler sampler |
| 08 | `heun_step` | 2nd-order Heun update |
| 09 | `meanflow_avgvel` | average velocity definition |
| 10 | `meanflow_displacement` | one-jump displacement |
| 11 | `meanflow_identity` | **the MeanFlow identity** |
| 12 | `meanflow_jvp` | total derivative = JVP |
| 13 | `meanflow_loss` | **the MeanFlow loss (Eq. 3.13)** |
| 14 | `meanflow_precond` | MeanFlow two-time preconditioner |
| 15 | `meanflow_sampler` | MeanFlow one/two-step sampler |
| 16 | `channel_norm` | channel-weighted L2 norm |
| 17 | `logpsd` | radial log-PSD regulariser |

(Authoritative ordering and labels are in `manifest.txt`.)

---

## Narrating MeanFlow: average velocity → the loss

A speaker's path through equations **09 → 13** for the defense. The throughline in
one sentence: *FlowCast learns the velocity at each instant and must integrate it;
MeanFlow learns the **average** velocity over a whole interval, so one evaluation
jumps the path — and that average is trainable through a single differential
identity that collapses back to flow matching.* Reveal the equations in order;
each beat is one slide.

**1. What we want — the average velocity.** `png/09_meanflow_avgvel.png`
> *Say:* "FlowCast learns the instantaneous velocity `v`. MeanFlow learns `u(z_r,r,t)`
> — the **average** velocity over the interval `[r,t]`." Point at the limit on the
> right (`lim_{t→r} u = v`): "when the interval shrinks to nothing, the average *is*
> the instantaneous velocity." Park that — it's the punchline two slides later.

**2. Why it's worth it — one jump, no solver.** `png/10_meanflow_displacement.png`
> *Say:* "If you know the average velocity, transport is one line of algebra: start,
> plus interval length times average velocity, equals destination. No ODE, no Euler
> steps. One evaluation at `(r,t)=(0,1)` takes noise straight to data." Sell the
> payoff *before* the difficulty.

**3. The catch, and the trick — the identity.** `png/11_meanflow_identity.png`
> *Say:* "The average is an integral we can't evaluate during training. So we don't
> evaluate it — we **differentiate** it. Clear the denominator, differentiate in `r`
> at fixed `t`, and the integral drops out, leaving the **MeanFlow identity**:
> `u = v + (t−r)·du/dr`." Stress the move: "an intractable integral became a local
> derivative — `u` defined using only `v`, which we have, plus a derivative of `u`
> itself."

**4. Why that derivative is cheap — one JVP.** `png/12_meanflow_jvp.png`
> *Say:* "That's a *total* derivative along the trajectory — a single
> Jacobian–vector product with tangent `(v,1,0)`: move the point at velocity `v`,
> advance `r`, hold `t` fixed. One extra forward pass, no second-order gradients."
> Keep it to a sentence — the audience needs *cheap*, not the AD mechanics.

**5. It's not a new objective — flow matching is the boundary.** (back to eq 09's limit)
> *Say:* "Set `r = t`. The correction `(t−r)·du/dr` vanishes and `u = v` — the
> objective is **exactly** flow matching. MeanFlow is FlowCast plus a finite-interval
> correction, and three-quarters of every training batch trains on this boundary."
> This is the controlled-comparison hook: MeanFlow-vs-FlowCast is an A/B on the
> correction alone.

**6. The objective.** `png/13_meanflow_loss.png` *(this is thesis Eq. 3.13)*
> *Say:* "Train the network to satisfy its own identity: regress `u_θ` onto the
> right-hand side `u_tgt`, **frozen with a stop-gradient** so the target is a fixed
> constant. `sg(w)` is an adaptive weight that down-weights hard samples; the last
> term is the precipitation log-PSD penalty inherited from FlowCast." Close on cost:
> "no teacher, one training run from scratch — and at inference it samples in **one
> or two** network calls (`15_meanflow_sampler`), then `X̂_t = M_t + σ_data·z_1`."

**If asked about signs.** The paper (Geng et al.) puts data at `s=0` and gets
`u = v − (t−r)·du/dt`; the thesis runs noise→data (`s=1`), so the derivative goes
through the lower limit and the sign flips — same identity, mirrored convention.

The longer written version of exactly this arc (with the FlowCast lead-in) is
[`../meanflow_explaination/meanflow_from_flowmatching.tex`](../meanflow_explaination/meanflow_from_flowmatching.tex).
