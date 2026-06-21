# Agent Handoff (for a different IDE agent / different machine)

Context for an AI coding agent picking up this repo on a setup other than the
one it was last worked on. Read this + [`STATUS.md`](STATUS.md) first.

## What this project is

PRIME / BlindSpot: studying **ReID-embedding poisoning** in multi-camera
vehicle tracking. Pipeline: footage → trim → patched **BoT-SORT** (YOLOX-x
detector + FastReID VeRi embeddings) exports per-camera detection+embedding
CSVs → merge to per-scenario `*_all-cams.csv` → optional ground-truth identity
join → anomaly/detector analysis → report. Scenarios are `S01`–`S18`, cameras
`c001/c002/c003` (export ids `c01/c02/c03`).

## Two execution environments (do not conflate)

| Role | Where | Has | Runs |
| --- | --- | --- | --- |
| **Researcher** | RunPod GPU pod, conda env `botsort` (Py 3.9), repo at `/workspace/blindspot-summer-2026`, footage at `/workspace/blindspot_data`, `vendor/BoT-SORT` checkout + weights | GPU, BoT-SORT | `scripts/run_baselines.py`, joins, diagnostics |
| **Student** | Normal laptop, project `.venv` (Py 3.12), `pip install -e .` | no GPU, no BoT-SORT | `scripts/analyze_embedding_export.py`, `scripts/visualize_boxes.py` |

This Windows checkout is used to **edit code and docs, then commit/push**; the
heavy commands are run by the user on the **pod** (paste output back). An agent
on another machine should assume the same split: you edit + push here, the user
executes on the pod.

## Key paths & scripts

- `scripts/run_baselines.py` — batch clean/poisoned BoT-SORT runs + merge. Data
  root via `BLINDSPOT_DATA_ROOT` or `/workspace/blindspot_data`. Detector cmd is
  in `build_command` (`yolox_x.py` + `yolox_x.pth`, `--prime-classes 2,3,5,7`).
- `scripts/build_track_ids.py` / `build_track_ids_all.sh` — join annotation
  ground-truth identities to exports via IoU matching (`--iou-threshold`).
- `scripts/diagnose_join_offsets.py` — diagnoses low join coverage: detection
  counts, box-size/extent comparison, IoU sweep (0.5→0.05), verdicts
  (UNDER-DETECTED / LOOSE BOXES / POOR OVERLAP / COORD MISMATCH / OK / PARTIAL).
- `scripts/sample_scenario_frames.py` — samples stills per camera and
  classifies DAY/DUSK/NIGHT by mean luma (footage triage).
- `scripts/visualize_boxes.py` — overlay a CSV's boxes onto its source video.
- The BoT-SORT patch lives in `patches/0001-Add-PRIME-ReID-poison-and-export-hooks.patch`
  (adds `--prime-*` flags + class filter + embedding export). `vendor/BoT-SORT`
  is pod-only / gitignored — not in this checkout.

## Current state (2026-06-20) — re-export + annotation rejoin done

**The blocking chain is complete: clean+poison re-export @1536 and the
ground-truth annotation rejoin are both done and published** (GitHub Release
`exports-2026-06-20`; 56 assets). Students can run real `track_id` analysis. The
preceding finding that drove it (kept here for context):

**The under-detection was a detector input-size bug, now fixed.** The export
pipeline never set `--tsize`, so every run used YOLOX-x's default **640**, which
cannot resolve the small/distant vehicles in these wide 1600x1200 intersection
views. A per-camera tsize sweep settled it (fresh runs, detection counts):

- S03/c01 (DAY): 24 dets @640 → **1328 @1536**; S13/c03 (DAY): 5 → **1300**. Full
  daylight, dense annotations — **resolution-limited, fully recoverable @1536.**
- S12·c03 / S18 (DUSK): 6 → 83 / 155 — resolution + low light, **partial recovery**;
  usable with a low-light caveat (S18 still cuts off mid-clip).
- S10 (night): sweep barely moves (8→89→106) → **smoke-only, unchanged.**
- The "detections stop after frame N" pattern was a red herring: all suspect
  `vdo_trim.mp4` decode fully (~1200 bright frames) and a fresh @640 run reproduced
  the stale export exactly — the detector just missed small vehicles until tsize
  rose.

**Fix:** `scripts/run_baselines.py` now has a `--tsize` flag, **default 1536**.
Default-640 under-counted *every* export, so a full re-export at 1536 was
required. **That re-export is now done** (2026-06-20, 6-worker parallel via
`scripts/reexport_parallel.sh` + `scripts/poison_parallel.sh`), as is the
annotation rejoin at IoU 0.2 (`build_track_ids_all.sh`) for the 14 usable
scenarios (S01–S08, S11, S13–S17; mean per-camera coverage ~0.45). All published
to Release `exports-2026-06-20`.

Full evidence: `STATUS.md` Decisions log (2026-06-19 "later" and 2026-06-20).

## Open threads / next actions

1. **Re-export @1536 + annotation rejoin — done** (2026-06-20, published as
   `exports-2026-06-20`). `--iou-threshold 0.2` was used for the rejoin. Remaining
   researcher work (`STATUS.md` TODOs): full epsilon sweep 0.1/1.0 (#3),
   single-camera poison sweep (#4), IDF1/HOTA/MOTA/IDS extraction (#6), and
   committing `run_manifest.csv` from the pod into `results/weekXX/` (#7).
2. Frame/tsize triage is **done** (day/night + resolution split finalized in
   `STATUS.md` Decisions log and the `docs/START_HERE.md` tier table).
3. Student onboarding: `docs/START_HERE.md` routes students; real `track_id`
   metrics are **ready** for the 14 usable scenarios (the old "gated on
   S07/S14/S15 annotation" framing is obsolete — annotations exist for all 18,
   joins published for 14). Open: Perry to confirm all 18 annotations are
   trustworthy (`STATUS.md` TODO #2).
4. Broader objective (paused): vehicle-capable detector + better visualization
   (transcode videos for inline Jupyter). Detector is already YOLOX-x+vehicle
   filter; the remaining viz work is transcoding/overlay UX.

## Conventions (must follow)

- **Never commit** CSVs, raw videos, or weights. Trimmed videos / merged exports
  go via **Git LFS** (`data/trimmed/`, `data/exports/`); raw footage + weights
  stay out of git.
- Pod pushes use a PAT baked into the remote URL; **Releases** need the classic
  token (org blocked the fine-grained one).
- Pod recovery after restart: `bash scripts/pod_bootstrap.sh --serve`
  (see `docs/setup/RECOVERY.md`). Report server = port 8890, JupyterLab = 8888.
- Do not add code comments unless asked; match existing script style (module
  docstring + argparse). Verify scripts with `python -m py_compile`.
- Keep `STATUS.md` current — it is the single source of truth for progress.
