# Start Here (Students)

One-screen front door. Follow the three steps, then use the data table to pick
what to work on. You analyze CSVs on a **normal laptop** — you do **not** run
BoT-SORT or need a GPU.

## 1. Set up (once)

```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate
pip install -e .
python scripts/smoke_test.py
```

Full prerequisites + daily git workflow: [`setup/STUDENT_SETUP.md`](setup/STUDENT_SETUP.md).

## 2. Get the data

Download the per-scenario embedding CSVs from the GitHub Release
**[`exports-2026-06-20`](https://github.com/perrymlab/blindspot-summer-2026/releases/tag/exports-2026-06-20)**
(clean + poisoned, detector input size `tsize=1536`). Always use the **all-cams**
files — the cross-camera detector needs every camera in one table. For real
metrics prefer the **`*_all-cams_tracked.csv.gz`** variant (has global `track_id`);
see "How to analyze" below. Never commit CSVs, videos, or weights.

Files are **gzipped** (`*.csv.gz`, ~4× smaller). You do **not** need to unzip
them: `analyze_embedding_export.py` / `visualize_boxes.py` use pandas, which reads
`.csv.gz` directly — just pass the `.gz` path. (To peek manually: `gunzip -k`.)

Header: `camera,frame,detection_index,x1,y1,x2,y2,embedding` (the `*_tracked` files
add `track_id,annotation_track,match_iou`).

> These supersede the older `report-2026-06-12` exports, which were detector
> input-size 640 and **under-detected** small/distant vehicles. Use
> `exports-2026-06-20` only.

## 3. Know which scenarios are usable

| Tier | Scenarios | Use for |
| --- | --- | --- |
| **Real ground truth** (track_id joined, published) | S01–S08, S11, S13–S17 (14) | real precision/recall via `*_all-cams_tracked.csv.gz`, `--track-column track_id` |
| **Low-light caveat** (dusk, partial recovery) | S12·c03, S18 | usable but sparse — label low-light, expect lower coverage; not poisoned/published |
| **Smoke-only / skip** (confirmed footage-limited) | S10 (night) | do **not** use for coverage |

> **Annotation re-join landed (2026-06-20):** the under-detection was a detector
> input-size bug (pipeline ran at YOLOX default 640); fixed at `--tsize 1536`, the
> full clean+poison set was re-exported, and ground-truth annotations were re-joined
> on the 1536 exports for all **14 usable scenarios** — published as
> `exports-2026-06-20` (28 `_tracked.csv`, mean per-camera coverage ~0.45). These 14
> now have real `track_id`; the old "placeholder-only except S07/S14/S15" split is
> obsolete. Coverage varies — strong: S03, S13·c03, S16, S17; weak: S01, S05·c02,
> S11·c03. Use placeholder (`detection_index`) only as a fallback where coverage is
> too low (see "How to analyze" below). S10 (night) and the dusk-caveat cameras are
> not poisoned/published. Always re-check the `docs/STATUS.md` Decisions log before
> starting.

## How to analyze (real metrics are ready)

Two file types per scenario are in the Release:

- **`*_all-cams_tracked.csv.gz`** — has a real global **`track_id`** from the
  ground-truth annotation join. **Use these for real precision/recall.**
- **`*_all-cams.csv.gz`** — placeholder; only a per-frame `detection_index`, no
  global identity. Use only as a fallback / for all-detection smoke checks.

1. **Real analysis (do this):**
   ```
   python scripts/analyze_embedding_export.py \
     --input S03_clean_all-cams_tracked.csv.gz --track-column track_id \
     --out-dir results/weekXX/S03_clean
   ```
   Run clean vs poisoned, sweep `--z-threshold`, write a run log to
   `results/weekXX/`. Walkthrough:
   [`experiments/STUDENT_EMBEDDING_ANALYSIS.md`](experiments/STUDENT_EMBEDDING_ANALYSIS.md).
   **Coverage varies by scenario** (mean ~45%; strong: S03, S13·c03, S16, S17;
   weak: S01, S05·c02, S11·c03 — see STATUS.md). The tracked file keeps only
   detections that matched an annotation, so it's a subset of the all-cams file.
2. **Placeholder fallback** — same script on `*_all-cams.csv.gz` with
   `--track-column detection_index`; **label results placeholder only.**
3. **Visualize / verify** — `scripts/visualize_boxes.py` overlays a CSV's boxes
   on its source video to confirm boxes land on vehicles.

## Where to go next

- Current progress + open TODOs: [`STATUS.md`](STATUS.md)
- Analysis details: [`experiments/STUDENT_EMBEDDING_ANALYSIS.md`](experiments/STUDENT_EMBEDDING_ANALYSIS.md)
- Git/PR workflow: [`setup/GITHUB_WORKFLOW_GUIDE.md`](setup/GITHUB_WORKFLOW_GUIDE.md)
- Run-log template: [`templates/RUN_LOG_TEMPLATE.md`](templates/RUN_LOG_TEMPLATE.md)
