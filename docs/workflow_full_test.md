# Full GitHub Workflow Test

This document describes how to test the professor/student GitHub workflow end to end without using Brian's or Sabrina's personal GitHub credentials as the student.

The test should confirm:

- A student can clone the repository.
- A student can set up the project using only local `.venv` packages.
- A student can create a `student/...` branch.
- A student can open a pull request into `main`.
- GitHub Actions runs the `Python tests` check.
- `main` cannot be updated directly by the student.
- Sabrina's review is required before merge.
- The PR can merge only after the required check passes.

## 1. Create A Test Student Account

Create one separate GitHub account for the test student.

Use a separate browser profile for this account. Do not sign into the test student account in the same browser profile used for Brian's or Sabrina's account.

## 2. Configure Repository Access

In the real repository, Sabrina should invite the test student account as a collaborator.

Grant the test student account `Write` access.

This project uses protected `main` plus student branches in the shared repository. Do not test the fork workflow for this project.

## 3. Protect `main`

Before testing, configure branch protection for `main`:

- Require pull request before merge.
- Require the `Python tests` status check before merge.
- Require at least one approving review.
- Block direct pushes to `main`.
- Block force pushes to `main`.

The required status check should match the workflow job name from `.github/workflows/ci.yml`: `Python tests`.

## 4. Create A Separate Student Clone

Use a separate local clone for the test student so local git settings do not mix with Brian's or Sabrina's working copy.

```bash
cd ~
git clone <repo-url> blindspot-student-test
cd blindspot-student-test
```

Configure identity only inside this clone:

```bash
git config user.name "Test Student"
git config user.email "test-student@example.com"
```

Do not use `git config --global` for the test identity.

Confirm the local identity:

```bash
git config user.name
git config user.email
```

## 5. Run The Student Setup

Use the Week 1 smaller setup path. This workflow test does not clone BoT-SORT and does not use CityFlowV2, model weights, videos, raw tracker outputs, or GPU compute.

The setup script creates a local `.venv`. After it finishes, run the smoke test and pytest through that virtual environment's Python executable. The path to that executable differs by operating system:

- Windows (cmd or PowerShell): `.venv\Scripts\python.exe`
- macOS / Linux: `.venv/bin/python`

On Windows, the system `python` launcher is usually named `python` (not `python3`).

Windows (cmd):

```bat
python scripts\setup_repo.py --skip-bot-sort
.venv\Scripts\python.exe scripts\smoke_test.py
.venv\Scripts\python.exe -m pytest
```

macOS / Linux:

```bash
python3 scripts/setup_repo.py --skip-bot-sort
.venv/bin/python scripts/smoke_test.py
.venv/bin/python -m pytest
```

Expected results:

```text
smoke tests passed
2 passed
```

This verifies that the test student can install dependencies locally into `.venv` and run the same checks that GitHub Actions runs.

## 6. Create A Student Branch

Simulate one Week 1 student assignment with this branch name:

```bash
git checkout main
git pull
git checkout -b student/test-week1-notes
```

Add a small temporary note in an assigned student area:

```text
papers/christina/week1-workflow-test.md
```

The note can be short:

```text
# Week 1 Workflow Test

This temporary note tests the protected-branch and pull-request workflow.

ReID embedding summary: a ReID embedding is a numeric feature vector used to compare whether detections from different cameras may represent the same person or object.
```

## 7. Verify And Push As The Student

Before committing:

```bash
git status
git diff
```

Then run the local checks through the virtual environment.

Windows (cmd):

```bat
.venv\Scripts\python.exe scripts\smoke_test.py
.venv\Scripts\python.exe -m pytest
```

macOS / Linux:

```bash
.venv/bin/python scripts/smoke_test.py
.venv/bin/python -m pytest
```

Commit and push:

```bash
git add papers/christina/week1-workflow-test.md
git commit -m "Add workflow test student note"
git push -u origin student/test-week1-notes
```

## 8. Open The Pull Request

Signed in as the test student, open a pull request into `main`.

Use this PR description:

```text
What changed:
- Added a temporary Week 1 workflow test note.

Why:
- Tests the student branch, PR, CI, and review workflow.

How checked:
- smoke_test.py via the local .venv Python
- pytest via the local .venv Python

Open questions:
- None. This PR is only for workflow validation.
```

Confirm:

- The PR targets `main`.
- The source branch is `student/test-week1-notes`.
- GitHub Actions starts automatically.
- The check name is `Python tests`.
- The test student cannot merge while required review is missing.

## 9. Test Direct Push Protection

From the student clone, confirm direct updates to `main` are blocked.

```bash
git checkout main
git pull
```

Create a temporary branch for the test first so no local work is lost:

```bash
git checkout -b student/direct-push-block-test
```

Make a tiny temporary file.

Windows (cmd):

```bat
> papers\christina\week1-direct-push-block-test.md echo # Direct Push Block Test
>> papers\christina\week1-direct-push-block-test.md echo.
>> papers\christina\week1-direct-push-block-test.md echo Temporary file for branch-protection validation.
git add papers/christina/week1-direct-push-block-test.md
git commit -m "Test direct push protection"
```

macOS / Linux:

```bash
printf "# Direct Push Block Test\n\nTemporary file for branch-protection validation.\n" > papers/christina/week1-direct-push-block-test.md
git add papers/christina/week1-direct-push-block-test.md
git commit -m "Test direct push protection"
```

Attempt to push that commit to `main`:

```bash
git push origin HEAD:main
```

Expected result: GitHub rejects the push because `main` is protected.

After the rejection, delete the local test branch:

```bash
git checkout main
git branch -D student/direct-push-block-test
```

Do not force push.

## 10. Review As Sabrina

Switch to Sabrina's browser profile.

Confirm:

- The `Python tests` check passed.
- The PR contains only the expected temporary student note.
- The PR cannot be merged until the required review is submitted.

Approve the PR as Sabrina.

Then confirm:

- Merge becomes available only after approval and passing checks.
- The student account did not approve its own PR.
- The merge button respects the repository's branch protection settings.

## 11. Cleanup

Remove the temporary workflow-test note with a cleanup PR after the workflow test:

```bash
git checkout main
git pull
git checkout -b docs/remove-workflow-test-note
git rm papers/christina/week1-workflow-test.md
git commit -m "Remove workflow test note"
git push -u origin docs/remove-workflow-test-note
```

Open a PR, let `Python tests` pass, review it, and merge it. This also tests the normal cleanup path.

## Pass Criteria

The workflow test passes when:

- The student setup works through `.venv`.
- Local smoke test passes.
- Local pytest passes.
- The student can push `student/test-week1-notes`.
- The student can open a PR into `main`.
- GitHub Actions runs `Python tests`.
- Direct push to `main` is rejected.
- Merge is blocked before approval.
- Merge is allowed after approval and passing checks.
- Temporary test artifacts are removed through the cleanup PR.
