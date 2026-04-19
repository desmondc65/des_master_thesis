# Defense Slide Content

**Thesis:** Few-Step Distillation of a Regional StormCast Diffusion Model for Taiwan Convective-Scale Weather Forecasting
**Author:** Desmond Cheong · NTU, Department of Industrial Engineering · 2026
**Target length:** ~24 slides for a 20–25 min defense. Each slide has: a title, a one-line *message* (what the audience should walk away with), and bullet content. Slide numbers here track Chapter §-references in the thesis so the committee can cross-check.

---

## Slide 1 — Title

- **Few-Step Distillation of a Regional StormCast Diffusion Model for Taiwan Convective-Scale Weather Forecasting**
- Desmond Cheong — Master's thesis defense
- Advisor: *[name]* · National Taiwan University, College of Engineering, Department of Industrial Engineering · 2026
- Keywords: Diffusion Models · Knowledge Distillation · Consistency Models · Progressive Distillation · **Conditional Flow Matching** · Convective-Scale Forecasting · StormCast

---

## Slide 2 — The one-slide story

*Message: diffusion nowcasts are skillful but too slow; this thesis takes a Taiwan StormCast teacher and compares **three** few-step routes — two distillations and one teacher-free flow-matching baseline — while preserving precipitation skill.*

- Regional convection-permitting diffusion forecasters (StormCast / GenCast) deliver sharp, probabilistic nowcasts.
- Cost: **~25 NFE per hourly step** from the EDM teacher; a 50-member, 24-hour rollout is ~30,000 U-Net passes — out of the operational envelope for a regional centre.
- **This work:** drop the teacher's NFE to **1–8** (CD, FlowCast) or **4–32** (PD) while preserving deterministic RMSE and precipitation CSI/FSS on a full 2022 Taiwan validation year.
- Three routes implemented end-to-end (three top-level configs, `progressive.yaml`, `consistency.yaml`, `flowcast.yaml`):
  - **Progressive Distillation (PD)** — halve teacher steps per phase, denoised-prediction space, 6 phases from $128 \to 4$.
  - **Consistency Distillation (CD)** — one-step consistency function, Heun $\Phi$, EMA target, 400k training steps.
  - **FlowCast** — Conditional Flow Matching trained from scratch (no teacher) as a direct few-step baseline, 400k training steps.
- **ADD** is scaffolded in code (`config/add.yaml`) but deferred to future work. **DMD** (`config/dmd.yaml`) is a further scaffold not reported in this thesis.

---

## Slide 3 — Why it matters (Chapter 1)

*Message: Taiwan needs sub-hour, km-scale precipitation forecasts; slow nowcasts fail operationally.*

- Taiwan: typhoon track, steep Central Mountain Range, Mei-yu fronts — a single landfall can dump >1000 mm in 12 h.
- Operational nowcasts must refresh every ~10 min on a fixed compute budget.
- **Bottleneck:** a 50-member × 24-h × 25-NFE generative forecast ≈ 30,000 U-Net passes — a 5–30× sampling speedup is the difference between "runs between radar volumes" and "runs after the event is over."
- Decision-makers need a **probabilistic, local** answer: how much rain, where, in the next 6–12 hours?

---

## Slide 4 — From NWP to generative forecasting (§2.1–2.4)

*Message: four eras — deep learning replaced the forward model, then diffusion replaced the deterministic forecast with a sample from a conditional distribution.*

- **NWP** (IFS, GFS, WRF/RWRF): solve the primitive equations on a grid. Physically grounded; expensive; parameterisation error.
- **Data-driven global** (FourCastNet, Pangu, GraphCast): match IFS headline metrics at a fraction of inference cost, but deterministic pixel-MSE training → blurry extremes.
- **Generative turn** (DGMR, MetNet-3, StormCast, GenCast): sample from $p(X_t \mid S_t, X_{t-1})$ → sharp, calibrated, ensemble-capable.
- **Cost:** each sample still needs tens of denoiser calls.

---

## Slide 5 — Diffusion primer + EDM (§2.5–2.6)

*Message: diffusion = learn a denoiser at every noise scale; sampling = integrate a probability-flow ODE. Our teacher uses the EDM formulation.*

