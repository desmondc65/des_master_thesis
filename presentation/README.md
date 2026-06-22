# Defense Presentation Package

Everything needed to assemble the ~27-minute master's-defense talk:
slide content with speaker scripts, every equation rendered to PNG, and a set of
explanatory animations. Grounded in the thesis chapters
([../contents/chapter01.tex](../contents/chapter01.tex) … `chapter05.tex`).

> **Note:** the talk reflects the *current* thesis — a three-way comparison of an
> **EDM diffusion** residual against two teacher-free flow-matching residuals,
> **FlowCast** (straight-line Conditional Flow Matching) and **MeanFlow**
> (average velocity). It supersedes the older `../slide_content.md`, which still
> describes the earlier PD/CD distillation framing.

## Contents

| File / dir | What it is |
|---|---|
| [presentation.md](presentation.md) | The deck: 26 slides + backup. Per slide — message, on-slide bullets, which asset to show, and the verbatim speaker script. |
| [speaker_script.md](speaker_script.md) | Timing budget, slide-to-slide transitions, a defense Q&A bank, and delivery tips. |
| `formulas/` | LaTeX → PNG for every equation. `src/*.tex` (editable), `png/*.png` (black, light slides), `png_white/*.png` (white, dark slides). |
| `animations/` | Python (matplotlib) animations → `out/*.gif` (PowerPoint/Keynote) and `out/*.mp4` (web/Reveal.js). |

## Rebuilding the assets

```bash
# Equations  (needs: pdflatex, pdftocairo)
cd formulas && python3 build_formulas.py          # all
python3 build_formulas.py icfm_path meanflow_identity   # just some

# Animations (needs: python3 + matplotlib; ffmpeg optional for mp4)
cd ../animations && bash build.sh                 # all
python3 anim_curved_vs_straight.py                # just one
```

Formula PNGs are 600-dpi, transparent background. For a dark slide template use the
matching file in `formulas/png_white/`.

## Slide → asset map

`F:` = thesis figure ([../figures/](../figures/)) · `E:` = equation (`formulas/png/`) · `A:` = animation (`animations/out/`)

| # | Slide | Assets |
|---|---|---|
| 1 | Title | F: concepts/taiwan_domain_rain_case |
| 2 | One-slide story | **A: anim_curved_vs_straight** |
| 3 | Why Taiwan | F: concepts/taiwan_domain_map · taiwan_domain_rain_case |
| 4 | History of forecasting | (timeline; optional concept icons) |
| 5 | Why generative (blurry mean) | F: concepts/blur_vs_members |
| 6 | Diffusion in 1 minute | **A: anim_noise_to_field** · E: forward_noising |
| 7 | Diffusion recipe + EDM | E: tweedie, pf_ode, edm_params, heun_nfe |
| 8 | The cost problem | **A: anim_cost_problem** · E: cost_blowup |
| 9 | The path is curved | **A: anim_integration_error** |
| 10 | FlowCast (straight line) | A: anim_curved_vs_straight · E: icfm_path, icfm_target, icfm_loss, flowcast_sampler |
| 11 | MeanFlow (average velocity) | **A: anim_meanflow_jump** · E: meanflow_avgvel, meanflow_displacement, meanflow_identity |
| 12 | StormCast two stages | F: stormcast_architecture · E: two_stage, conditioning |
| 13 | ★ Experimental design | F: concepts/diffusion_vs_flow_2d_paths |
| 14 | Data: Taiwan RWRF | F: concepts/taiwan_domain_map · E: hr_stats |
| 15 | qpepre is the hard channel | F: highres_distributions/…_qpepre_gaussian_check · E: channel_l2, logpsd, log1p |
| 16 | Three heads side by side | (table) · concept icons icon_curved/straight/meanflow |
| 17 | Metrics | E: rmse, csi_far, fss |
| 18 | ★ Headline scoreboard | F: results/scoreboard_3way (table embedded) |
| 19 | Cost–quality Pareto | F: results/nfe_pareto · **A: anim_speedup_bars** |
| 20 | Precip skill by threshold | F: results/csi_per_threshold · fss_p16 |
| 21 | Rollout + qualitative | F: results/rollout_rmse · qual_qpepre_seq00 · qual_u10_seq00 |
| 22 | Failure modes | F: results/crps_per_channel |
| 23 | ★ Contributions | (list) · results/scoreboard_3way thumb |
| 24 | Limitations & future work | (lists) |
| 25 | Conclusion | F: concepts/path_cartoon_triptych · A: anim_curved_vs_straight |
| 26 | Thank you / Q&A | F: concepts/taiwan_domain_rain_case |

## Animation index

| File | Slide | What it shows |
|---|---|---|
| `anim_curved_vs_straight` | 2, 10, 25 | Same noise→forecast journey, three routes: diffusion (curved, 35 calls) / FlowCast (straight, ~10) / MeanFlow (1 jump). The concept centerpiece. |
| `anim_noise_to_field` | 6 | A precip field is noised to static, then a generative model integrates noise back into a sharp forecast. *(Use the `.mp4`; the `.gif` is ~13 MB.)* |
| `anim_integration_error` | 9 | Approximating a path with K straight hops: a curve needs many; a straight line is exact at K=1. |
| `anim_meanflow_jump` | 11 | Instantaneous velocity (many small arrows) vs average velocity (one big arrow across the interval). |
| `anim_cost_problem` | 8 | 35 NFE × 24 h × 50 members = 42,000 U-Net passes per cycle, assembled live. |
| `anim_speedup_bars` | 19 | Wall-clock bars: diffusion 21.78 s → FlowCast 5.88 s (3.7×) → MeanFlow 2.35 s (9.3×). |

## Key numbers (verified against the thesis chapters)

- Diffusion teacher: 35 NFE/step (18-step Heun) · EDM σ = (0.002, 80, 0.5, ρ=7).
- Cost blow-up: 50 × 24 × 35 = 42,000 passes/cycle.
- Scoreboard (2022, 10-member, +12 h): EDM 21.78 s / CRPS 0.6783 · FlowCast K=10 5.88 s / 0.6833 (**3.7×**) · MeanFlow K=2 2.35 s / 0.7265 (**~9×**); MeanFlow K=2 best t2m (0.9999 K).
- Losses: β = (1,1,1,2), λ_spec = 0.1, log1p qpepre (σ 9.12 → ≈0.37).
- Backbone: SongUNet `channel_mult [1,2,2,2,2]`, ≈78.7 M params, shared by all heads.
