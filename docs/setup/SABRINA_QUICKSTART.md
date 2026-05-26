# Perry — QuickStart

Repo: `https://github.com/perrymlab/blindspot-summer-2026`

---

## 1 · One-time setup

1. Install Git, Python 3.10+, and ffmpeg
   - Windows: `winget install Gyan.FFmpeg`
   - Mac: `brew install ffmpeg`

2. Clone the repo
   ```bash
   git clone https://github.com/perrymlab/blindspot-summer-2026.git
   cd blindspot-summer-2026
   ```

3. Set your identity (this repo only)
   ```bash
   git config user.name "Sabrina Perry"
   git config user.email "your-noreply@users.noreply.github.com"
   ```
   Get your noreply email from `https://github.com/settings/emails`.

4. Create the Python environment
   ```bash
   python scripts/setup_repo.py --skip-bot-sort
   ```

5. Activate the environment every session
   - Mac/Linux: `source .venv/bin/activate`

---

## 2 · Daily workflow

```bash
# 1. Start fresh
git checkout main
git pull

# 2. Create a branch
git checkout -b docs/week2-rubric
# Naming: docs/ · assignments/ · fix/

# 3. Edit files locally in your editor

# 4. Stage, commit, push
git add .
git commit -m "Short description"
git push -u origin <branch-name>
```

5. Open a PR on GitHub — base: `main` — wait for **Python tests** to pass
6. Merge using **Squash and merge** only

```bash
# 7. Clean up
git checkout main 
git pull
git branch -d <branch-name>
git fetch --prune
```

---

## 3 · Where files go

| Folder | Contents |
|---|---|
| `papers/christina/` | Christine's reading notes, assignments, presentations |
| `papers/floyd/` | Floyd's reading notes, assignments, presentations |
| `papers/shared-bibliography/` | Bibliography for both students |
| `experiments/weekXX-topic/` | Weekly experiment work |
| `docs/weekly-briefs/` | Briefs and rubrics you author |

---

## 4 · Never do these

- **Don't use the GitHub pencil/editor** — it creates messy `patch-N` branches
- **Don't push directly to `main`** — it will be rejected
- **Don't commit `.venv`, datasets, or large files** — check `git status` before staging
- **Don't force-push or reset shared branches** — 
