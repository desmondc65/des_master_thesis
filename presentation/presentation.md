# Master's Defense — Presentation Content

**Title:** *Few-Step MeanFlow Residuals for Convection-Allowing Forecasting over Taiwan*

**Author:** Desmond Cheong (鍾鎮嶸) · National Taiwan University, Graduate Institute of Networking and Multimedia, College of EECS · Advisor: Cheng-Fu Chou (周承復) · 2026

**Format:** 26 content slides + backup. Target **25–30 minutes** (~1 min/slide, results slides slightly longer).
**Audience:** thesis committee, some members new to diffusion / flow matching. Stay high-level; anchor every abstract idea to "the model that predicts what the radar shows next hour."

**Structure:** the deck follows a seven-part thesis arc —
**Introduction → Related Work → Dataset → Method → Experiments → Discussion → Conclusion.**
Each part is a `# Part N` header below; slides are numbered sequentially within the arc.

---

## How to read this file

Each slide has four blocks:

- **MESSAGE** — the one sentence the audience should remember.
- **ON SLIDE** — the bullets / visual that actually goes on the slide (keep it sparse).
- **SHOW** — the figure, animation, or rendered equation to display, with its file path.
- **SCRIPT** — what you say out loud (the "explanation script"). ~45–70 s each.

Asset locations (paths are from the **workspace root**):
- Thesis figures → [des_master_thesis/figures/](../figures/)
- Rendered equation PNGs → [des_master_thesis/presentation/formulas/png/](formulas/png/) (white-text versions in `formulas/png_white/`)
- Animations → [des_master_thesis/presentation/animations/out/](animations/out/) (`.gif` for PowerPoint/Keynote, `.mp4` for web)

A compact **slide → asset map** is in [README.md](README.md) (its numeric `#` column predates this seven-part
reorganization, but the slide titles and asset paths still resolve). A clean continuous narration with timing is
in [speaker_script.md](speaker_script.md).

---

# Part 1 — Introduction

## Slide 1 — Title

**MESSAGE:** A fast, sharp, probabilistic regional weather forecaster is possible by learning the *average velocity* of the noise→data path and jumping it in one or two network calls — MeanFlow.

**ON SLIDE**
- Title (above) + your name, advisor (Cheng-Fu Chou), institute (Networking & Multimedia, College of EECS), date.
- One-line subtitle: *"Making generative convective-scale forecasting fast enough to run between radar volumes."*
- **Research question:** *Can a single-run, teacher-free **average-velocity** residual (MeanFlow) cut generative sampling to **one or two network calls** — without losing the diffusion model's forecast skill?*
- Keywords: **Average-velocity flow matching (MeanFlow)** · Flow Matching · Diffusion · StormCast · Convective-scale precipitation · Taiwan RWRF.

**SHOW:** [taiwan_domain_rain_case.png](../figures/concepts/taiwan_domain_rain_case.png) faint as a title background.

**SCRIPT:**
Good morning, and thank you for being here. My thesis is about making *generative* weather forecasting fast enough to actually deploy. Diffusion models like StormCast and GenCast have become the state of the art for short-range, convective-scale forecasting — they are sharp and they are probabilistic — but they are slow to sample. I take a StormCast model trained on a Taiwan regional dataset and ask a simple question: instead of distilling a slow model into a fast one, can we just change the *shape of the path* the generative model takes from noise to a forecast? The method I propose is **MeanFlow** — it learns the *average* velocity over the whole noise-to-data interval, so a single network call jumps across it with no integration at all. I measure it against two baselines on the very same axis: the EDM diffusion model it sets out to accelerate, and FlowCast, the straight-line flow-matching special case that MeanFlow generalises. I'll show that MeanFlow recovers the diffusion model's forecast skill at about a tenth of the cost — in one or two calls, with no teacher and a single training run.

---

## Slide 2 — The one-slide story

**MESSAGE:** Problem: diffusion is skillful but ~35 model calls per step. Method (this thesis): learn the *average* velocity and jump the path in 1–2 calls — MeanFlow. Result: diffusion-level skill, ~9× cheaper, no teacher.

**ON SLIDE** (three columns: Problem → Method → Result)
- **Problem:** EDM diffusion baseline = **35 network calls per forecast step** → a 50-member, 24-h ensemble ≈ **42,000 U-Net passes**.
- **Method:** the diffusion path noise→data is *curved* (many steps). One axis fixes it: **straighten it** (FlowCast — the flow-matching baseline) and then **remove the integral entirely** by learning the *average velocity* — **MeanFlow**, the method of this thesis, **1–2 calls, no integration**.
- **Result:** at a matched training budget, **MeanFlow** reaches the diffusion baseline's deterministic + categorical skill class at **1–2 calls (~9× faster)**, with the best temperature in the study; the FlowCast baseline marks the midpoint — matched CRPS, better winds/precip RMSE and false alarms, **3.7× faster**.

**SHOW:** [anim_curved_vs_straight.gif](animations/out/anim_curved_vs_straight.gif)

**SCRIPT:**
Here is the whole talk on one slide. The problem is cost: the diffusion sampler needs about 35 neural-network evaluations for *one* forecast hour, and operational use multiplies that by the forecast horizon and the ensemble size — tens of thousands of passes per cycle. The reason it needs so many is that the path a diffusion model follows from random noise to a clean forecast is *curved*, and you can't shortcut a curve. So I think of a single axis along which to fix the path. Flow matching first makes it a *straight line*, which integrates in a handful of steps — that's FlowCast, and I keep it as the flow-matching baseline. Then the method of my thesis, MeanFlow, goes one decisive notch further: it learns the *average* velocity over the whole interval, so a single evaluation jumps you across — no integration at all. The punchline is that MeanFlow matches the diffusion model's forecast skill while running about nine times faster, in one or two calls — and crucially it needs no teacher, training from scratch in a single run. FlowCast sits between them on the same axis, already recovering most of the diffusion skill at about a quarter of the cost.

---

## Slide 3 — Why this matters: Taiwan

**MESSAGE:** Taiwan needs sub-hour, kilometer-scale, *probabilistic* precipitation forecasts; the operational value is in the extremes, and the extremes are the hard part.

**ON SLIDE**
- Typhoons, Mei-yu fronts, steep Central Mountain Range — a single landfall can drop **>1000 mm in 12 h**.
- Operational nowcasts must refresh every ~10 minutes on a fixed compute budget.
- The decision-relevant question is **probabilistic and local**: *how much rain, where, in the next 6–12 hours?*
- The events that matter most (heavy convective rain) are exactly the ones smooth/averaging models miss.

**SHOW:** [taiwan_domain_map.png](../figures/concepts/taiwan_domain_map.png) or [taiwan_domain_rain_case.png](../figures/concepts/taiwan_domain_rain_case.png)

