# 論文精簡摘要 — 致口試委員 / Extended Summary for the Committee

**題目 / Title:** Distilling a Regional Taiwan-Domain StormCast Diffusion Forecaster into a Few-Step Average-Velocity Student (MeanFlow)

---

## 繁體中文（精簡、以結果為導向）

本論文將台灣區域 RWRF 兩階段對流尺度 StormCast 預報模式（凍結的回歸均值加上生成式殘差頭）蒸餾為僅需一至兩次網路評估（NFE）的少步學生模型，最大成果是以約十分之一的取樣成本，達到擴散模式等級的預報技巧。所提方法 MeanFlow 學習整段噪聲到資料軌跡的「平均速度」，單次前向即橫跨全程，完全不需數值 ODE 積分；它無需教師、單階段訓練即可完成，據我們所知為 MeanFlow 首次應用於台灣區域、對流尺度的逐時天氣預報。在 2022 全年逐時驗證、約兩百萬樣本相同訓練預算下，MeanFlow（K=2，即 2 NFE 對比擴散的 35）達到 EDM 擴散基線的確定性與分類降水技巧水準。以單張 RTX A6000 跑 50 成員、24 小時集合預報為例，擴散約需 32 分鐘，K=2 約 4 分鐘（快 7.9 倍），K=1 約 3.2 分鐘（快 9.9 倍），快到足以在雷達掃描體積更新之間刷新。在 15 公里主視窗，MeanFlow K=2 的降水命中技巧（CSI-M 0.269、HSS-M 0.315）甚至高於擴散（0.262／0.293），溫度精度更居全體各頭之冠（t2m RMSE 0.732 K，較擴散 0.802 K 低約 9%），並在 +1、+2 小時滾動預報領先。唯一代價是系集離散度略窄、滾動 CRPS 約差一成，多算一次推論即可大致補回，故建議以 K=2 運作。

**三大亮點**

- 僅 1–2 次網路評估、約十分之一推論成本，達擴散級技巧
- 50 成員 24 小時集合：擴散約 32 分鐘 → K=2 約 4 分鐘（快 7.9 倍）
- 15 公里降水命中率 CSI-M 0.269、HSS-M 0.315，超越擴散 0.262／0.293
- 唯一代價：系集離散度略窄、滾動 CRPS 約差一成，K=2 大致補回

---

## English (concise, result-oriented)

This thesis distils a regional Taiwan-domain (RWRF) two-stage convection-permitting StormCast forecaster — a frozen deterministic regression mean plus a generative residual head — into a few-step student needing only 1–2 network evaluations (NFE), reaching diffusion-grade forecast skill at roughly a tenth of the sampling cost. The proposed method, MeanFlow, learns the average velocity across the entire noise-to-data interval, so a single forward pass crosses the whole trajectory with no numerical ODE integration; it is teacher-free, trained in a single stage, and is to our knowledge the first application of MeanFlow to regional, convection-permitting, hourly weather prediction (the Taiwan RWRF domain). On the full 2022 hourly validation year under a matched ~2M-sample budget, MeanFlow at K=2 (2 NFE versus diffusion's 35) reaches the EDM diffusion baseline's deterministic and categorical precipitation skill class. For a 50-member, 24-hour ensemble on a single RTX A6000, diffusion takes ~32 min versus ~4 min for MeanFlow K=2 (7.9× faster) and ~3.2 min for K=1 (9.9× faster) — fast enough to refresh between radar volumes. At the 15 km headline window MeanFlow K=2 posts the best precipitation hit rates of any head (CSI-M 0.269, HSS-M 0.315, above diffusion's 0.262/0.293) and the best temperature accuracy of any head (t2m RMSE 0.732 K, ≈9% below diffusion's 0.802 K), and it wins the +1 h and +2 h rollout. The one cost is a narrowed ensemble spread, a modest ~10% rollout-CRPS gap at K=2 that one extra evaluation mostly closes, making K=2 the recommended operating point.

**Key results**

- Diffusion-grade skill at 1–2 NFE (vs 35), ~1/10 the cost
- 50-member 24 h ensemble: ~32 min diffusion → ~4 min at K=2 (7.9×)
- Best precip hit rates at 15 km: CSI-M 0.269 / HSS-M 0.315, above diffusion 0.262/0.293
- One tradeoff: narrowed spread, ~10% rollout-CRPS gap, mostly closed at K=2