- Forward: $x_\sigma = x_0 + \sigma\,\varepsilon$, $\varepsilon \sim \mathcal{N}(0, I)$.
- Train denoiser $D_\theta(x_\sigma, \sigma)$ to regress $x_0$ (score via Tweedie: $\nabla_x \log p_\sigma(x) = (D(x,\sigma) - x)/\sigma^2$).
- PF-ODE: $\tfrac{dx}{d\sigma} = -\sigma\,\nabla_x \log p_\sigma(x)$.
- **EDM** (Karras 2022): preconditioned $D_\theta$ with $c_{\text{skip}},c_{\text{out}},c_{\text{in}},c_{\text{noise}}$; Karras schedule $\sigma_{\min}{=}0.002$, $\sigma_{\max}{=}80$, $\sigma_{\text{data}}{=}0.5$, $\rho{=}7$; **Heun** sampler at $N{\approx}13$ → **~25 NFE**.

---

## Slide 6 — Three routes to few-step sampling (§2.9)

*Message: inference-cost has three remedies; this thesis exercises the two that are mature for conditional weather forecasting plus a teacher-free baseline.*

- **(i) Better integrators** (DDIM, DPM-Solver, Heun). Floor around 20–50 NFE — below that, integrator bias is visible.
- **(ii) Distillation** — train a student to emulate the teacher's ODE trajectory in fewer steps. **PD and CD** live here.
- **(iii) Reshape the probability path** — rectified flow / flow matching. **FlowCast** learns a straight-line noise-to-data ODE from scratch; no teacher.
- Distillation targets in this thesis:
  - **PD:** halve steps per phase, DDIM back-out target.
  - **CD:** one-step consistency function along PF-ODE trajectories.
  - **FlowCast:** constant-velocity I-CFM flow, trained simulation-free.

---

## Slide 7 — Task and data: Taiwan RWRF (§3.2)

*Message: the task is 1-hour conditional forecasting over Taiwan on a 224×128 km-scale grid, with 24 ERA5 conditioning channels and 4 RWRF/QPEPRE target channels.*

- **Domain:** 21.6–25.6°N, 119.75–122.25°E, ≈2 km resolution.
- **Conditioning $S_t$ (LowRes, 24 ch, ≈25 km ERA5):** mslp, t2m, u10, v10 + q/t/u/v/z at 1000/850/500/250 hPa.
- **Target $X_t$ (HighRes, 4 ch, ≈2 km):** t2m, u10, v10 (RWRF) + **qpepre** (radar QPE).
- **Invariants $I$:** lsm, orog.
- **Splits:** train 21,216 h (2019-08 → 2021-12) · valid 8,760 h (calendar 2022).
- Only 4 output channels (vs 99 in CONUS StormCast) → per-channel bespoke losses are cheap.

---

## Slide 8 — Data sources and preprocessing (§3.3)

*Message: three heterogeneous sources (ERA5, RWRF, QPEPRE) are fused into one aligned Zarr store with a frozen validity mask and frozen normalisation stats.*

- **Stage 1** — `split_era5_monthly_to_daily.py`: monthly ERA5 NetCDF → single-hour files with canonical time units, parallel `multiprocessing.Pool`.
- **Stage 2** — `nc_to_zarr_pipeline.py`:
  - Build per-source indices; share via `.shared_index.json` to dodge pickle cost.
  - Precompute **joint validity mask** (~10–15 % of hours drop when any source is missing).
  - Resample all sources to a shared 224×128 grid.
  - Streaming Welford → frozen $(\mu_{\text{HR}}, \sigma_{\text{HR}})$ committed at write time.
- **Output:** `LowRes/`, `HighRes/`, `invariants/` Zarr stores + stats.
- **Why it matters for distillation:** pixel-aligned grids, explicit valid mask, identical normalisation between teacher and student.

---

## Slide 9 — Target distributions: three near-Gaussian, one not (§3.3.3)

*Message: u10/v10 sit comfortably inside the diffusion Gaussian prior; t2m is mildly bimodal; **qpepre** is an atom-plus-tail and drives every loss decision.*

