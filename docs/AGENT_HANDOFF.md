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

## Current state (2026-06-19) — the important recent finding

Re-exported S03/S08–S13/S18 (`--overwrite`). Join coverage was low; diagnosis:

- **Several cameras are under-detected** (few, oversized boxes): S03, S10,
  S12·c03, S13·c03, S18. The detector is *capable* — same settings give S11·c03
  = 1742 detections vs S10·c01 = 8; input-size sweep barely moved S10 (tsize
  640→1280→1536 = 8→89→106); dropping the class filter was a no-op (106==106).
- **S10 confirmed footage-limited:** sampled frames are ~9 PM dusk; COCO YOLOX-x
  is daytime-biased → **S10 is smoke-only.**
- **NOT confirmed for S03 et al.:** S03 is **not** night/low-light (per frame
  check), so its under-detection has a different, still-open cause. **Do not
  classify S03/S12·c03/S13·c03/S18 as footage-limited yet** — triage first with
  `scripts/sample_scenario_frames.py` (DAY/DUSK/NIGHT) + repeat the S10 detector
  checks per scenario.
- **Recoverable at lower IoU** (re-join `--iou-threshold 0.2`): S08·c01,
  S09·c01, S09·c03, S11·c01, S11·c02, S12·c01, S13·c02. **Dense/OK:** S08·c03,
  S11 (all), S13·c01–c02.

Full evidence: `STATUS.md` Decisions log 2026-06-19.

## Open threads / next actions

1. User runs `bash scripts/build_track_ids_all.sh S08 S09 S11 S12 S13 -- --iou-threshold 0.2`;
   if coverage improves, **fold `--iou-threshold 0.2` into `build_track_ids_all.sh`**
   as the default for these scenarios.
2. User runs `python scripts/sample_scenario_frames.py` to triage all 18; then
   finalize the day/night classification in `STATUS.md` and the table in
   `docs/START_HERE.md`.
3. Student onboarding: `docs/START_HERE.md` (new) routes students; real metrics
   gated on S07/S14/S15 annotation join (`STATUS.md` TODO #2).
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
