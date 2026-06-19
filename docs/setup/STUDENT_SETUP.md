# Daily Git Workflow
---

> **Run this every session:** Before you write a single line, pull. Before you close your laptop, push.

---

## Step 0 — Open Your Terminal

Every git command runs in the terminal. Open it before anything else.

- **Mac:** press `Command + Space`, type `Terminal`, hit Enter.
- **Windows:** press the Windows key, type `cmd` or `PowerShell`, hit Enter.

---

## First Time Only — Install Prerequisites

These are one-time installs on a new machine. Skip any you already have.

- **Git** — required to clone and push. Verify with `git --version`.
  - Windows: install Git for Windows from `https://git-scm.com/download/win`.
  - macOS: `git --version` will offer to install Xcode Command Line Tools.
  - Linux: `sudo apt install git` (or distro equivalent).
- **Python 3.10 or newer** — required to run the project. Verify with
  `python --version` (Windows) or `python3 --version` (macOS/Linux).
  - Windows: install from `https://www.python.org/downloads/` and tick
    *Add Python to PATH* during install.
  - macOS/Linux: usually already present; otherwise install from your
    package manager or `https://www.python.org/downloads/`.
- **ffmpeg** — required for the scenario trim and quicklook scripts. Verify
  with `ffmpeg -version`.
  - Windows: `winget install --id=Gyan.FFmpeg -e`, then open a new terminal.
  - macOS: `brew install ffmpeg`.
  - Linux: `sudo apt install ffmpeg`.

---

## First Time Only — Clone the Repo

Do this once to get the repository on your machine. You won't need to do this again.

```bash
git clone https://github.com/perrymlab/blindspot-summer-2026
cd blindspot-summer-2026
python scripts/setup_repo.py
```

---

## First Time Only — Set Up GitHub Credentials

Cloning a public repo does not need credentials, but the first `git push` you
run will. Set this up before you start writing code so it does not surprise
you mid-task.

### Stamp your commits as you

So your work shows up under your GitHub account on the PR page. Run these
inside the cloned repo (they apply to this repo only, not your other
projects):

```bash
git config user.name "Your Name"
git config user.email "<your-noreply-email>"
```

For `<your-noreply-email>`:

1. Sign in to `https://github.com/settings/emails` as your GitHub account.
2. Tick **Keep my email addresses private**.
3. Copy the line that looks like
   `12345678+yourusername@users.noreply.github.com` and paste it as the
   value above.

Verify:

```bash
git config user.name
git config user.email
```

### Authenticate the first push

When `git push` asks for credentials the first time, use a **Personal Access
Token (PAT)**. Do **not** paste your GitHub password — GitHub disabled
password authentication for git operations.

1. Go to `https://github.com/settings/tokens` signed in as the same account.
2. Click **Generate new token** -> **Fine-grained tokens**.
3. Name: `blindspot-summer-2026`.
4. Expiration: 90 days.
5. Repository access: **Only select repositories** -> pick
   `perrymlab/blindspot-summer-2026`.
6. Permissions -> Repository: **Contents: Read and write** and
   **Pull requests: Read and write**. Leave the rest at their defaults.
7. Click **Generate token** and copy the token immediately. You cannot view
   it again after closing the page.
8. When git prompts for **username**, type your GitHub username. When it
   prompts for **password**, paste the token.

Your OS credential manager (Windows Credential Manager, macOS Keychain,
Linux keyring) saves the token after the first successful push, so you will
not be prompted again on this machine for this repo.

If credentials misbehave, ask Dr. Perry before retrying. **Never** paste the
token into commits, chat messages, or files in this repo.

---

> **Run this every session:** Before you write a single line, pull. Before you close your laptop, push.

---

## Step 1 — Pull the Latest Changes

Always start here. This keeps your local copy in sync with the team.

```bash
git checkout main
git pull
```

---

## Step 2 — Create or Return to Your Branch

Never work on main. Start a new branch for each piece of work, or check out your existing one if you're continuing.

Starting something new:
```bash
git checkout -b student/<your-name>-<short-topic>
```

Returning to existing work:
```bash
git checkout student/<your-name>-<short-topic>
```

---

## Step 3 — Do Your Work, Then Commit

Check what changed, stage everything, and commit with a clear message.

```bash
git status
git diff
git add .
git commit -m "Describe the change"
git push -u origin student/<your-name>-<short-topic>
```

---

## Step 4 — Open a Pull Request When Ready

When your work is ready for review, open a pull request into `main` on GitHub.

---

> **Quick rule:** Pull → Branch → Commit → Push. Every session, every time.

---

## Practice Exercise — Day 1 Reflection

Put the whole workflow into practice right now. Follow these steps:

1. Open your terminal and pull the latest changes (Step 1).

2. Create your branch (Step 2):
   ```bash
   git checkout -b student/<your-name>-day1-reflection
   ```

3. Open a text editor and write one paragraph reflecting on your first session. Some things to consider:
   - What did you set up today?
   - What felt confusing or unclear?
   - What are you curious about going into Week 1?

4. Save the file to your folder:
   ```
   Christine →  papers/christina/day1-reflection.md
   Floyd     →  papers/floyd/day1-reflection.md
   ```

5. Stage, commit, and push (Step 3):
   ```bash
   git add .
   git commit -m "Add day 1 reflection"
   git push -u origin student/<your-name>-day1-reflection
   ```

6. Open a pull request into `main` on GitHub (Step 4).

> **You're done when:** Your reflection file is visible in your pull request on GitHub.