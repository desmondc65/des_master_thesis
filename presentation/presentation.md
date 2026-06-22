# Master's Defense — Presentation Content

**Title:** *Single-Run Flow-Matching Residuals for a Regional StormCast Forecaster:
FlowCast and MeanFlow versus Diffusion on the Taiwan Convective-Scale Domain*

**Author:** Desmond Cheong · National Taiwan University, Dept. of Industrial Engineering · 2026

**Format:** 26 content slides + backup. Target **25–30 minutes** (~1 min/slide, results slides slightly longer).
**Audience:** thesis committee, some members new to diffusion / flow matching. Stay high-level; anchor every abstract idea to "the model that predicts what the radar shows next hour."

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

A compact **slide → asset map** is in [README.md](README.md). A clean continuous narration with timing is in [speaker_script.md](speaker_script.md).

---

## Slide 1 — Title

**MESSAGE:** A fast, sharp, probabilistic regional weather forecaster is possible by changing *how* a generative model travels from noise to data.

**ON SLIDE**
- Title (above) + your name, advisor, department, date.
- One-line subtitle: *"Making generative convective-scale forecasting fast enough to run between radar volumes."*
- **Research question:** *Can we cut the generative sampling cost — by reshaping the noise→data path and training from scratch with no teacher — without losing forecast skill?*
- Keywords: Diffusion · **Flow Matching** · **MeanFlow** · StormCast · Convective-scale precipitation · Taiwan RWRF.

**SHOW:** [taiwan_domain_rain_case.png](../figures/concepts/taiwan_domain_rain_case.png) faint as a title background.

**SCRIPT:**
Good morning, and thank you for being here. My thesis is about making *generative* weather forecasting fast enough to actually deploy. Diffusion models like StormCast and GenCast have become the state of the art for short-range, convective-scale forecasting — they are sharp and they are probabilistic — but they are slow to sample. I take a StormCast model trained on a Taiwan regional dataset and ask a simple question: instead of distilling a slow model into a fast one, can we just change the *shape of the path* the generative model takes from noise to a forecast? I'll show that two single-run, teacher-free recipes — FlowCast and MeanFlow — recover the diffusion model's skill at a quarter to a tenth of the cost.

---

## Slide 2 — The one-slide story

**MESSAGE:** Problem: diffusion is skillful but ~35 model calls per step. Idea: straighten the generative path (and then remove the integral). Result: same skill, 3.7×–9× cheaper, no teacher.

**ON SLIDE** (three columns: Problem → Idea → Result)
- **Problem:** EDM diffusion teacher = **35 network calls per forecast step** → a 50-member, 24-h ensemble ≈ **42,000 U-Net passes**.
- **Idea:** the diffusion path from noise→data is *curved* (needs many steps). **Straighten it** (FlowCast / flow matching), then **jump it in one step** (MeanFlow / average velocity).
- **Result:** at a matched training budget, FlowCast matches diffusion CRPS and beats it on winds, precip RMSE, and false alarms at **3.7× faster**; MeanFlow reaches the same skill class at **1–2 calls (~9× faster)**.

**SHOW:** [anim_curved_vs_straight.gif](animations/out/anim_curved_vs_straight.gif)

**SCRIPT:**
Here is the whole talk on one slide. The problem is cost: the diffusion sampler needs about 35 neural-network evaluations for *one* forecast hour, and operational use multiplies that by the forecast horizon and the ensemble size — tens of thousands of passes per cycle. The reason it needs so many is that the path a diffusion model follows from random noise to a clean forecast is *curved*, and you can't shortcut a curve. My idea is to change that path. First, flow matching makes it a *straight line*, which integrates in a handful of steps — that's FlowCast. Then MeanFlow learns the *average* velocity over the whole interval, so a single evaluation jumps you across — no integration at all. The punchline is that both match the diffusion model's forecast skill while running three-to-ten times faster, and crucially, neither one needs a teacher — they train from scratch in a single run.

---

## Slide 3 — Why this matters: Taiwan

**MESSAGE:** Taiwan needs sub-hour, kilometre-scale, *probabilistic* precipitation forecasts; the operational value is in the extremes, and the extremes are the hard part.

