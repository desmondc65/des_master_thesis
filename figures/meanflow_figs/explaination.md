# MeanFlow StormCast — Figure Explanations

This document explains the three TikZ figures in this folder block-by-block, so
the diagrams can be narrated in the thesis / a talk. Everything here is taken
from the actual implementation:

- training loop — [`stormcast/utils/trainer_meanflow.py`](../../../stormcast/utils/trainer_meanflow.py)
- objective / loss — [`stormcast/utils/meanflow_loss.py`](../../../stormcast/utils/meanflow_loss.py)
- network wrapper — [`stormcast/utils/meanflow_precond.py`](../../../stormcast/utils/meanflow_precond.py)
- conditioning / sampler glue — [`stormcast/utils/nn.py`](../../../stormcast/utils/nn.py)
- config — [`config/model/meanflow.yaml`](../../../stormcast/config/model/meanflow.yaml), [`config/training/meanflow.yaml`](../../../stormcast/config/training/meanflow.yaml)
- write-up — [`stormcast/docs/meanflow.md`](../../../stormcast/docs/meanflow.md)

Method reference: Geng et al. 2025, *Mean Flows for One-step Generative Modeling*
(arXiv:2505.13447).

The three figures are:

| File | What it shows |
|---|---|
| `meanflow_overall.png` | the whole training step (data → frozen regression → condition/residual → objective → optimizer/EMA → validation) |
| `meanflow_network.png` | the `MeanFlowPrecond` network internals (SongUNet + the two time embeddings) |
| `meanflow_objective.png` | the MeanFlow loss: time sampling, the I-CFM vs JVP-identity targets, and the loss terms |

---

## 0. Notation & symbols (shared by all figures)

| Symbol | Meaning | Channels / shape |
|---|---|---|
| $X_{t-1}$ | previous HighRes atmospheric state (the autoregressive input) | 4 ch: t2m, u10, v10, qpepre |
| $S_t$ | ERA5 background / low-res conditioning for the current hour | 24 ch |
| $I$ | static invariants (land–sea mask, orography) | 2 ch |
| $X_t$ | **target** HighRes state at the current hour | 4 ch |
| $F_\xi$ | frozen regression net (`StormCastUNet`) | — |
| $M_t = F_\xi(X_{t-1},S_t,I)$ | deterministic regression **mean** | 4 ch |
| $R_t = X_t - M_t$ | **residual** the flow model actually learns | 4 ch |
| $c_t = \mathrm{concat}(X_{t-1}, M_t, I)$ | conditioning bundle fed to the flow net | **10 ch** (4+4+2) |
| $\sigma_{\text{data}}=0.5$ | std used to standardize the residual | scalar |
| $x_1 = R_t/\sigma_{\text{data}}$ | standardized data endpoint of the flow ($\tau=1$) | 4 ch |
| $x_0 \sim \mathcal N(0,I)$ | noise endpoint of the flow ($\tau=0$) | 4 ch |
| $v = x_1 - x_0$ | **instantaneous** velocity (constant on the straight path) | 4 ch |
| $r \le t$ | the two flow times in $[0,1]$ | scalars per sample |
| $z_r = (1-r)x_0 + r\,x_1$ | point on the trajectory at time $r$ | 4 ch |
| $u_\theta(z_r, r, t, c_t)$ | **average** velocity over $[r,t]$ — the network output | 4 ch |

**Key idea in one line.** Instead of learning the *instantaneous* velocity $v$ (which
needs many integration steps to sample), MeanFlow learns the *average* velocity
$u$ over a whole interval $[r,t]$, so a single network call jumps across the
interval: $z_t = z_r + (t-r)\,u_\theta(z_r,r,t)$. That is what enables 1–2 step
sampling.

> **Why a residual?** The expensive flow model only has to represent the
> *stochastic correction* $R_t$ on top of the cheap deterministic mean $M_t$ from
> the (already trained, frozen) regression model. This is the StormCast two-stage
> design, reused unchanged.
>
> **Why is $S_t$ not in $c_t$?** $S_t$ (24 ch ERA5) is consumed only by the
> regression net $F_\xi$. The flow net conditions on
> `diffusion_conditions = [state, regression, invariant]` = $(X_{t-1}, M_t, I)$ →
> 10 channels. This is deliberate and matches the EDM/FlowCast setups.

---

## 1. `meanflow_overall.png` — the training step (macro view)

**Purpose.** One full optimization step of `trainer_meanflow.py`, left-to-right:
load a batch → run the frozen regression → build the condition and the residual
target → evaluate the MeanFlow objective → back-prop → AdamW + EMA → (periodically)
validate and checkpoint.

