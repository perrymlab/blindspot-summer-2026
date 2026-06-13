# Project Status & TODO

Living document. Update when batches finish, gates close, or priorities shift.
Last updated: **2026-06-13**

> **Repo is messy.** See `docs/CONSOLIDATION_PLAN.md` for the cleanup task list.

## Where we are

The full researcher pipeline works end to end on real footage: organize →
trim → batch clean/poisoned runs → merged per-scenario exports → detector
analysis → shareable report. As of 2026-06-12: clean + poisoned (eps 0.5,
cameras c01,c02, seed 7) batch run completed for **S01–S18** (where trim
windows are valid); report generated, GitHub Release `report-2026-06-12`
published. **However:** S01, S08, S09–S13 have broken trim windows (see
TODO #1), so their metrics from this run are meaningless — do not cite them.
Valid results: **S02–S07, S14–S18** at eps 0.5 on `detection_index` (placeholder
identities; real ground-truth requires annotation, see TODO #4).

| Gate (REAL_DATA_IMPLEMENTATION_PLAN.md) | Status | Last verified |
| --- | --- | --- |
| 1. Environment and data | **Done** (RunPod /workspace persistent; footage replaced CityFlowV2) | 2026-06-12 |
| 2. Clean baseline | **Partial** — S02–S07, S14–S18 done @ eps 0.5; S01/S08–S13 broken windows; IDF1/HOTA/MOTA/IDS not implemented | 2026-06-12 |
| 3. Poisoning runs | **Partial** — eps 0.5 batch done (valid scenarios); eps 0.1 / 1.0 pending | 2026-06-12 |
| 4. Detector on real outputs | **Partial** — runs end to end but on `detection_index`; join pipeline code done (build_track_ids.py); annotation in progress (S07, S14, S15) | 2026-06-13 |
| 5. Scalability / boundaries | **Not started** — majority-poisoned caveat documented in week06 README | — |
| 6. Writing / publication | **Not started** | — |

## TODO — researcher (Brian / Sabrina)

> See `docs/CONSOLIDATION_PLAN.md` for the full cleanup plan (stale docs,
> dead code, week tracking).

### Blocking — do these first

1. **Fix `data/scenario_windows.csv`** ⚠️ CRITICAL  
   S01 (20s), S08 (5s), S09–S13 (2–3s) have wrong durations (start/end
   pairs mistakenly entered as durations). Reconcile with Christine's sheet
   and `data/edited scenario windows.csv`, get Sabrina's approval, delete
   the alternate files, re-trim + re-run affected scenarios.  
   *Blocks: full sweep, annotation coverage, all publishable metrics.*

2. **Resolve merge conflict in `docs/data/SCENARIO_TRIMMING.md`** lines 199–203  
   "Sabrina" vs. "Dr. Perry" — five-minute fix.

### Active

3. **Annotate S07, S14, S15** for real cross-camera identity  
   *In progress (2026-06-13):* Brian annotating S07 using multicam-reid
   (https://github.com/figaone/multicam-reid).  
   After each: `bash scripts/save_annotations.sh <scenario>` → commit → run join.  
   Full walkthrough: `docs/data/ANNOTATION_GUIDE.md`.  
   *Unblocks: TODO #4 results, publishable precision/recall.*

4. **Full sweep** (eps 0.1 and 1.0; valid scenarios only)  
   `python scripts/run_baselines.py --all --epsilons 0.1,0.5,1.0 --apply`  
   inside tmux; completed runs auto-skip. Run after TODO #1 fixes S08–S13.

5. **Single-camera poison sweep** (`--poison-cameras c01`)  
   For the detector's minority assumption test.  
   See `experiments/week06-detector/README.md`.

### Pending

6. **Fill in week results README.md files**  
   `results/week03/` through `results/week07/` are empty placeholders.  
   Add a run table (date, scenarios, epsilon, status) to each.  
   See `docs/CONSOLIDATION_PLAN.md §3b` for the template.

7. **IDF1 / HOTA / MOTA / IDS extraction**  
   From tracker output. Week 3 gate requirement, still unimplemented.

8. **Publish run manifest after each batch**  
   After runs: `cp runs/run_manifest.csv results/weekXX/`  
   (currently gitignored and never committed — orphans the REPORT.md).

9. **LFS / Release budget** — decide once full-sweep sizes are known.

## TODO — students (Christine / Floyd)

1. **Wait for annotation (TODO #3 above)** before running the full analysis —
   until then use `--track-column detection_index` and label results as
   placeholder only.
2. Run `scripts/analyze_embedding_export.py` on published `*_all-cams.csv`
   files (clean vs. poisoned), sweep `--z-threshold`, write run logs, PR
   summaries to `results/weekXX/`.
3. Week 6 detector review — include the majority-poisoned caveat
   (`experiments/week06-detector/README.md`).

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
