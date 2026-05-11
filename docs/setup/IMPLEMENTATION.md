# PRIME MTMC Poisoning Implementation

This repository contains the first working implementation layer for the project described in `docs/schedules/PRIME_Schedule_new_revised.pdf`, plus a patched local BoT-SORT checkout for ReID embedding export and poisoning.

## What Is Implemented

- Synthetic MTMC-like embedding generator.
- Random and targeted embedding-space poisoning.
- Camera-level cross-camera embedding consistency detector.
- Camera-level precision, recall, and F1 reporting.
- CLI runner for reproducible smoke experiments.
- Dependency-free smoke test runner.
- BoT-SORT cloned at `vendor/BoT-SORT`.
- BoT-SORT PRIME integration branch: `prime-reid-poison-export`.
- BoT-SORT patch commit: `e9dafea0ad85f8bbfb6ad6e7626aa3e31a511285`.
- ReID poisoning/export hook in `vendor/BoT-SORT/fast_reid/fast_reid_interfece.py`.
- PRIME CLI flags added to `vendor/BoT-SORT/tools/demo.py` and `vendor/BoT-SORT/tools/mc_demo.py`.
- Project-side analyzer for exported BoT-SORT embeddings: `scripts/analyze_embedding_export.py`.

## Not Yet Implemented

- CityFlowV2 download/setup automation.
- Real CityFlowV2 S01 clean baseline run.
- Merge from BoT-SORT detection-level embedding exports to tracker/global IDs.
- Real tracking metric extraction for IDF1, HOTA, MOTA, and IDS.
- Full experiment matrix across epsilon levels, camera counts, and scenarios.
- Publication-quality plots.

## Run The Smoke Experiment

Fresh clone setup:

```bash
python scripts/setup_repo.py
```

For package-only setup without cloning BoT-SORT:

```bash
python scripts/setup_repo.py --skip-bot-sort
```

```bash
python scripts/run_synthetic_experiment.py --out-dir runs/synthetic
```

Expected outputs:

- `runs/synthetic/clean_embeddings.csv`
- `runs/synthetic/poisoned_eps_*.csv`
- `runs/synthetic/scores_*.csv`
- `runs/synthetic/summary.csv`

Run dependency-free smoke checks:

```bash
python scripts/smoke_test.py
```

## BoT-SORT PRIME Hook

The BoT-SORT checkout is intentionally kept under `vendor/` and ignored by the parent repository. It is still a Git repo itself:

```bash
git -C vendor/BoT-SORT status --short --branch
```

Expected branch:

```text
## prime-reid-poison-export
```

Useful demo flags now available in the patched checkout:

- `--prime-camera-id c01`
- `--prime-poison-cameras c01,c02`
- `--prime-poison-epsilon 0.5`
- `--prime-poison-seed 7`
- `--prime-export-embeddings ../../runs/botsort/clean_c01.csv`

Example clean per-camera export:

```bash
cd vendor/BoT-SORT
python tools/demo.py video --path <path-to-S01-c001-video> --with-reid --prime-camera-id c01 --prime-export-embeddings ../../runs/botsort/clean_c01.csv
```

Example poisoned per-camera export:

```bash
cd vendor/BoT-SORT
python tools/demo.py video --path <path-to-S01-c001-video> --with-reid --prime-camera-id c01 --prime-poison-cameras c01,c02 --prime-poison-epsilon 0.5 --prime-export-embeddings ../../runs/botsort/poisoned_c01.csv
```

See `docs/botsort-integration/BOTSORT_INTEGRATION.md` for hook details and run-log requirements.

## Next Real-Data Step

1. Set up BoT-SORT runtime dependencies, detector weights, and FastReID weights.
2. Download/organize CityFlowV2 S01 camera videos.
3. Run patched BoT-SORT once per camera with `--prime-export-embeddings`.
4. Merge exported detection-level embeddings with tracker-assigned global IDs or controlled ground-truth IDs.
5. Run `scripts/analyze_embedding_export.py` on the merged embedding table.
6. Repeat with `--prime-poison-cameras` and `--prime-poison-epsilon` for clean-vs-poisoned comparison.
