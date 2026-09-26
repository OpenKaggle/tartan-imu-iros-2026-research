# Submission Form Checklist

Official form:
https://docs.google.com/forms/d/e/1FAIpQLSc_3Pq2Bs4ytd0lfHHLsU_qoO5z0BP6Psnsqo7e5nOyBTlCjQ/viewform

The live form was read successfully on 2026-09-09. It requires Google sign-in;
Google records the submitting account's name, email, and profile photo.

## Exact live fields

1. **Email** — required.
2. **Kaggle Team Name** — required.
3. **Public LB Score** — required.
4. **Method Summary** — required.
5. **What is novel in your approach** — required.
6. **Is this a single unified model?** — required Yes/No.
7. **Prediction CSV** — required, one file, maximum 10 MB.
8. **Model Checkpoint Hugging Face URL** — only needed for the last submission.
9. **Technical Report PDF** — only needed for the last submission, PDF, maximum
   10 MB.

## Known official requirements

- Complete the form for every Kaggle submission to be considered.
- Attach the exact prediction CSV uploaded to Kaggle.
- Team name must exactly match Kaggle: **Jiayi Du**.
- Submit the form again to attach the final technical report; the organizer's
  latest announcement says the latest form controls.
- Final prediction and public model weights: 2026-09-20 23:55 UTC
  (2026-09-21 07:55 China Standard Time).
- Technical report and final form: 2026-09-23 23:59 EDT
  (2026-09-24 11:59 China Standard Time).

## E001 record

- Kaggle ref: `56108171`
- Public score: `0.77197`
- CSV: `tartan_imu/submissions/E001_catboost_v1.csv`
- SHA-256:
  `bb0e651a656e89cabf33c97d38d374e56b751e3d11d506e02b0ea4d0b9630e1d`
- Form status: **pending; not intended as final candidate**.

## E002 record

- Kaggle ref: `56115700`
- Public score: `0.63718`
- CSV: `tartan_imu/submissions/E002_stacked_unified.csv`
- SHA-256:
  `51a0ae83e638655887a609a5a06dec583cdb5a840c2b1ed7c3be8d66e04134dd`
- Form status: **pending user-authenticated Google Form**.

### Prepared E002 form text

- Kaggle Team Name: `Jiayi Du`
- Public LB Score: `0.63718`
- Single unified model: `Yes`
- Method Summary: `One unified platform-agnostic velocity regressor combines
  deterministic same-trajectory IMU features with the shared temporal
  representation and all four continuous outputs of the official unified
  TartanIMU backbone. A single CatBoost MultiRMSE head predicts vx, vy, vz.`
- Novelty: `Instead of recovering platform identity or selecting an expert,
  the method exposes every continuous head output simultaneously to one shared
  regressor, which learns a smooth cross-platform calibration under equal
  platform and trajectory weighting.`
- Required upload:
  `tartan_imu/submissions/E002_stacked_unified.csv` (1.2 MB).

## E003 record — current selected candidate

- Kaggle ref: `56117057`
- Public score: `0.63142`
- CSV: `tartan_imu/submissions/E003_stacked_1000.csv`
- MD5: `f571673079b05623e658a14410ef0063`
- SHA-256:
  `4644bb8e11df4a02417902c83b65bff5777a0e98db5bb67923f62c73bcec267a`
- Single unified model: `Yes`
- Method Summary: use the prepared E002 text; only the selected CatBoost tree
  count changes from 600 to 998.
- Novelty: use the prepared E002 text unchanged.
- Email: `jiayi.du@mail.louisenlund.de`
- Public Hugging Face repository:
  `https://huggingface.co/duj626/tartanimu-e003`
- Public release status: **uploaded and independently re-downloaded; 64/64
  files match the frozen local SHA-256 values**. Verified remote revision:
  `3c5677e82c7a2d5f05d96f1c5c163e0936d2f0e8`.
- Form status: **submitted successfully on 2026-09-17 09:10 CST**. Google Forms
  displayed `我们已收到您的回答` after transmitting the exact E003 CSV, public
  Hugging Face repository URL, and final technical report PDF.

## Final report package status

- Final IEEE report:
  `tartan_imu/output/pdf/TartanIMU_E003_Technical_Report_FINAL.pdf`
- Report SHA-256:
  `ae0607c7995e48f1f77ae93ec64336dab195eff0e3dae49ad72ff048c3ed020c`
- Editable source archive:
  `tartan_imu/output/pdf/TartanIMU_E003_IEEE_Source_FINAL.zip`
- Source archive SHA-256:
  `926f34d38e62c98587cfff2328d6e521acda0795c37817772cc1ba3ff354c8ac`
- PDF status: **rendered and visually checked; 5 US-letter pages; embedded
  Type 1 fonts; below the 10 MB upload limit**.
- The report contains the official overall, per-platform, and all 89
  per-sequence results, plus all five required compliance answers.
- Final identity: **Jiayi Du / Stiftung Louisenlund / Germany /
  jiayi.du@mail.louisenlund.de**.
- There are no remaining report placeholders. The public Hugging Face repository
  contains the complete 64-file frozen release and passed full remote re-download
  SHA-256 verification.
- Public release commit: `3c5677e82c7a2d5f05d96f1c5c163e0936d2f0e8`.
- The authoritative offline runtime is **117.42 seconds** with **723,648,512
  bytes** maximum resident memory. It supersedes the earlier development timing
  and is now used consistently in current release documentation.

## Submission receipt

- Submitted: **2026-09-17 09:10 CST**.
- Google account recorded by the form: `jydu_seven@outlook.com`.
- Contact email entered in the form: `jiayi.du@mail.louisenlund.de`.
- Confirmation shown: `我们已收到您的回答`.
- Final candidate transmitted: E003, Kaggle ref `56117057`, public score
  `0.63142`.
