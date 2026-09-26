# Dataset receipt — 2026-09-09

- Official Kaggle archive: `tartan-imu-challenge-iros2026.zip`
- Downloaded size shown by CLI: 1.26 GiB (1.3G on disk).
- SHA-256: `ca8d6c15894064e2a4db25d1f01f6c3db7f51454eea0b52afa81d835aa394d8d`
- ZIP integrity test: passed with no errors.
- Extracted files: 570.
- License: CC BY-NC-SA 4.0 plus competition restriction to competition
  purposes and non-commercial academic research.

## Indexed split receipt

| split | trajectories | windows | index columns |
|---|---:|---:|---|
| train | 395 | 81,931 | window_id, platform, traj_id, win_idx, lb |
| val | 80 | 23,714 | window_id, platform, traj_id, win_idx, lb |
| test | 89 | 30,644 | window_id, traj_id, win_idx |

`lb` is present but entirely null in train/validation. It is ignored. Test has
no platform or `platform_id`. All `window_id` values and `(traj_id, win_idx)`
pairs are unique within each split. `sample_submission.csv` has exactly the
same 30,644 IDs in the same order as `index/test_windows.csv`.

Every sampled/fully audited IMU array is finite with shape `(N, 6)`. Train and
validation NPZs also contain `ts`, `pos`, `quat`, `vel_body`, `platform_id`, and
`fs`; test NPZs contain only `imu`, `ts`, and `fs`.

