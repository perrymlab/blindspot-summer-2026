# Daily Git Workflow
---

> **Run this every session:** Before you write a single line, pull. Before you close your laptop, push.

---

## Step 0 — Open Your Terminal

Every git command runs in the terminal. Open it before anything else.

- **Mac:** press `Command + Space`, type `Terminal`, hit Enter.
- **Windows:** press the Windows key, type `cmd` or `PowerShell`, hit Enter.

---

## First Time Only — Clone the Repo

Do this once to get the repository on your machine. You won't need to do this again.

```bash
git clone https://github.com/perrymlab/blindspot-summer-2026
cd blindspot-summer-2026
python scripts/setup_repo.py
```

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
   Christina →  papers/christina/day1-reflection.md
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