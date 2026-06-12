# Blindspot Summer 2026

Working repository for the PRIME summer project on detecting poisoned frames in multi-camera tracking. Sabrina Perry is the faculty researcher; Christine Page and Floyd Dodwell are the students.

## Repository Layout

- `docs/`: schedules, weekly briefs, setup notes, and BoT-SORT integration documentation.
- `papers/`: student paper notes, annotated bibliography entries, and shared bibliography work.
- `experiments/`: week-specific experiment protocols, commands, configs, and notes.
- `src/prime_mtmc/`: reusable Python package for embedding poisoning and camera-level detection.
- `scripts/`: command-line utilities for smoke tests, synthetic experiments, and exported embedding analysis.
- `results/`: small week-specific summaries and tables. Large raw outputs should remain local or external.
- `paper-draft/`: manuscript sections, outlines, revision plans, and venue notes.
- `vendor/`: ignored local clone of BoT-SORT.

## Current Status

Implemented:

- MTMC-like synthetic embedding generation.
- Random and targeted additive embedding poisoning.
- Cross-camera embedding consistency detector.
- Camera-level precision, recall, and F1 metrics.
- Synthetic experiment CLI with CSV outputs.
- BoT-SORT integration notes for the ReID feature hook.
- Local BoT-SORT clone in `vendor/BoT-SORT`.
- Patched BoT-SORT branch `prime-reid-poison-export` with ReID poisoning/export flags.
- Export analyzer for BoT-SORT embedding CSVs.
- Scenario trimming workflow (`scripts/trim_scenarios.py` + committed window manifest).
- Batch baseline runner (`scripts/run_baselines.py`): clean + poisoned passes per scenario, merged per-scenario `*_all-cams.csv`, provenance manifest.
- Real-data runs on trimmed local footage: S01 clean + poisoned (eps 0.5) completed 2026-06-12.
- Shareable progress reports (`scripts/make_progress_report.py`): score tables, annotated stills/videos, self-contained HTML.
- LFS publishing of exports/trimmed videos (`scripts/publish_run_outputs.sh`) and GPU-pod recovery (`scripts/pod_bootstrap.sh`).

Not yet implemented:

- Merge from BoT-SORT detection-level embedding exports to tracker/global IDs (analysis currently uses `detection_index`; identity-level numbers are placeholders until then).
- Tracking metrics such as IDF1, HOTA, MOTA, and IDS from real tracker output.
- Publication-quality plots.

## Quick Run

Set up a fresh clone:

```bash
python scripts/setup_repo.py
```

This creates `.venv`, installs the local package, clones BoT-SORT into `vendor/BoT-SORT`, applies the PRIME patch from `patches/`, and runs the smoke test.

If you only want the local Python package and smoke test:

```bash
python scripts/setup_repo.py --skip-bot-sort
```

```bash
python scripts/run_synthetic_experiment.py --out-dir runs/synthetic
```

Run dependency-free smoke checks:

```bash
python scripts/smoke_test.py
```

## Real-Data Input Format

The detector expects one CSV row per detection:

- `scenario`
- `camera`
- `frame`
- `track_id`
- `e0 ... eN`

Use `prime_mtmc.data.EmbeddingTable.from_csv` to load exported embeddings.

## Next Engineering Step

S01 clean + poisoned (eps 0.5) runs are complete on trimmed footage. Next: fix the suspect rows in `data/scenario_windows.csv` (see `docs/STATUS.md`), run the full sweep (`python scripts/run_baselines.py --all --epsilons 0.1,0.5,1.0 --apply`), then implement the tracker/global-ID merge and IDF1/HOTA/MOTA/IDS metric extraction. Current progress and open TODOs: `docs/STATUS.md`.

## BoT-SORT Clone

The upstream BoT-SORT repo is cloned into `vendor/BoT-SORT` by `scripts/setup_repo.py` and patched locally with PRIME ReID poisoning/export flags. See `docs/botsort-integration/BOTSORT_INTEGRATION.md` for commands and caveats.
