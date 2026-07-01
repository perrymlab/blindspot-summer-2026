# Week 04 Results — Poisoning Runs

## Status: Partial ⚠️

eps 0.5 poisoned batch **re-exported at `--tsize 1536`** 2026-06-20 (published as
Release `exports-2026-06-20`), superseding the 2026-06-12 tsize-640 run. The old
"S01/S08–S13 broken trim windows" caveat is resolved (windows verified valid
2026-06-19; the issue was detector input size — see week03). 17 scenarios
poisoned (S10 skipped, smoke-only). eps 0.1 and 1.0 **not yet run**.

## Run log

| Date | Scenarios | Epsilon | Poison cameras | Valid? | Notes |
|------|-----------|---------|----------------|--------|-------|
| 2026-06-12 | S01–S18 | 0.5 | c01, c02 | superseded | tsize 640, under-detected |
| 2026-06-20 | 17 (S10 skipped) | 0.5 | c01, c02 | 14 daytime usable | re-export @ tsize 1536, 6-worker parallel |
| — | all | 0.1 | c01, c02 | — | Not yet run |
| — | all | 1.0 | c01, c02 | — | Not yet run |
| — | all | 0.5 | c01 only | — | Single-cam sweep not yet run (STATUS TODO #4) |

## Open items before gate closes

- [x] Trim windows resolved + eps 0.5 re-exported @1536 (2026-06-20)
- [ ] Full sweep: eps 0.1 and 1.0 (`run_baselines.py --all --epsilons 0.1,0.5,1.0 --apply`) (STATUS TODO #3)
- [ ] Single-camera poison sweep (`--poison-cameras c01`) (STATUS TODO #4)
- [ ] Commit run_manifest.csv (pod-side) to this folder (STATUS TODO #7)