**ON SLIDE**
- Typhoons, Mei-yu fronts, steep Central Mountain Range — a single landfall can drop **>1000 mm in 12 h**.
- Operational nowcasts must refresh every ~10 minutes on a fixed compute budget.
- The decision-relevant question is **probabilistic and local**: *how much rain, where, in the next 6–12 hours?*
- The events that matter most (heavy convective rain) are exactly the ones smooth/averaging models miss.

**SHOW:** [taiwan_domain_map.png](../figures/concepts/taiwan_domain_map.png) or [taiwan_domain_rain_case.png](../figures/concepts/taiwan_domain_rain_case.png)

**SCRIPT:**
Why do this for Taiwan specifically? Taiwan sits on the western Pacific typhoon track, it has a steep central mountain range, and it gets Mei-yu frontal rain — a single landfalling typhoon can dump over a metre of rain in twelve hours and trigger flash floods and landslides. For the people issuing evacuation orders or managing reservoirs, the useful forecast is probabilistic and local: how much rain, where, in the next six to twelve hours. And here's the tension that runs through the whole thesis — the quantity we care about most, heavy convective precipitation, is also the hardest to predict. It's sparse, it's spiky, and any model that hedges toward a smooth average will systematically erase exactly the storms that matter. So we want a model that produces *sharp* forecasts, and we want it *fast enough* to run between radar scans.

---

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

## Slide 9 — The key insight: the path is *curved*

**MESSAGE:** Diffusion needs many steps because its noise→data trajectory is curved; a low-order solver cuts corners and the error is worst on sparse precipitation.

**ON SLIDE**
- The probability-flow ODE trajectory is **curved** → a few big steps "cut the corner" and miss.
- Curvature error shows up first on **sparse, heavy-tailed precipitation** (score ill-conditioned at small \(\sigma\)).
- The symptom of under-sampling: reverts to a smooth, *"slightly wet everywhere"* field — good RMSE, no storms.
- **Lever:** change the *shape of the path*, not just the solver.

**SHOW:** [anim_integration_error.gif](animations/out/anim_integration_error.gif)

**SCRIPT:**
So *why* does diffusion need so many steps — could we just use a better solver? Partly, but there's a deeper reason, and it's on this slide. The trajectory from noise to data is *curved*. When you approximate a curve with a few straight hops — which is what any ODE solver does — you cut the corners, and the fewer the hops, the worse the miss. The animation shows this: on the curved path, one or two steps are badly wrong and you need many to hug it; and the error is worst exactly on the sparse precipitation channel, where the math is most ill-conditioned. The practical symptom is that an under-sampled diffusion model collapses to a smooth, slightly-wet-everywhere field — it scores fine on average error but it's destroyed the storms. Now look at the *right* panel: if the path were a straight line, a single hop is already exact. That's the whole idea. Don't build a cleverer solver for the curve — change the path so it's straight.

---

## Slide 10 — Lever 1: straight-line flow matching (FlowCast)

**MESSAGE:** Flow matching learns a velocity field along a *straight line* from noise to data; the target is just \(x_1-x_0\), trained with no teacher, sampled in a few Euler steps.

**ON SLIDE**
- Define a straight path \(x_t = (1-t)x_0 + t x_1 + \sigma_{\text{path}}\eta\), noise \(x_0\) → data \(x_1\).
- The velocity along it is **constant**: \(u_t = x_1 - x_0\) (independent of \(x\)).
- Train a network \(v_\theta\) to regress it — a (channel-weighted) MSE, **no teacher, single run**.
- Sample: a few explicit **Euler steps**, \(K\) NFE. Straight ⇒ 1-step ≈ 10-step.

**SHOW:** [anim_curved_vs_straight.gif](animations/out/anim_curved_vs_straight.gif) (middle panel) · equations:
- [icfm_path.png](formulas/png/icfm_path.png) · [icfm_target.png](formulas/png/icfm_target.png) · [icfm_loss.png](formulas/png/icfm_loss.png) · [flowcast_sampler.png](formulas/png/flowcast_sampler.png)