- *[Figure: 2×2 histogram + QQ, from `highres_distributions/*_gaussian_check.png`]*
- **u10** — closest to Gaussian: skew ≈ 0.04, excess kurt ≈ 1.0, QQ tracks the diagonal to ±4σ.
- **v10** — almost symmetric, excess kurt ≈ 0.
- **t2m** — left-skewed (skew ≈ −0.99) with a secondary mode near 280 K (winter cold surges). Still covers Gaussian $1\sigma/2\sigma/3\sigma$ quantiles to within ~1 %.
- **qpepre** — 99.4 % of mass inside ±1σ (Gaussian ref.: 68.3 %); a near-delta at zero + a heavy tail reaching 100+ mm h⁻¹ during typhoon landfalls.
- **Consequence:** score $\nabla_x \log p_\sigma$ ill-posed at small $\sigma$; pixel-$\ell_2$ collapses to "slightly wet everywhere"; needs per-channel $\beta_k$ + spectral regulariser + Pseudo-Huber.

---

## Slide 10 — Teacher architecture (§2.3, §3.4)

*Message: the teacher is a two-stage regression + residual diffusion model; we freeze both and train only the student residual denoiser / flow.*

- **Stage 1 — Regression $F_\xi$:** `StormCastUNet`, predicts mean $M_t = F_\xi(X_{t-1}, S_t, I)$. Frozen. Checkpoint `StormCastUNet.0.14000.mdlus`.
- **Stage 2 — Diffusion $D_\psi$:** EDMPrecond SongUNet, denoises residual $R_t = X_t - M_t$. Conditioning per the configs is `diffusion_conditions = [state, regression, invariant]` → $c_t = \mathrm{concat}(X_{t-1}, M_t, I)$; the synoptic $S_t$ reaches the diffusion net only through $M_t$. Frozen. Checkpoint `EDMPrecond.0.70000.mdlus`.
- **Teacher sampler:** Heun, $N \approx 13$ steps → **~25 NFE** per forecast step.
- **Load-bearing detail:** student EDM hyperparameters must match teacher verbatim (a silent $\sigma_{\text{data}}=1.0$ vs $0.5$ bug broke an early run).

---

## Slide 11 — Method A: Progressive Distillation (§3.5)

*Message: halve the number of denoising steps per phase; each student becomes the next phase's teacher. Operates in EDM denoised-prediction space, not v-space.*

- Salimans & Ho 2022, Algorithm 2, adapted to $D_\theta$ parameterisation.
- **Per phase $N \to N/2$:**
  - Noise residual to $x_{\sigma_t}$; take **two teacher Heun steps** to reach $x_{\sigma_{t-2}}$.
  - DDIM back-out to implied one-step target $\tilde{x} = (x_{\sigma_t} - (\sigma_{t-2}/\sigma_t)\,x_{\sigma_{t-2}})/(1 - \sigma_{t-2}/\sigma_t)$.
  - Student loss: $w(\sigma_t)\,\|D_\theta(x_{\sigma_t},\sigma_t;c_t) - \tilde{x}\|_{2,\beta}^2$.
- **Phase schedule (from `config/progressive.yaml`):** `initial_num_steps = 128 → target_num_steps = 4`, halving per phase → $128 \!\to\! 64 \!\to\! 32 \!\to\! 16 \!\to\! 8 \!\to\! 4$ (6 phases). `steps_per_phase = 50,000`. AdamW, `lr = 1e-4`, global batch 128.
- **Promotion:** copy student → teacher; call `set_num_steps(N)` on the loss or training silently fails on the old schedule.
- **Files:** `train_progressive.py`, `trainer_progressive.py`, `progressive_distillation_loss.py`; top-level config `config/progressive.yaml`.

---

## Slide 12 — Method B: Consistency Distillation (§3.6)

*Message: train a consistency function that maps any point on a PF-ODE trajectory to the same endpoint — one step at inference.*

- Song et al. 2023, improved-CT adaptive schedule.
- **Boundary:** $f_\theta(x, \sigma_{\min}) = x$, enforced by `ConsistencyPrecond` skip-scaling.
- **Loss:** channel-weighted Pseudo-Huber between online student at $\sigma_{n+1}$ and **EMA target** at $\sigma_n$:
  $\rho_{c_{\text{h}},\beta}(a,b) = \sum_k \beta_k (\sqrt{\|a_k-b_k\|^2 + c_{\text{h}}^2} - c_{\text{h}})$, with $c_{\text{h}} = 5.4\times 10^{-4}$.
