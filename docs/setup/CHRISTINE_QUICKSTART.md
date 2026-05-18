# Christine Quickstart

One-page setup and daily workflow for the repo. Follow this end to end after a fresh clone. If anything in this guide conflicts with another doc, this one wins for Christine specifically.

Repo: `https://github.com/perrymlab/blindspot-summer-2026`

## 1. One-time setup on a new machine

### 1a. Install prerequisites

- Git for Windows (or git on macOS/Linux).
- Python 3.10 or newer.
- A terminal: Command Prompt or PowerShell on Windows, Terminal on macOS, any shell on Linux.

### 1b. Fresh clone

Pick a folder you want the project under (for example `Documents\`), then:

```bash
git clone https://github.com/perrymlab/blindspot-summer-2026.git
cd blindspot-summer-2026
```

### 1c. Set your git identity for this clone only

This stamps your commits so they show up as you on GitHub, but only for this repo. It does not change git settings on other projects you might have.

```bash
git config user.name "Christine Page"
git config user.email "<your-noreply-email>"
```

For `<your-noreply-email>`:

1. Sign in to GitHub as your student account.
2. Open `https://github.com/settings/emails`.
3. Make sure "Keep my email addresses private" is checked.
4. Copy the line that looks like `12345678+cpage15@users.noreply.github.com`. Paste it above.

Verify:

```bash
git config user.name
git config user.email
```

### 1d. Authenticate once with a Personal Access Token

The first time you push, git will prompt for credentials. Use a Personal Access Token (PAT). Passwords no longer work for git pushes.

1. Go to `https://github.com/settings/tokens` while signed in as your GitHub account.
2. Click "Generate new token" -> "Fine-grained tokens".
3. Name: `blindspot-summer-2026`.
4. Expiration: 90 days.
5. Repository access: "Only select repositories" -> pick `perrymlab/blindspot-summer-2026`.
6. Permissions -> Repository: Contents read/write, Pull requests read/write, Metadata read (default).
7. Click "Generate token". **Copy the token now** - you will not see it again.
8. When git prompts for username, type your GitHub username. When it prompts for password, paste the token.

Windows stores this in Credential Manager and reuses it forever. You will not be prompted again on this machine.

### 1e. Python environment

From the repo root:

```bash
python scripts/setup_repo.py --skip-bot-sort
```

This creates `.venv`, installs the local package, and runs the smoke test.

To activate the environment in future sessions:

- Windows Command Prompt: `.venv\Scripts\activate.bat`
- PowerShell: `.venv\Scripts\Activate.ps1`
- macOS/Linux: `source .venv/bin/activate`

## 2. Daily workflow

Do every change through a branch and a pull request. Never edit files directly on `main`, and never use the "Edit this file" pencil icon on the GitHub website.

### 2a. Pull the latest `main`

```bash
git checkout main
git pull
```

### 2b. Create a branch for your task

Pick a short descriptive name. Use the `student/christina-<topic>` prefix so Sabrina can spot your work easily.

```bash
git checkout -b student/christina-week2-poisoning-notes
```

Other examples:

- `student/christina-week1-reid-summary`
- `student/christina-week3-rubric-draft`
- `student/christina-bibliography-cina-wild-patterns`

### 2c. Edit files in your folder

Your folder is **`papers/christina/`**. Add or edit `.md` files there using any text editor (VS Code, Notepad++, plain Notepad). Save normally.

You may also contribute to:

- `papers/shared-bibliography/` for shared citations.
- Assigned `experiments/weekXX-<topic>/` folders when Sabrina directs you there.

Do not edit files in `src/`, `scripts/`, or `docs/setup/` without checking with Sabrina first.

### 2d. Stage, commit, and push

```bash
git status
git add papers/christina/<your-file>.md
git commit -m "Add Christine week 2 poisoning notes"
git push -u origin student/christina-week2-poisoning-notes
```

The first push of a new branch prints a "Create a pull request" URL.

### 2e. Open the pull request

Click the URL printed by the push, or visit `https://github.com/perrymlab/blindspot-summer-2026/pulls` and click "New pull request".

On the PR creation page:

- Base: `main`.
- Compare: your branch.
- Title: clear short summary (e.g. "Add Week 2 poisoning notes").
- Description: what changed, why, how you checked it.
- Click "Create pull request".

### 2f. Wait for `Python tests` (about 1 minute)

GitHub runs the `Python tests` check automatically on every PR. If it goes green, you are ready for review. If it fails, click the failed check, read the log, fix the file locally, commit, and push again. The PR updates automatically.

### 2g. Wait for Sabrina to review and merge

You **cannot** merge your own PR. Sabrina will review and click **Squash and merge** when ready. If she requests changes, edit the file locally, commit, and push again — the PR updates automatically.

After she merges, the branch is auto-deleted on the remote.

### 2h. Update your local `main`

```bash
git checkout main
git pull
git branch -d student/christina-week2-poisoning-notes
```

## 3. Pitfalls and how to avoid them

### 3a. Do not use the GitHub website's file editor

The pencil icon, "Add file -> Upload files", and "Add file -> Create new file" on github.com all silently create branches named `<your-username>-patch-N`. **Always edit locally** in your clone, then commit and push.

If you accidentally click one of those buttons, close the tab without committing.

### 3b. Do not push directly to `main`

```bash
git push origin main
```

Will be rejected with `GH006: Protected branch update failed`. This is by design. Always work on a `student/christina-<topic>` branch.

### 3c. Do not force-push or reset shared branches

If something goes wrong, stop and ask Sabrina or Brian. Send them:

```bash
git status
git --no-pager branch -a
git --no-pager log --oneline -5
```

### 3d. Do not commit large data, datasets, or `.venv`

Already excluded by `.gitignore`, but double check `git status` before staging. If you see large folders listed, do not `git add` them.

### 3e. Edit your own folder

`papers/christina/` is yours. Floyd has `papers/floyd/`. Do not edit Floyd's files; do not edit `docs/setup/*` or `src/*` without asking.

## 4. Quick reference card

```bash
# start every change
git checkout main
git pull
git checkout -b student/christina-<topic>

# work happens here in your editor — files in papers/christina/

git status
git add papers/christina/<file>.md
git commit -m "Short message"
git push -u origin student/christina-<topic>

# open PR on GitHub, wait for tests, wait for Sabrina to merge

git checkout main
git pull
git branch -d student/christina-<topic>
```

If you keep to this card, your work flows in cleanly and Sabrina can review quickly.