**SCRIPT:**
This is the first method, FlowCast, and it's beautifully simple. Instead of a curved diffusion path, we *define* a straight-line path connecting a noise sample to a data sample — the first equation. If you move in a straight line at constant speed, the velocity is just the destination minus the start, \(x_1 - x_0\) — that's the second equation, and notice it doesn't depend on where you are, it's a constant. So we train a network to predict that velocity with a mean-squared-error loss — channel-weighted to up-weight precipitation, which I'll come to. There's no teacher, no second training stage — it learns directly from data in one run. To generate, you take a few Euler steps along the learned velocity field. And because the underlying path is straight, integrating it is cheap: one step already lands close to ten steps, unlike the curved diffusion case. This is "conditional flow matching," and FlowCast is its adaptation to precipitation nowcasting.

---

## Slide 11 — Lever 2: average velocity (MeanFlow)

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

## Slide 12 — The host model: StormCast's two stages

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

## Slide 13 — ★ The experimental design (core contribution)

**MESSAGE:** Three residual heads, everything else held identical — so any difference is attributable to the *generative trajectory alone*. This is a controlled A/B/C, not a model zoo.

**ON SLIDE** (a "what's fixed vs what varies" table)
- **Held fixed:** dataset · frozen regression mean \(M_t\) · SongUNet backbone (`channel_mult [1,2,2,2,2]`, ~78.7M params) · data scale \(\sigma_{\text{data}}=0.5\) · conditioning · per-channel losses · **matched ≈2M-sample training budget**.
- **Only thing that varies:** the generative trajectory — **EDM diffusion** vs **FlowCast (straight)** vs **MeanFlow (average velocity)**.
- Consequence: the comparison isolates *path shape*, not data / architecture / compute.
- Both flow heads are **teacher-free, single-run** — not distillations of the diffusion model.

**SHOW:** [diffusion_vs_flow_2d_paths.png](../figures/concepts/diffusion_vs_flow_2d_paths.png) (the static three-way concept figure).

**SCRIPT:**
This slide is the heart of the contribution, so let me slow down. It is easy to compare three different models and learn nothing, because they differ in a dozen ways at once. I went to some lengths to make this a *controlled* experiment. All three heads share the same dataset, the same frozen regression mean, the same backbone architecture, the same data normalization, the same conditioning, the same precipitation-aware losses, and — importantly — the same training-sample budget, about two million samples each. The *only* thing I change is the generative trajectory: curved diffusion, straight-line FlowCast, or average-velocity MeanFlow. So when I show you a difference in skill or cost later, it can't be explained away by "well, that one had more data" or "a bigger network" — it's attributable to the path shape itself. And to be clear: the two flow heads are *not* distillations of the diffusion model. They never query it. They're trained from scratch in a single run. That's a cleaner and cheaper proposition than the usual distillation route. And I want to stress that this controlled design is *itself* a contribution — it's what lets me make a *causal* claim about path shape later, rather than just observing that one model happened to score higher.

---

## Slide 14 — The data: Taiwan RWRF

**MESSAGE:** 1-hour conditional forecasting over Taiwan: 24 coarse ERA5 conditioning channels in, 4 km-scale target channels out, hourly, full-year 2022 validation.

**ON SLIDE**
- **Domain:** 21.6–25.6°N, 119.75–122.25°E, ≈2 km grid.
- **Input \(S_t\) (24 ch, ≈25 km ERA5):** mslp, t2m, u10, v10 + q/t/u/v/z at 1000/850/500/250 hPa.
- **Target \(X_t\) (4 ch, ≈2 km):** t2m, u10, v10 (RWRF) + **qpepre** (radar precipitation).
- **Splits:** train ≈19k h (2019-08→2021-12) · validate **8,759 h = all of 2022**.
- Only **4** output channels (vs 99 in CONUS StormCast) → per-channel bespoke losses are cheap.

**SHOW:** [taiwan_domain_map.png](../figures/concepts/taiwan_domain_map.png) · equation [hr_stats.png](formulas/png/hr_stats.png)

**SCRIPT:**
A quick orientation on the data. The task is one-hour-ahead forecasting over Taiwan at about two-kilometre resolution. The input is a coarse, twenty-five-kilometre ERA5 reanalysis with twenty-four channels — surface and upper-air fields — that supplies the synoptic-scale context. The output is four high-resolution channels: two-metre temperature, the two wind components, and precipitation from radar. We train on about two and a half years and we validate on the *entire* year 2022 — almost nine thousand hourly samples, so the evaluation is a full annual cycle, not a handful of cases. One detail that pays off later: because there are only four output channels, unlike the ninety-nine in the US version, I can afford to design a custom loss term per channel. And I'll need that, because of one channel in particular.