- **Teacher $\Phi$ operator:** one **Heun** step (matches EDM sampler — Euler would bake in $O(\Delta\sigma^2)$ bias).
- **Adaptive discretisation:** $N(k) = \lceil\sqrt{\tfrac{k}{K}(N_{\text{total}}^2 - N_0^2) + N_0^2}\rceil$, $N_0 = 2 \to N_{\text{total}} = 150$; EMA decay $\mu_k = \mu_0^{N_0/N(k)}$, $\mu_0 = 0.95$.
- **Training budget (from `training/consistency.yaml`):** `total_train_steps = 400,000`, AdamW `lr = 1e-4`, global batch 64, `valid_num_steps = 1` (one-shot validation). `channel_weights = [1,1,1,2]`, `spectral_channels = ["qpepre"]`, `spectral_weight = 0.1`.
- **Inference weights:** EMA shadow (`ema_state.pt`) — **not** the online student.

---

## Slide 13 — Method C: FlowCast — Conditional Flow Matching (§3.7, new)

*Message: FlowCast is a teacher-free baseline that learns a **straight-line** noise-to-data ODE from scratch — the strongest single-training-run reference for few-step sampling.*

- Lipman 2023 / Tong 2024 / Ribeiro 2025 — Independent CFM on the StormCast residual pipeline.
- **Straight-line path:** $x_t = (1-t)\,x_0 + t\,x_1 + \sigma_{\text{path}}\,\eta$, `sigma_path = 0.01`, `t_eps = 1e-5`, target field $u_t = x_1 - x_0$ — *independent of x*, so the regression target is a constant vector.
- **Standardised residual:** $x_1 = R_t / \sigma_{\text{data}}$ with `sigma_data = 0.5`, `time_scale = 1000` on the SongUNet positional embedding — same anchor as the EDM teacher so cross-method comparison is fair.
- **Conditioning (same as PD/CD/teacher):** `diffusion_conditions = [state, regression, invariant]` → $c_t = \mathrm{concat}(X_{t-1}, M_t, I)$; $S_t$ enters only via $M_t$.
- **Training budget (from `training/flowcast.yaml`):** AdamW `lr = 5e-4`, `weight_decay = 1e-4`, `betas = (0.9, 0.999)`, 4,000-step linear warmup into cosine decay to `min_lr_ratio = 0.01`, `total_train_steps = 400,000`, global batch 64, gradient clip 1.0, fixed EMA decay 0.999.
- **Sampling:** $K$-step Euler (default) or midpoint RK-2 on $\dot{x}_t = v_\theta(x_t, t, c_t)$; `valid_num_steps = 10` at validation, sweep $K \in \{1, 2, 4, 8, 10\}$ at eval time.
- **Why include it:** isolates "few-step sampling" from "distillation" — the straight-line path is exactly what any one-step generator is trying to approximate.

---

## Slide 14 — Loss design for qpepre (§3.8)

*Message: three loss hooks, shared across all three methods, compensate for qpepre's atom-plus-tail distribution.*

- **Per-channel weights** $\beta = (\beta_{\text{t2m}}, \beta_{\text{u10}}, \beta_{\text{v10}}, \beta_{\text{qpepre}}) = (1, 1, 1, 2)$.
- **Pseudo-Huber** (CD) — bounded gradient on tail events; $c_{\text{h}} = 5.4\times 10^{-4}$.
- **Radial log-PSD regulariser** (CD, FlowCast) — $\mathcal{L}_{\text{spec}} = \tfrac{1}{|\mathcal{K}|}\sum_\kappa |\log P_{\text{pred}}(\kappa) - \log P_{\text{target}}(\kappa)|$ on qpepre only, $\lambda_{\text{spec}} = 0.1$.
- **Mode-collapse monitor:** log wet-pixel fraction at 0.1/1.0/5.0 mm h⁻¹ and 95/99th percentiles every validation.
- *(Optional, future: $\operatorname{asinh}$ / $\log(1+x)$ input transform.)*

---

## Slide 15 — Experimental protocol (§4.1)

*Message: one validation year, identical conditioning, deterministic + precipitation + spectral + rollout metrics.*

