# Week 07 Analysis Guide — S01–S08

**Applies to:** The entire team everyone as we are running the Week 07 S01–S08 analysis.
**Pairs with:** `results/week07/RUN_LOG_TEMPLATE_WK7.md` one log per run, filed per its naming rules.
**Condition:** two-cam poison (`c01,c02`), seed 7, epsilons 0.1 / 0.5 / 1.0.

**What we are doing:** Running the embedding analysis script on 8 scenarios, 4 runs each — one clean and three poisoned at different attack strengths. You are comparing your results against each other to confirm the pipeline is consistent and to build the dataset for the paper.

## Before you start

Run clean first for every scenario. The run log has a drop table that compares your poisoned mean distances against the clean baseline — you cannot fill that in until you have the clean numbers.

**Run order for each scenario:**
1. Clean
2. Poisoned eps 0.1
3. Poisoned eps 0.5
4. Poisoned eps 1.0

Finish all four logs for one scenario and commit them before starting the next.

---


## 1. One-time setup

Do this once on your laptop. No GPU needed.

```bash
python -m venv .venv
source .venv/bin/activate        # Mac/Linux
# .venv\Scripts\activate         # Windows
pip install -e .
python scripts/smoke_test.py
```

You will know the environment is active because `(.venv)` appears at the front of your terminal prompt. If you skip this step you will get confusing errors — activate first every time you open a new terminal.

---


## 2. Get the data (once)

All the files you need are in the GitHub release **`exports-2026-07-12`** — 32 files total. Download them into your `data/` folder:

```bash
gh release download exports-2026-07-12 -D data/
```

If you do not have the `gh` command, go to the release page on GitHub and download the files manually into your `data/` folder.

**A few important rules:**

- Use only the `_all-cams_tracked.csv.gz` files. The analysis needs the `track_id` column that only the tracked files have.
- Do not unzip anything — the script reads `.csv.gz` directly.
- Never commit CSV files to the repo.
- Ignore the `exports-2026-07-11` release — that is a different experiment (single camera) and will give you wrong comparisons if you mix it in.

Before you run anything, confirm the exact filename by running `ls data/` in your terminal and copying the name directly. 

## 3. Standard settings
Everyone uses these exact settings. Do not change them. If you want to try something different, start a separate log file and note that it is a test run.

```
--track-column track_id
--z-threshold 1.25
--poisoned-cameras c01,c02   (poisoned runs only — leave this out for clean runs)
```

Because the analysis is deterministic — same input, same flags, same numbers.

---


## 4. Run

Clean (example S01):

```bash
python scripts/analyze_embedding_export.py --input "data/S01_clean_all-cams_tracked.csv.gz" --track-column track_id --scenario S01 --out-dir "results/week07/S01_clean"
```

Poisoned (one per epsilon; quote paths — filenames contain dots):

```bash
python scripts/analyze_embedding_export.py --input "data/S01_poison_c01-c02_eps0.1_seed7_all-cams_tracked.csv.gz" --track-column track_id --scenario S01 --poisoned-cameras c01,c02 --out-dir "results/week07/S01_poisoned_eps0.1"
```

You can also run all eight scenarios in one pass — bash:

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

## 5. Read the outputs

Each `--out-dir` folder will contain three files:

| File | What it contains |
|---|---|
| `camera_scores.csv` | The main results table — mean distance, variance, z-score, and flagged status per camera. Copy these numbers into your run log. |
| `metrics.csv` | Poisoned runs only — TP, FP, FN, TN, precision, recall, F1. |
| `normalized_embeddings.csv` | The embeddings after normalization. You rarely need to open this directly. |

Copy your numbers from `camera_scores.csv` into the run log. Do not type from memory.

---

## 6. Interpretation — read before answering template

In our experiments c01 and c02 are always the poisoned cameras that is 2 out of 3. The detector works by comparing each camera against the others. When two out of three cameras are poisoned, the poisoned cameras can look like the majority and the clean camera (c03) ends up looking like the outlier. If c03 flags on your poisoned run, that is not a mistake in your run it is a known behavior of the detector in this configuration. Report it and explain what you think caused it.

**Recording the drop**

When you fill in the drop table, write signed numbers poisoned mean minus clean mean. The drop should be negative because poisoning pulls the mean distance down. If you see a positive number, double-check that you are comparing the right scenario.

**When c01 gets a z-score of exactly zero**

This means c01 is sitting exactly at the group median. With two poisoned cameras, the median is already shifted by the poison so c01 landing at zero does not mean it is unaffected. The real signal is in the drop from the clean baseline, not the z-score alone.


## 7. File your logs

One `.md` file per run, saved to `results/week07/`. Name each file like this:

```
S01_clean_Perry_2026-07-14.md
S01_poisoned_eps0.1_Perry_2026-07-14.md
S01_poisoned_eps0.5_Perry_2026-07-14.md
S01_poisoned_eps1.0_Perry_2026-07-14.md
```