**SCRIPT:**
Why do this for Taiwan specifically? Taiwan sits on the western Pacific typhoon track, it has a steep central mountain range, and it gets Mei-yu frontal rain — a single landfalling typhoon can dump over a metre of rain in twelve hours and trigger flash floods and landslides. For the people issuing evacuation orders or managing reservoirs, the useful forecast is probabilistic and local: how much rain, where, in the next six to twelve hours. And here's the tension that runs through the whole thesis — the quantity we care about most, heavy convective precipitation, is also the hardest to predict. It's sparse, it's spiky, and any model that hedges toward a smooth average will systematically erase exactly the storms that matter. So we want a model that produces *sharp* forecasts, and we want it *fast enough* to run between radar scans.

---

# Part 2 — Related Work

## Slide 4 — Background: how forecasting got here

**MESSAGE:** Four eras — physics-based NWP, then data-driven neural forecasters, then the *generative* turn that trades a single blurry prediction for a sample from a distribution.

**ON SLIDE** (timeline)
- **Numerical Weather Prediction (NWP):** solve the physics on a grid (IFS, GFS, WRF/RWRF). Accurate, physically grounded, *expensive*.
- **Data-driven global (2022–):** FourCastNet, Pangu, GraphCast — match NWP at a fraction of inference cost, but trained with pixel-MSE → **blurry, under-predicted extremes**.
- **Generative turn:** DGMR, StormCast, GenCast — sample from \(p(X_t \mid S_t, X_{t-1})\) → sharp, calibrated, ensemble-capable.
- **The cost:** each sample still needs tens of denoiser calls.

**SHOW:** simple 4-box timeline (build your own) — optional icons from [figures/concepts/](../figures/concepts/).

**SCRIPT:**
A little background, because not everyone here works on this. Weather prediction has gone through four phases. For a century it's been *numerical weather prediction* — you discretize the atmosphere and solve the fluid-dynamics equations. It's physically faithful but computationally heavy. Around 2022, a wave of *data-driven* models — FourCastNet, Pangu, GraphCast — showed a neural network could match those physics models at a tiny fraction of the cost. But they were trained with a pixelwise error, so they learned to predict the *average* outcome, which makes them blurry and makes them under-predict extremes. The fix is the *generative turn*: instead of predicting one field, you learn the whole *distribution* of plausible fields and draw samples from it. That gives you sharpness and a free ensemble. GenCast and StormCast are the leading examples. The catch — and this is my entry point — is that drawing each sample is expensive.

---

## Slide 5 — Why generative? The blurry-mean problem

**MESSAGE:** A model trained to minimise pixel error converges to the *mean* of all plausible weather — which is smooth and rain-free. Sampling a distribution keeps the storms.

**ON SLIDE**
- Pixel-MSE optimum = conditional **mean** → "slightly wet everywhere," no sharp cells.
- A generative model draws **distinct sharp members**; their *spread* is the forecast uncertainty.
- For precipitation this isn't cosmetic — the mean has the wrong *statistics* (intensity, area, spectrum).

**SHOW:** [blur_vs_members.png](../figures/concepts/blur_vs_members.png)

**SCRIPT:**
Let me make the "blurry mean" point concrete, because it's the reason generative models win here. Suppose tomorrow's rain could fall as a sharp cell slightly east or slightly west — both equally likely. A model trained to minimize pixel error won't pick one; it minimizes its loss by predicting the *average* of the two, which is a smeared, low-intensity blob that never actually occurs. On this slide, the left panel is that mean — smooth, washed-out. The right panels are individual generative samples — each one sharp, each one a physically plausible storm, and the differences between them *are* the uncertainty. For precipitation this matters enormously: the averaged field has the wrong rain rates, the wrong coverage, the wrong spatial texture. So we genuinely want to sample from a distribution, not regress to its mean — and that is exactly what diffusion and flow matching do.

---

## Slide 6 — Diffusion in one minute

**MESSAGE:** A diffusion model learns to turn noise into data by reversing a gradual noising process; sampling = walk a clean field back out of pure noise.

**ON SLIDE**
- **Forward (fixed):** corrupt a clean field with Gaussian noise until it's pure noise.
- **Learn:** a network that, at any noise level, predicts the clean field (a *denoiser*).
- **Sample (generate):** start from noise, repeatedly denoise → a sharp forecast.
- Different noise seeds → different members → a free ensemble.

**SHOW:** [anim_noise_to_field.mp4](animations/out/anim_noise_to_field.mp4) (use the `.mp4`; the `.gif` is large) · equation:
- [forward_noising.png](formulas/png/forward_noising.png) — \(x_\sigma = x_0 + \sigma\varepsilon,\ \varepsilon\sim\mathcal N(0,I)\)

**SCRIPT:**
So what *is* a diffusion model, in one minute? Watch the animation. We take a clean weather field and we keep adding Gaussian noise — that's the forward process, and it's fixed, no learning. After enough noise the field is indistinguishable from static. Now we train a single network to do the *reverse*: given a noisy field and the current noise level, predict the clean weather pattern hiding under the static — that's all a "denoiser" is. Once you have it, you can *generate*: start from pure noise and apply the network over and over, peeling noise away until a sharp forecast emerges — that's the second half of the animation, noise turning into rain. And because you start from a *random* noise field, every run gives a different but equally plausible forecast. That's where the ensemble comes from. The one equation here is the forward step: a clean field plus sigma times Gaussian noise. Everything else is learning to undo it.

---

## Slide 7 — The diffusion recipe and the EDM teacher

**MESSAGE:** Denoising at every noise level *is* learning the score; sampling integrates a "probability-flow" ODE; our teacher uses the EDM formulation and a 35-call Heun sampler.

**ON SLIDE**
- Denoiser ↔ **score** (Tweedie): \(\nabla_x\log p_\sigma(x) = \dfrac{D_\theta(x;\sigma)-x}{\sigma^2}\).
- Sampling = integrate the **probability-flow ODE** \( \dfrac{dx}{d\sigma} = -\sigma\,\nabla_x\log p_\sigma(x)\).
- **EDM** (Karras 2022): the teacher; fixed \(\sigma_{\min}{=}0.002,\ \sigma_{\max}{=}80,\ \sigma_{\text{data}}{=}0.5,\ \rho{=}7\).
- Sampler = 2nd-order **Heun**, \(N{=}18\) steps → **\(2N{-}1 = 35\) NFE per forecast step**.

**SHOW** (rendered equations):
- [tweedie.png](formulas/png/tweedie.png) · [pf_ode.png](formulas/png/pf_ode.png) · [edm_params.png](formulas/png/edm_params.png) · [heun_nfe.png](formulas/png/heun_nfe.png)

**SCRIPT:**
One slightly more technical slide, then I'll stay visual. Two facts make diffusion work. First, that denoiser we just trained is secretly the *score* — the gradient of the log-density — by a classical identity called Tweedie's formula. Second, once you know the score at every noise level, sampling is just integrating an ordinary differential equation, the "probability-flow ODE," from pure noise down to clean data. Our teacher uses a specific, well-tuned recipe called EDM. I won't walk through the four constants on the slide — the only one that matters for *today* is the data scale, sigma-data equals one-half, because all three of my models reuse it and therefore see the exact same residual statistics; that's what keeps the comparison fair. The number to actually take away is the last line: EDM samples with a second-order Heun integrator — "second-order" just means it evaluates the network twice per step — over eighteen steps, so *thirty-five* network calls for a single forecast hour. Hold onto thirty-five; it's the cost the rest of the thesis is trying to beat.