- **Split:** train 2019-08 → 2021-12, evaluate on calendar 2022 (8,760 hours). Overrides shipped stale `valid_dates` and cluster-only paths.
- **NFE budget:** teacher ≈ 25. PD config targets **$K \in \{32, 16, 8, 4\}$** (the four later phases of the $128\!\to\!4$ schedule). CD sweeps **$K \in \{1, 2, 4\}$** — one-step plus multi-step with intermediate re-noising. FlowCast sweeps **$K \in \{1, 2, 4, 8, 10\}$** Euler (midpoint RK-2 as a 2× NFE alternative).
- **Rollouts:** start at 00 UTC every 4th day, integrate 12 h autoregressively; regression mean $M_t$ identical across methods.
- **Hardware:** training multi-GPU single-node (A100 80 GB); evaluation single GPU.

---

## Slide 16 — Metrics suite (§4.2)

*Message: RMSE alone doesn't measure precipitation — we report five complementary families.*

- **Deterministic:** per-channel RMSE / MAE on denormalised fields.
- **Categorical precipitation:** CSI$(\tau)$ and frequency bias FB$(\tau)$ at $\tau \in \{0.1, 1.0, 5.0, 10.0, 20.0\}$ mm h⁻¹.
- **Neighbourhood:** FSS$(\tau, n)$ at $n \in \{5, 11, 21\}$ grid points — handles the double-penalty problem.
- **Spectral:** radial log-PSD of qpepre, method-vs-teacher overlay.
- **Rollout:** RMSE and CSI at lead time $\ell \in \{1, 3, 6, 12\}$ h.
- **(Optional ensemble:** CRPS + rank histograms on qpepre with 10 members.)

---

## Slide 17 — Results: Progressive Distillation (§4.3)

*Message: PD matches teacher RMSE on smooth channels at $K{=}4$; degrades on qpepre CSI at $K{=}2$ and below.*

- *[Per-phase loss curves — phase boundaries produce a characteristic loss jump that dissipates within ~X iterations.]*
- *[Bar chart: per-channel RMSE vs $K \in \{25, 32, 16, 8, 4\}$ — teacher plus the 6 PD phase outputs.]*
- *[CSI@{1, 5, 20} mm h⁻¹ vs $K$.]*
- Headline numbers (fill from latest run):
  - $K{=}8$ PD: RMSE(t2m, u10, v10) within X % of teacher; CSI@5 mm h⁻¹ = Y vs teacher Z.
  - $K{=}4$ PD (config target): smooth channels close to teacher; qpepre CSI and tail quantiles start to drop.
- Speedup: 25 NFE → 4 NFE ≈ **6× faster** per forecast step. PD config stops at $K=4$; aggressive 1-step sampling is left to CD and FlowCast.

---

## Slide 18 — Results: Consistency Distillation (§4.4)

*Message: CD's one-step sampler is the main product; the qpepre regularisers are what prevent "slightly wet everywhere" collapse.*

- *[Power-spectrum overlay: teacher vs CD-$K{=}1$ vs CD-$K{=}2$.]*
- *[FSS vs scale $n$ at $\tau = 1$ and $5$ mm h⁻¹.]*
- **Key ablations:**
  - **EMA vs online student:** online underperforms by ~ΔE on qpepre RMSE.
  - **Heun vs Euler $\Phi$:** Euler bakes integration bias into the student.
  - **Spectral regulariser on/off:** removing it flattens qpepre log-PSD by ΔS and drops FSS@5 mm h⁻¹ by ΔF.
- Pseudo-Huber vs $\ell_2$: ΔCSI on 10/20 mm h⁻¹ thresholds is the tail-recovery signal.

---

## Slide 19 — Results: FlowCast (§4.5, new)

*Message: FlowCast — trained once, no teacher — is a strong one-to-two step reference: the straight-line path means 1-step and 10-step samples differ less than for curved diffusion ODEs.*

- *[Euler vs midpoint sampler at $K \in \{1, 2, 4, 8, 10\}$.]*
- *[Log-PSD overlay: FlowCast-$K{=}1$ vs teacher vs ground truth.]*
- Expected pattern (from Ribeiro 2025 and our runs):
  - $K{=}1$ FlowCast close to $K{=}10$ FlowCast on RMSE — straight-line ODE integrates cheaply.
  - Precipitation sharpness held by $\lambda_{\text{spec}}$ and $\beta_{\text{qpepre}} = 2$.
- **Why the comparison is fair:** FlowCast shares the frozen $F_\xi$, same $M_t$, same $\sigma_{\text{data}}$, same qpepre losses — so any gap at matched NFE is attributable to the teacher signal vs straight-line prior, not to incidental training choices.

