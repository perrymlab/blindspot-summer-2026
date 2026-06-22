# Start Here (Students)

Work through the steps in order before you touch the analysis script. Everything here runs on your normal machine. 


## 1. Set up, once

From the repo root, in the project virtual environment (Python 3.12):

```bash
cd ~/blindspot-summer-2026
python -m venv .venv
source .venv/bin/activate
```
You will know it worked because (.venv) appears at the front of your terminal prompt. If you skip activate you will get confusing errors.

Once you are in the environment, verify everything is installed correctly by running:

```bash
pip install -e .
python scripts/smoke_test.py
```
You only need to run those two lines once, if the smoke test already passed for you, you are good to go.

## 2. Get the data

Download the per-scenario embedding CSVs from the GitHub Release [`exports-2026-06-20`](https://github.com/perrymlab/blindspot-summer-2026/releases/tag/exports-2026-06-20) (clean and poisoned, detector input size `tsize=1536`). The release contains 58 files total — do not download all of them. You only need the `_tracked` versions for your assigned scenarios, which means two files per scenario: the clean tracked file and the poisoned tracked file. For example, for S03 that is `S03_clean_all-cams_tracked.csv.gz` and `S03_poison_c01-c02_eps0.5_seed7_all-cams_tracked.csv.gz`. The non-tracked all-cams files are a fallback for low-coverage situations and you will rarely need them.

Christine: you are working S01 through S08. 
Floyd: you are working S11 and S13 through S17. 

Neither of you has S09 or S10 (night footage, skip entirely). Download only your scenarios and move them into the `data/` folder as described below. Do not commit CSVs, videos, or weights to the repo.

Once downloaded, do not leave the files sitting in your Downloads folder. You should already have a `data/` folder inside the repo root from the trimming work you completed, move your `.csv.gz` files into there. If for some reason it does not exist, create it in VS Code by right-clicking the file explorer panel and hitting New Folder. The scripts expect you to pass the path to wherever the file actually lives, so if it is still in Downloads the command will fail with a file not found error.

Before you run any script, confirm the exact filename by running `ls data/` in your terminal and copying the name directly from that output into your command. Do not type the filename from memory, the poisoned files contain dots and numbers that are easy to misread. A poisoned file named `S03_poison_c01-c02_eps0.5_seed7_all-cams_tracked.csv.gz` tells you exactly what was done, the poison was injected into c01 and c02, at epsilon 0.5, with random seed 7. That configuration is the same across all 14 scenarios, so any differences you see between scenarios are about the footage and coverage, not about different attack parameters.

The files are gzipped (`*.csv.gz`, about four times smaller). You do not need to unzip anything `analyze_embedding_export.py` and `visualize_boxes.py` both read `.csv.gz` directly through pandas, so just point them at the `.gz` path. If you ever want to peek at a file by hand, `gunzip -k` will do it without deleting the original.

The header is `camera,frame,detection_index,x1,y1,x2,y2,embedding`. The `*_tracked` files add `track_id,annotation_track,match_iou`.

## 3. Know which scenarios are usable

Fourteen scenarios have real ground truth and are safe to use for actual precision and recall: S01 through S08, S11, and S13 through S17. Two are usable with a caveat — S12·c03 and S18 are dusk shots with partial recovery, so expect sparse coverage, label anything from them as low-light, and check with me before using either for anything beyond exploration; neither is poisoned or published. S10 is night footage and is confirmed footage-limited, do not use it for coverage at all, smoke-testing only.


## 4. How to analyze


For real analysis, use `*_all-cams_tracked.csv.gz`, which carries an actual global `track_id` from the ground-truth annotation join. This is what you want for real precision and recall. Run it on both clean and poisoned versions of a scenario, sweep `--z-threshold`, and write a run log to `results/week06/`. For a clean run:

```bash
python scripts/analyze_embedding_export.py \
  --input "data/S03_clean_all-cams_tracked.csv.gz" \
  --track-column track_id \
  --out-dir results/week01/S03_clean
```

For a poisoned run, add `--poisoned-cameras` so the script can score detection. Read the targeted cameras straight off the filename — `poison_c01-c02` means `--poisoned-cameras c01,c02`:

```bash
python scripts/analyze_embedding_export.py \
  --input "data/S03_poison_c01-c02_eps0.5_seed7_all-cams_tracked.csv.gz" \
  --track-column track_id \
  --poisoned-cameras c01,c02 \
  --out-dir results/week01/S03_poisoned
```

Always wrap the input path in quotes in case the filename contains dots or other characters that the terminal might misinterpret.

If a scenario's coverage is too low to be useful, fall back to `*_all-cams.csv.gz` with `--track-column detection_index` instead. This only gives you a per-frame placeholder ID, not a real global identity, so label anything you produce this way as placeholder only.


## 5. Read the outputs

The script writes three files to `--out-dir`:

`normalized_embeddings.csv` contains the embeddings after L2 normalization, with `scenario,camera,frame,track_id`. `camera_scores.csv` contains per-camera consistency scores showing how anomalous each camera's embeddings look. `metrics.csv` is only produced when `--poisoned-cameras` is given and contains detection metrics showing how well the poisoned cameras were flagged.

The script also prints `camera_scores` and metrics to the terminal. Once you have output, do not just record the numbers and move on. The output gives you a z-score and a flagged status per camera, your job is to think about what those mean. Which cameras got flagged? Were those the cameras the poison was actually injected into, or is the detector flagging the wrong ones? Did the mean distance drop on the poisoned cameras compared to clean, even if they did not cross the flagging threshold? A poisoning attack pulls embeddings closer together, so a drop in mean distance on the targeted cameras is a real signal even when flagged reads False. These are the questions that go in your run log, not just the raw numbers.

Run clean and poisoned for the same scenario, then sweep `--z-threshold` — the default is 1.25, try 0.5, 1.0, and 2.0 and note how the flagging changes. You are trying to find the threshold sensitive enough to catch the poisoned cameras without flagging cameras that are clean. Keep in mind the tracked file only keeps detections that matched an annotation, so it is a subset of the all-cams file that is expected, not a bug.


## 6. Record your run

Copy `templates/STUDENT_RUN_LOG_TEMPLATE.md` into your week's results folder with a dated filename and fill it out for every run. Record which input CSV you used, the exact command with `--track-column` and `--z-threshold`, the output paths and key numbers, and your reading of the result not just what the numbers are but what you think they mean.


## 7. See the bounding boxes

The annotated video with boxes and track IDs is produced on the GPU box and is not typically shared. But since the CSV already contains the detection coordinates, if you also have the source video file you can redraw the boxes locally using `scripts/visualize_boxes.py`. 

```bash
pip install opencv-python
```

Then run:

```bash
python scripts/visualize_boxes.py \
  --csv "data/S03_clean_all-cams_tracked.csv.gz" \
  --video /path/to/S03/c01/vdo.mp4 \
  --camera c01 \
  --out results/week01/S03_clean_c01_boxes.mp4
```

Replace `/path/to/S03/c01/vdo.mp4` with wherever the source video lives on your machine. The output is a new mp4 open it in any video player. Boxes are colored by `--color-by` (default `detection_index`); if your CSV has merged global ids use `--color-by track_id` to color per identity. If it reports "0 boxes drawn" the CSV and video do not line up — wrong video file or a frame-base mismatch. Do not use this as a routine step for every scenario — use it when a result looks suspicious, like a z-score that seems implausibly high or a camera flagging when it should not.


## 8. Troubleshooting

If you see `input must contain an embedding column`, you opened the wrong CSV — use the `_tracked` export. If you see `input does not contain 'track_id'`, use `--track-column detection_index` for a smoke check or confirm you downloaded the `_tracked` file. If you see `ModuleNotFoundError: prime_mtmc`, activate `.venv` and run `pip install -e .`. Do not spend more than 15 minutes stuck on the same error before you bring it to me.