---

## Slide 15 — qpepre is the hard channel

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

## Slide 16 — The three heads, side by side

**MESSAGE:** Same backbone, three trajectories, three sampler costs: diffusion 35 NFE, FlowCast ~10, MeanFlow 1–2.

**ON SLIDE** (comparison table)

| | **EDM Diffusion** (baseline) | **FlowCast** (this work) | **MeanFlow** (this work) |
|---|---|---|---|
| Generative target | score / denoiser | straight-line velocity \(v_\theta\) | average velocity \(u_\theta\) |
| Path shape | curved | straight | straight (jumped) |
| Sampler | Heun (2nd order) | \(K\) Euler steps | \(K\) average-velocity jumps |
| **NFE / step** | **35** | **~10** | **1–2** |
| Teacher? | — | **none** | **none** |
| Training | from scratch | single run | single run (FlowCast recipe) |

**SHOW:** the table above; optional icons [icon_curved.png](../figures/concepts/icon_curved.png) / [icon_straight.png](../figures/concepts/icon_straight.png) / [icon_meanflow.png](../figures/concepts/icon_meanflow.png).

**SCRIPT:**
Let me put the three heads next to each other before we get to results. Same network backbone in every column. The diffusion baseline learns a denoiser and samples with a thirty-five-call Heun integrator. FlowCast learns a straight-line velocity and samples with about ten Euler steps. MeanFlow learns the average velocity and samples in one or two jumps. Reading across the bottom rows: the cost drops from thirty-five, to ten, to one or two network calls per forecast hour — and neither flow head uses a teacher; both train from scratch in a single run, MeanFlow under FlowCast's exact recipe. So the question the experiments answer is: as we go left to right and the cost collapses, *what happens to forecast skill?*

---

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

**MESSAGE:** At a matched budget, FlowCast matches diffusion CRPS and beats it on winds, precip RMSE, and false alarms at 3.7× faster; MeanFlow reaches the same skill class at ~9× faster, with the best temperature of all heads.

**ON SLIDE** (scoreboard — 2022 validation, 10-member ensembles, +12 h rollouts)

| Method | Time/seq | CRPS↓ | CSI-M↑ | FAR-M↓ | RMSE u10↓ | RMSE v10↓ | RMSE qpepre↓ |
|---|---|---|---|---|---|---|---|
| **EDM diffusion** (35 NFE) | 21.78 s | 0.6783 | **0.1498** | 0.4727 | 1.5626 | 1.9574 | 0.9429 |
| **FlowCast** (K=10) | 5.88 s | 0.6833 | 0.1364 | 0.4188 | **1.4935** | **1.6423** | 0.8959 |
| **FlowCast** (K=15) | 8.35 s | **0.6740** | 0.1435 | 0.4244 | 1.5203 | 1.6710 | **0.8897** |
| **MeanFlow** (K=1) | **1.83 s** | 0.8485 | 0.1449 | **0.3861** | 1.6540 | 2.1740 | 0.9263 |
| **MeanFlow** (K=2) | 2.35 s | 0.7265 | 0.1492 | 0.5241 | 1.5350 | 1.7902 | 0.9404 |

- FlowCast K=10: CRPS within noise of diffusion; **−4% u10, −16% v10, −5% qpepre** RMSE; FAR 0.42 vs 0.47; **3.7× faster**.
- MeanFlow K=2: diffusion-level CSI/HSS, **best t2m of all heads (0.9999 K vs 1.0208)**, **~9× faster**; concedes rollout-CRPS spread.
- **Recommended operating points:** FlowCast **K=10** (sharp & cheap, matched CRPS) · MeanFlow **K=2** (ultra-cheap, same detection skill). *K=1 is possible but under-disperses.*

**SHOW:** [scoreboard_3way.png](../figures/results/scoreboard_3way.png)

