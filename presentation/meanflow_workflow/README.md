# MeanFlow StormCast — workflow figures

Professional TikZ diagrams of the **core MeanFlow** distillation method (average-velocity
flow matching on the frozen-regression residual), drawn to match the thesis figure style
(viridis palette + `standalone` → `pdflatex` → PNG, same pipeline as `../formulas/`).

| File | What it shows |
|---|---|
| `meanflow_training.png` / `.pdf` | One **training step**: batch → frozen regression mean `M_t=F_ξ(X_{t-1},S_t,I)` → residual `R_t=X_t−M_t` → flow-space setup → MeanFlow-identity (25 %, JVP stop-grad) vs I-CFM (75 %) targets → single forward `u_θ(z_r,r,t,c_t)` → adaptive velocity-matching loss + qpepre spectral loss → AdamW + EMA → `ema_state.pt`. |
| `meanflow_inference.png` / `.pdf` | One **autoregressive inference step**: regression mean → condition `c_t=concat(X_{t-1},M_t,I)` → latent `z_0∼N(0,I)` → 1–2 NFE average-velocity sampler `z_{(i+1)/K}=z_{i/K}+\tfrac1K u_θ` → de-standardize `R̂_t=σ_data z_1` → compose `X̂_t=M_t+R̂_t` (expm1 for qpepre) → autoregressive feedback. EMA student weights. |

Notation follows the thesis formula deck (`../formulas/`): `X_{t-1}` = previous HighRes state,
`M_t` = regression mean, `c_t` = conditioning bundle. (In the code the same tensors are named
`M_t` for the state and `μ_{t+1}` for the mean — only the symbols differ.)

## Rebuild

```bash
./build.sh                       # both figures, 600 dpi PNG + PDF
DPI=300 ./build.sh meanflow_inference   # one figure at a custom DPI
```

Sources live in `src/` (`meanflow_training.tex`, `meanflow_inference.tex`, shared
`mf_style.tex`). Requires `pdflatex` (TeX Live: `standalone`, `tikz`, `pgfplots`) and
`pdftocairo` (poppler) — both already used by `../formulas/build_formulas.py`.
