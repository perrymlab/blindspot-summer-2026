# Daily Git Workflow

> Pull before you start. Push before you close your laptop.

---

## Opening Your Terminal

Every git command runs in the terminal. Open it before anything else.

- **Mac:** press `Command + Space`, type `Terminal`, hit Enter
- **Windows:** press the Windows key, type `cmd` or `PowerShell`, hit Enter

---

## First Time Only

Do these steps once on a new machine. Skip anything you already have.

**Install Git**

Verify with `git --version`. If not installed:
- Mac: running `git --version` will offer to install it automatically
- Windows: download from git-scm.com/download/win

**Install Python 3.10 or newer**

Verify with `python3 --version`. If not installed, download from python.org/downloads.

**Install ffmpeg**

Verify with `ffmpeg -version`. If not installed:
- Mac: `brew install ffmpeg`

**Clone the repo**

```bash
git clone https://github.com/perrymlab/blindspot-summer-2026
cd blindspot-summer-2026
python scripts/setup_repo.py
```



## Every Session — Four Steps

**Step 1 — Pull**

Always start here:

```bash
git checkout main
git pull
```

**Step 2 — Create or return to your branch**

Never work on main. Create a new branch for each piece of work:

```bash
git checkout -b student/yourname-short-topic
```

Returning to a branch you already created:

```bash
git checkout student/yourname-short-topic
```

**Step 3 — Work, then commit**

```bash
git status
git add .
git commit -m "describe what you changed"
git push -u origin student/yourname-short-topic
```

---

> Pull → Branch → Commit → Push. Every session, every time.

---

## Practice — Day 1 Reflection

Try the full workflow right now:

1. Pull the latest changes
2. Create your branch:
   ```bash
   git checkout -b student/yourname-day1-reflection
   ```
3. Write one paragraph about your first session — what did you set up, what felt unclear, what are you curious about
4. Save it to your folder:
   - Christine → `papers/christina/day1-reflection.md`
   - Floyd → `papers/floyd/day1-reflection.md`
5. Commit and push:
   ```bash
   git add .
   git commit -m "add day 1 reflection"
   git push -u origin student/yourname-day1-reflection
   ```
6. Open a pull request into main on GitHub

You are done when your reflection file is visible in your pull request.

---