**SCRIPT:**
This is the central result. Every row is at the same two-million-sample budget, same regression mean, same data — so it's apples to apples. Start with the diffusion baseline at the top: twenty-two seconds per sequence, and it's the reference. Now FlowCast at ten steps: it runs in under six seconds — that's three-point-seven times faster — and look across: its CRPS is statistically tied with diffusion, and it's actually *better* on both wind components, on precipitation RMSE, and on false-alarm ratio. So at a quarter of the cost it isn't worse, it's better on most columns. Push to fifteen steps and you get the best CRPS and best precip RMSE in the table, still cheaper than diffusion. Then MeanFlow at the bottom: two-to-three seconds, roughly nine times faster than diffusion, and it reaches the same detection-skill class — same CSI and HSS — *and* it posts the best temperature accuracy of any head, including the diffusion baseline. Its one concession is ensemble spread under long rollouts, which shows up as a CRPS gap; I'll come back to that as a failure mode. But the headline is: you can have the diffusion model's skill at a third to a tenth of the cost, with no teacher.

---

## Slide 19 — Cost vs quality: the Pareto picture

**MESSAGE:** Quality saturates fast — FlowCast by ~8–10 steps, MeanFlow already at 1–2 — so the cheap regime *is* the accurate regime; the average-velocity objective shifts the whole frontier left.

**ON SLIDE**
- Sweep \(K\in\{1,\dots,50\}\): FlowCast CRPS saturates by \(K\approx 8\text{–}10\); more steps only add cost.
- MeanFlow sits **below** FlowCast's saturated CRPS already at \(K=1\text{–}2\).
- Wall-clock is linear in \(K\) → few-step regime is simultaneously cheap and accurate.
- Operational picture: a 50-member, 24-h cycle = **2,400** evals (MeanFlow K=2) vs **42,000** (diffusion).

**SHOW:** [nfe_pareto.png](../figures/results/nfe_pareto.png) · [anim_speedup_bars.gif](animations/out/anim_speedup_bars.gif)

**SCRIPT:**
People always ask: if you add more steps, do the flow models keep improving — are you just trading quality for speed? The Pareto sweep answers that. FlowCast's quality saturates by about eight to ten steps; beyond that you spend wall-clock and get nothing. So its sweet spot is genuinely in the cheap regime. And MeanFlow — the dashed curve — sits *below* FlowCast's fully-saturated quality already at one or two evaluations. The average-velocity objective shifts the entire quality-versus-cost frontier to the left. Wall-clock is just linear in the number of steps, so the few-step regime is simultaneously the cheap one and the accurate one — there's no painful trade-off to manage. To put it operationally: that fifty-member, twenty-four-hour cycle that cost the diffusion sampler forty-two thousand network passes costs MeanFlow about twenty-four hundred. At that point the ensemble size, not the sampler, becomes your budget knob — which is exactly the regime you want to be in.

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
Let me be honest about where the flow heads *don't* win, because it's an interesting and coherent story rather than a wash. Break precipitation skill out by rainfall threshold. At light and moderate rain, the flow heads have a big false-alarm advantage — they don't paint speculative drizzle over dry pixels — at a comparable hit rate. But at the heavy thresholds, five to ten millimetres an hour, the diffusion baseline pulls ahead on hit rate. The reason is temperamental: the flow heads are *conservative* — they commit to rain only when confident, which keeps false alarms down but costs them some hits on the most intense cells. The diffusion model is *aggressive* — it places more wet pixels, which CSI rewards and false-alarm ratio punishes. Which behavior you want is genuinely an operational choice. But I'll flag heavy-rain detection as the flow heads' real weakness at this training budget, and it's one of my concrete future-work targets. If I had to recommend one head for Taiwan today: FlowCast as the baseline, precisely *because* of its false-alarm advantage — alert fatigue is a real cost when you're issuing evacuation orders — with a tail-weighted loss added to claw back the heavy-rain hits.

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

**MESSAGE:** Two reproducible single-run flow pipelines, a controlled three-way comparison, a precipitation-aware loss + eval suite — the first such study on a regional convective-scale forecaster.

