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
resolved. **Update 2026-06-19 (later):** the remaining near-empty exports
(S03, S12·c03, S13·c03, S18) were *not* stale window artifacts — they were a
detector input-size bug. The pipeline ran at YOLOX's default `--tsize 640`,
which can't resolve the small/distant vehicles in these wide intersection views.
Raising to 1536 recovers daytime scenarios fully (S03/c01 24→1328 dets); this
affected **all** exports, so a full re-export at the new default is required
(`run_baselines.py` now defaults `--tsize 1536` — see TODO #1).
Valid results: **S02–S07, S14–S18** at eps 0.5 on `detection_index` (placeholder
identities; real ground-truth requires annotation, see TODO #4).

| Gate (REAL_DATA_IMPLEMENTATION_PLAN.md) | Status | Last verified |
| --- | --- | --- |
| 1. Environment and data | **Done** (RunPod /workspace persistent; footage replaced CityFlowV2) | 2026-06-12 |
| 2. Clean baseline | **Partial** — all 18 windows/trims verified valid (2026-06-19); detector input-size bug found (ran at tsize 640) → full re-export at `--tsize 1536` pending (TODO #1); IDF1/HOTA/MOTA/IDS not implemented | 2026-06-19 |
| 3. Poisoning runs | **Partial** — eps 0.5 batch done (valid scenarios); eps 0.1 / 1.0 pending | 2026-06-12 |
| 4. Detector on real outputs | **Partial** — real `track_id` joins done on 1536 exports for 14 usable scenarios (mean coverage ~0.45, IoU 0.2); annotations exist for **all 18** (STATUS was stale on "S07/S14/S15 in progress" — Perry should confirm all are trustworthy); IDF1/HOTA/MOTA/IDS still not extracted | 2026-06-20 |
| 5. Scalability / boundaries | **Not started** — majority-poisoned caveat documented in week06 README | — |
| 6. Writing / publication | **Not started** | — |

## TODO — researcher (Perry)

> See `docs/CONSOLIDATION_PLAN.md` for the full cleanup plan (stale docs,
> dead code, week tracking).

### Blocking — do these first

1. **Re-export ALL scenarios at `--tsize 1536`** — ⚠️ blocking students  
   Triage (Decisions log 2026-06-19 "later") found the under-detection was the
   detector input size, not footage: the pipeline ran at YOLOX's default 640.
   `run_baselines.py` now defaults `--tsize 1536` (proven: S03/c01 24→1328,
   S13/c03 5→1300). Default-640 under-counted small/distant vehicles in **every**
   export. **This is the gate on student embedding analysis** — they need correct
   clean+poison `*_all-cams.csv`. Ordered sequence:  
   - **(a) Clean re-export @1536** — ✅ done (2026-06-20). 6-worker parallel run
     (`scripts/reexport_parallel.sh`, ~3 h); 54/54 per-cam CSVs, 18 all-cams merges,
     no errors. Verified: S03/c01 24→1328, S13/c03 5→1307.  
   - **(b) Poison re-export @1536** (eps 0.5, c01/c02) — ✅ done (2026-06-20).
     6-worker parallel (`scripts/poison_parallel.sh`); 17 scenarios (**S10 skipped**
     — smoke-only), 17 all-cams merges, no errors. Row counts match clean (poison
     perturbs embeddings, not detections).  
   - **(c) Publish** — ✅ done (2026-06-20). gzipped clean+poison `*_all-cams.csv`
     for the 14 daytime-usable scenarios (S01–S08, S11, S13–S17), 28 assets / 5.7 GB,
     published as GitHub Release **`exports-2026-06-20`**. `START_HERE.md` updated to
     point students there (gzip is pandas-transparent — no gunzip). Settles the
     LFS/Release-budget question (TODO #8): Release assets, gzipped, not LFS.  
   - **(d) Re-join annotations** → `*_tracked.csv` — ✅ done (2026-06-20).
     `build_track_ids_all.sh ... --iou-threshold 0.2` on the 1536 exports for the 14
     usable scenarios (28 joins, 0 failures); deleted 8 stale 640-era `_tracked.csv`
     (S09/S10/S12/S18). **Mean per-camera coverage ~0.45** (vs 0.00 at 640) — range
     0.15 (S01/c03) to 0.85 (S13/c03); strong on S03, S13/c03, S16, S17. The 28
     `_tracked.csv` are gzipped and published to Release `exports-2026-06-20`
     (56 assets total) — smoke-tested: `analyze_embedding_export.py --track-column
     track_id` produces real cross-camera metrics. **Students can do real analysis.**  
   Pod already at the commit with the `--tsize` flag (pushed 2026-06-19).  
   *Triage sub-task — ✅ done (2026-06-19):*  
   - **S03, S13/c03 — DAY, resolution-limited → recoverable @1536.** Promote to
     usable after re-export.  
   - **S12/c03, S18 — DUSK, resolution + low-light → partial @1536.** Usable with
     low-light caveat (S18 still cuts off mid-clip).  
   - **S10 — smoke-only, unchanged** (night; tsize does not help).  
   - **Recoverable at lower IoU** (re-join after re-export):
     `bash scripts/build_track_ids_all.sh S08 S09 S11 S12 S13 -- --iou-threshold 0.2`  
   Alternate manifest `data/edited scenario windows.csv` deleted 2026-06-19.

### Active

2. **Annotations + joins** — ✅ largely done (2026-06-20)  
   `data/annotations/` has matches.json + 3 track files for **all 18** scenarios
   (annotated via multicam-reid, https://github.com/figaone/multicam-reid). Joins
   to the 1536 exports done for the 14 usable scenarios (see TODO #1d, mean coverage
   ~0.45). **Open:** (a) Perry to confirm all 18 annotations are trustworthy (this
   item used to say only S07/S14/S15 were in progress); (b) publish the `_tracked.csv`
   for real-`track_id` analysis; (c) extract IDF1/HOTA/MOTA/IDS (TODO #6).  
   Walkthrough: `docs/data/ANNOTATION_GUIDE.md`.

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

1. **Real analysis is ready** — download `*_all-cams_tracked.csv.gz` from Release
   `exports-2026-06-20` and run `scripts/analyze_embedding_export.py
   --track-column track_id` (clean vs poisoned), sweep `--z-threshold`, write run
   logs + PR summaries to `results/weekXX/`. See `docs/START_HERE.md` "How to analyze."
   Mind per-scenario coverage (mean ~0.45; weak on S01/S05·c02/S11·c03).
2. Placeholder fallback only where coverage is too low: `*_all-cams.csv.gz` with
   `--track-column detection_index`, labelled placeholder.
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

- 2026-06-20: **Annotation re-join lands at 1536 — real `track_id` recovered.** With
  the dense 1536 exports, `build_track_ids_all.sh ... --iou-threshold 0.2` produced
  usable ground-truth identity for the 14 daytime-usable scenarios: **mean per-camera
  coverage ~0.45** (vs **0.00** at 640 — S03/c01 went 0.00 → 0.76), range 0.15–0.85.
  Joins are fast (~12 s/scenario, CPU/pandas — no GPU). 8 stale 640-era `_tracked.csv`
  (S09/S10/S12/S18) deleted to keep `make_progress_report` from preferring them.
  Surprise: `data/annotations/` is complete for **all 18** scenarios, not just the
  S07/S14/S15 that STATUS claimed were "in progress" — Perry to confirm all are
  trustworthy. IoU 0.2 chosen (vs default 0.5) per the 2026-06-19 box-mismatch
  finding; revisit now that 1536 boxes align better.

- 2026-06-20: **Full clean+poison re-export at tsize 1536 done — run it PARALLEL.**
  The serial `run_baselines` left the pod ~95% idle (one process = 3.5 of 128 cores,
  GPU 0–26% util / 2.3 of 24 GB) because the pipeline is CPU/IO-bound, not GPU-bound
  (decode, 1536 resize, ReID crops, writing huge embedding CSVs). Switching to **6
  parallel workers** over disjoint scenario subsets (`scripts/reexport_parallel.sh`,
  `scripts/poison_parallel.sh`; GPU then ~14 GB / 25–44 %) cut each pass ~10 h → ~3 h.
  Both passes verified, no errors; S10 skipped for poison (smoke-only). **File sizes
  are large** (S01 clean all-cams 1.2 GB; ~21 GB clean) — distribution to students is
  now the gating decision (TODO #1c / #8). SSH-kill gotcha: never `pkill -f <pat>`
  when `<pat>` is in your own remote command — it kills the shell (use PID kills
  excluding `$$`).

- 2026-06-19 (later): **Under-review under-detection is a DETECTOR INPUT-SIZE bug,
  not footage — fixed by raising `--tsize`.** The export pipeline never set
  `--tsize`, so every run used YOLOX-x's default **640**, which cannot resolve the
  small/distant vehicles in these wide 1600x1200 intersection views. Proven by a
  per-camera tsize sweep (fresh detector runs, IoU-independent detection counts):

  | camera | light | dets @640 | dets @1536 | frame span @1536 |
  | --- | --- | --- | --- | --- |
  | S03/c01 | DAY  | 24 | **1328** | 29–1013 (full clip) |
  | S13/c03 | DAY  | 5  | **1300** | 27–1098 (full clip) |
  | S12/c03 | DUSK | 6  | **83**   | 3–1024 (full but sparse) |
  | S18/c01 | DUSK | 6  | **155**  | 3–545 (still dies mid-clip) |

  The "detections stop after frame N" pattern was a red herring: all suspect
  `vdo_trim.mp4` decode fully (~1200 frames, bright ~130 luma throughout) and a
  fresh @640 run reproduced the stale export exactly — the detector simply only
  caught the occasional close/large vehicle (bus/truck) and missed the small
  distant ones until the input size was raised. Contrast S10 night, where the same
  sweep barely moved (8→89→106). **Verdicts:**
  - **S03, S13/c03 — DAY, resolution-limited → fully recoverable @1536** (not
    footage-limited). Promote to usable after re-export.
  - **S12/c03, S18 — DUSK, resolution + low-light → partial @1536** (full-clip span
    for S12 but sparse; S18 still cuts off at frame 545). Usable with a low-light
    caveat; between S10 (smoke-only) and the daytime scenarios.
  - **S10 — unchanged, smoke-only** (night; tsize does not help).

  Fix landed in `scripts/run_baselines.py`: new `--tsize` flag, **default 1536**.
  Implication: the default-640 under-detection affected **all** prior exports
  (dense daytime scenarios merely looked populated via their close vehicles), so a
  full re-export at 1536 is warranted before any real analysis — see TODO #1.

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
