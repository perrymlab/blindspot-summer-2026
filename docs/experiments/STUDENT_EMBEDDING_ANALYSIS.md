# Student Guide: Analyzing Exported Embeddings

This guide is for **students**. You analyze the ReID embedding CSVs that a
researcher exports from BoT-SORT. **You do not run BoT-SORT yourself** -- no
GPU, no conda, no `vendor/BoT-SORT`. If you are looking to *produce* the CSVs,
that is the researcher workflow in
[`docs/botsort-integration/BOTSORT_GPU_RUNBOOK.md`](../botsort-integration/BOTSORT_GPU_RUNBOOK.md).

Everything below runs on a normal laptop with the project's own `.venv`.

---

## 1. One-time setup

From the repo root, in the project virtual environment (Python 3.12):

```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate
pip install -e .
```

That installs the `prime_mtmc` package and `pandas`/`numpy`, which the
analysis script uses. Verify:

```bash
python scripts/smoke_test.py
```

---

## 2. Get a CSV from the researcher

A researcher hands you one or more embedding CSVs (e.g. `clean_c01.csv`,
`poisoned_c01.csv`). Save them somewhere outside git, for example
`runs/botsort/`. **Never commit CSVs, videos, or weights.**

Each CSV has one row per detection with this header:

```
camera,frame,detection_index,x1,y1,x2,y2,embedding
```

`embedding` is a space-separated float vector (the ReID feature).

---

## 3. Understand the track-id requirement

The raw BoT-SORT export does **not** contain a global track id -- only a
per-frame `detection_index`. The analysis groups detections by identity, so it
needs a track column:

- **Smoke check / first look:** pass `--track-column detection_index`. This
  treats every detection independently. It confirms the pipeline runs but the
  per-identity numbers are not meaningful.
- **Real analysis:** the researcher must first merge the export with
  tracker-assigned global ids (or ground-truth ids) into a `track_id` column.
  Then pass `--track-column track_id`. Ask the researcher which file already
  has global ids before doing real analysis.

---

## 4. Run the analysis

```bash
python scripts/analyze_embedding_export.py \
  --input runs/botsort/clean_c01.csv \
  --track-column detection_index \
  --scenario S01 \
  --out-dir runs/embedding_analysis/clean_c01
```

For a poisoned run, tell the script which cameras were poisoned so it can score
detection:

```bash
python scripts/analyze_embedding_export.py \
  --input runs/botsort/poisoned_c01.csv \
  --track-column track_id \
  --scenario S01 \
  --poisoned-cameras c01,c02 \
  --out-dir runs/embedding_analysis/poisoned_c01
```

---

## 5. Read the outputs

The script writes to `--out-dir`:

| File | What it is |
| --- | --- |
| `normalized_embeddings.csv` | The embeddings after L2 normalization, with `scenario,camera,frame,track_id`. |
| `camera_scores.csv` | Per-camera consistency scores -- how anomalous each camera's embeddings look. |
| `metrics.csv` | Only when `--poisoned-cameras` is given: detection metrics (e.g. how well the poisoned cameras are flagged). |

The script also prints `camera_scores` (and metrics, if computed) to the
terminal. A camera that was poisoned should stand out in the consistency
scores; that is the signal the project is studying.

`--z-threshold` (default `1.25`) controls how aggressive the anomaly flag is.
Try a couple of values and note the effect in your run log.

---

## 6. (Optional) See the bounding boxes

The researcher's annotated video (boxes + track ids) is produced on the GPU box
with `--save_result` and usually isn't shared. But the CSV already contains the
detection boxes (`x1,y1,x2,y2`), so if you also have the **source video** you can
redraw them locally with `scripts/visualize_boxes.py`:

```bash
pip install opencv-python   # not a default project dep
python scripts/visualize_boxes.py \
  --csv runs/botsort/clean_c01.csv \
  --video /path/to/S01/c001/vdo.mp4 \
  --camera c01 \
  --out runs/embedding_analysis/clean_c01_boxes.mp4
```

Open the output mp4 in any player. Notes:

- Boxes are colored by `--color-by` (default `detection_index`). If your CSV has
  merged global ids, use `--color-by track_id` to color per identity.
- BoT-SORT frame numbers are 1-based. If the boxes look one frame off, pass
  `--frame-offset 1` or `--frame-offset -1`.
- If it reports "0 boxes drawn", the CSV and video don't line up (wrong video,
  or a frame-base mismatch).

---

## 7. Record your run

Copy `docs/templates/RUN_LOG_TEMPLATE.md` into your week's experiment folder
with a dated filename and record:

- Which input CSV you used (and which researcher run produced it).
- The exact command, `--track-column`, and `--z-threshold`.
- The output paths and the key numbers.
- Your reading of the result.

Add summaries to `results/` only after Sabrina approves them.

---

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| `input must contain an embedding column` | You opened the wrong CSV; use the `--prime-export-embeddings` output. |
| `input does not contain 'track_id'` | Use `--track-column detection_index` for a smoke check, or get a merged-id CSV from the researcher. |
| `ModuleNotFoundError: prime_mtmc` | Activate `.venv` and run `pip install -e .`. |