---

## Slide 8 — The catch: inference cost

**MESSAGE:** 35 calls/step is fine once, but rollout × ensemble turns it into ~42,000 U-Net passes per cycle — outside the operational budget.

**ON SLIDE**
- One forecast hour: **35 NFE**.
- 24-hour autoregressive rollout: **× 24**.
- 50-member ensemble: **× 50**.
- \( 50 \times 24 \times 35 = \mathbf{42{,}000} \) U-Net passes **per forecast cycle** → must refresh every ~10 min.

**SHOW:** [anim_cost_problem.gif](animations/out/anim_cost_problem.gif) · equation [cost_blowup.png](formulas/png/cost_blowup.png)

**SCRIPT:**
Here's why thirty-five matters. For a single forecast hour, thirty-five passes is nothing. But operational forecasting compounds it. You roll the model forward autoregressively for a 24-hour forecast — multiply by twenty-four. You run an ensemble for uncertainty — say fifty members — multiply by fifty. Now you're at roughly forty-two *thousand* large U-Net evaluations for one forecast cycle, and you have to produce that every ten minutes or so, between radar volumes. That's simply outside the compute budget of a regional forecasting center. To make it concrete: one diffusion forecast takes about twenty-two seconds on a single GPU, so a full fifty-member ensemble simply doesn't fit inside a ten-minute refresh cycle. The entire value proposition of generative forecasting — sharp, probabilistic, ensemble-ready — is gated behind this sampling cost. That's the wall this thesis sets out to knock down.

---

# Part 3 — Dataset

## Slide 9 — The data: Taiwan RWRF

**MESSAGE:** 1-hour conditional forecasting over Taiwan: 24 coarse ERA5 conditioning channels in, 4 km-scale target channels out, hourly, full-year 2022 validation.

**ON SLIDE**
- **Domain:** 21.6–25.6°N, 119.75–122.25°E, ≈2 km grid.
- **Input \(S_t\) (24 ch, ≈25 km ERA5):** mslp, t2m, u10, v10 + q/t/u/v/z at 1000/850/500/250 hPa.
- **Target \(X_t\) (4 ch, ≈2 km):** t2m, u10, v10 (RWRF) + **qpepre** (radar precipitation).
- **Splits:** train ≈19k h (2019-08→2021-12) · validate **8,759 h = all of 2022**.
- Only **4** output channels (vs 99 in CONUS StormCast) → per-channel bespoke losses are cheap.

**SHOW:** [taiwan_domain_map.png](../figures/concepts/taiwan_domain_map.png) · equation [hr_stats.png](formulas/png/hr_stats.png)

**SCRIPT:**
A quick orientation on the data. The task is one-hour-ahead forecasting over Taiwan at about two-kilometer resolution. The input is a coarse, twenty-five-kilometer ERA5 reanalysis with twenty-four channels — surface and upper-air fields — that supplies the synoptic-scale context. The output is four high-resolution channels: two-metre temperature, the two wind components, and precipitation from radar. We train on about two and a half years and we validate on the *entire* year 2022 — almost nine thousand hourly samples, so the evaluation is a full annual cycle, not a handful of cases. One detail that pays off later: because there are only four output channels, unlike the ninety-nine in the US version, I can afford to design a custom loss term per channel. And I'll need that, because of one channel in particular.

---

## Slide 10 — qpepre is the hard channel

**MESSAGE:** Three channels are near-Gaussian; precipitation is an atom-at-zero plus a heavy tail. That single fact drives every loss decision: channel weighting, a spectral term, and a log transform.

**ON SLIDE**
- t2m / u10 / v10: roughly Gaussian → standard losses are fine.
- **qpepre:** ~99% of pixels near zero (dry) + a heavy tail to 100+ mm/h → pixel-MSE collapses to "slightly wet everywhere."
- Three loss hooks (shared by all heads):
  - **Channel-weighted L2**, \(\beta=(1,1,1,w_{\text{pr}}),\ w_{\text{pr}}=2\).
  - **Radial log-PSD regulariser** on qpepre (keeps the spectrum sharp), \(\lambda_{\text{spec}}=0.1\).
  - **\(\log(1+x)\) encoding** → compresses σ from 9.12 mm/h to ≈0.37.

**SHOW:** [stormcast_test_train_HighRes_qpepre_gaussian_check.png](../figures/highres_distributions/stormcast_test_train_HighRes_qpepre_gaussian_check.png) · equations [channel_l2.png](formulas/png/channel_l2.png) · [logpsd.png](formulas/png/logpsd.png) · [log1p.png](formulas/png/log1p.png)

**SCRIPT:**
Here is that channel. Temperature and the winds are, statistically, well-behaved — close to Gaussian, so standard losses handle them. Precipitation is a completely different animal. Look at the distribution: almost all pixels are dry, a spike at zero, and then a long heavy tail out to extreme rain rates during typhoons. If you train this channel with a plain pixel error, the model discovers it can minimize the loss by painting a little bit of rain everywhere and never committing to a sharp storm — the mode-collapse failure. So all three of my heads share three precipitation-specific fixes: I up-weight the precipitation channel in the loss; I add a spectral regularizer — it measures how much energy the rain field has at each spatial scale and penalizes the model when the fine scales are too weak, which is the fingerprint of blur; and most importantly I encode rain as log-of-one-plus-x, which compresses that nasty dynamic range from a standard deviation of nine down to about a third. That log encoding turns out to be the single most consequential preprocessing choice — I'll show its ablation.

---

# Part 4 — Method

## Slide 11 — The key insight: the path is *curved*

**MESSAGE:** Diffusion needs many steps because its noise→data trajectory is curved; a low-order solver cuts corners and the error is worst on sparse precipitation.

**ON SLIDE**
- The probability-flow ODE trajectory is **curved** → a few big steps "cut the corner" and miss.
- Curvature error shows up first on **sparse, heavy-tailed precipitation** (score ill-conditioned at small \(\sigma\)).
- The symptom of under-sampling: reverts to a smooth, *"slightly wet everywhere"* field — good RMSE, no storms.
- **Lever:** change the *shape of the path*, not just the solver.

**SHOW:** [anim_integration_error.gif](animations/out/anim_integration_error.gif)