### Inputs (left column)
- **`X_{t-1}` — HighRes state · 4 ch.** The previous hour's forecast (or ground
  truth during teacher forcing). Top label *“`InfiniteSampler` → DataLoader batch”*
  notes that batches come from an **infinite, rank-sharded sampler** (no epoch
  boundaries) — `trainer_meanflow.py`.
- **`S_t` — ERA5 background · 24 ch.** Low-res conditioning for the current hour.
- **`I` — invariants (lsm, orog) · 2 ch.** Static fields, broadcast across the batch.
- **`X_t` — target HighRes · 4 ch.** The field we are trying to generate; used
  only to form the residual target (it never enters the network as an input).

### Phase 1 — frozen regression (shared with StormCast)
- **`regression F_ξ` (dashed border = frozen).** `StormCastUNet`; weights loaded
  from a pretrained checkpoint and **not** updated here. Consumes $(X_{t-1}, S_t, I)$.
- **`M_t` — regression mean · 4 ch.** Output $M_t = F_\xi(X_{t-1},S_t,I)$. This is
  the deterministic “best guess” that the flow model will correct.

### Building the conditioning and the target (middle)
- **`concat` (black box).** Channel-wise concatenation $X_{t-1}\,\Vert\,M_t\,\Vert\,I$.
- **`condition c_t` · 10 ch.** The bundle fed to the flow network as conditioning.
- **`−` (circle).** Subtraction node.
- **`residual R_t = X_t − M_t` · 4 ch.** The actual learning target. Built by
  `build_network_condition_and_target` in `nn.py`.

### Phase 2 — MeanFlow objective (highlighted box, “trained student”)
- **`MeanFlow objective`.** A single box standing in for the network + loss
  (which are expanded in figures 2 and 3). The text reminds you of the essentials:
  the trained **average-velocity net** $u_\theta(z_r,r,t,c_t)$, the **75 % I-CFM +
  25 % JVP-identity** batch split, and that it is **one network forward per
  micro-batch** (no teacher rollouts, no inner ODE solve at train time).
- **`loss L`.** The scalar minimized: $\mathcal L = \mathcal L_{\text{MF}} + 0.1\,\mathcal L_{\text{spec}}$,
  with per-channel weights $\beta=(1,1,1,2)$ and a qpepre log-PSD term (detailed in fig. 3).

### Optimization (lower-right)
- **`backward → AdamW`.** Back-prop with **gradient accumulation**, **NaN-cleaning**
  (non-finite grads sanitized), **gradient clipping at 1.0**, AdamW with
  $\text{lr}=5\times10^{-4}$, **4 000-step linear warm-up → cosine decay** to
  $0.01\times$ lr. Trained in fp32 (`fp_optimizations: fp32`), `batch_size=64`,
  `total_train_steps=400 000`.
- **`EMA`.** Exponential moving average of the weights,
  $\bar\theta \leftarrow 0.999\,\bar\theta + 0.001\,\theta$, written to
  **`ema_state.pt`**. *Sampling always uses the EMA weights, never the raw online weights.*
- **`update θ` (dashed loop-back).** Closes the training loop: the updated student
  is used on the next batch.

### Validation branch (bottom)
- **`validation` (every 500 steps).** Generates with the **EMA** weights using the
  **2-NFE** few-step sampler and reconstructs the field
  $\hat X_t = M_t + \sigma_{\text{data}}\,z_1$ (`valid_num_steps=2`).
- **metrics box.** RMSE / MAE / log-PSD per field, validation heatmaps, and a
  checkpoint every 5 000 steps.

### Legend
data/tensors (white) · frozen, shared with StormCast (dashed) · trained MeanFlow
net (grey fill) · loss (double border) · optimizer/EMA/validation (grey) · concat ·
subtract.

---

## 2. `meanflow_network.png` — the `MeanFlowPrecond` network

**Purpose.** What is inside the “MeanFlow objective” box at forward time: a
`SongUNet` that maps the current state + condition + the **two times** to the
average velocity. From `meanflow_precond.py`.

Forward call (the one line the whole figure draws):
```
u = model( cat[z_r, c_t],  r * time_scale,  augment_labels = FF(t − r) )
```

### Input assembly (left)
- **`z_r` — state on trajectory · 4 ch.** The current point on the flow path.
- **`condition c_t` · 10 ch.** $\mathrm{concat}(X_{t-1},M_t,I)$ from figure 1.
- **`concat`.** Channel concatenation of state and condition.
- **`arg` · 14 ch.** The actual tensor handed to the SongUNet (4 + 10 = 14 input channels).

