# Disaster Recovery: rebuilding a researcher GPU box

Cloud GPU instances (vast.ai, etc.) are **ephemeral**. Stopping an instance does
**not** guarantee your data survives -- the container disk is not backed up, and
if the host is reclaimed or goes offline the disk is wiped. Treat every box as
disposable. This repo is built so that everything needed to rebuild a working
BoT-SORT export box lives in git; only re-obtainable artifacts (footage,
weights, exported CSVs) live off-git.

## What is safe vs what is lost

| In git (always recoverable) | Off-git (must re-obtain) |
| --- | --- |
| PRIME patch (`patches/`) | Raw footage (`blindspot_data/`) -- re-sync from Sabrina |
| `scripts/setup_repo.py` (recreates + patches BoT-SORT) | Model weights (`pretrained/`) -- re-download, see `DOWNLOADS.md` |
| `requirements-botsort-py39.txt` (exact pins) | Exported CSVs (`runs/botsort/*.csv`) -- **regenerate** by re-running the demo |
| Runbook + exact demo command | Annotated `track_vis` videos -- regenerate with `--save_result` |

The only true data loss is the exported CSVs/videos, and the documented demo
command regenerates them.

## Fresh-instance recovery checklist

1. Clone the repo. On a cloud GPU box, clone into `/workspace` (the default
   working directory and, if you mounted one, the persistent volume) so the
   paths below and in the runbook line up:
   ```bash
   cd /workspace
   git clone https://github.com/perrymlab/blindspot-summer-2026.git
   cd blindspot-summer-2026
   ```
   The rest of this doc assumes the repo lives at
   `/workspace/blindspot-summer-2026`. On a local machine, any directory works
   -- just adjust the paths accordingly.
2. Create the Python 3.9 env (BoT-SORT/FastReID require 3.9):
   ```bash
   conda create -y -n botsort python=3.9
   conda activate botsort
   python --version   # must say 3.9.x
   # If it still shows 3.12, vast.ai's default `/venv/main` env is shadowing
   # conda on PATH. Leave it first, then re-activate:
   #     deactivate 2>/dev/null; conda activate botsort; which python
   ```
3. Install the pinned PyTorch (a bare `pip install torch` pulls a build with no
   3.9 wheels):
   ```bash
   pip install torch==2.5.1 torchvision==0.20.1 --index-url https://download.pytorch.org/whl/cu121
   ```
4. Install the rest:
   ```bash
   pip install -r requirements-botsort-py39.txt
   ```
5. Recreate and patch BoT-SORT. On the GPU box you only need the BoT-SORT
   checkout (you run BoT-SORT from this 3.9 `botsort` env), so skip the project
   `.venv` -- the project package requires Python >=3.10 and would fail to
   install under 3.9:
   ```bash
   python scripts/setup_repo.py --skip-venv
   ```
   (The project `.venv` and `prime_mtmc` analysis package are only needed for
   the CSV-analysis workflow, which runs on a separate Python 3.10+ interpreter
   -- see `docs/experiments/STUDENT_EMBEDDING_ANALYSIS.md`.)
6. Re-fetch the off-git artifacts:
   - Weights into `vendor/BoT-SORT/pretrained/` (`yolox_x.pth` COCO detector,
     `veri_sbs_R50-ibn.pth` VeRi ReID) -- see `docs/setup/DOWNLOADS.md`.
   - Footage into your data root (`$BLINDSPOT_DATA_ROOT` or `~/blindspot_data`)
     -- re-sync from Sabrina. If the raw captures are in the original
     `video N/Intersection-Camera-K_*.mp4` layout, normalize them to the
     project's `S0N/c00K/vdo.mp4` layout (dry-run first, then `--apply`):
     ```bash
     python scripts/organize_blindspot_data.py            # dry run
     python scripts/organize_blindspot_data.py --apply
     ```
     See `docs/setup/DOWNLOADS.md` and `docs/data/SCENARIO_TRIMMING.md` for the
     layout and trimming details.
7. Confirm readiness:
   ```bash
   python scripts/check_research_readiness.py --detector-weights <...> --reid-weights <...>
   ```
8. Re-run the export and validation per
   `docs/botsort-integration/BOTSORT_GPU_RUNBOOK.md`.

## After every pod stop/restart

Apt packages and `/root` dotfiles do not survive a RunPod restart. One command
puts back tmux, ffmpeg, git-lfs, gh, and the conda shell hookup (and
optionally the reports HTTP server):

```bash
bash scripts/pod_bootstrap.sh           # tools + shell
bash scripts/pod_bootstrap.sh --serve   # also serve reports/ on port 8890
```

## Prevent the next loss

- **Use persistent storage.** Put `blindspot_data/`, `vendor/BoT-SORT/pretrained/`,
  and `runs/` on a mounted persistent volume so they survive stop/destroy.
- **Pull artifacts off the box immediately.** After each run, copy the CSVs and
  any video to your machine or cloud:
  ```bash
  scp -r root@<box-host>:/workspace/blindspot-summer-2026/runs/botsort/ .
  ```
- **Sync exports off the box** (and optionally version them in the repo via Git
  LFS or a Release) -- see `docs/data/SYNCING_RUN_OUTPUTS.md`.
- **Commit run logs, not data.** Record each run's metadata
  (`docs/templates/RUN_LOG_TEMPLATE.md`: command, weights, scenario, epsilon,
  seed, metrics) and commit it. Even if a CSV is lost, the provenance and the
  exact command to regenerate it are not.
- **Never assume "stopped" means "saved."** Verify your data is on persistent
  storage before stopping an instance.
