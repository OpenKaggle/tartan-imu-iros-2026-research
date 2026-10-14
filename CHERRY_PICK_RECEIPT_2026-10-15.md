# Cherry-pick publication receipt — 2026-10-15

Project: `tartan_imu` → repository `OpenKaggle/tartan-imu-iros-2026-research`.
This commit publishes files that were present in the local workspace,
listed in the 853-row first-party source manifest, and missing from the
remote repository at the time of the dry-run comparison. Every file was
re-verified before commit: SHA-256 and byte count match the manifest entry
exactly (see `state` column).

## Files added

- `release/predictions/E003_stacked_1000.csv` (1252494 bytes)
  - sha256 `4644bb8e11df4a02417902c83b65bff5777a0e98db5bb67923f62c73bcec267a`  - class `source-or-derived-text-candidate`
- `reports/official_scoring/E003/official_per_sequence.csv` (2403 bytes)
  - sha256 `a19ce372160879e6af66b7377ab44d8be11e017ab469e16e114b4eef5e9debff`  - class `source-or-derived-text-candidate`

## Review notes

- E003 stacked predictions (30,644 rows) and official per-sequence scoring.
  Numeric-only; hash matches the pre-existing
  `release/predictions/E003_stacked_1000.receipt.json`.

## Source of truth

- Local workspace: `~/Desktop/kagglepred/tartan_imu/`
- Source manifest: `outputs/kagglepred-release-audit-2026-09-28/first-party-source-manifest.csv` (project rows for `tartan_imu`).
