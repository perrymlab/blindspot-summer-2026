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

A researcher publishes per-scenario embedding CSVs. **Always use the
`*_all-cams.csv` files** (the cross-camera detector needs every camera in one
table). Never commit CSVs, videos, or weights.

Header: `camera,frame,detection_index,x1,y1,x2,y2,embedding`.

## 3. Know which scenarios are usable

| Tier | Scenarios | Use for |
| --- | --- | --- |
| **Real ground truth** (when join lands) | S07, S14, S15 | real precision/recall — gated on annotation |
| **Placeholder-only** (daytime, dense) | S01, S02, **S03**, S04–S06, S08, S11, **S13**, S16, S17 | `detection_index` smoke analysis, **labeled placeholder** |
| **Low-light caveat** (dusk, partial recovery) | S12·c03, S18 | usable but sparse — label low-light, expect lower coverage |
| **Smoke-only / skip** (confirmed footage-limited) | S10 (night) | do **not** use for coverage |

> **Re-export pending (2026-06-19):** the under-detection on S03/S13·c03/etc. was a
> detector input-size bug (pipeline ran at YOLOX default 640). `run_baselines.py`
> now defaults `--tsize 1536`; S03 and S13·c03 are daytime and recover fully, so
> they move to placeholder-usable. **The published CSVs predate this fix** — wait
> for the re-exported `*_all-cams.csv` files (STATUS.md TODO #1) before trusting
> coverage. Always re-check the `docs/STATUS.md` Decisions log before starting.

## What you can do today (before annotation)

1. **Placeholder analysis** — `scripts/analyze_embedding_export.py` on a
   daytime `*_all-cams.csv`, clean vs poisoned, sweep `--z-threshold`, write a
   run log to `results/weekXX/`. Use `--track-column detection_index` and label
   results **placeholder only**. Walkthrough:
   [`experiments/STUDENT_EMBEDDING_ANALYSIS.md`](experiments/STUDENT_EMBEDDING_ANALYSIS.md).
2. **Visualize / verify** — `scripts/visualize_boxes.py` overlays a CSV's boxes
   on its source video so you can confirm boxes land on vehicles.

## What waits for real annotation

Real precision/recall needs `track_id` (global identity), which comes from the
annotation join on S07/S14/S15. When those land, swap
`--track-column detection_index` → `--track-column track_id` — **same scripts,
better input.** Status: `docs/STATUS.md` TODO #2.

## Where to go next

- Current progress + open TODOs: [`STATUS.md`](STATUS.md)
- Analysis details: [`experiments/STUDENT_EMBEDDING_ANALYSIS.md`](experiments/STUDENT_EMBEDDING_ANALYSIS.md)
- Git/PR workflow: [`setup/GITHUB_WORKFLOW_GUIDE.md`](setup/GITHUB_WORKFLOW_GUIDE.md)
- Run-log template: [`templates/RUN_LOG_TEMPLATE.md`](templates/RUN_LOG_TEMPLATE.md)