**SCRIPT:**
So *why* does diffusion need so many steps — could we just use a better solver? Partly, but there's a deeper reason, and it's on this slide. The trajectory from noise to data is *curved*. When you approximate a curve with a few straight hops — which is what any ODE solver does — you cut the corners, and the fewer the hops, the worse the miss. The animation shows this: on the curved path, one or two steps are badly wrong and you need many to hug it; and the error is worst exactly on the sparse precipitation channel — the qpepre channel we just looked at — where the math is most ill-conditioned. The practical symptom is that an under-sampled diffusion model collapses to a smooth, slightly-wet-everywhere field — it scores fine on average error but it's destroyed the storms. Now look at the *right* panel: if the path were a straight line, a single hop is already exact. That's the whole idea. Don't build a cleverer solver for the curve — change the path so it's straight.

---

## Slide 12 — Lever 1: straight-line flow matching (FlowCast)

**MESSAGE:** Flow matching learns a velocity field along a *straight line* from noise to data; the target is just \(x_1-x_0\), trained with no teacher, sampled in a few Euler steps.

**ON SLIDE**
- Define a straight path \(x_t = (1-t)x_0 + t x_1 + \sigma_{\text{path}}\eta\), noise \(x_0\) → data \(x_1\).
- The velocity along it is **constant**: \(v = x_1 - x_0\) (independent of \(x\)).
- Train a network \(v_\theta\) to regress it — a (channel-weighted) MSE, **no teacher, single run**.
- Sample: a few explicit **Euler steps**, \(K\) NFE. Straight ⇒ 1-step ≈ 10-step.

**SHOW:** [anim_curved_vs_straight.gif](animations/out/anim_curved_vs_straight.gif) (middle panel) · equations:
- [icfm_path.png](formulas/png/icfm_path.png) · [icfm_target.png](formulas/png/icfm_target.png) · [icfm_loss.png](formulas/png/icfm_loss.png) · [flowcast_sampler.png](formulas/png/flowcast_sampler.png)

**SCRIPT:**
This is the flow-matching baseline, FlowCast, and it's beautifully simple — and it's the stepping-stone to the method, because MeanFlow is defined relative to it. Instead of a curved diffusion path, we *define* a straight-line path connecting a noise sample to a data sample — the first equation. If you move in a straight line at constant speed, the velocity is just the destination minus the start, \(x_1 - x_0\) — that's the second equation, and notice it doesn't depend on where you are, it's a constant. So we train a network to predict that velocity with a mean-squared-error loss — channel-weighted to up-weight precipitation, the qpepre weighting I described in the data section. There's no teacher, no second training stage — it learns directly from data in one run. To generate, you take a few Euler steps along the learned velocity field. And because the underlying path is straight, integrating it is cheap: one step already lands close to ten steps, unlike the curved diffusion case. This is "conditional flow matching," and FlowCast is its adaptation to precipitation nowcasting — the baseline my method then improves on.

---

## Slide 13 — Lever 2: average velocity (MeanFlow)

**MESSAGE:** MeanFlow learns the *average* velocity over a whole interval, so one network call jumps from noise to data with no integration — and it's a strict generalisation of FlowCast.

**ON SLIDE**
- Even a straight-line flow is *integrated* (~10 steps) because the learned marginal field is curved.
- **Average velocity** \(u(z_r,r,t) = \frac{1}{t-r}\int_r^t v\,d\tau\) ⇒ transport is one algebraic jump: \(z_t = z_r + (t-r)\,u\).
- The integral is removed by a differential **identity**: \(u = v + (t-r)\,\frac{d}{dr}u\) (one JVP, stop-gradient).
- At \(t=r\) it *is* FlowCast → strict generalisation, **same recipe**. Sampling: **1–2 NFE**.

**SHOW:** [anim_meanflow_jump.gif](animations/out/anim_meanflow_jump.gif) · equations:
- [meanflow_avgvel.png](formulas/png/meanflow_avgvel.png) · [meanflow_displacement.png](formulas/png/meanflow_displacement.png) · [meanflow_identity.png](formulas/png/meanflow_identity.png)

**SCRIPT:**
FlowCast still pays for about ten Euler steps, because the *average* field it learns is itself a little curved. MeanFlow removes the integration entirely. The idea: instead of the instantaneous velocity, learn the *average* velocity over a whole time interval. If you know the average velocity, transport is a single algebraic step — start, plus interval length times average velocity, equals destination. No solver. The catch is that the average is defined by an integral you can't compute directly. The trick — and this is the clever part — is a differential *identity*: the average velocity equals the instantaneous velocity plus a small correction term, and that correction is just a derivative you get from one extra gradient pass, which we compute once and freeze as a fixed target. No integral, no teacher, no second training stage. The animation shows it: where FlowCast follows many little arrows, MeanFlow takes one big arrow across the whole gap. And beautifully, when the interval shrinks to zero, MeanFlow's objective becomes exactly FlowCast's — so it's a strict generalization, trained with the identical recipe, and it samples in one or two network calls.

---

## Slide 14 — The host model: StormCast's two stages

**MESSAGE:** StormCast splits forecasting into a frozen deterministic mean plus a generative *residual*; we freeze everything and swap only the residual head.

**ON SLIDE**
- **Stage 1 — Regression \(F_\xi\):** predicts the conditional mean \(M_t = F_\xi(X_{t-1}, S_t, I)\). **Frozen.**
- **Stage 2 — Residual head:** generates the residual \(R_t = X_t - M_t\); final \(\hat X_t = M_t + \hat R_t\).
- Conditioning bundle \(c_t = \mathrm{concat}(X_{t-1}, M_t, I)\) (same for all heads; the synoptic input \(S_t\) reaches the residual *only* through the mean \(M_t\)).
- We **only swap the residual head**: EDM diffusion ↔ FlowCast ↔ MeanFlow.

**SHOW:** [stormcast_architecture.png](../figures/stormcast_architecture.png) · equations [two_stage.png](formulas/png/two_stage.png) · [conditioning.png](formulas/png/conditioning.png)

**SCRIPT:**
Now, where do these flow models actually live? StormCast has a two-stage design, and it's important for understanding my comparison. Stage one is a plain deterministic network that predicts the *mean* next-hour state — the easy, predictable part. We take that off the shelf and freeze it. Stage two is the generative part: it only has to model the *residual*, what's left after subtracting the mean — and that residual is closer to Gaussian, which makes generative training easier. The final forecast is mean plus generated residual. The key design move in my thesis is that I hold stage one completely fixed, hold the conditioning fixed, and swap *only* the stage-two residual head — diffusion, FlowCast, or MeanFlow. Everything those three see is identical except the generative recipe itself.

---

## Slide 15 — ★ The experimental design (core contribution)

**MESSAGE:** One method (MeanFlow) measured against two baselines on a single axis — everything else held identical — so any difference is attributable to the *generative trajectory alone*. A controlled comparison, not a model zoo.

