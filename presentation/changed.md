# Review — `few_step_Stormcast_via_meanflow.pdf`

Grammar / fluency + content validation pass. Slide numbers are the PDF page
numbers (bottom-right of each slide). Validated against the repo ground truth:
`CLAUDE.md`, `experiment_scripts/results/.../scoreboard_3way.csv`, and
`presentation/citations.md`.

---

## A. High-impact content (defense risks) — fix first

- [ ] **Slide 41 shows the wrong table.** Title says *"Thresholds (3 km, grid)"*
  but the table header reads **"Neighbourhood kernel: 15 km"** and every value is
  identical to slide 42 — it is a duplicate of the 15 km table. The 3 km
  grid-scale results are missing. Regenerate slide 41 with the real 3 km kernel.

- [ ] **Method names are inconsistent across the results section** — the same
  model is called three different things:

  | Slide 39 (Overview) | Slide 40 (chart legend) | Slides 41–43 |
  |---|---|---|
  | EDM diffusion | stormcast (192×96) | stormcast (192×96) |
  | FlowCast (K=10) | I-CFM (10 NFE) | I-CFM |
  | Legacy EDM (224×128) | stormcast (224×128) | — |
  | MeanFlow (K=1/2) | MeanFlow (1/2 NFE) | MeanFlow (1/2 NFE) |

  "FlowCast" ↔ "I-CFM", "EDM diffusion" ↔ "stormcast (192×96)", and "K=10" ↔
  "10 NFE" are the same things. Pick one scheme (recommend the slide-39 names)
  and apply everywhere.

- [ ] **Dataset slide (17) has the wrong citation.** Footer
  *"Perrone Ribeiro & Faganeli Pucer (2025), arXiv"* is the **FlowCast** paper,
  copy-pasted onto an ERA5/RWRF/QPEPRE slide. Replace with ERA5
  (Hersbach et al. 2020) / RWRF-NCDR, or remove it.

- [ ] **"Same / similar forecasting quality" overclaims (slides 45 & 47).**
  The scoreboard (slide 39) shows MeanFlow **CRPS 0.6710 (K=1) / 0.6093 (K=2)
  vs EDM 0.5537** — probabilistic skill is ~10–21% *worse*, and the deck itself
  lists "under-dispersion at K=1" as a failure mode. RMSE is competitive (K=2
  beats EDM on u10/v10/qpepre), so reword to: *"matches EDM on deterministic
  (RMSE) skill at ~10× lower cost; ensemble calibration (CRPS) lags slightly →
  future work."*

---

## B. Grammar / fluency (by slide)

- [ ] **4:** "per forecast steps" → "per forecast **step**"; "Precipitation is
  hard to predict yet on generative-based..." → "Precipitation **remains hard to
  predict, even for** generative forecasting models."
- [ ] **8:** "Changes in resolutions **has**" → "Changes in resolution
  **have**"; "mathematically stable" → "**numerically** stable" (CFL is a
  numerical-stability condition).
- [ ] **9:** "2,050 **Tb**" / "4,850 **Tb**" → "**TB**" (terabytes, not terabits).
- [ ] **10:** "8.333 **times of change**" → "a factor of 8.33×"; "~4821 more
  **expansive**" → "more **expensive**" (typo).
- [ ] **14:** "6-hour **roll out**" → "rollout".
- [ ] **15:** "**Solvenian**" → "Slovenia"; "**futures** frames" → "future frames".
- [ ] **17:** "Samples: 29976 samples" → "Samples: **29,976**".
- [ ] **25:** "Train a U-Net **learn**" → "Train a U-Net **to learn**".
- [ ] **27:** "learn **residual of next** timestep" → "learn **the residual of
  the next** timestep".
- [ ] **29:** "between 0 **to** 1" → "between 0 **and** 1".
- [ ] **31:** "Rearrangement, **is** (r, t) is set to (0, 1) it is..." →
  "Rearranging: **if** (r, t) = (0, 1), it becomes a one-step evaluation."
- [ ] **32:** title "MeanFlow **Indentity**" → "**Identity**"; "w.r.t. **to** r"
  → "w.r.t. r"; "Hence, **integrate is killed**" → "Hence, the **integral is
  eliminated**."
- [ ] **33:** "total derivative **to** r" → "w.r.t. r".
- [ ] **37:** units "ms-1" → "**m s⁻¹**" ("ms-1" reads as per-millisecond);
  "mismatches qpepre's domain" → "(different qpepre grid/encoding)".
- [ ] **45:** "applied **by** similar use case **that** computational usage is a
  concern" → "applied **to** similar use cases **where** compute is a concern";
  "Heavy rain still **under-detection**" → "under-detected"; "Under-dispersion
  at K=1**, **K=2 is recommended" → "…at K=1**; **K=2 recommended."
- [ ] **47:** "Apply to **application of** lower time/space resolution" → "Apply
  to lower-resolution settings"; "~10 **times**" → "~10×".

---

## C. Minor / notation / consistency

- [ ] **35:** `p(M_{t+1}|M_t,S_t) = r_{t+1} + μ_{t+1}` sets a *density* equal to
  a *field sum*. Write `M_{t+1} = μ_{t+1} + r_{t+1}`, with
  `M_{t+1} ∼ p(·|M_t,S_t)`.
- [ ] **31:** diagram labels ε at **t=1** / data at **t=0**, but slide 29 +
  "integrate t=0→1 from noise to data" imply the opposite. Math is correct
  either way — just make the noise↔t convention uniform.
- [ ] **20:** surface panel labeled "**s2m**" → "t2m" (slide-17 table uses t2m).
- [ ] **17 vs 21:** target written `X_t` on slide 17 but `X_{t+1}` on slide 21 —
  use `X_{t+1}` (the target is next-hour).
- [ ] **38 vs 41–43:** glossary uses CSI/HSS/FAR/FSS; result tables use lowercase
  csi/hss/far/fss — unify casing.
- [ ] **9:** double-check **"997 PetaFLOPS"** for Fugaku — standard FP64 is ≈537
  (peak) / 442 (Rmax) PF; 997 doesn't match a common figure.
- [ ] **4:** the "50-member" ensemble is hypothetical while StormCast (slide 14)
  is 5-member — add "e.g." to avoid the apparent clash.
- [ ] **1:** the date field (日期：) is empty.

---

## D. Validated correct (no change needed)

- **MeanFlow derivation (30–34)** is mathematically sound — verified
  `(t−r)u = z_t − z_r ⇒ u = v + (t−r)·du/dr` and `du/dr = v·∂_z u + ∂_r u`;
  the loss target matches the codebase.
- **Arithmetic:** 35×50×24 = 42,000 ✓; 8.33⁴ ≈ 4,822 ✓; log1p example
  (0.81; 0.60 vs 0.009) ✓.
- **Scoreboard (39)** matches the repo CSVs exactly; speedups 12.1× / 9.6× /
  3.7× check out.
- **Citations** (GenCast 2312.15796, StormCast 2408.10958, FlowCast, MeanFlow
  2505.13447) all correct.
- **Dataset specs** (24 LowRes / 4 HighRes channels, lat/lon, 29,976 =
  21,216 + 8,760) and **distribution stats** (slide 18 means/stds) match
  `CLAUDE.md`.

---

## E. Notes on fixing

- Items **A1, A2, and the C-casing** trace back to repo-generated assets under
  `experiment_scripts/` (threshold tables, rollout chart legend, metrics
  glossary) — fixable at the source and re-exported.
- The deck (50-page PDF) appears built from Google Slides / PPTX, **not**
  directly from `presentation.md`, so the B/C text edits need to be applied in
  the deck's own source.