### SongUNet backbone (the U)
A standard encoder–bottleneck–decoder with skip connections.
- **`enc ×1`, `enc ×2`, `enc ×2`** — encoder stages; the `×k` is the channel
  multiplier from `channel_mult = [1, 2, 2, 2, 2]`. Spatial resolution halves each
  step down.
- **`bott. ×2`** — bottleneck (lowest resolution, largest receptive field).
- **`dec ×2`, `dec ×2`, `dec ×1`** — decoder stages; resolution doubles each step up.
- **`skip` (dashed horizontals).** Skip connections carry high-resolution features
  from each encoder stage to the matching decoder stage. Three exact horizontals,
  one per level.
- **Tag under the U:** *SongUNet · additive spatial pos. embed ·
  `attn_resolutions = ∅`* — i.e. `spatial_pos_embed = True` (a learned additive
  positional map) and **no self-attention blocks** in this configuration.

### Output (right)
- **`u_θ(z_r, r, t, c_t)` — average velocity · 4 ch.** Same channel layout as the
  residual. Note: querying with **`t = r` collapses the average velocity to the
  instantaneous velocity** (the FlowCast/flow-matching field), so this network is a
  strict generalization of a one-time-variable flow model.

### Time conditioning (top rails → single injection)
The two times enter through **two different pathways**, then are broadcast to every
residual block:
- **Rail 1 (state time `r`):** `r · time_scale (×1000)` → fed to SongUNet's usual
  **noise / positional embedding**. Scaling $r\in[0,1]$ by `time_scale = 1000`
  matches the range the embedding layer expects (same convention as FlowCast/EDM).
- **Rail 2 (interval length `t − r`):** `sin/cos Fourier` features with
  `gap_freqs` log-spaced from **1 → 1000** → produces **`augment_labels`, dim 32**
  (`gap_embed_dim = 32`, fixed/non-learned), injected via SongUNet's `augment`
  pathway.
- **`timestep conditioning`.** The merge of the two embeddings; the single arrow
  into the top of the U with the note *“added into every residual block”* indicates
  the embedding is added inside **every** enc / bottleneck / dec residual block
  (drawn as one arrow purely to keep the diagram readable).

> **Reading tip.** Two distinct things are encoded: *where on the path we are* ($r$)
> and *how far we are integrating* ($t-r$). The network needs both to predict an
> average (not instantaneous) velocity.

---

## 3. `meanflow_objective.png` — the loss / JVP identity

**Purpose.** How the training target is constructed and how the loss is computed —
the core of `meanflow_loss.py`. Two batch sub-populations get **two different
targets**; both are regressed against the single network prediction.

### Flow-space setup (left)
- **`R_t` — residual.** Comes from figure 1.
- **`x_1 = R_t/σ_data` — standardize ($\sigma_{\text{data}}=0.5$).** Puts the
  residual into roughly unit variance so the flow runs between $\mathcal N(0,I)$ and
  unit-scale data.
- **`x_0 ∼ N(0,I)`.** Fresh Gaussian noise (the $\tau=0$ endpoint).
- **`v = x_1 − x_0` — instantaneous velocity.** For a straight-line path the
  velocity is constant and equal to this difference. This is the ground-truth
  *instantaneous* velocity.
- **`z_r = (1−r)x_0 + r·x_1` — point on trajectory.** The network input state, the
  linear interpolation at time $r$.

### Time sampler (top)
- **`r, t ∼ U(ε, 1−ε)`**, clamped with `t_eps = 1e-5`, then **sorted so `r ≤ t`**.
- **`mf_mask ∼ Bernoulli(0.25)`** (`mf_ratio = 0.25`). Selects which samples are
  “true MeanFlow” (off-diagonal, $r<t$).
- **I-CFM rows: set `t := r`.** The remaining **75 %** are forced onto the diagonal
  $t=r$ (instantaneous flow matching).

### Single network forward (center)
- **`u_pred = u_θ(z_r, r, t, c_t)` — one forward, full batch.** The whole batch
  (both sub-populations) goes through the network **once**. $c_t$ is the 10-ch
  condition from figure 1.

### The two targets (the heart of the figure)
- **`I-CFM` (`t = r`, 75 %): `u_tgt = v`.** On the diagonal the average velocity
  *equals* the instantaneous one, so the target is simply $v$ — an **exact,
  low-variance** target. This also enforces the boundary condition that makes the
  network a valid flow field.
