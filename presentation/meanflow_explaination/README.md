# MeanFlow explanation — "from flow matching to the objective"

A compact, **non-tedious** introduction to the MeanFlow training objective for the
thesis / defense: it starts from the straight-line flow-matching objective the
FlowCast baseline already uses and shows MeanFlow is its *strict one-equation
generalisation* (the diagonal `r = t` collapses exactly onto flow matching).

Convention used throughout (the repo's mirror of Geng et al. 2025): flow time
`τ ∈ [0,1]` with `τ = 0` at noise and `τ = 1` at data; the field is evaluated at
the **lower** edge `z_r` and differentiated w.r.t. `r` at fixed `t`
(JVP tangent `(v, 1, 0)`). Working space is the standardized residual
`x₁ = R / σ_data`, matching the EDM teacher and FlowCast student.

## What's here

| File | What it is |
|---|---|
| [`meanflow_from_flowmatching.tex`](meanflow_from_flowmatching.tex) | The narrative. Self-contained article (3-page PDF): §1 flow matching → §2 average velocity → §3 the MeanFlow identity → §4 the loss → §5 sampling, plus a provenance paragraph. This is the prose+equations to lift into the thesis / slide narration. Compile with **two** `pdflatex` passes (or `latexmk -pdf`) so the `\eqref` cross-references resolve — a single pass prints `(??)`. |
| `meanflow_from_flowmatching.pdf` | Compiled output. |
| [`individual_equations/`](individual_equations/) | Each equation in the chain as a standalone slide PNG (black + white), built like the deck's [`../formulas/`](../formulas/). |

## Individual equations (slide assets)

`individual_equations/build_equations.py` is the single source of truth: one
ordered manifest, zero-padded stems so the directory lists in derivation order,
bodies matching `meanflow_from_flowmatching.tex` equation-for-equation.

```bash
cd individual_equations
python3 build_equations.py            # build all 14
python3 build_equations.py 08_mf_identity   # or a subset
```

Outputs (600-dpi, transparent):

- `src/<stem>.tex` — standalone LaTeX source (black text)
- `png/<stem>.png` — black text, for light slides
- `png_white/<stem>.png` — white text, for dark slides

The chain, in order:

| Stem | Equation |
|---|---|
| `01_fm_path` | Straight-line interpolant `z_τ = (1−τ)x₀ + τx₁` |
| `02_fm_velocity` | Instantaneous velocity `v = x₁ − x₀` (constant) |
| `03_fm_loss` | Conditional flow-matching loss (the FlowCast head) |
| `04_fm_sampler` | Euler sampler — the `K≈10`-step cost we remove |
| `05_mf_avgvel` | Average velocity `u = (t−r)⁻¹ ∫ v dτ` |
| `06_mf_displacement` | One algebraic jump `z_t = z_r + (t−r)u` |
| `07_mf_integral` | Cleared relation `(t−r)u = ∫ᵣᵗ v dτ` |
| `08_mf_identity` | **The MeanFlow identity** `u = v + (t−r) du/dr` |
| `09_mf_jvp` | Total derivative = one JVP, tangent `(v,1,0)` |
| `10_mf_boundary` | `r→t` recovers flow matching exactly |
| `11_mf_target` | Bootstrap target `u_tgt` (the target line of the loss) |
| `12_mf_loss` | **The MeanFlow loss** — verbatim thesis Eq. (3.13), with `sg(u_tgt)` + `λ_spec L_spec` |
| `13_mf_weight` | Adaptive per-sample weight `w` |
| `14_mf_sampler` | One/two-step sampler + field reconstruction |

## Background / provenance

Notation here is kept identical to the thesis and the implementation, so the
slides, the handout, and the methods chapter all read the same.

**In the thesis** (`des_master_thesis/`):
- [`contents/chapter03.tex`](../../contents/chapter03.tex) §"The MeanFlow Residual"
  — the canonical derivation (average velocity, identity, loss, sampler) and the
  precipitation loss design this note condenses.
- [`contents/chapter02.tex`](../../contents/chapter02.tex) §"Flow Matching,
  FlowCast, and MeanFlow" — the background CFM theory MeanFlow generalises.

**In the code** (`stormcast/`):
- [`utils/meanflow_loss.py`](../../../stormcast/utils/meanflow_loss.py) (`MeanFlowLoss`)
  — the objective, JVP target, batch split, adaptive weight, spectral term.
- `utils/trainer_meanflow.py`, `utils/meanflow_precond.py`,
  `meanflow_model_forward` in `utils/nn.py`, configs
  `config/{training,model}/meanflow.yaml`.
- Long-form notes: [`docs/meanflow.tex`](../../../stormcast/docs/meanflow.tex) / `docs/meanflow.md`.

**Papers:**
- Geng et al., *Mean Flows for One-step Generative Modeling*, 2025 —
  [arXiv:2505.13447](https://arxiv.org/abs/2505.13447) (the objective and identity;
  note the data-at-0 sign convention differs from the thesis's noise→data one).
- Yang & Xue, *MeLISA: Towards Scalable One-step Generative Modeling for
  Autoregressive Dynamical System Forecasting*, 2026 —
  [arXiv:2605.05540](https://arxiv.org/abs/2605.05540) (pixel-space MeanFlow for
  autoregressive physical dynamics — the same one-step-rollout motivation).