**ON SLIDE** (a "what's fixed vs what varies" table)
- **Held fixed:** dataset · frozen regression mean \(M_t\) · SongUNet backbone (`channel_mult [1,2,2,2,2]`, ~78.7M params) · data scale \(\sigma_{\text{data}}=0.5\) · conditioning · per-channel losses · **matched ≈2M-sample training budget**.
- **Only thing that varies:** the generative trajectory along one axis — **EDM diffusion (baseline)** → **FlowCast (straight-line baseline)** → **MeanFlow (average velocity — this thesis)**.
- **Cleanest leg:** MeanFlow's objective collapses *exactly* to FlowCast's at zero interval length (75% of each batch), so **MeanFlow-vs-FlowCast is an A/B on the training objective alone**.
- Consequence: the comparison isolates *path shape*, not data / architecture / compute.
- MeanFlow (and the FlowCast baseline) are **teacher-free, single-run** — not distillations of the diffusion model.

**SHOW:** [diffusion_vs_flow_2d_paths.png](../figures/concepts/diffusion_vs_flow_2d_paths.png) (the static three-way concept figure).

**SCRIPT:**
This slide is the heart of the contribution, so let me slow down. It is easy to compare three different models and learn nothing, because they differ in a dozen ways at once. I went to some lengths to make this a *controlled* experiment. All three heads share the same dataset, the same frozen regression mean, the same backbone architecture, the same data normalization, the same conditioning, the same precipitation-aware losses, and — importantly — the same training-sample budget, about two million samples each. The *only* thing I change is the generative trajectory, and the three heads sit on a *single axis*: curved diffusion is the baseline I set out to accelerate; FlowCast straightens the path and is my flow-matching baseline; and MeanFlow — the method of this thesis — removes the integral entirely by learning the average velocity. The cleanest comparison of all is MeanFlow versus FlowCast: MeanFlow's objective collapses *exactly* to FlowCast's whenever the time interval has zero length — which is three-quarters of every training batch — so the two differ *only* by the average-velocity bootstrap. That makes it a genuine A/B test on the training objective alone. So when I show you a difference in skill or cost later, it can't be explained away by "that one had more data" or "a bigger network" — it's attributable to the path shape itself. And to be clear: neither flow head is a distillation of the diffusion model. They never query it; they're trained from scratch in a single run — a cleaner and cheaper proposition than the usual distillation route. I want to stress that this controlled design is *itself* a contribution: it's what lets me make a *causal* claim about path shape, rather than just observing that one model happened to score higher.

---

## Slide 16 — The three heads, side by side

**MESSAGE:** Same backbone, one trajectory axis, three sampler costs: diffusion baseline 35 NFE → FlowCast baseline ~10 → MeanFlow (this work) 1–2.

**ON SLIDE** (comparison table)

| | **EDM Diffusion** (reference baseline) | **FlowCast** (flow-matching baseline) | **MeanFlow** (this thesis) |
|---|---|---|---|
| Generative target | score / denoiser | straight-line velocity \(v_\theta\) | average velocity \(u_\theta\) |
| Path shape | curved | straight (integrated) | straight (jumped) |
| Sampler | Heun (2nd order) | \(K\) Euler steps | \(K\) average-velocity jumps |
| **NFE / step** | **35** | **~10** | **1–2** |
| Teacher? | — | **none** | **none** |
| Training | from scratch | single run | single run (= FlowCast at \(t{=}r\), 75% of batch) |
| Role | the model we accelerate | the straight-line special case | **the method** — generalises FlowCast |

**SHOW:** the table above; optional icons [icon_curved.png](../figures/concepts/icon_curved.png) / [icon_straight.png](../figures/concepts/icon_straight.png) / [icon_meanflow.png](../figures/concepts/icon_meanflow.png).

**SCRIPT:**
Let me put the three heads next to each other before we get to results. Same network backbone in every column — they sit on one axis. The diffusion baseline, on the left, learns a denoiser and samples with a thirty-five-call Heun integrator; it's the model I set out to accelerate. The FlowCast baseline learns a straight-line velocity and samples with about ten Euler steps. And MeanFlow, on the right — the method of this thesis — learns the *average* velocity and samples in one or two jumps, generalising FlowCast exactly: on three-quarters of every training batch its objective *is* FlowCast's. Reading across the bottom rows: the cost drops from thirty-five, to ten, to one or two network calls per forecast hour — and neither flow head uses a teacher; both train from scratch in a single run. So the question the experiments answer is: as we move along this axis and the cost collapses to one or two calls, *what happens to forecast skill?*

---

# Part 5 — Experiments

## Slide 17 — How we measure skill

**MESSAGE:** RMSE alone rewards blur, so we use five complementary families: deterministic, probabilistic, categorical-precip, spectral, and rollout.

**ON SLIDE**
- **Deterministic:** per-channel RMSE / MAE (physical units).
- **Probabilistic:** **CRPS** on 10-member ensembles (sharp *and* calibrated).
- **Categorical precip:** **CSI**, **FAR**, **HSS**, **FSS** at thresholds 0.1–16 mm/h.
- **Spectral:** radial log-PSD of qpepre (is it sharp?).
- **Rollout:** RMSE vs lead time out to 12 h (autoregressive error growth).

**SHOW:** equations [rmse.png](formulas/png/rmse.png) · [csi_far.png](formulas/png/csi_far.png) · [fss.png](formulas/png/fss.png)

**SCRIPT:**
A word on evaluation, because how you score precipitation determines what you conclude. Average error — RMSE — is necessary but it actively rewards blur, so it can't be the only metric. I use five families. Deterministic RMSE and MAE per channel. CRPS, which is the standard probabilistic score — it rewards a forecast that's both sharp and well-calibrated, computed over ten-member ensembles. Then the operational precipitation scores — critical success index and Heidke skill score, which reward correct detection; false-alarm ratio, which punishes crying wolf; and the fractions skill score, which forgives a small spatial displacement — all evaluated at rainfall thresholds from drizzle up to heavy rain. A spectral diagnostic that asks whether the predicted rain has the right small-scale texture. And finally rollout error versus lead time, because single-step skill understates the risk once you chain the model autoregressively. Only when a method holds up across all five do I trust the comparison.

---

## Slide 18 — ★ Headline result: the three-way scoreboard

**MESSAGE:** The headline: at a matched budget, **MeanFlow** reaches the diffusion baseline's deterministic + categorical skill class at **1–2 calls (~9× faster)** with the best temperature of all heads; the FlowCast baseline marks the midpoint — matched CRPS, better winds/precip RMSE & false alarms, 3.7× faster.

**ON SLIDE** (scoreboard — 2022 validation, 10-member ensembles, +12 h rollouts)

| Method | Time/seq | CRPS↓ | CSI-M↑ | FAR-M↓ | RMSE u10↓ | RMSE v10↓ | RMSE qpepre↓ |
|---|---|---|---|---|---|---|---|
| **EDM diffusion** (35 NFE) | 21.78 s | 0.6783 | **0.1498** | 0.4727 | 1.5626 | 1.9574 | 0.9429 |
| **FlowCast** (K=10) | 5.88 s | 0.6833 | 0.1364 | 0.4188 | **1.4935** | **1.6423** | 0.8959 |
| **FlowCast** (K=15) | 8.35 s | **0.6740** | 0.1435 | 0.4244 | 1.5203 | 1.6710 | **0.8897** |
| **MeanFlow** (K=1) | **1.83 s** | 0.8485 | 0.1449 | **0.3861** | 1.6540 | 2.1740 | 0.9263 |
| **MeanFlow** (K=2) | 2.35 s | 0.7265 | 0.1492 | 0.5241 | 1.5350 | 1.7902 | 0.9404 |