- **`MeanFlow` (`r < t`, 25 %): `u_tgt = v + (t−r)·du/dr`.** Off the diagonal we use
  the **MeanFlow identity**. The derivative $\mathrm{d}u/\mathrm{d}r$ is the *total*
  derivative of the network's own output along the trajectory, computed by a
  **JVP** (Jacobian–vector product, forward-mode autodiff) with **tangent
  `(v, 1, 0)`** over the inputs $(z, r, t)$ — i.e. $\dot z = v$, $\dot r = 1$,
  $\dot t = 0$. The target is **stop-grad** (`sg`): we evaluate the JVP to build the
  target but do **not** let gradients flow into it, which keeps training stable (a
  self-distillation / bootstrap target).
- **`sg` (circle).** The switch that, per `mf_mask`, selects which of the two
  targets each sample uses, and detaches it — yielding $u_{\text{tgt}}$.

> **Why mix 75/25?** Diagonal I-CFM gives exact but “short-interval” supervision;
> off-diagonal MeanFlow gives the self-consistent “long-interval” average-velocity
> signal that actually enables few-step sampling but is higher-variance. The
> 25 % ratio (`mf_ratio`) and `adaptive_p = 1.0` are the paper-optimal settings
> from Geng et al. 2025. (One known divergence from the paper: we sample $r,t$
> **uniformly**, whereas the paper's best is a logit-normal$(-0.4, 1.0)$ sampler.)

### Loss terms (right)
- **`adaptive matching` — $\mathcal L_{\text{MF}} = w\,\lVert u_{\text{pred}} - \mathrm{sg}(u_{\text{tgt}})\rVert^2$.**
  Squared velocity-matching error with a **per-sample adaptive weight**
  $w = (\text{mse} + \epsilon)^{-p}$, $p = 1$ (`adaptive_p`), $\epsilon=10^{-3}$
  (`adaptive_eps`), and a **per-channel weight** $\beta=(1,1,1,2)$ that
  up-weights the hard **qpepre** (precipitation) channel. $w$ is itself stop-grad,
  so it acts as a normalizer that prevents a few large-error samples from
  dominating.
- **`spectral` (qpepre) — $\mathcal L_{\text{spec}} = \lVert \log\mathrm{PSD}(\hat x_1) - \log\mathrm{PSD}(x_1)\rVert_1$.**
  An L1 match of the **radially-averaged log power spectrum** of qpepre, applied
  **only on the I-CFM subset** (where $u_{\text{pred}}$ implies a clean field
  $\hat x_1$). This fights precipitation **mode collapse / blurring** by forcing
  the small-scale spectral content to match.
- **`total` — $\mathcal L = \mathcal L_{\text{MF}} + 0.1\,\mathcal L_{\text{spec}}$**
  (`spectral_weight = 0.1`). This scalar is what `backward()` is called on in figure 1.

### Legend
data/tensors · operation · student forward · loss term · total · `sg` = stop-gradient.

---

## 4. How the three figures connect

```
 fig.1 (overall)  ──>  the "MeanFlow objective" box expands into:
                        ├─ fig.2 (network)    : how u_θ(z_r,r,t,c_t) is computed
                        └─ fig.3 (objective)  : how u_tgt and the loss are computed
```

- $c_t$ and $R_t$ are produced in **fig. 1** and consumed in **figs. 2 & 3**.
- $u_\theta$ from **fig. 2** is the `u_pred` in **fig. 3**.
- the scalar $\mathcal L$ from **fig. 3** is what **fig. 1** back-propagates.

## 5. Inference (not a separate figure, but worth stating)

At rollout time (and in the validation branch of fig. 1), generation is the
few-step average-velocity integrator from `nn.py:meanflow_model_forward`:

$$z_0 \sim \mathcal N(0,I),\qquad
z_{\frac{i+1}{K}} = z_{\frac{i}{K}} + \tfrac{1}{K}\,u_\theta\!\big(z_{\frac{i}{K}}, \tfrac{i}{K}, \tfrac{i+1}{K}, c_t\big),\qquad i=0,\dots,K-1$$

then de-standardize $\hat R_t = \sigma_{\text{data}}\,z_1$ and compose
$\hat X_t = M_t + \hat R_t$ (with qpepre mapped back via `expm1` → mm/h). Validation
uses $K = 2$ (`valid_num_steps = 2`), i.e. **2 network evaluations per hour**,
versus ≈35 for the EDM teacher.