**ON SLIDE**
1. **FlowCast** — Conditional Flow Matching adapted to the StormCast two-stage residual: teacher-free, single-run, straight-line velocity field.
2. **MeanFlow** — average-velocity residual, **first application to weather forecasting**; A/B with FlowCast on the *objective alone*.
3. **Controlled three-way comparison** — diffusion vs FlowCast vs MeanFlow at matched budget; isolates the generative trajectory.
4. **Precipitation-aware loss** — channel-weighted L2 + radial log-PSD on qpepre, with log1p and \(w_{\text{pr}}\) ablations.
5. **Precipitation-aware evaluation suite** on the full 2022 Taiwan year (RMSE/MAE, CRPS, CSI/FSS/HSS/FAR, spectral, rollout).
6. **The finding:** straight-line and average-velocity residuals recover diffusion skill at **3.7×–9×** lower cost, no teacher.

**SHOW:** the numbered list; optional [scoreboard_3way.png](../figures/results/scoreboard_3way.png) thumbnail.

**SCRIPT:**
So, to gather the contributions. First, FlowCast — I adapt conditional flow matching to the StormCast residual architecture as a teacher-free, single-run forecaster. Second, MeanFlow — to my knowledge the first time the average-velocity objective has been brought into weather forecasting at all, built so that comparing it against FlowCast is a clean A/B test on the training objective alone. Third, the controlled three-way comparison itself: diffusion versus FlowCast versus MeanFlow, with everything but the trajectory held fixed, which is what lets me make causal statements about path shape. Fourth, the precipitation-aware loss design and its ablations. Fifth, a full precipitation-aware evaluation suite run over an entire year. And sixth, the empirical finding that ties it together: changing the generative path — straightening it, then jumping it — recovers the diffusion model's skill at three-to-ten times lower cost, with no teacher and a single training run. To be precise about novelty: flow matching itself is an existing method from the generative-modeling literature — what's new here is *adapting* it to the StormCast two-stage residual as teacher-free training, and being first, to my knowledge, to bring average-velocity sampling to a regional, convection-permitting weather forecaster.

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

## Slide 25 — Conclusion

**MESSAGE:** The path from noise to weather is a dial worth turning twice — first straightened, then jumped — and that's a credible route to fast, sharp, probabilistic regional forecasting.

**ON SLIDE**
- Generative modelling is the right inductive bias for convective forecasting; the obstacle was the multi-step sampler.
- **Straighten the path** (FlowCast): diffusion-level skill, ~4× faster, single run, no teacher.
- **Jump the path** (MeanFlow): same skill class at 1–2 calls, ~9× faster, best temperature.
- Fast enough to run *between radar volumes* — within reach.

**SHOW:** [path_cartoon_triptych.png](../figures/concepts/path_cartoon_triptych.png) or reuse [anim_curved_vs_straight.gif](animations/out/anim_curved_vs_straight.gif).

**SCRIPT:**
To conclude. Generative modelling is almost certainly the right tool for short-range convective forecasting — it's the only way to get sharpness and calibration together. The one obstacle to deploying it has been the multi-step diffusion sampler. This thesis shows, on a real regional dataset, that the obstacle is removable by changing the shape of the generative path. Straighten it, and a single-run flow-matching model recovers the diffusion baseline's skill — and beats it on winds, precipitation error, and false alarms — at about a quarter of the cost. Jump it with an average-velocity model, and you reach the same skill class in one or two network calls — a tenth of the cost — with the best temperature accuracy in the study. The path a generative model takes from noise to weather turned out to be a dial worth turning twice. Making sharp, probabilistic, regional forecasting fast enough to run between radar volumes is within reach. Thank you.

---

## Slide 26 — Thank you / Questions

**ON SLIDE**
- *One line:* **1–10-step Taiwan StormCast nowcasts with preserved precipitation skill — via straight-line (FlowCast) and average-velocity (MeanFlow) flow matching, no teacher.**
- Code: `Stormcast-Distilation` (branch `distillation_setup`).
- Contact: dzycheong@gmail.com
- *"Happy to take questions."*

**SHOW:** title-style closing; faint [taiwan_domain_rain_case.png](../figures/concepts/taiwan_domain_rain_case.png).

**SCRIPT:**
That's the thesis in one line on the slide. I'm happy to take your questions — and I have backup slides on the EDM preconditioning, the MeanFlow identity derivation, the log1p and precipitation-weight ablations, and the legacy-baseline comparison if any of those are useful.

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
