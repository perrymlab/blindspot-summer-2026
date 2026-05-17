# Sabrina Quickstart

One-page setup and daily workflow for the repo. Follow this end to end after a fresh clone. If anything in this guide conflicts with another doc, this one wins for Sabrina specifically.

Repo: `https://github.com/perrymlab/blindspot-summer-2026`

## 1. One-time setup on a new machine

### 1a. Install prerequisites

- Git for Windows (or git on macOS/Linux).
- Python 3.10 or newer.
- A terminal you are comfortable with: Command Prompt, PowerShell, or Git Bash.

### 1b. Fresh clone

Pick a folder you want the project under, then:

```bash
git clone https://github.com/perrymlab/blindspot-summer-2026.git
cd blindspot-summer-2026
```

### 1c. Set your git identity for this clone only

This stamps your commits so they show up as you on GitHub, but only for this repo. It does not change git settings on other projects.

```bash
git config user.name "Sabrina Perry"
git config user.email "<your-noreply-email>"
```

For `<your-noreply-email>`:

1. Open `https://github.com/settings/emails` while signed in as the GitHub account you want to commit as.
2. Make sure "Keep my email addresses private" is checked.
3. Copy the line that looks like `12345678+sabrina-perry@users.noreply.github.com`. That is the value to paste above.

Verify:

```bash
git config user.name
git config user.email
```

### 1d. Authenticate once

The first time you push, git will prompt for credentials. Use either of these:

- Easiest: a Personal Access Token (PAT).
  1. Go to `https://github.com/settings/tokens` while signed in as the account that owns the repo.
  2. Click "Generate new token" -> "Fine-grained tokens".
  3. Name: `blindspot-summer-2026`.
  4. Expiration: 90 days.
  5. Repository access: "Only select repositories" -> pick `perrymlab/blindspot-summer-2026`.
  6. Permissions -> Repository: Contents read/write, Pull requests read/write, Metadata read (default).
  7. Generate the token. Copy it once.
  8. When git prompts for username, use your GitHub username. When it prompts for password, paste the token.
- Alternative: GitHub CLI (`gh auth login`) handles this automatically.

Windows stores this in Credential Manager and reuses it forever. You will not be prompted again on this machine for this repo.

### 1e. Python environment

From the repo root:

```bash
python scripts/setup_repo.py --skip-bot-sort
```

This creates `.venv`, installs the local package, and runs the smoke test. Use `python scripts/setup_repo.py` instead if you also want BoT-SORT cloned.

To activate the environment in future sessions:

- Windows Command Prompt: `.venv\Scripts\activate.bat`
- PowerShell: `.venv\Scripts\Activate.ps1`
- macOS/Linux/Git Bash: `source .venv/bin/activate`

## 2. Daily workflow

Do every change through a branch and a pull request. Never edit files directly on `main`, and never use the "Edit this file" pencil icon on the GitHub website. Both of those paths created the messy `suhbrina-perry-patch-1/2/3` branches.

### 2a. Make sure your local copy is fresh

```bash
git fetch --prune
git --no-pager branch -a
git checkout main
git pull
```

### 2b. Create a branch for the change

Pick a short descriptive name. Examples:

- `docs/week2-rubric`
- `assignments/christina-week1`
- `assignments/floyd-week1`
- `fix/readme-typo`

```bash
git checkout -b docs/week2-rubric
```

### 2c. Edit files in your local clone

Use any text editor (VS Code, Notepad++, plain Notepad). Save files normally. Do not use the GitHub website's editor.

### 2d. Stage, commit, and push

```bash
git status
git add <paths>
git commit -m "Short description of what you changed"
git push -u origin docs/week2-rubric
```

The first push of a new branch prints a "Create a pull request" URL. Click it

### 2e. Open the pull request

On the GitHub page that opens:

- Base: `main`.
- Compare: your branch.
- Title: a clear short summary.
- Description: what changed, why, how you checked it.
- Click "Create pull request".

### 2f. Wait for `Python tests` (about 1 minute)

GitHub runs the `Python tests` check automatically on every PR. The merge button stays disabled until it passes. If it fails, click the failed check, read the log, fix locally, commit, and push again. The PR updates automatically.

### 2g. Merge your own PR

Because you are the repo owner, you can merge without a second reviewer once tests pass.

- Click the green merge dropdown.
- Choose **Squash and merge** (this is the only option enabled by repo settings).
- Confirm.

The branch is auto-deleted on the remote.

### 2h. Update your local main

```bash
git checkout main
git pull
git branch -d docs/week2-rubric
```

## 3. Where to put student materials

Students see everything on `main`. Place files in the folders they own so they show up in the right place when they pull.

- Christina's folder: `papers/christina/`.
  - Reading notes, assigned writing, paper presentations.
  - Christina is expected to edit files inside this folder.
- Floyd's folder: `papers/floyd/`.
  - Same idea for Floyd.
- Shared bibliography (both students): `papers/shared-bibliography/`.
- Weekly experiment work: `experiments/weekXX-<topic>/`.
- Weekly briefs and rubrics you author: `docs/weekly-briefs/`.

For example, to add Christina's Week 2 reading assignment:

```bash
git checkout main
git pull
git checkout -b assignments/christina-week2
# create or edit papers/christina/week2-assignment.md in your editor
git add papers/christina/week2-assignment.md
git commit -m "Add Christina Week 2 reading assignment"
git push -u origin assignments/christina-week2
```

Then open the PR, wait for tests, squash-merge.

## 4. Pitfalls and how to avoid them

### 4a. Do not use the GitHub website's file editor

The pencil icon, "Add file -> Upload files", and "Add file -> Create new file" on github.com all silently create branches named `<your-username>-patch-N`. If you do not finish the PR, these branches pile up and clutter the repo. **Always edit locally.**

If you ever do click one of those buttons by accident, either complete the PR and merge it immediately, or delete the branch from `https://github.com/perrymlab/blindspot-summer-2026/branches`.

### 4b. Do not push directly to `main`

```
git push origin main
```

Will be rejected with `GH006: Protected branch update failed`. This is by design. The only way work reaches `main` is via a PR. Always start with `git checkout -b <branch-name>` after pulling.

### 4c. Do not force-push or reset shared branches

If something goes wrong, stop and ask. Send Brian:

```bash
git status
git --no-pager branch -a
git --no-pager log --oneline -5
```

### 4d. Do not commit large data, datasets, or `.venv`

Already excluded by `.gitignore`, but double check `git status` before staging. If you see large folders listed, do not `git add` them.

## 5. Quick reference card

```bash
# start every change
git checkout main
git pull
git checkout -b <branch-name>

# work happens here in your editor

git status
git add <files>
git commit -m "Short message"
git push -u origin <branch-name>

# open PR on GitHub, wait for tests, Squash and merge

git checkout main
git pull
git branch -d <branch-name>
```

If you keep to this card, the repo stays clean and student work flows in without surprises.
