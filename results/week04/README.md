# Week 04 Results — Poisoning Runs

## Status: Partial ⚠️

eps 0.5 batch done 2026-06-12 for all scenarios (same validity caveat as
week03 — S01/S08–S13 are bad). eps 0.1 and 1.0 **not yet run**.

## Run log

| Date | Scenarios | Epsilon | Poison cameras | Valid? | Notes |
|------|-----------|---------|----------------|--------|-------|
| 2026-06-12 | S01–S18 | 0.5 | c01, c02 | S02–S07, S14–S18 | S01/S08–S13 bad trim windows |
| — | all | 0.1 | c01, c02 | — | Not yet run |
| — | all | 1.0 | c01, c02 | — | Not yet run |
| — | all | 0.5 | c01 only | — | Single-cam sweep not yet run (STATUS TODO #5) |

## Open items before gate closes

- [ ] Fix S01/S08–S13 trim windows, re-run (STATUS TODO #1)
- [ ] Full sweep: eps 0.1 and 1.0 (`run_baselines.py --all --epsilons 0.1,0.5,1.0 --apply`)
- [ ] Single-camera poison sweep (`--poison-cameras c01`)
- [ ] Commit run_manifest.csv to this folder
