# Week 03 Results — Clean Baseline

## Status: Partial ⚠️

S02–S07, S14–S18 clean runs completed 2026-06-12. **S01, S08–S13 have broken
trim windows** (STATUS TODO #1 — durations recorded as 2–20s instead of
120–300s). Do not cite their metrics until re-trimmed and re-run.
IDF1/HOTA/MOTA/IDS not yet extracted (STATUS TODO #7).

## Run log

| Date | Scenarios | Config | Valid? | Notes |
|------|-----------|--------|--------|-------|
| 2026-06-12 | S01–S18 (clean) | `run_baselines.py --all` | S02–S07, S14–S18 only | S01/S08–S13 bad trim windows |

## What was run

BoT-SORT + fast-reid (VeRi SBS R50-ibn), no poisoning, COCO YOLOX-x detector,
`--prime-classes 2,3,5,7`, `--aspect_ratio_thresh 10`.
Exports per camera → merged `<scenario>_all-cams.csv`.

## Provenance

- Progress report: `reports/2026-06-12/REPORT.md`
- Run manifest (pod only, not committed): `runs/run_manifest.csv`

## Open items before gate closes

- [ ] Fix S01/S08–S13 trim windows, re-run (STATUS TODO #1)
- [ ] Commit run_manifest.csv to this folder (STATUS TODO #8)
- [ ] IDF1/HOTA/MOTA/IDS from tracker stdout (STATUS TODO #7)
