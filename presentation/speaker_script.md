# Speaker Script & Delivery Notes

Companion to [presentation.md](presentation.md). The **verbatim narration** lives in the
`SCRIPT` block of each slide there. This file adds what a defense actually needs:
a **timing budget**, **transitions** between slides, an **anticipated Q&A bank**, and
**delivery tips**. Read this the night before; glance at the timing column while presenting.

---

## 1. Timing budget (target 27 min talk + 8–13 min Q&A)

| Block | Slides | Minutes | Cumulative |
|---|---|---|---|
| Hook + one-slide story | 1–2 | 2.5 | 2:30 |
| Motivation (Taiwan, why generative) | 3–5 | 3.5 | 6:00 |
| Background (diffusion, EDM, the cost) | 6–8 | 4.0 | 10:00 |
| The idea (curved → straight → jump) | 9–11 | 4.0 | 14:00 |
| Setup (StormCast, the design, data, qpepre) | 12–15 | 4.0 | 18:00 |
| Methods recap + metrics | 16–17 | 1.5 | 19:30 |
| **Results** (scoreboard, Pareto, thresholds, rollout) | 18–21 | 5.0 | 24:30 |
| Failure modes + contributions | 22–23 | 1.5 | 26:00 |
| Limitations + conclusion + thanks | 24–26 | 1.5 | 27:30 |

**Pacing rule of thumb:** ~60 s/slide; results slides (18, 19) get ~75 s. If you're behind,
the *compressible* slides are 4, 7, 17, 24 — trim to 30 s each. **Never** rush 13 (the design)
or 18 (the scoreboard) — those are the slides that earn the degree.

---

## 2. Transitions (the one sentence that carries you into the next slide)

- **1→2:** "Let me give you the entire argument on one slide, then we'll unpack it."
- **2→3:** "Start with *why* — why does a regional center care about sampling speed?"
- **5→6:** "So we want to sample a distribution. The dominant way to do that is diffusion — here's how it works."
- **8→9:** "Forty-two thousand passes is the wall. Now *why* does diffusion need so many steps?"
- **9→10:** "If curvature is the problem, the obvious fix is: make the path straight."
- **11→12:** "Two recipes — but where do they actually plug in? Into StormCast's second stage."
- **13→14:** "That's the experiment. Now the data it runs on."
- **15→16:** "With the data and losses set, here are the three contenders side by side."
- **17→18:** "Five metric families, one validation year — here's what they say."
- **18→19:** "You might ask: would more steps change the verdict? No — here's why."
- **21→22:** "I've shown you where they win; let me be equally clear about where they don't."
- **23→24:** "Those are the contributions; here's what I have *not* yet shown."
- **25→26:** "…within reach. Thank you — questions?"

---

## 3. Anticipated Q&A bank (rehearse these out loud)

**Q: Why three methods — isn't this just a model zoo?**
A: They isolate different things. The diffusion baseline is the reference everyone trusts.
FlowCast isolates the effect of *straightening the path*. MeanFlow isolates the effect of
*removing the integral*, and because its objective collapses to FlowCast's, it's a clean A/B on
the training objective alone. Everything else is held fixed, so it's a controlled comparison, not a zoo.

**Q: FlowCast/MeanFlow don't use the teacher at all — so why call this "distillation"?**
A: I don't, in the thesis — and that's the point. The standard route to a fast sampler is
distillation: train a student to imitate a slow teacher, in a second stage. I show you can skip
that entirely by reshaping the generative path and training once, from scratch. The repository is
historically named "distillation," but the contribution is the teacher-free alternative.

**Q: Is the comparison fair if the methods use different batch sizes / step counts?**
A: I compare at a matched *training-sample* budget (~2M samples), not matched optimizer steps,
precisely because batch sizes differ. And the inference cost is reported as wall-clock per sequence
and as NFE, so the speed claims are direct. The one caveat is single-snapshot validation noise of
10–30%, which is why I only emphasize gaps larger than that.

**Q: Your heavy-rain CSI is worse than diffusion — isn't that disqualifying for Taiwan?**
A: It's the honest weak point. But two mitigations: the neighbourhood FSS recovers part of it, so
it's partly a displacement not a pure miss; and the flow heads' *false-alarm* advantage is large,
which matters just as much operationally. It's a conservative-vs-aggressive trade, and I have
concrete fixes scoped — tail-quantile loss, higher precipitation weight, longer training.

