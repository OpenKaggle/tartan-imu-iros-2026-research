# TartanIMU Challenge Technical Report — Working Outline

Status: working skeleton, not yet submitted. The final paper must use the
official `ieeeconf` template, contain at most 6 pages excluding references and
7 pages total including references, and attach through the Submission Form.

## Title and authors

- Working title: **A Platform-Agnostic Stacked Regressor for Unified Inertial Odometry**
- Team name: **Jiayi Du**
- Author name, affiliation, email: **USER INPUT REQUIRED — do not infer**

## Abstract

We study unified body-frame velocity regression from raw 6-axis IMU streams
across car, quadruped, drone, and human motion. The submitted system uses one
shared released ResNet–LSTM feature extractor followed by one platform-agnostic
multi-output CatBoost regressor. It consumes no platform label and performs no
classification, routing, specialist dispatch, ensembling, checkpoint averaging,
or test-time augmentation. Development uses the released trajectory-disjoint
validation split and exact organizer metric implementation.

## I. Introduction

- Motivation: single-model inertial odometry across heterogeneous embodiments.
- Challenge: high-frequency temporal structure, platform imbalance, and large
  high-speed drone error.
- Contributions:
  1. auditable trajectory/platform-balanced validation;
  2. one continuous, platform-agnostic stacked regressor;
  3. fail-closed submission validation and deterministic offline inference.

## II. Data and protocol

- Dataset archive SHA-256:
  `ca8d6c15894064e2a4db25d1f01f6c3db7f51454eea0b52afa81d835aa394d8d`.
- Released splits: train 81,931 windows / 395 trajectories; validation 23,714
  / 80; test 30,644 / 89.
- Input: one-second, 200 Hz, 6-axis IMU windows.
- Target: mean body-frame velocity `(vx, vy, vz)`.
- Grouping: all selection is on the official released validation trajectories;
  reporting is macro-averaged over trajectories and then the four platforms.
- No external datasets are used. The only external artifact is the official
  released unified TartanIMU checkpoint.

## III. Method

### A. Released shared temporal backbone

- Official unified checkpoint SHA-256:
  `ca8cc3e15a42ec91c0cda4c63ade1b068ea92039469104b40ea63f18130e97f4`.
- ResNet-1D + two-layer LSTM, 128-dimensional shared representation.
- All four continuous head outputs are exposed simultaneously; no head is
  selected or routed at inference.

### B. Deterministic IMU features

- Window statistics, quantiles, slopes, differences, FFT bands, correlations,
  chunk summaries, and same-trajectory IMU context.
- Past and future context is restricted to the same released test trajectory,
  which the organizer explicitly allows.

### C. One unified regression head

- Concatenate 493 deterministic IMU/context features, 128 shared backbone
  features, and 12 continuous outputs from all four unified heads: 633 total.
- Train one CatBoost `MultiRMSE` regressor for `(vx, vy, vz)`.
- Equal platform weight, then equal trajectory weight within platform.
- Current frozen hyperparameters: depth 8, learning rate 0.04, L2 8.0,
  Bayesian bootstrap temperature 0.4, seed 20260909.

## IV. Experiments

### A. Baselines and ablations

| ID | One changed hypothesis | Val AVE | Val ATE20 | Val score | Public score |
|---|---|---:|---:|---:|---:|
| E000 | all-zero anchor; not uploaded | — | — | 1.0146 | official zero 1.054 |
| E001 | deterministic IMU/context features only | 0.39172 | 1.68739 | 0.53610 | 0.77197 |
| E002 | add official temporal representation and all continuous heads | 0.34187 | 1.14334 | 0.42560 | 0.63718 |
| E003 | only increase maximum tree count 600 → 1000 | 0.33202 | 1.10818 | 0.41305 | 0.63142 |

### B. Per-platform validation

| System | Car AVE / ATE20 | Dog AVE / ATE20 | Drone AVE / ATE20 | Human AVE / ATE20 |
|---|---:|---:|---:|---:|
| E001 | 0.336 / 1.960 | 0.210 / 1.230 | 0.836 / 1.737 | 0.185 / 1.823 |
| E002 | 0.204 / 0.969 | 0.139 / 0.693 | 0.905 / 1.847 | 0.120 / 1.064 |

E002 improves the macro score and three platforms strongly, while drone is
slightly worse than E001. The next method-family change, if tree-count scaling
fails twice, should therefore target high-dynamic drone regression without
platform routing.

### C. Official test tables

Tables III–V must be populated only from the organizer's official scoring
service. Do not copy local validation calculations into these tables.

- Official scoring receipt: TartanIMU score **0.53485**, macro AVE
  **0.43938 m/s**, macro ATE20 **1.37483 m**, and macro RTE@5s
  **1.79401 m**.
- The receipt is bound to team `Jiayi Du` and submission MD5
  `f571673079b05623e658a14410ef0063`.

| Platform | ATE20 (m) | AVE (m/s) | RTE@5s (m) | Trajectories | Windows |
|---|---:|---:|---:|---:|---:|
| Wheeled / Car | 1.15466 | 0.17411 | 0.94733 | 18 | 10,584 |
| Handheld / Human | 1.32241 | 0.11215 | 0.49305 | 10 | 11,264 |
| Legged / Quadruped | 0.79201 | 0.12454 | 0.52236 | 16 | 6,697 |
| Aerial / Drone | 2.23022 | 1.34673 | 5.21329 | 45 | 2,099 |
| Macro average | 1.37483 | 0.43938 | 1.79401 | 89 | 30,644 |

- Tables III and IV can be transcribed from the overall and platform values
  above.
- Table V must be transcribed from `official_per_sequence.csv` (89 rows). The
  file is retained locally with the official response and must not be used for
  model selection or tuning.

## V. Reproducibility and runtime

- Single model package: official unified backbone checkpoint plus one CatBoost
  regression head and one inference entry point.
- No network access during inference.
- A cold, offline run of the frozen release package reproduced the exact CSV in
  **117.42 s** wall time with **723,648,512 bytes** maximum resident memory,
  well below the 16 GB and two-hour limits.
- Exact prediction hashes, model hashes, package manifest, and runtime log will
  be supplied.

## VI. Limitations

- Validation-to-public distribution shift is material (E001).
- High-speed drone motion remains the dominant error regime.
- The official released backbone is reused rather than trained from scratch.

## Required compliance declaration

1. **Single model/shared weights?** Yes. Predictions come from one released
   shared backbone plus one unified regression head distributed as one package.
2. **Platform classification, routing, or specialization at inference?** No.
   The system consumes no platform label and performs no classification or
   head selection. All continuous head outputs are simultaneous input features.
3. **Ensembling, checkpoint averaging, or TTA?** No.
4. **Leakage prevention?** Test pose, orientation, velocity, platform identity,
   manual categorization, and leaderboard-derived labels are never used. Model
   selection uses only the released train/validation split and organizer metric.
5. **Development vs submitted system?** Development caches intermediate
   features for speed; the submitted entry point recomputes the same frozen
   transforms offline and emits the identical CSV. Any remaining differences
   must be listed after byte-for-byte reproduction testing.

## References

- TartanIMU repository and released unified model.
- Official challenge rules, setup guide, and scoring implementation.
- CatBoost multi-output regression.
