# Reproducibility guide

## Snapshot purpose

This post-deadline archive preserves TartanIMU source, protocol, release
documentation, and lightweight receipts. It excludes competition data, model
weights/regressors, generated submissions, caches, and large output bundles.

## Primary entry point

`release/REPRODUCE.md` is the authoritative offline inference protocol. From
the `release/` directory, after independently supplying the exact authorized
input layout, official source, configuration, and model files named there, its
entry point is:

```bash
python src/predict_frozen.py --help
```

Use the full frozen arguments and acceptance checks in
`release/REPRODUCE.md`; `--help` alone is shown here only to identify the
public source entry without pretending the excluded payloads are present.
`src/validate_submission.py` is the retained research-workspace validator.

## Required boundary checks

1. Obtain competition data only under its recorded competition and
   CC BY-NC-SA 4.0 boundary; do not republish it.
2. Obtain official code and model files from their documented sources and
   preserve their own licenses and hashes.
3. Keep data, models, checkpoints, submissions, and caches outside public Git.
4. Match the expected schema, IDs, order, finite-value checks, and frozen hashes
   recorded by the release protocol.

The public Git snapshot cannot by itself perform the cold-start reproduction
or recreate the historical submission. A source check is not a claim of a new
score, current competition status, or renewed submission authority.
