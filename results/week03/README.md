# Week 03 Results — Clean Baseline

## Status: Partial ⚠️

Clean runs completed for all 18 scenarios. The earlier "S01/S08–S13 broken trim
windows" concern was **resolved 2026-06-19**: all 18 windows/trims verified valid
(`scripts/check_scenario_windows.py`); the real cause of sparse exports was a
detector input-size bug (ran at YOLOX default 640). Fixed at `--tsize 1536` and
**re-exported 2026-06-20** (published as Release `exports-2026-06-20`). Usable set
is now the 14 daytime scenarios (S01–S08, S11, S13–S17); S10 night is smoke-only,
S12·c03/S18 dusk are low-light caveats. IDF1/HOTA/MOTA/IDS still not extracted
(STATUS TODO #6).

## Run log

| Date | Scenarios | Config | Valid? | Notes |
|------|-----------|--------|--------|-------|
| 2026-06-12 | S01–S18 (clean) | `run_baselines.py --all` (tsize 640) | superseded | under-detected small vehicles @640 |
| 2026-06-20 | S01–S18 (clean) | `run_baselines.py` @ `--tsize 1536`, 6-worker parallel | 14 daytime usable | re-export; S03/c01 24→1328 dets |

## What was run

BoT-SORT + fast-reid (VeRi SBS R50-ibn), no poisoning, COCO YOLOX-x detector,
`--prime-classes 2,3,5,7`, `--aspect_ratio_thresh 10`.
Exports per camera → merged `<scenario>_all-cams.csv`.

## Provenance

- Progress report: `reports/2026-06-12/REPORT.md`
- Run manifest (pod only, not committed): `runs/run_manifest.csv`

## Open items before gate closes

- [x] Trim windows verified valid + 1536 re-export done (2026-06-20)
- [ ] Commit run_manifest.csv (pod-side) to this folder (STATUS TODO #7)
- [ ] IDF1/HOTA/MOTA/IDS from tracker stdout (STATUS TODO #6)