**Q: How do you know the precipitation skill comes from the flow head, not the frozen regression mean?**
A: All three heads share the *same* frozen regression mean, so the mean cancels out of the
comparison. Any difference between diffusion, FlowCast, and MeanFlow is attributable to the
residual head. The residual carries the sharp convective structure; the mean is smooth.

**Q: Why is MeanFlow's CRPS worse at K=1 if its single-step skill is the best in the study?**
A: Under-dispersion. One average-velocity jump lands each ensemble member almost on the conditional
mean, so the ensemble is too narrow — deterministic accuracy is intact but the *spread* is too small,
and CRPS penalizes that. A second evaluation restores most of the spread, which is why I recommend K=2.
The deficit compounds over rollout because each hour's narrow ensemble seeds the next.

**Q: Why not just use a faster diffusion solver (DPM-Solver, etc.)?**
A: Better solvers help but bottom out around 10–20 NFE because the path is still curved — below
that, curvature error becomes visible, worst on precipitation. Reshaping the path to a straight
line removes the curvature itself, so 1–2 steps become viable. They're complementary ideas; I take
the structural one.

**Q: Does the log1p encoding bias the metrics?**
A: All metrics are computed on *denormalized* fields in physical units (mm/h) — the encoding is
inverted per-pixel before scoring. The log1p ablation is reported in standardized space only because
inverting a scalar RMSE through expm1 is mathematically invalid; the mm/h-correct comparison is the
denormalized scoreboard.

**Q: Would these results transfer to another region / a larger ensemble?**
A: Untested, and I list both as future work. The pipeline is region-agnostic in principle (swap the
regression mean), and the cheap sampler is exactly what makes 50–100-member calibration studies
affordable for the first time — that's the payoff I most want to chase next.

**Q: 78.7M-parameter backbone — same for all heads?**
A: Yes, identical SongUNet backbone (`channel_mult [1,2,2,2,2]`) for all three. MeanFlow adds only a
tiny Fourier-feature map for the second time input — negligible against the backbone.

---

## 4. Delivery tips

- **Anchor every abstract word.** Whenever you say "denoiser," "residual," "velocity field," add
  "…the part that predicts what the radar will show next hour." The non-ML committee members will
  stay with you only if you keep tying back to rain on a map.
- **The three colours are a through-line.** Orange = diffusion, blue = FlowCast, green = MeanFlow,
  consistently from Slide 2's animation to the scoreboard. Point at the colour, not the name.
- **Lead with the number, then explain.** On the scoreboard say "3.7× faster, same CRPS" *first*,
  then justify. Committees remember the headline number.
- **Two equations are load-bearing; the rest are reassurance.** Spend real time only on Slide 10
  (straight-line target \(u_t=x_1-x_0\)) and Slide 11 (the boxed MeanFlow identity). Let the others
  flash by — "the details are standard / in the thesis."
- **Rehearse the failure-mode slide (22) most.** Confidently owning your weaknesses is what reads as
  mastery in a defense. Don't apologize — diagnose.
- **Animations:** set them to play on click, not auto-loop, so you control the beat. Have the static
  fallback figure ([diffusion_vs_flow_2d_paths.png](../figures/concepts/diffusion_vs_flow_2d_paths.png))
  one click away in case a video fails on the projector.
- **If a question stumps you:** "That's exactly the experiment I'd run next" is honest and strong when
  it's true (convergence, transfer, large ensembles all qualify).

---

## 5. The 60-second version (if the chair says "you have one minute")

"Diffusion weather models are sharp and probabilistic but need ~35 network calls per forecast hour —
forty-two thousand per operational cycle. That's because the path they travel from noise to a forecast
is curved. I show that if you *straighten* that path with flow matching — FlowCast — you recover the
diffusion model's skill, and beat it on winds, precipitation error, and false alarms, at a quarter of
the cost, trained from scratch with no teacher. And if you learn the *average* velocity over the
interval — MeanFlow — you jump from noise to forecast in one or two calls, a tenth of the cost, with
the best temperature accuracy in the study. Same backbone, same data, same regression mean — only the
generative path changes. The path from noise to weather is a dial worth turning twice."
