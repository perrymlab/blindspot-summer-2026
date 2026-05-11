# Blindspot Summer 2026

Working repository for the PRIME summer project on detecting poisoned frames in multi-camera tracking. Sabrina Perry is the faculty researcher; Christina Page and Floyd Dodwell are the students.

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

Not yet implemented:

- CityFlowV2 ingestion.
- Merge from BoT-SORT detection-level embedding exports to tracker/global IDs.
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

Set up BoT-SORT runtime dependencies and weights, download/organize CityFlowV2 S01, then export clean and poisoned per-camera embeddings with the patched BoT-SORT flags described in `docs/botsort-integration/BOTSORT_INTEGRATION.md`.

## BoT-SORT Clone

The upstream BoT-SORT repo is cloned into `vendor/BoT-SORT` by `scripts/setup_repo.py` and patched locally with PRIME ReID poisoning/export flags. See `docs/botsort-integration/BOTSORT_INTEGRATION.md` for commands and caveats.
