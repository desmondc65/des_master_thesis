# Slide Citations — GenCast · StormCast · FlowCast · MeanFlow

Footer-ready citation strings for the four works the talk leans on, with full references
and the matching thesis BibTeX keys (so `\cite{...}` stays consistent with
[back/references.bib](../back/references.bib)).

**House style for a slide footer:** small, gray, bottom-left — *first-author et al. (year), source*.
Show only the one or two citations relevant to the slide, not all four every time.

---

## 1. Copy-paste footer strings (recommended)

Drop one of these into the footer of the relevant slide.

| Work | **Footer (recommended)** |
|---|---|
| **GenCast** | `Price et al. (2024), Nature — arXiv:2312.15796` |
| **StormCast** | `Pathak et al. (2024), arXiv:2408.10958` |
| **FlowCast** | `Perrone Ribeiro & Faganeli Pucer (2025), arXiv` |
| **MeanFlow** | `Geng et al. (2025), arXiv:2505.13447` |

**Ultra-compact** (when the footer is tight or several stack on one slide):

| Work | Footer (ultra-compact) |
|---|---|
| GenCast | `GenCast — Price et al. 2024` |
| StormCast | `StormCast — Pathak et al. 2024` |
| FlowCast | `FlowCast — Perrone Ribeiro & Faganeli Pucer 2025` |
| MeanFlow | `MeanFlow — Geng et al. 2025` |

**With the method name leading** (good when the slide *is* about that method):

| Work | Footer (named) |
|---|---|
| GenCast | `GenCast: Price et al., Nature (2024)` |
| StormCast | `StormCast: Pathak et al., arXiv:2408.10958 (2024)` |
| FlowCast | `FlowCast: Perrone Ribeiro & Faganeli Pucer, arXiv (2025)` |
| MeanFlow | `MeanFlow: Geng et al., arXiv:2505.13447 (2025)` |

---

## 2. Per-work detail

### GenCast
- **What it is:** probabilistic ML weather forecasting (diffusion-based global ensemble) — the "generative turn" reference in Related Work.
- **Footer:** `Price et al. (2024), Nature — arXiv:2312.15796`
- **Full reference:** I. Price, A. Sanchez-Gonzalez, F. Alet, T. R. Andersson, A. El-Kadi, D. Masters, T. Ewalds, J. Stott, S. Mohamed, P. Battaglia, R. Lam, M. Willson. *Probabilistic Weather Forecasting with Machine Learning.* **Nature** (2024). arXiv:2312.15796.
- **BibTeX key:** `price2024gencast`

### StormCast
- **What it is:** the host model — kilometer-scale convection-allowing emulation via generative diffusion; the EDM diffusion residual is the baseline this thesis accelerates.
- **Footer:** `Pathak et al. (2024), arXiv:2408.10958`
- **Full reference:** J. Pathak, Y. Cohen, P. Garg, P. Harrington, N. Brenowitz, D. Durran, M. Mardani, A. Vahdat, S. Xu, K. Kashinath, M. Pritchard. *Kilometer-Scale Convection Allowing Model Emulation using Generative Diffusion Modeling.* **arXiv preprint** arXiv:2408.10958 (2024).
- **BibTeX key:** `pathak2024stormcast`

### FlowCast
- **What it is:** straight-line conditional-flow-matching precipitation nowcasting — the flow-matching baseline MeanFlow generalises.
- **Footer:** `Perrone Ribeiro & Faganeli Pucer (2025), arXiv`
- **Full reference:** B. Perrone Ribeiro, J. Faganeli Pucer. *FlowCast: Advancing Precipitation Nowcasting with Conditional Flow Matching.* **arXiv preprint** (2025).
- **BibTeX key:** `ribeiro2025flowcast`

### MeanFlow
- **What it is:** average-velocity flow matching for one-step generation — the method of this thesis.
- **Footer:** `Geng et al. (2025), arXiv:2505.13447`
- **Full reference:** Z. Geng, M. Deng, X. Bai, J. Z. Kolter, K. He. *Mean Flows for One-step Generative Modeling.* **arXiv preprint** arXiv:2505.13447 (2025).
- **BibTeX key:** `geng2025meanflow`

---

## 3. Ready-to-paste "References" slide

Use this block on a closing/backup references slide.

```
References

[1] J. Pathak et al. "Kilometer-Scale Convection Allowing Model Emulation using
    Generative Diffusion Modeling." arXiv:2408.10958, 2024.  (StormCast)

[2] I. Price et al. "Probabilistic Weather Forecasting with Machine Learning."
    Nature, 2024. arXiv:2312.15796.  (GenCast)

[3] B. Perrone Ribeiro and J. Faganeli Pucer. "FlowCast: Advancing Precipitation
    Nowcasting with Conditional Flow Matching." arXiv preprint, 2025.  (FlowCast)

[4] Z. Geng, M. Deng, X. Bai, J. Z. Kolter, K. He. "Mean Flows for One-step
    Generative Modeling." arXiv:2505.13447, 2025.  (MeanFlow)
```

---

## 4. Which slides each footer belongs on

(Slide numbers per the reorganized [presentation.md](presentation.md).)

| Slide | Topic | Footer to show |
|---|---|---|
| 1 — Title | StormCast + MeanFlow named | `StormCast — Pathak et al. 2024` · `MeanFlow — Geng et al. 2025` |
| 2 — One-slide story | the whole axis | StormCast · FlowCast · MeanFlow |
| 4 — Forecasting history | generative turn | `GenCast — Price et al. 2024` |
| 6–7 — Diffusion / EDM teacher | StormCast diffusion baseline | `StormCast — Pathak et al. 2024` |
| 12 — FlowCast (straight line) | the FM baseline | `FlowCast — Perrone Ribeiro & Faganeli Pucer 2025` |
| 13 — MeanFlow (average velocity) | the method | `MeanFlow — Geng et al. 2025` |
| 14 — StormCast two stages | host architecture | `StormCast — Pathak et al. 2024` |
| 16 — Three heads | all three heads | StormCast · FlowCast · MeanFlow |

---

## 5. Footer syntax cheatsheet

- **PowerPoint / Keynote** (`thesis_defense.pptx`): Insert → Header & Footer → Footer; paste the recommended string. Or a small left-aligned gray text box, ~10–12 pt, in the bottom margin.
- **Beamer:** put it in the frame, not the global footline, so it only shows where relevant:
  ```latex
  \frame{ ... \vfill {\tiny\color{gray} Pathak et al. (2024), arXiv:2408.10958} }
  ```
  or as a margin note: `\footnotetext[0]{\tiny StormCast: Pathak et al. (2024), arXiv:2408.10958}`.
- **Reveal.js / Marp / Markdown slides:** a footer line in muted text:
  ```markdown
  <small style="color:#888">StormCast — Pathak et al. (2024), arXiv:2408.10958</small>
  ```
- Keep it to **one line**; if two works share a slide, separate with ` · ` (middot).
