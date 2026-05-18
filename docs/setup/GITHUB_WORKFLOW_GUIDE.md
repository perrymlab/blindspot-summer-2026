# GitHub Workflow Guide

This is the short daily workflow for each contributor.

> **Windows users:** the commands below are written for macOS/Linux. On Windows, replace `.venv/bin/python` with `.venv\Scripts\python.exe`. See `docs/setup/PYTHON_ENVIRONMENT.md` for the full command convention.

## Sabrina / Researcher

Owns `main`, permissions, review, and final research record.

Weekly:

1. Create or update one GitHub issue for the week's schedule goals.
2. Confirm which folders students should edit.
3. Confirm dataset, weights, and output locations for experiment weeks.
4. Review student pull requests.
5. Merge only reviewed work into `main`.
6. Decide what result summaries become part of the permanent repo.

Recommended GitHub settings:

- Protect `main`.
- Require pull requests before merge.
- Require the `Python tests` status check before merge.
- Require at least one approving review.
- Block force-pushes to `main`.
- Let students push to their own branches.

Automated testing:

- The GitHub Actions workflow in `.github/workflows/ci.yml` runs on pull requests into `main`, pushes to `main`, and manual `workflow_dispatch` runs.
- It installs the local package, runs `python scripts/smoke_test.py`, and runs `python -m pytest`.
- The workflow intentionally does not clone BoT-SORT or download CityFlowV2, model weights, videos, or raw experiment outputs. Those remain local/manual checks because they require external data and compute.

## Christine

Use this pattern for paper notes, bibliography entries, and assigned experiment notes.

```bash
git checkout main
git pull
git checkout -b student/christina-<topic>
```

Work in assigned folders, usually:

- `papers/christina/`
- `papers/shared-bibliography/`
- assigned `experiments/weekXX-topic/`
- approved summaries in `results/weekXX/`

Before opening a pull request:

```bash
git status
git diff
.venv/bin/python scripts/smoke_test.py
.venv/bin/python -m pytest
git add <files>
git commit -m "Add Christine week X notes"
git push -u origin student/christina-<topic>
```

Then open a pull request into `main`.
GitHub will run the `Python tests` check automatically. If it fails, click the failed check, read the log, fix the branch, and push again.

## Floyd

Use this pattern for paper notes, bibliography entries, and assigned experiment notes.

```bash
git checkout main
git pull
git checkout -b student/floyd-<topic>
```

Work in assigned folders, usually:

- `papers/floyd/`
- `papers/shared-bibliography/`
- assigned `experiments/weekXX-topic/`
- approved summaries in `results/weekXX/`

Before opening a pull request:

```bash
git status
git diff
.venv/bin/python scripts/smoke_test.py
.venv/bin/python -m pytest
git add <files>
git commit -m "Add Floyd week X notes"
git push -u origin student/floyd-<topic>
```

Then open a pull request into `main`.
GitHub will run the `Python tests` check automatically. If it fails, click the failed check, read the log, fix the branch, and push again.

## Group Rules

- Do not work directly on `main`.
- Pull latest `main` before starting.
- Use one branch per task.
- Keep commits focused.
- Put exact experiment commands in run logs.
- Do not commit datasets, model weights, videos, raw tracker outputs, `.venv`, `runs/`, or `vendor/`.
- Ask Sabrina before changing shared code in `src/` or `scripts/`.
- Every pull request should say what changed, why it changed, and how it was checked.

## Branch Names

```text
student/christina-week1-poisoning-notes
student/floyd-week1-bytetrack-notes
student/christina-week3-baseline-log
student/floyd-week4-poisoning-table
docs/week2-threat-model
research/week6-detector-review
```

## Pull Request Template

Use `docs/templates/PULL_REQUEST_TEMPLATE.md` when writing the PR description.

Minimum PR description:

```text
What changed:
Why:
How checked: .venv/bin/python scripts/smoke_test.py; .venv/bin/python -m pytest; GitHub Actions Python tests
Open questions:
```

## If Something Goes Wrong

Do not force-push or reset unless Sabrina tells you to.

Instead, save the exact error and ask for help with:

```bash
git status
git branch
git log --oneline -5
```
