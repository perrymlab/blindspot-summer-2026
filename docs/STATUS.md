# Project Status & TODO

Living document. Update when batches finish, gates close, or priorities shift.
Last updated: **2026-06-12** 

## Where we are

The full researcher pipeline works end to end on real footage: organize →
trim → batch clean/poisoned runs → merged per-scenario exports → detector
analysis → shareable report. S01 is the proof: clean + poisoned (eps 0.5,
cameras c01,c02, seed 7) completed 2026-06-12 on trimmed footage, report
generated, GitHub Release `report-2026-06-12` published.

| Gate (REAL_DATA_IMPLEMENTATION_PLAN.md) | Status |
| --- | --- |
| 1. Environment and data | **Done** (RunPod /workspace persistent volume; local footage replaced CityFlowV2) |
| 2. Clean baseline | Partial — S01 done; other scenarios pending; **IDF1/HOTA/MOTA/IDS not implemented** |
| 3. Poisoning runs | Partial — S01 @ eps 0.5 done; eps 0.1 / 1.0 pending |
| 4. Detector on real outputs | Partial — runs end to end, but on `detection_index` (no track-id merge yet) |
| 5. Scalability / boundaries | Not started (note the majority-poisoned caveat, week06 README) |
| 6. Writing / publication | Not started |

## TODO — researcher (Brian / Sabrina)

1. **Fix `data/scenario_windows.csv`** — S01 (20s), S08 (5s), S09–S13 (2–3s)
   look like start/end pairs entered as durations; target is 120–300s.
   Reconcile with Christine's sheet, re-trim, re-run affected scenarios.
   *Blocks the full sweep being meaningful.*
2. **Full sweep:** `python scripts/run_baselines.py --all --epsilons 0.1,0.5,1.0 --apply`
   (inside tmux; completed runs auto-skip).
3. **Single-camera poison sweep** (`--poison-cameras c01`) for the detector's
   minority assumption — see `experiments/week06-detector/README.md`.
4. **Tracker/global-ID merge** so analysis uses `track_id`, not
   `detection_index`. Until then identity-level numbers are placeholders.
5. **IDF1 / HOTA / MOTA / IDS extraction** from tracker output (Week 3 gate
   requirement, still unimplemented).
6. Publish exports (`bash scripts/publish_run_outputs.sh --commit`) and run
   logs + summaries into `results/week03/` and `results/week04/`.
7. Decide LFS budget vs. Releases once full-sweep sizes are known.

## TODO — students (Christine / Floyd)

1. Run `scripts/analyze_embedding_export.py` on the published
   `*_all-cams.csv` files (clean vs. poisoned), sweep `--z-threshold`, write
   run logs, PR small summaries to `results/weekXX/`.
2. Week 6: detector review — include the majority-poisoned caveat.

## Infrastructure notes

- GPU pod: RunPod, persistent `/workspace` (repo, conda at
  `/workspace/miniforge3`, footage, runs, reports). Everything else dies on
  restart — recover with `bash scripts/pod_bootstrap.sh --serve`
  (see `docs/setup/RECOVERY.md`).
- Report server: port **8890** (8888 is JupyterLab), serves `reports/` only.
- Pushes from the pod use a fine-grained/classic PAT baked into the remote
  URL; releases need the classic token (org blocked the fine-grained one).

## Decisions log

- 2026-06-12: trimmed videos + merged exports are committable via LFS
  (`data/trimmed/`, `data/exports/`); raw footage and weights stay out of git.
- 2026-06-12: progress reports = `reports/<date>/REPORT.md` + stills in git,
  videos + self-contained HTML on a GitHub Release.
- 2026-06-10 (Sabrina): scenario window edits in `data/scenario_windows.csv`
  (#73) — under review, see TODO 1.
