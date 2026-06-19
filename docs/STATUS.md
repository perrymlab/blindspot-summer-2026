# Project Status & TODO

Living document. Update when batches finish, gates close, or priorities shift.
Last updated: **2026-06-19**

> **Repo is messy.** See `docs/CONSOLIDATION_PLAN.md` for the cleanup task list.

## Where we are

The full researcher pipeline works end to end on real footage: organize →
trim → batch clean/poisoned runs → merged per-scenario exports → detector
analysis → shareable report. As of 2026-06-12: clean + poisoned (eps 0.5,
cameras c01,c02, seed 7) batch run completed for **S01–S18** (where trim
windows are valid); report generated, GitHub Release `report-2026-06-12`
published. **Update 2026-06-19:** all 18 trim windows are now verified valid
via `scripts/check_scenario_windows.py` — every window fits its ~600s footage
and every `vdo_trim.mp4` is a full 120s. The earlier "broken windows" issue is
resolved; what remains is that the export CSVs for **S03, S08–S13, S18** are
stale near-empty artifacts from the bad-window era and must be regenerated with
`run_baselines --overwrite` (see TODO #1).
Valid results: **S02–S07, S14–S18** at eps 0.5 on `detection_index` (placeholder
identities; real ground-truth requires annotation, see TODO #4).

| Gate (REAL_DATA_IMPLEMENTATION_PLAN.md) | Status | Last verified |
| --- | --- | --- |
| 1. Environment and data | **Done** (RunPod /workspace persistent; footage replaced CityFlowV2) | 2026-06-12 |
| 2. Clean baseline | **Partial** — all 18 windows/trims verified valid (2026-06-19); stale exports S03/S08–S13/S18 pending `--overwrite` re-export; IDF1/HOTA/MOTA/IDS not implemented | 2026-06-19 |
| 3. Poisoning runs | **Partial** — eps 0.5 batch done (valid scenarios); eps 0.1 / 1.0 pending | 2026-06-12 |
| 4. Detector on real outputs | **Partial** — runs end to end but on `detection_index`; join pipeline code done (build_track_ids.py); annotation in progress (S07, S14, S15) | 2026-06-13 |
| 5. Scalability / boundaries | **Not started** — majority-poisoned caveat documented in week06 README | — |
| 6. Writing / publication | **Not started** | — |

## TODO — researcher (Perry)

> See `docs/CONSOLIDATION_PLAN.md` for the full cleanup plan (stale docs,
> dead code, week tracking).

### Blocking — do these first

1. **Re-export stale scenarios** — ✅ done (2026-06-19)  
   Re-exported S03, S08–S13, S18 with `--overwrite`; diagnosed coverage with
   `scripts/diagnose_join_offsets.py`. Outcome (see Decisions log 2026-06-19):  
   - **Confirmed smoke-only:** S10 — night/low-light footage (frames ~9 PM),
     detector-capable but daytime-biased. Do not treat as ground truth.  
   - **Under-detected, cause UNDER REVIEW:** S03, S12/c03, S13/c03, S18 — few
     boxes but S03 is *not* night, so not yet classified. Triage before labeling:  
     `python scripts/sample_scenario_frames.py` then repeat the S10 detector checks.  
   - **Recoverable at lower IoU** — re-join the rest at `--iou-threshold 0.2`:  
     `bash scripts/build_track_ids_all.sh S08 S09 S11 S12 S13 -- --iou-threshold 0.2`  
   Alternate manifest `data/edited scenario windows.csv` deleted 2026-06-19.

### Active

2. **Annotate S07, S14, S15** for real cross-camera identity  
   *In progress (2026-06-13):* Perry annotating S07 using multicam-reid
   (https://github.com/figaone/multicam-reid).  
   After each: `bash scripts/save_annotations.sh <scenario>` (or `all` for every
   completed annotation) → commit → run join.  
   Full walkthrough: `docs/data/ANNOTATION_GUIDE.md`.  
   *Unblocks: TODO #4 results, publishable precision/recall.*

3. **Full sweep** (eps 0.1 and 1.0; valid scenarios only)  
   `python scripts/run_baselines.py --all --epsilons 0.1,0.5,1.0 --apply`  
   inside tmux; completed runs auto-skip. Run after TODO #1 re-export of
   S03, S08–S13, S18.

4. **Single-camera poison sweep** (`--poison-cameras c01`)  
   For the detector's minority assumption test.  
   See `experiments/week06-detector/README.md`.

### Pending

5. **Fill in week results README.md files**  
   `results/week03/` through `results/week07/` are empty placeholders.  
   Add a run table (date, scenarios, epsilon, status) to each.  
   See `docs/CONSOLIDATION_PLAN.md §3b` for the template.

6. **IDF1 / HOTA / MOTA / IDS extraction**  
   From tracker output. Week 3 gate requirement, still unimplemented.

7. **Publish run manifest after each batch**  
   After runs: `cp runs/run_manifest.csv results/weekXX/`  
   (currently gitignored and never committed — orphans the REPORT.md).

8. **LFS / Release budget** — decide once full-sweep sizes are known.

## TODO — students (Christine / Floyd)

1. **Wait for annotation (TODO #2 above)** before running the full analysis —
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

- 2026-06-19: **Several cameras are under-detected (few, oversized boxes) after
  re-export — cause confirmed for S10, still open for the rest.** After the
  `--overwrite` re-export, `scripts/diagnose_join_offsets.py` showed S03, S10,
  S12/c03, S13/c03, S18 emit very few, oversized boxes (e.g. S10/c01 = 8 det vs
  4672 annotation boxes). The detector is ruled in as *capable* via a control: at
  identical settings S11/c03 → 1742 det while S10/c01 → 8; an input-size sweep
  barely moved S10 (tsize 640→1280→1536 = 8→89→106) and dropping the
  `--prime-classes` filter was a no-op (106==106). **S10 confirmed footage-limited:**
  sampled frames are ~9 PM dusk — only close, headlight-lit vehicles resolve;
  COCO YOLOX-x is daytime-biased. **S10 → smoke-only.**
  **NOT yet confirmed for S03 et al.:** S03 is *not* night/low-light (per frame
  check 2026-06-19), so its under-detection has a different, still-open cause — do
  not classify it as footage-limited until triaged. **Next:** run
  `python scripts/sample_scenario_frames.py` (objective DAY/DUSK/NIGHT) + repeat
  the S10 detector checks per scenario before labeling any as smoke-only.
  **Recoverable at lower IoU** (re-join `--iou-threshold 0.2`): S08/c01, S09/c01,
  S09/c03, S11/c01, S11/c02, S12/c01, S13/c02. **Dense/OK:** S08/c03, S11 (all
  cams), S13/c01–c02.
- 2026-06-19: scenario windows + trims verified valid for all 18 scenarios
  (`scripts/check_scenario_windows.py`); alternate `data/edited scenario windows.csv`
  deleted. The remaining S03/S08–S13/S18 problem is **stale exports**, not
  windows — fix is `run_baselines --overwrite` + re-join, no re-trim needed.
- 2026-06-12: trimmed videos + merged exports are committable via LFS
  (`data/trimmed/`, `data/exports/`); raw footage and weights stay out of git.
- 2026-06-12: progress reports = `reports/<date>/REPORT.md` + stills in git,
  videos + self-contained HTML on a GitHub Release.
- 2026-06-10 (Perry): scenario window edits in `data/scenario_windows.csv`
  (#73) — under review, see TODO 1.