- **MeanFlow K=2 (the method):** diffusion-level CSI/HSS, **best t2m of all heads (0.9999 K vs 1.0208)**, **~9× faster**; single-step precip CRPS **undercuts FlowCast at any step count**; concedes only a rollout-CRPS spread gap.
- FlowCast K=10 (flow-matching baseline): CRPS within noise of diffusion; **−4% u10, −16% v10, −5% qpepre** RMSE; FAR 0.42 vs 0.47; **3.7× faster** — the intermediate point on the same axis.
- **Recommended operating point:** **MeanFlow K=2** — diffusion skill at a tenth of the cost. *(FlowCast K=10 if you want the sharpest precip & lowest FAR; MeanFlow K=1 is possible but under-disperses.)*

**SHOW:** [scoreboard_3way.png](../figures/results/scoreboard_3way.png)

**SCRIPT:**
This is the central result. Every row is at the same two-million-sample budget, same regression mean, same data — so it's apples to apples. Start with the diffusion baseline at the top: twenty-two seconds per sequence, the reference I'm trying to beat. Now jump to the bottom, to MeanFlow — the method of the thesis — at two evaluations: two-and-a-half seconds, roughly nine times faster than diffusion, and it reaches the same detection-skill class, the same CSI and HSS, *and* it posts the best temperature accuracy of any head, including the diffusion baseline; its single-step precipitation CRPS is below FlowCast's at any step count. Its one concession is ensemble spread under long rollouts, which shows up as a CRPS gap — I'll come back to that as a failure mode. In between sits the FlowCast baseline at ten steps: under six seconds, three-point-seven times faster, its CRPS statistically tied with diffusion and actually *better* on both wind components, on precipitation RMSE, and on false-alarm ratio — so the straight-line path already recovers most of the diffusion skill before the average-velocity jump removes the last of the integration cost. The headline is: you can have the diffusion model's skill at a tenth of the cost, in one or two calls, with no teacher.

---

## Slide 19 — Cost vs quality: the Pareto picture

**MESSAGE:** Precipitation-CRPS quality saturates fast — FlowCast by ~8–10 steps, MeanFlow already below it at 1–2 — so the cheap regime *is* the accurate regime; the average-velocity objective shifts the whole frontier left.

**ON SLIDE**
- Sweep \(K\in\{1,\dots,50\}\): FlowCast **precipitation CRPS** saturates by \(K\approx 8\text{–}10\); more steps only add cost.
- MeanFlow's precipitation-CRPS curve sits **below** FlowCast's saturated curve at **every** \(K\), and already undercuts it at \(K=1\text{–}2\). *(The narrowed-spread rollout-CRPS gap of Slide 18 is the separate aggregate metric.)*
- Wall-clock is linear in \(K\) → few-step regime is simultaneously cheap and accurate.
- Operational picture: a 50-member, 24-h cycle = **2,400** evals (MeanFlow K=2) vs **42,000** (diffusion).

**SHOW:** [nfe_pareto.png](../figures/results/nfe_pareto.png) · [anim_speedup_bars.gif](animations/out/anim_speedup_bars.gif)