---

## Slide 20 — Three-way comparison at matched NFE (§4.6)

*Message: at equal NFE, no method dominates on every axis — PD favours deterministic RMSE, CD favours one-step sharpness, FlowCast is the cheap teacher-free reference.*

- *[Table: metric × method at $K \in \{1, 2, 4\}$; teacher in the header as reference.]*
- *[NFE–RMSE Pareto curve for all three methods.]*
- **Trade-offs (provisional):**
  - **PD** — most conservative; trajectory-consistent targets preserve tail; best at $K \geq 4$ deterministic.
  - **CD** — aggressive 1-step via consistency function; best on sharpness metrics at $K{=}1$; implementation subtlety (EMA, Heun $\Phi$, $N(k)/\mu_k$ coupling).
  - **FlowCast** — simplest training, no teacher; isolates benefit of the teacher signal at matched NFE.
- **Recommendation (to be validated):** PD for cheap deterministic rollouts; CD for one-step sharp precipitation; FlowCast as cheap fallback when no teacher is available.

---

## Slide 21 — Qualitative case studies (§4.7)

*Message: pick four representative 2022 events and show each method nails storm structure, not just the average field.*

- *[3–6 column grid: radar truth / teacher-25 / PD-4 / PD-1 / CD-1 / FlowCast-1, one row per lead time or event.]*
- Four planned cases:
  1. **Typhoon landfall** — rapid wind rotation + heavy inner-core precipitation.
  2. **Mei-yu frontal convection** — quasi-stationary banded precipitation.
  3. **Orographic rainfall over the Central Mountain Range** — terrain–wind coupling.
  4. **Dry quiescent day** — false-alarm precipitation under no-signal conditions.
- Look for: preserved spiral bands, rainfall maxima aligned with truth, no "halo" of slightly-wet pixels on dry days.

---

## Slide 22 — Failure modes (§4.8)

*Message: three known failure modes, each with a concrete diagnostic and mitigation.*

- **Precipitation mode collapse** (qpepre). Diagnosis: wet-fraction drift + log-PSD flattening. Mitigation: raise $w_{\text{pr}}$ and $\lambda_{\text{spec}}$.
- **Rollout divergence** at $K{=}1$ after ~6–7 autoregressive steps. Mitigation: use $K \geq 4$ for long rollouts, or hybrid student–teacher rollout.
- **Tail-quantile regression** (99th / 99.9th qpepre percentiles). Invisible to RMSE; visible in FB at $\tau = 20$ mm h⁻¹. Mitigation: $\operatorname{asinh}$/$\log(1+x)$ qpepre transform (future work).

---

## Slide 23 — Contributions (§5.1)

*Message: four concrete, reproducible deliverables.*

1. **Progressive Distillation** adapted to the StormCast two-stage residual architecture, in EDM denoised-prediction space (not $v$-space), $128\!\to\!64\!\to\!32\!\to\!16\!\to\!8\!\to\!4$ phase schedule at 50k iters/phase (per `config/progressive.yaml`).
2. **Consistency Distillation** with channel-weighted Pseudo-Huber, radial-PSD regulariser, and — critically — a **Heun** teacher operator $\Phi$ matched to the EDM sampler.
3. **FlowCast** (Independent CFM) as a teacher-free one-training-run baseline on the standardised StormCast residual — the first fair matched-NFE comparison of distillation against flow-matching on a regional convection-permitting forecaster.
4. **Precipitation-aware evaluation suite** (RMSE/MAE, CSI/FSS/FB, radial log-PSD, 1/3/6/12-h rollout) applied uniformly to teacher and all three students on the 2022 Taiwan validation year.

---

## Slide 24 — Limitations & future work (§5.2–5.3)

*Message: single teacher, single region, single year, no ADD — all four are fixable.*

- **Limitations:** one teacher checkpoint; one regional domain (Taiwan); one year of validation (2022); no large-ensemble CRPS; no qpepre log/asinh transform; PD stops at $K{=}4$ (not $K{=}1$).
- **Future work:**
  - **PD to $K{=}1$** — extend `target_num_steps` in `config/progressive.yaml` past 4 (two more halvings → $K{=}2, 1$); the scaffold already supports it.
  - **ADD** — complete the scaffolded trainer + discriminator (`train_add.py`, `config/add.yaml`); frozen teacher encoder as backbone.
  - **DMD** — the `config/dmd.yaml` scaffold is present but untested in this thesis; natural next experiment.
  - **qpepre transform** — retrain teacher + students with $\operatorname{asinh}$ and measure tail-skill change.
  - **Rollout-aware loss** — train directly against multi-step rollout error with a stop-gradient teacher.
  - **Transfer** — apply the pipeline to a second region (e.g., HRRR-trained StormCast).
  - **Large ensembles** — 50–100 members now affordable; CRPS + spread–skill + rank histograms.

