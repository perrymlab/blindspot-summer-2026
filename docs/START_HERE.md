# Start Here (Students)

Work through steps 1 through 3 in order before you touch any analysis script. Everything here runs on a normal laptop, you are analyzing CSVs, not running BoT-SORT, and you do not need a GPU.

## 1. Set up, once

```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate
pip install -e .
python scripts/smoke_test.py
```

## 2. Get the data

Download the per-scenario embedding CSVs from the GitHub Release [`exports-2026-06-20`](https://github.com/perrymlab/blindspot-summer-2026/releases/tag/exports-2026-06-20) (clean and poisoned, detector input size `tsize=1536`). Always use the all-cams files — the cross-camera detector needs every camera in one table. Never commit CSVs, videos, or weights to the repo.

The files are gzipped (`*.csv.gz`, about four times smaller). You do not need to unzip anything — `analyze_embedding_export.py` and `visualize_boxes.py` both read `.csv.gz` directly through pandas, so just point them at the `.gz` path. If you ever want to peek at a file by hand, `gunzip -k` will do it without deleting the original.

The header is `camera,frame,detection_index,x1,y1,x2,y2,embedding`. The `*_tracked` files add `track_id,annotation_track,match_iou`.

These exports supersede the older `report-2026-06-12` set, which ran at detector input size 640 and under-detected small or distant vehicles. Use `exports-2026-06-20` only — if you find an old `report-2026-06-12` file sitting around, delete it.

## 3. Know which scenarios are usable

Fourteen scenarios have real ground truth and are safe to use for actual precision and recall: S01 through S08, S11, and S13 through S17. Two are usable with a caveat, S12·c03 and S18 are dusk shots with partial recovery, so expect sparse coverage, label anything from them as low-light, and check with me before using either for anything beyond exploration; neither is poisoned or published. S10 is night footage and is confirmed footage-limited, do not use it for coverage at all.

This split is current as of the annotation re-join on 2026-06-20, which fixed a detector input-size bug (the pipeline had been running at the YOLOX default of 640) and re-exported the full clean-and-poison set at `--tsize 1536`. Ground truth was re-joined on those 1536 exports for all fourteen usable scenarios, published as `exports-2026-06-20`. If you're working from an older mental model where only S07, S14, and S15 had real track IDs, that's obsolete now — all fourteen do. Coverage still varies scenario to scenario: S03, S13·c03, S16, and S17 are strong; S01, S05·c02, and S11·c03 are weak. Mean per-camera coverage across the set is around 0.45. Always check the Decisions log in `docs/STATUS.md` before you start, in case something has changed since this was written.

## 4. How to analyze

There are two file types per scenario in the Release, and which one you use depends on coverage.

For real analysis, use `*_all-cams_tracked.csv.gz`, which carries an actual global `track_id` from the ground-truth annotation join. This is what you want for real precision and recall, and it's the default path, run it on both clean and poisoned versions of a scenario, sweep `--z-threshold`, and write a run log to `results/weekXX/`:

```
python scripts/analyze_embedding_export.py \
  --input S03_clean_all-cams_tracked.csv.gz --track-column track_id \
  --out-dir results/weekXX/S03_clean
```

The full walkthrough is in [`experiments/STUDENT_EMBEDDING_ANALYSIS.md`](experiments/STUDENT_EMBEDDING_ANALYSIS.md). Keep in mind the tracked file only keeps detections that matched an annotation, so it's a subset of the all-cams file — that's expected, not a bug.

If a scenario's coverage is too low to be useful, fall back to `*_all-cams.csv.gz` with `--track-column detection_index` instead. This only gives you a per-frame placeholder ID, not a real global identity, so label anything you produce this way as placeholder only.

Once you have results, use `scripts/visualize_boxes.py` to overlay a CSV's boxes back onto its source video and confirm the boxes are actually landing on vehicles before you trust the numbers.

## Where to go next

Current progress and open TODOs are in [`STATUS.md`](STATUS.md). Analysis details are in [`experiments/STUDENT_EMBEDDING_ANALYSIS.md`](experiments/STUDENT_EMBEDDING_ANALYSIS.md). The git and PR workflow is in [`setup/GITHUB_WORKFLOW_GUIDE.md`](setup/GITHUB_WORKFLOW_GUIDE.md), and the run-log template is in [`templates/RUN_LOG_TEMPLATE.md`](templates/RUN_LOG_TEMPLATE.md).