**SCRIPT:**
People always ask: if you add more steps, do the flow models keep improving — are you just trading quality for speed? The Pareto sweep answers that, and to be precise it plots the *precipitation* CRPS — the channel we care about. FlowCast's precipitation CRPS saturates by about eight to ten steps; beyond that you spend wall-clock and get nothing. So its sweet spot is genuinely in the cheap regime. And MeanFlow — the dashed curve — sits *below* FlowCast's fully-saturated precipitation CRPS at every step count, already at one or two evaluations. (That's the single-step precipitation calibration; the small rollout-CRPS gap I showed on the scoreboard is the separate aggregate, spread-driven, metric.) The average-velocity objective shifts the entire quality-versus-cost frontier to the left. Wall-clock is just linear in the number of steps, so the few-step regime is simultaneously the cheap one and the accurate one — there's no painful trade-off to manage. To put it operationally: that fifty-member, twenty-four-hour cycle that cost the diffusion sampler forty-two thousand network passes costs MeanFlow about twenty-four hundred. At that point the ensemble size, not the sampler, becomes your budget knob — which is exactly the regime you want to be in.

---

## Slide 20 — Precipitation skill by threshold: a real trade-off

**MESSAGE:** The flow heads are *conservative* (fewer false alarms, slightly fewer hits); diffusion is *aggressive* (more hits, more false alarms). At the heaviest rain, diffusion keeps a hit-rate edge.

**ON SLIDE**
- Light–moderate rain: flow heads' **FAR much lower** (e.g. 0.33 vs 0.46 at 0.1 mm/h) at comparable CSI.
- Heavy rain (5–10 mm/h): **diffusion leads CSI** — it places intense cells more aggressively.
- It's a coherent *trade*, not a wash: conservative (FlowCast) vs aggressive (diffusion). Which you prefer is operational.
- Heavy-rain CSI is the flow heads' weakest point at this budget → a named target for future work.

**SHOW:** [csi_per_threshold.png](../figures/results/csi_per_threshold.png) · (heavy-rain FSS caveat) [fss_p16.png](../figures/results/fss_p16.png)

**SCRIPT:**
Let me be honest about where the flow heads *don't* win, because it's an interesting and coherent story rather than a wash. Break precipitation skill out by rainfall threshold. At light and moderate rain, the flow heads have a big false-alarm advantage — they don't paint speculative drizzle over dry pixels — at a comparable hit rate. But at the heavy thresholds, five to ten millimetres an hour, the diffusion baseline pulls ahead on hit rate. The reason is temperamental: the flow heads are *conservative* — they commit to rain only when confident, which keeps false alarms down but costs them some hits on the most intense cells. The diffusion model is *aggressive* — it places more wet pixels, which CSI rewards and false-alarm ratio punishes. Which behavior you want is genuinely an operational choice. But I'll flag heavy-rain detection as the flow heads' real weakness at this training budget, and it's one of my concrete future-work targets. My headline recommendation is MeanFlow at two evaluations — the method — purely for the cost: diffusion-level skill at a tenth of the budget. The one case where I'd reach for the FlowCast baseline instead is when the lowest possible false-alarm rate is paramount — alert fatigue is a real cost when you're issuing evacuation orders — and in either case a tail-weighted loss is the fix for clawing back the heavy-rain hits.

---

## Slide 21 — Rollout stability and qualitative cases

**MESSAGE:** Neither flow head destabilises over a 12-h rollout; visually they keep dry regions dry while preserving sharp convective structure — MeanFlow at two evaluations.

**ON SLIDE**
- Rollout RMSE grows monotonically; **no blow-up** (the straight-line ODE is stable).
- FlowCast tracks/beats diffusion on winds & precip across the horizon; one weak signal: **t2m drift after ~8 h**.
- Qualitatively: flow heads keep dry areas dry (the FAR win, made visible), sharp storms preserved.
- MeanFlow's 2-evaluation fields are **not** visibly blurrier than FlowCast's 10-step fields.

**SHOW:** [rollout_rmse.png](../figures/results/rollout_rmse.png) · [qual_qpepre_seq00.png](../figures/results/qual_qpepre_seq00.png) · [qual_u10_seq00.png](../figures/results/qual_u10_seq00.png)

**SCRIPT:**
Two robustness checks. First, rollout: I chain the model forward for twelve hours and watch the error grow. Both flow heads grow gracefully and monotonically — crucially, *neither* shows the unphysical blow-up that aggressively under-sampled diffusion models are prone to, which I attribute to the stability of the straight-line ODE. FlowCast tracks or beats diffusion on winds and precipitation across the whole horizon; its one weak signal is temperature drifting upward after about eight hours. Second, the qualitative panels — and this is where you see the false-alarm advantage with your own eyes. The flow heads keep the dry regions genuinely dry while preserving sharp, coherent storm structure, whereas the diffusion baseline sprinkles more weak rain around. And notice MeanFlow's fields, generated in *two* network calls, are not visibly smoother than FlowCast's ten-step fields — the average-velocity sampler doesn't pay the blurring penalty you'd expect from truncating an integration so aggressively.

---

# Part 6 — Discussion

## Slide 22 — Failure modes (told honestly)

**MESSAGE:** Three named, diagnosed, mitigable failure modes — this is where the honest science is.

**ON SLIDE**
- **Heavy-rain under-detection** (both flow heads): conservative behaviour costs hits at 5–10 mm/h. → tail-quantile loss, higher \(w_{\text{pr}}\), longer training.
- **t2m rollout drift** (FlowCast only): temperature error grows after ~8 h. *MeanFlow does **not** inherit it* → it's the learned trajectory, not the backbone.
- **One-evaluation under-dispersion** (MeanFlow K=1): a single jump lands on the mean → narrow ensemble → CRPS lags; compounds over rollout (6%→17%). \(K{=}2\) restores most spread.

**SHOW:** [crps_per_channel.png](../figures/results/crps_per_channel.png) (supports t2m / spread discussion).

**SCRIPT:**
I want to spend a slide on failure modes, because that's where the real understanding is. Three of them. One: both flow heads under-detect heavy rain — the conservatism we just saw. That's a loss-design problem, and the fixes are concrete: a tail-quantile loss, more precipitation weight, longer training. Two: FlowCast's temperature drifts under long rollouts. The telling detail is that MeanFlow, which shares FlowCast's backbone and losses exactly, does *not* inherit this drift — so it's a property of FlowCast's learned trajectory, not the architecture, which itself is a useful scientific finding. Three: MeanFlow at a *single* evaluation under-disperses — one jump lands each member almost on the mean, so the ensemble is too narrow and CRPS suffers, and that deficit compounds under rollout from six percent to seventeen. The fix is cheap — a second evaluation restores most of the spread, which is exactly why I recommend K equals two. None of these is fatal; all three are diagnosed and have a clear path forward.

---

## Slide 23 — ★ Contributions

**MESSAGE:** One reproducible single-run average-velocity pipeline (MeanFlow), two retained baselines that make the comparison controlled, a precipitation-aware loss + eval suite — the first study of average-velocity flow matching on a regional convective-scale forecaster.

**ON SLIDE**
1. **MeanFlow for StormCast** — the average-velocity residual, **first application to weather forecasting**: JVP-bootstrapped stop-gradient target, **1–2 NFE, no ODE solver**, teacher-free, single run, on the 4-channel Taiwan target. *(The method.)*
2. **Controlled same-axis comparison (two retained baselines)** — against the **EDM diffusion** residual (the 35-NFE model we accelerate) and the **FlowCast** straight-line I-CFM baseline MeanFlow generalises; MeanFlow-vs-FlowCast is an **A/B on the objective alone** (collapses at zero interval).
3. **Same-trajectory-axis engineering** — all three heads share *exactly* the frozen regression mean, normalisation, backbone, and \(\sigma_{\text{data}}\), so only the generative trajectory varies.
4. **Precipitation-aware loss** — channel-weighted L2 + radial log-PSD on qpepre, with log1p and \(w_{\text{pr}}\) ablations.
5. **Precipitation-aware evaluation suite** on the full 2022 Taiwan year (RMSE/MAE, CRPS, CSI/FSS/HSS/FAR, spectral, rollout).
6. **The finding:** an average-velocity residual recovers diffusion skill at **~9×** lower cost (1–2 calls, no teacher); the straight-line FlowCast baseline marks the **3.7×** midpoint on the same axis.

**SHOW:** the numbered list; optional [scoreboard_3way.png](../figures/results/scoreboard_3way.png) thumbnail.

**SCRIPT:**
So, to gather the contributions. The headline one is MeanFlow — to my knowledge the first time the average-velocity objective has been brought into weather forecasting at all. I adapt it to the StormCast two-stage residual as the generative head: it learns the displacement over a whole interval through a single Jacobian–vector-product stop-gradient target, samples in one or two calls with no ODE solver, and trains teacher-free in a single run. Second, to make that a *controlled* claim rather than just a high score, I retain two baselines on the same backbone and budget — the EDM diffusion model I set out to accelerate, and FlowCast, the straight-line flow-matching special case MeanFlow generalises; because MeanFlow's objective collapses exactly to FlowCast's at zero interval length, comparing them is a clean A/B on the training objective alone. Third is the engineering that holds the regression mean, normalisation, backbone and data scale identical across all three. Fourth, the precipitation-aware loss design and its ablations. Fifth, a full precipitation-aware evaluation suite run over an entire year. And sixth, the empirical finding that ties it together: an average-velocity residual recovers the diffusion model's skill at about a tenth of the cost, with no teacher and a single run, and FlowCast charts the intermediate point at a quarter of the cost. To be precise about novelty: flow matching and MeanFlow are existing methods from the generative-modeling literature — what's new here is *adapting* average-velocity sampling to the StormCast two-stage residual, and being first, to my knowledge, to bring it to a regional, convection-permitting weather forecaster.

---

## Slide 24 — Limitations & future work

**MESSAGE:** Single snapshot, single domain, heavy-rain gap, low-NFE spread — all four are concrete and addressable.

**ON SLIDE**
- **Limitations:** one ~2M-sample snapshot (10–30% validation noise); one regression mean / one domain (Taiwan); heavy-rain CSI gap; MeanFlow under-dispersion at K=1; **no distilled-diffusion comparator** (prior distillation bottoms out at ~10–15 NFE and needs a second training stage; the flow heads remove that stage — a head-to-head is future work).
- **Future work:**
  - Train all heads to **convergence** and re-score (beat down snapshot noise).
  - **Close the heavy-rain gap** — tail-quantile/focal loss, stronger transform.
  - **Restore low-NFE rollout spread** — stochastic single jump, noise re-injection.
  - **Large-ensemble calibration** (50–100 members) — now affordable; rank histograms, spread–skill.
  - **Transfer** to another domain (e.g. HRRR/CONUS StormCast).

**SHOW:** the two lists.

**SCRIPT:**
The honest limitations. These numbers are at a single, relatively early training snapshot, where validation noise is ten to thirty percent — the headline trends are robust to that, but the fine ordering isn't, and training to convergence is my single most important next step. Everything is anchored to one regression mean on one domain, Taiwan, so transfer is untested. The heavy-rain detection gap is real. And MeanFlow under-disperses at a single evaluation. The good news is that each of these has a concrete fix already scoped: train to convergence and average over snapshots; a tail-aware loss for heavy rain; a stochastic single-jump sampler to restore spread; large-ensemble calibration studies that the cheap sampler finally makes affordable; and a transfer experiment to a second domain. None of these require new theory — they're engineering and compute.

---

# Part 7 — Conclusion

## Slide 25 — Conclusion

**MESSAGE:** Learning the *average velocity* of the noise→weather path — MeanFlow — lets one or two network calls do what diffusion needs thirty-five for, a credible route to fast, sharp, probabilistic regional forecasting.

**ON SLIDE**
- Generative modelling is the right inductive bias for convective forecasting; the obstacle was the multi-step sampler.
- **The axis:** diffusion (curved, 35 calls) → **straighten it** (FlowCast baseline: diffusion-level skill, ~3.7× faster) → **jump it** with the average velocity.
- **MeanFlow (the method):** same skill class at **1–2 calls, ~9× faster**, best temperature, teacher-free, single run.
- Fast enough to run *between radar volumes* — within reach.

**SHOW:** [path_cartoon_triptych.png](../figures/concepts/path_cartoon_triptych.png) or reuse [anim_curved_vs_straight.gif](animations/out/anim_curved_vs_straight.gif).

**SCRIPT:**
To conclude. Generative modelling is almost certainly the right tool for short-range convective forecasting — it's the only way to get sharpness and calibration together. The one obstacle to deploying it has been the multi-step diffusion sampler. This thesis shows, on a real regional dataset, that the obstacle is removable by changing the shape of the generative path along a single axis. Straighten it, and a flow-matching baseline already recovers the diffusion model's skill — and beats it on winds, precipitation error, and false alarms — at about a quarter of the cost. Then the method of this thesis goes the last step: learn the *average* velocity over the whole interval, and a single network call — MeanFlow — jumps from noise to forecast in one or two evaluations, a tenth of the diffusion cost, reaching the same skill class with the best temperature accuracy in the study, no teacher, one training run. The path a generative model takes from noise to weather turned out to be one you can not just straighten but jump. Making sharp, probabilistic, regional forecasting fast enough to run between radar volumes is within reach. Thank you.

---

## Slide 26 — Thank you / Questions

**ON SLIDE**
- *One line:* **One-to-two-step Taiwan StormCast nowcasts via average-velocity flow matching (MeanFlow) — diffusion-level skill at a tenth of the cost, no teacher; the FlowCast straight-line baseline marks the midpoint.**
- Code: `Stormcast-Distilation` (branch `distillation_setup`).
- Contact: dzycheong@gmail.com
- *"Happy to take questions."*

**SHOW:** title-style closing; faint [taiwan_domain_rain_case.png](../figures/concepts/taiwan_domain_rain_case.png).

**SCRIPT:**
That's the thesis in one line on the slide. I'm happy to take your questions — and I have backup slides on the MeanFlow identity derivation, the EDM preconditioning of the baseline, the log1p and precipitation-weight ablations, and the legacy-baseline comparison if any of those are useful.

---

# Backup slides

**B1 — EDM preconditioning.** \(D_\theta = c_{\text{skip}}x + c_{\text{out}}F_\theta(c_{\text{in}}x, c_{\text{noise}})\); the unique scaling that keeps input/target/loss scale uniform across \(\sigma\). → [edm_precond.png](formulas/png/edm_precond.png), [edm_schedule.png](formulas/png/edm_schedule.png)

**B2 — The MeanFlow identity, derived.** Differentiate \((t-r)u=\int_r^t v\,d\tau\) along the trajectory → \(u=v+(t-r)\frac{d}{dr}u\); evaluated by one JVP, stop-gradient. → [meanflow_identity.png](formulas/png/meanflow_identity.png), [meanflow_jvp.png](formulas/png/meanflow_jvp.png), [meanflow_loss.png](formulas/png/meanflow_loss.png), [meanflow_sampler.png](formulas/png/meanflow_sampler.png)

**B3 — FlowCast preconditioning & recipe.** \(v_\theta=\mathrm{SongUNet}(\mathrm{concat}[x_t,c_t], t\tau),\ \tau{=}1000\); AdamW lr 5e-4, wd 1e-4, 400k steps, batch 96, EMA 0.999, \(\sigma_{\text{path}}{=}0.01\). → [flowcast_precond.png](formulas/png/flowcast_precond.png)

**B4 — MeanFlow specifics.** Two-time embedding (\(r\) via positional embed, \(\Delta{=}t{-}r\) via Fourier features); MeanFlow ratio \(\rho_{\text{MF}}{=}0.25\); adaptive weight \(w=(\lVert\Delta\rVert^2+\varepsilon)^{-1}\); batch 112.

**B5 — log1p ablation.** log1p improves *both* heads on t2m (~20–25%) and u10 by removing the badly-scaled raw qpepre's contamination of the shared trunk. (Thesis Table 4.4.)

**B6 — Precipitation-weight sweep.** \(w_{\text{pr}}\in[1.0,2.4]\): no clean monotone trend; \(w_{\text{pr}}{=}2.0\) wins t2m & is competitive on qpepre (headline); \(w_{\text{pr}}{=}1.4\) best for winds. (Thesis Table 4.5.)

**B7 — Legacy baseline.** Old StormCast (raw qpepre, 224×128): 49.55 s, CRPS 0.8762, CSI-M 0.0614. Cleaning + log1p + retrain is most of the headline jump; the flow heads then add the cost & FAR wins. (Thesis Table 4.6.)

**B8 — Spectral sharpness.** FlowCast's qpepre radial log-PSD tracks the observation spectrum into high wavenumbers (the spectral regulariser working). → [qpepre_spectrum.png](../figures/flowcast/qpepre_spectrum.png), [loss_curves.png](../figures/flowcast/loss_curves.png)

**B9 — Why Heun, why σ_data matched, why EMA weights.** Matching the teacher's σ_data=0.5 keeps the residual distribution identical across heads; flow heads sample from the EMA shadow (`ema_state.pt`), not the online weights.