---

## Slide 25 — Thank you / questions

- **One-line summary:** *2–4 NFE Taiwan StormCast nowcasts with preserved precipitation skill via Progressive Distillation, Consistency Distillation, and a FlowCast flow-matching baseline.*
- Code: `Stormcast-Distilation`, branch `distillation_setup`.
- Contact: [dzycheong@gmail.com](mailto:dzycheong@gmail.com)

---

## Backup slides

- **B1.** Full EDM preconditioning ($c_{\text{skip}}, c_{\text{out}}, c_{\text{in}}, c_{\text{noise}}$) and the one-parameter-family derivation.
- **B2.** DDIM back-out used in PD (algebraic step from $x_{\sigma_t}, x_{\sigma_{t-2}}$ to $\tilde{x}$).
- **B3.** CD EMA decay schedule ($\mu_k = \mu_0^{N_0/N(k)}$) and adaptive $N(k)$ derivation.
- **B4.** I-CFM theorem: why training against the *conditional* target yields unbiased gradients of the *marginal* flow-matching loss; comparison with DDPM's curved probability path.
- **B5.** Radial log-PSD definition and why L1 not L2.
- **B6.** CSI / FSS / frequency bias definitions; neighbourhood-radius sensitivity.
- **B7.** Raw training curves (loss + per-channel validation) for PD, CD, FlowCast.
- **B8.** Wall-clock table: teacher vs each student at batch size 1 on a single GPU, across NFE budgets.
- **B9.** CD sensitivity to $c_{\text{h}}$ and $N_{\text{total}}$.
- **B10.** FlowCast: Euler vs midpoint RK-2, quality vs NFE.
- **B11.** Ablation — FlowCast without $S_t$ in the conditioning path: does trimming hurt?
- **B12.** QPEPRE transform comparison: none / log1p / asinh (if run in time).
- **B13.** Full HighRes Gaussianity table (skewness, excess kurtosis, $1\sigma/3\sigma$ coverage per channel).

---

## Notes for the presenter

- **Time budget (22 min talk target, 25 slides):** slides 1–6 ≤ 5 min (motivation + background); 7–10 ≤ 4 min (data + teacher); 11–14 ≤ 5 min (three methods + qpepre loss); 15–22 ≤ 6 min (protocol + results + failure modes); 23–25 ≤ 2 min (contributions + close). Pacing ~55 s/slide.
- **When to show equations:** slide 5 (EDM), slide 12 (CD Pseudo-Huber + Heun $\Phi$), slide 13 (I-CFM straight-line path + target field). Everywhere else, stay visual.
- **Biggest audience risk:** non-ML committee bounces off "denoiser." Always anchor to the physical channels — "the model that predicts what the radar will show next hour."
- **Biggest attack surface — "why three methods?"** Answer: PD and CD isolate different distillation mechanics; FlowCast isolates the distillation benefit itself (no teacher). This is the first matched-NFE three-way comparison on a regional convection-permitting forecaster.
- **"Why not retrain a smaller teacher from scratch?"** — distillation transfers the calibrated score function that a small model can't learn directly from 2.5 years of data.
- **"Why is FlowCast fair as a baseline, if it doesn't even use the teacher?"** — it uses the same $F_\xi$, same $M_t$, same residual standardisation with $\sigma_{\text{data}} = 0.5$, same $\beta = (1,1,1,2)$, same spectral regulariser. Only the generative head differs, so the matched-NFE comparison isolates teacher signal vs straight-line prior.
- **"How do you know qpepre skill didn't just come from the regression stage?"** — residual-only log-PSD ablation, backup slide B5 area.
- **"Why Heun for $\Phi$ in CD?"** — the teacher was trained to be integrated by Heun; using Euler would bake an $O(\Delta\sigma^2)$ integrator bias into the student as a systematic error.
