# Official status receipt — 2026-09-09

Observed at `2026-09-08T21:54:37Z` / `2026-09-09T05:54:37+08:00`.

Competition: `tartan-imu-challenge-iros2026`

## Entry and platform status

- Official URL: https://www.kaggle.com/competitions/tartan-imu-challenge-iros2026
- Authenticated Kaggle API deadline: `2026-09-20 23:55:00 UTC`.
- Authenticated API before acceptance: `userHasEntered=False`.
- The live Kaggle UI was used to review and accept the competition-specific and
  Foundational Rules. The UI then displayed `You have accepted the rules for
  this competition` and unlocked `Submit Prediction`, `Team`, and `Submissions`.
- Authenticated API after acceptance: `userHasEntered=True`,
  `submissionsDisabled=False`, `reward=Kudos`, `teamCount=78`.
- There were no prior submissions for this account at observation time.

## Entry, team merger, and final deadline

The authenticated competition object exposes `newEntrantDeadline=None` and
`mergerDeadline=None`; the Rules page contains no separate earlier deadline.
The effective entry and team-merger cutoff is therefore no later than the final
competition deadline, `2026-09-20 23:55 UTC`. Entry is already complete.

The competition-specific Rules page caps teams at 5. A public API metadata
field reported 10; this campaign follows the stricter participant-facing rule
of 5.

## Prizes and required artifacts

- No money, Kaggle points, or medals. Recognition is leaderboard placement and
  possible invitation to the IROS 2026 workshop.
- Maximum 5 Kaggle submissions per team per day.
- Each submission claimed for official ranking needs the host Submission Form
  and the exact prediction CSV.
- Final package needs a public Hugging Face repository with the single unified
  model's frozen weights, runnable offline inference, pinned requirements, and
  the exact `submission.csv`.
- Re-execution: one GPU, at most 16 GB VRAM, at most 2 hours, no internet.
- Reports must answer five compliance questions covering one-model status,
  routing/specialization, ensembling/TTA, leakage prevention, and differences
  between development and submitted systems.

## Deadline conflict and conservative resolution

The live Kaggle Rules page says the report and model weights are due
`2026-09-27 23:55 UTC`. Newer organizer materials supersede this operationally:

- Organizer announcement #739576 (2026-09-04): final Kaggle submissions and
  model weights `2026-09-20 23:55 UTC`; technical report
  `2026-09-23 23:59 EDT`.
- Live challenge website announcement/setup page: same strict deadlines.
- The host says the final Submission Form may be filed/re-filed until the report
  deadline, with the last response controlling.

Campaign deadlines therefore use the strictest published values:

- Predictions + public weights/offline inference: `2026-09-20 23:55 UTC` =
  `2026-09-21 07:55 China Standard Time`.
- Report + final Form: `2026-09-24 03:59 UTC` =
  `2026-09-24 11:59 China Standard Time`.

Sources:

- https://www.kaggle.com/competitions/tartan-imu-challenge-iros2026/rules
- https://www.kaggle.com/competitions/tartan-imu-challenge-iros2026/discussion/739576
- https://superodometry.com/imuchallenge/
- https://superodometry.com/imuchallenge/setup/#schedule-rules-and-leaderboard
- https://docs.google.com/forms/d/e/1FAIpQLSc_3Pq2Bs4ytd0lfHHLsU_qoO5z0BP6Psnsqo7e5nOyBTlCjQ/viewform

## Official code receipt

- Repository: https://github.com/superxslam/TartanIMU
- Checked-out commit: `fba699eb96fd3d3b0cd303695143725fd3aeb082`
- Commit time/message: `2026-07-29T22:37:56-04:00 update installation`

