# Student Setup And Weekly Workflow

This document is for Christina and Floyd.

Source of truth: `docs/schedules/PRIME_Schedule_new_revised.pdf`. This document turns the schedule into setup and git steps.

> **Windows users:** the commands below are written for macOS/Linux. On Windows, replace `python3` with `python` and replace `.venv/bin/python` with `.venv\Scripts\python.exe`. See `docs/setup/PYTHON_ENVIRONMENT.md` for the full command convention.

## Goal

By the end of Week 1, each student should be able to:

- Explain what a ReID embedding is.
- Explain why BoT-SORT is relevant to multi-camera tracking.
- Run the project smoke test.
- Confirm Python and PyTorch are installed.
- Confirm BoT-SORT is cloned.
- Know where CityFlowV2 Scenario S01 is stored.
- Know where their notes and experiment logs belong.

## First-Time Setup

Install:

- Git
- Python 3.10 or newer
- PyTorch, once the researcher confirms the official install target for your machine
- A terminal you are comfortable using

The official schedule says to create a conda environment. This repository currently provides a `venv` setup helper. Use the setup method Sabrina confirms for the group.

Detailed Python setup commands are in:

- `docs/setup/PYTHON_ENVIRONMENT.md`

The first-assignment walkthrough is in:

- `docs/setup/WEEK1_STUDENT_WALKTHROUGH.md`

Clone the repository:

```bash
git clone <repo-url>
cd blindspot-summer-2026
```

Run setup:

```bash
python scripts/setup_repo.py
```

If BoT-SORT setup fails or model weights are not ready yet, run the smaller setup path:

```bash
python scripts/setup_repo.py --skip-bot-sort
.venv/bin/python scripts/smoke_test.py
.venv/bin/python -m pytest
```

Expected success message:

```text
smoke tests passed
```

## Daily Git Workflow

Start by updating your copy:

```bash
git checkout main
git pull
```

Create a branch for your work:

```bash
git checkout -b student/<your-name>-<short-topic>
```

Check what changed before committing:

```bash
git status
git diff
```

Commit small, related changes:

```bash
git add <files-you-changed>
git commit -m "Describe the change"
git push -u origin student/<your-name>-<short-topic>
```

Open a pull request into `main` when the work is ready to review.

## Where Work Goes

Use these folders:

- Christina paper notes: `papers/christina/`
- Floyd paper notes: `papers/floyd/`
- Shared bibliography: `papers/shared-bibliography/`
- Experiment commands and protocols: `experiments/weekXX-topic/`
- Small result summaries: `results/weekXX/`
- Draft writing: `paper-draft/`

Do not commit:

- Large videos
- Large model checkpoints
- Raw tracker outputs
- Virtual environments
- Local dataset folders

## Run Log Template

For every experiment, record:

```text
Date:
Student:
Branch:
Commit:
Dataset/scenario:
Command:
Machine:
CPU/GPU:
Weights used:
Output path:
Result summary:
Problems or questions:
```

## Week 1 Ownership

Christina:

- Poisoning survey vocabulary.
- Question: what is data poisoning and why does it matter for vision?
- Read Seed 1: Cinà et al., Wild Patterns Reloaded.
- One annotated bibliography entry submitted before Friday.
- 10-minute Friday presentation using the 6-point format.

Floyd:

- ByteTrack and tracking metric basics.
- Question: how does ByteTrack work, and what are MOTA and IDF1?
- Read Seed 2: Zhang et al., ByteTrack.
- One annotated bibliography entry submitted before Friday.
- 10-minute Friday presentation using the 6-point format.

Both:

- Run the smoke test.
- Run `pytest` through the local virtual environment.
- Write one paragraph explaining ReID embeddings.
- Clone BoT-SORT.
- Confirm Python and PyTorch install.
- Confirm CityFlowV2 S01 location once provided.
- Bring setup problems to the group with the exact command and error message.

## Week 2 Preview

Both students:

- Read BadNets.
- Read the MOT tracker adversarial attack paper.
- Create one threat model diagram showing attack entry points in a BoT-SORT-ReID multi-camera pipeline.
- Find one additional paper independently and annotate it.
- Confirm BoT-SORT-ReID runs on a test clip with `--with-reid` once weights/data are available.
