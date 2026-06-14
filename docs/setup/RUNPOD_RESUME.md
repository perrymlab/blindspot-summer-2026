# RunPod: stop anytime, resume with no manual setup

Goal: stop the pod whenever you're not using it (so you're not paying for an
idle GPU) and have it come back automatically, with no multi-step setup each
time. This works because everything heavy lives on the **network volume**
(`/workspace`), which survives stop *and* terminate; only the container disk
(apt packages, `/root` dotfiles) is wiped, and the resume script rebuilds that.

## One-time setup

### 1. Keep all persistent state on `/workspace`

The network volume must hold: the repo clone, the conda install
(`/workspace/miniforge3`) and the `botsort` env, model weights
(`vendor/BoT-SORT/pretrained/`), footage, and `runs/`. If your repo isn't under
`/workspace`, move it there (see `docs/setup/RECOVERY.md` for a from-scratch
rebuild). `scripts/prestop_check.sh` will warn you if anything important is off
the volume.

### 2. Add two environment variables to the pod template

In the RunPod template (Edit Template -> Environment Variables):

- `RUNPOD_API_KEY` = your key from Account -> Settings -> API Keys (enables
  idle auto-stop and `runpod_stop.sh`).
- `RUNPOD_POD_ID` is set automatically by most RunPod images; if yours doesn't,
  add it.

### 3. Set the resume script as the container start command

In the template's **Container Start Command** (or Docker Command), put:

```bash
bash -lc 'bash /workspace/blindspot-summer-2026/scripts/runpod_resume.sh --serve'
```

That's the whole trick: every time the pod starts, RunPod runs this, which
restores tools, hooks conda into your shell, optionally serves `reports/`, and
starts the idle watcher. Adjust the path if your repo lives elsewhere on
`/workspace`.

## Daily use

**Start it again** (after a manual or idle stop) — pick one:

- **RunPod console:** the pod shows as Stopped; click **Start/Resume**.
- **CLI:** `runpodctl start pod <pod-id>`.
- **From your laptop:** `bash scripts/runpod_start.sh` (needs `RUNPOD_API_KEY`
  and `RUNPOD_POD_ID` in your *local* shell, since the pod is off).

However you start it, the container start command runs `runpod_resume.sh`
automatically — open a terminal and conda is already active, in the repo
directory. Nothing else to do.

Caveat: a stopped GPU pod can occasionally fail to resume if no GPU of that
type is free in the region right then. Retry shortly, or create a fresh pod
from the template attached to the volume — the start command self-configures it
identically.

**Stop (manual, safe):**

```bash
bash scripts/runpod_stop.sh        # runs a pre-stop check, asks to confirm, stops
bash scripts/runpod_stop.sh --force  # skip checks/prompt
```

**Stop (automatic):** the idle watcher started by resume stops the pod after 30
idle minutes (no GPU load, no heavy job, no attached tmux/SSH). Tune it:

```bash
# inside the start command, change the resume flags:
runpod_resume.sh --serve --idle-min 45     # wait 45 min
runpod_resume.sh --serve --no-idle         # disable auto-stop
```

The watcher logs to `/workspace/idle_autostop.log`.

## What each script does

| Script | Role |
|--------|------|
| `scripts/runpod_resume.sh` | Idempotent resume; wire as the start command. apt tools, conda hookup, sanity check, optional report server, starts idle watcher. |
| `scripts/idle_autostop.sh` | Background watcher; stops the pod after sustained idle. Needs `RUNPOD_API_KEY`. |
| `scripts/runpod_stop.sh` | Manual safe stop (pre-stop check + confirm). |
| `scripts/prestop_check.sh` | Read-only check: repo on `/workspace`? uncommitted/unpushed git? job running? |

## Stop vs terminate (cost)

- **Stop**: GPU billing ends; you keep the same pod and a small charge for its
  stopped container disk + the volume. Fastest resume. The idle watcher and
  `runpod_stop.sh` do this.
- **Terminate**: pod destroyed, you pay only for the network volume. Cheapest.
  To resume, create a new pod from the template attached to the volume — the
  start command makes it self-configure, same as a stop/start.

## Recovery

If the conda env or weights are ever missing (e.g. the volume was recreated),
`runpod_resume.sh` warns and points you to `docs/setup/RECOVERY.md`, which has
the full from-scratch rebuild.
