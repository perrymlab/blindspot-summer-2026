# Week 1 Student Walkthrough

This walkthrough is the first assignment path from the student point of view. It uses a local `.venv` only. Do not install project packages into the system Python.

> **Windows users:** the commands below are written for macOS/Linux. On Windows, replace `python3` with `python` and replace `.venv/bin/python` with `.venv\Scripts\python.exe`. See `docs/setup/PYTHON_ENVIRONMENT.md` for the full command convention.

## 1. Clone The Repository

```bash
git clone <repo-url>
cd blindspot-summer-2026
```

Check that Python is available:

```bash
python3 --version
```

Use Python 3.10 or newer.

## 2. Create The Local Virtual Environment

For Week 1, use the smaller setup path if BoT-SORT weights, CityFlowV2, or GPU access are not ready yet:

```bash
python3 scripts/setup_repo.py --skip-bot-sort
```

This creates `.venv`, installs the local project and test tools into `.venv`, and runs the smoke test.

After setup, run checks through the virtual environment:

```bash
.venv/bin/python scripts/smoke_test.py
.venv/bin/python -m pytest
```

Expected smoke-test output:

```text
smoke tests passed
```

Expected pytest result:

```text
2 passed
```

## 3. Create Your Week 1 Branch

Start from the latest `main`:

```bash
git checkout main
git pull
```

Christine:

```bash
git checkout -b student/christina-week1-poisoning-notes
```

Floyd:

```bash
git checkout -b student/floyd-week1-bytetrack-notes
```

## 4. Complete The First Assignment

Christine:

- Read Seed 1: Cinà et al., Wild Patterns Reloaded.
- Write one annotated bibliography entry about data poisoning and why it matters for vision.
- Prepare a 10-minute Friday presentation using the 6-point format Sabrina gives the group.
- Save your notes under `papers/christina/`.

Floyd:

- Read Seed 2: Zhang et al., ByteTrack.
- Write one annotated bibliography entry about ByteTrack, MOTA, and IDF1.
- Prepare a 10-minute Friday presentation using the 6-point format Sabrina gives the group.
- Save your notes under `papers/floyd/`.

Both students:

- Run the smoke test.
- Run `pytest`.
- Write one paragraph explaining what a ReID embedding is and why it matters for multi-camera tracking.
- Ask Sabrina for the confirmed CityFlowV2 S01 location. Do not commit dataset files or local paths with private machine details.

Suggested Week 1 note filenames:

```text
papers/christina/week1-wild-patterns-reloaded.md
papers/christina/week1-reid-embedding-summary.md
papers/floyd/week1-bytetrack.md
papers/floyd/week1-reid-embedding-summary.md
```

## 5. Check Your Work Locally

Before committing:

```bash
git status
git diff
.venv/bin/python scripts/smoke_test.py
.venv/bin/python -m pytest
```

Do not commit:

- `.venv/`
- `vendor/`
- `runs/`
- datasets
- model weights
- raw videos
- raw tracker outputs

## 6. Commit And Push

Christine example:

```bash
git add papers/christina/week1-wild-patterns-reloaded.md papers/christina/week1-reid-embedding-summary.md
git commit -m "Add Christine week 1 notes"
git push -u origin student/christina-week1-poisoning-notes
```

Floyd example:

```bash
git add papers/floyd/week1-bytetrack.md papers/floyd/week1-reid-embedding-summary.md
git commit -m "Add Floyd week 1 notes"
git push -u origin student/floyd-week1-bytetrack-notes
```

## 7. Open The Pull Request

Open a pull request into `main`.

Use this PR description shape:

```text
What changed:
- Added Week 1 annotated bibliography notes.
- Added a short ReID embedding summary.

Why:
- Completes the Week 1 reading and setup assignment.

How checked:
- .venv/bin/python scripts/smoke_test.py
- .venv/bin/python -m pytest

Open questions:
- <anything Sabrina should answer>
```

GitHub Actions will run the `Python tests` check automatically on the pull request. If it fails, open the failed check log, fix the branch, rerun the local checks, and push again.
