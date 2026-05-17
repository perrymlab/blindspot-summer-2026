# Researcher Setup And Project Status

This document is for Sabrina or whoever is coordinating the summer project.

Source of truth: `docs/schedules/PRIME_Schedule_new_revised.pdf`. This setup document translates that schedule into repository actions and readiness checks.

## Current Completion Status

From a researcher point of view, the repository is ready for Week 1 orientation, local setup checks, and synthetic proof-of-concept experiments. It partially supports the Week 1 and Week 2 setup goals in the schedule, but it is not yet a finished real-data MTMC experiment pipeline.

Implemented and usable:

- Python package under `src/prime_mtmc/`.
- Synthetic MTMC-like embedding generation.
- Random and targeted embedding-space poisoning.
- Camera-level cross-camera consistency detector.
- Precision, recall, and F1 reporting for poisoned-camera detection.
- Smoke test script: `scripts/smoke_test.py`.
- Synthetic experiment runner: `scripts/run_synthetic_experiment.py`.
- Fresh-clone setup helper: `scripts/setup_repo.py`.
- BoT-SORT patch file for ReID poisoning/export hooks under `patches/`.
- BoT-SORT integration notes under `docs/botsort-integration/`.

Not yet complete:

- CityFlowV2 download and folder-layout automation.
- Confirmed object detector weights and FastReID weights.
- Clean BoT-SORT baseline run on CityFlowV2 S01.
- Merge from BoT-SORT detection-level exports to tracker/global IDs.
- Real MTMC tracking metrics such as IDF1, HOTA, MOTA, and IDS.
- Full experiment matrix and publication-quality plots.

## Researcher Setup

Use Python 3.10 or newer.

Before real-data work, review required external downloads:

- `docs/setup/DOWNLOADS.md`

For the concise Python environment setup, use:

- `docs/setup/PYTHON_ENVIRONMENT.md`

From the repository root:

```bash
python scripts/setup_repo.py
```

This creates `.venv`, installs the local package, clones BoT-SORT into `vendor/BoT-SORT`, applies the tracked PRIME patch, and runs the smoke test.

If BoT-SORT setup is not needed yet:

```bash
python scripts/setup_repo.py --skip-bot-sort
```

Run the dependency-light smoke test:

```bash
python scripts/smoke_test.py
```

Run the synthetic experiment:

```bash
python scripts/run_synthetic_experiment.py --out-dir runs/synthetic
```

Expected synthetic outputs:

- `runs/synthetic/clean_embeddings.csv`
- `runs/synthetic/poisoned_eps_*.csv`
- `runs/synthetic/scores_*.csv`
- `runs/synthetic/summary.csv`

## Researcher Decisions Needed

Before students start real-data runs, decide:

- Official branch: normally `main`, unless a specific integration branch is being reviewed.
- Whether to use the repository `.venv` setup helper or require a conda environment, since the schedule says conda while this repo currently automates `venv`.
- CityFlowV2 S01 local folder layout. The schedule says S01 should be downloaded directly from `aicitychallenge.org`.
- Detector and FastReID weight paths.
- Whether students can use CPU-only machines for setup, or need GPU access for real tracker runs.
- Where large outputs live. Keep large raw outputs out of git.
- How to demonstrate OSNet/ReID embeddings on two crop images during Week 1.

## Definition Of Ready For Student Work

Students can begin Week 1 work when:

- Each student can clone the repo.
- Each student can run `python scripts/smoke_test.py`.
- Each student understands that BoT-SORT adds a ReID embedding layer.
- BoT-SORT is cloned on each student machine.
- Python and PyTorch are confirmed on each student machine.
- CityFlowV2 Scenario S01 is downloaded and linked or documented.

## Schedule-Aligned Researcher Checkpoints

Week 1:

- Orient students to the PRIME mission, 10-week arc, and stack: BoT-SORT-ReID, CityFlowV2, embedding-space attack.
- Explain why ByteTrack alone is insufficient: no ReID means no identity-layer attack surface.
- Demonstrate a ReID embedding with OSNet on two crop images and cosine similarity.
- Confirm CityFlowV2 S01 download and path.

Week 2:

- Walk through the BoT-SORT-ReID codebase and the FastReID embedding hook.
- Demonstrate why pixel noise is not the intended attack layer and why embedding shifts matter.
- Confirm BoT-SORT-ReID runs on a test clip with `--with-reid`.

Weeks 3-4:

- Confirm CityFlowV2 S01 clean baseline runs and metrics.
- Guide the embedding poisoning hook and verify clean versus poisoned comparison tables.

Weeks 6-7:

- Review detector implementation for statistical correctness.
- Lock the paper argument after scalability and boundary-condition experiments.

## Definition Of Complete For The Current Research Phase

The current phase should be considered complete only after:

- Clean BoT-SORT-ReID baseline outputs exist for the chosen CityFlowV2 scenario.
- Poisoned embedding exports exist for the selected camera and epsilon settings.
- Exported embeddings are merged to a valid `track_id` field.
- `scripts/analyze_embedding_export.py` runs on the merged clean and poisoned tables.
- The group has a tracked summary table and notes explaining what was run.
