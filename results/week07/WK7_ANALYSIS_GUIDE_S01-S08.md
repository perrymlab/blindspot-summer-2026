# Week 07 Analysis Guide — S01–S08 (all operators)

**Applies to:** everyone running the Week 07 S01–S08 analysis.
**Pairs with:** `results/week07/RUN_LOG_TEMPLATE_WK7.md` — one log per run, filed per its naming rules.
**Condition:** two-cam poison (`c01,c02`), seed 7, epsilons 0.1 / 0.5 / 1.0.

Four runs per scenario, in this order: clean, eps 0.1, eps 0.5, eps 1.0.
Run clean first — the template's drop table needs your clean means.

## 1. One-time setup

Laptop only; no GPU needed. From the repo root:

```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate     macOS/Linux:  source .venv/bin/activate
pip install -e .
python scripts/smoke_test.py
```

## 2. Get the data (once)

All inputs are in the GitHub release **`exports-2026-07-12`** — 32 files:
per scenario, clean + three poisoned epsilons, all `_all-cams_tracked.csv.gz`.

```bash
gh release download exports-2026-07-12 -D data/
```

(No `gh`? Download the assets from the release page into `data/`.)

Rules:
- Use only the `_tracked.csv.gz` files — the analysis needs the joined `track_id`.
  Do not use plain `_all-cams.csv` or per-camera files.
- Do not unzip; the script reads `.csv.gz` directly.
- Never commit CSVs.
- Ignore the `exports-2026-07-11` release for this task — that's a different
  condition (single-cam c01) and will corrupt comparisons if mixed in.

## 3. Standard settings — identical for everyone

```
--track-column track_id
--z-threshold 1.25   (script default; do not override)
variance channel on  (do not pass --no-variance)
--poisoned-cameras c01,c02   (poisoned runs only)
```

The analysis is deterministic: same input + same flags gives identical numbers
for every operator. If two people disagree, compare input hashes
(`shasum -a 256 data/<file>` / `Get-FileHash data\<file>`) and flags — the
mismatch is there, not in the detector.

## 4. Run

Clean (example S01):

```bash
python scripts/analyze_embedding_export.py --input "data/S01_clean_all-cams_tracked.csv.gz" --track-column track_id --scenario S01 --out-dir "results/week07/S01_clean"
```

Poisoned (one per epsilon; quote paths — filenames contain dots):

```bash
python scripts/analyze_embedding_export.py --input "data/S01_poison_c01-c02_eps0.1_seed7_all-cams_tracked.csv.gz" --track-column track_id --scenario S01 --poisoned-cameras c01,c02 --out-dir "results/week07/S01_poisoned_eps0.1"
```

All eight scenarios in one pass — bash:

```bash
for s in S01 S02 S03 S04 S05 S06 S07 S08; do
  python scripts/analyze_embedding_export.py --input "data/${s}_clean_all-cams_tracked.csv.gz" --track-column track_id --scenario $s --out-dir "results/week07/${s}_clean"
  for e in 0.1 0.5 1.0; do
    python scripts/analyze_embedding_export.py --input "data/${s}_poison_c01-c02_eps${e}_seed7_all-cams_tracked.csv.gz" --track-column track_id --scenario $s --poisoned-cameras c01,c02 --out-dir "results/week07/${s}_poisoned_eps${e}"
  done
done
```

PowerShell:

```powershell
foreach ($s in 'S01','S02','S03','S04','S05','S06','S07','S08') {
  python scripts/analyze_embedding_export.py --input "data/${s}_clean_all-cams_tracked.csv.gz" --track-column track_id --scenario $s --out-dir "results/week07/${s}_clean"
  foreach ($e in '0.1','0.5','1.0') {
    python scripts/analyze_embedding_export.py --input "data/${s}_poison_c01-c02_eps${e}_seed7_all-cams_tracked.csv.gz" --track-column track_id --scenario $s --poisoned-cameras c01,c02 --out-dir "results/week07/${s}_poisoned_eps${e}"
  }
}
```

## 5. Outputs

Each `--out-dir` gets:

| File | What it is |
| --- | --- |
| `camera_scores.csv` | Per-camera: `mean_distance, variance, pair_count, mean_z_score, variance_z_score, z_score, flagged` — the template's Step 4 table. |
| `metrics.csv` | Poisoned runs only: TP/FP/FN/TN, precision, recall, F1. |
| `normalized_embeddings.csv` | L2-normalized embeddings (rarely needed directly). |

Copy template numbers from `camera_scores.csv`, not from memory.

## 6. Interpretation — read before answering template Q1–Q6

- **c01+c02 is a 2-of-3 majority poison.** The detector compares each camera to
  the cross-camera median and assumes poisoned cameras are the minority. With
  two of three poisoned, the clean camera (c03) can look like the outlier and
  flag instead. If that happens, it is a known property of this configuration —
  report it, don't treat it as a mistake in your run.
- **Record signed drops** (poisoned − clean mean distance) per camera; don't
  assume the direction.
- **Q5 (z-score of exactly zero)** means that camera sits exactly at the median —
  note that with 2 of 3 cameras poisoned, the median itself is poison-dominated.
- **Coverage:** `_tracked` files keep only annotation-matched detections, so
  they're smaller than the raw exports — expected. Note `pair_count`; very low
  coverage weakens any claim.

## 7. File your logs

One `.md` per run in `results/week07/`, named per the template
(e.g. `S01_poisoned_eps0.1_Lastname_2026-07-14.md`). Commit all four for a
scenario before starting the next.

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| `input must contain an embedding column` | Wrong CSV; use the `_tracked` export. |
| `input does not contain 'track_id'` | You grabbed a non-tracked file; re-download from `exports-2026-07-12`. |
| `ModuleNotFoundError: prime_mtmc` | Activate `.venv`, `pip install -e .`. |
| File not found | Check exact name with `ls data/` / `Get-ChildItem data`; quote the path. |
