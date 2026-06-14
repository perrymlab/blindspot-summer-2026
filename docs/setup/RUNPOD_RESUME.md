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
rebuild). `scripts/prestop_check.sh` warns you if anything important is off the
volume.

### 2. API key — only needed on your laptop

Good news: every RunPod pod ships with `runpodctl` already installed and
configured with a **pod-scoped key**, so stopping the pod from the pod itself
(idle auto-stop and `runpod_stop.sh`) needs **no key setup at all**.

You only need an API key on **your laptop**, for `runpod_start.sh` (the pod is
off, so it can't use its own runpodctl). On the laptop run once:
`runpodctl config --apiKey=<key>` (or set `RUNPOD_API_KEY`). `RUNPOD_POD_ID` is
set automatically on the pod; pass `--pod-id` to the start script from the
laptop.

### 3. Set the resume script as the container start command

In the template's **Container Start Command** (or Docker Command), put:

    bash -lc 'bash /workspace/blindspot-summer-2026/scripts/runpod_resume.sh --serve'

Every time the pod starts, RunPod runs this, which restores tools, hooks conda
into your shell, optionally serves `reports/`, and starts the idle watcher.
Adjust the path if your repo lives elsewhere on `/workspace`.

## Daily use

**Start it again** (after a manual or idle stop) — pick one:

- **RunPod console:** the pod shows as Stopped; click **Start/Resume**.
- **CLI:** `runpodctl start pod <pod-id>`.
- **From your laptop:** `bash scripts/runpod_start.sh` (needs `RUNPOD_API_KEY`
  and `RUNPOD_POD_ID` in your *local* shell, since the pod is off).

However you start it, the container start command runs `runpod_resume.sh`
automatically — open a terminal and conda is already active, in the repo
directory. Nothing else to do.

Caveat: a stopped GPU pod can occasionally fail to resume if no GPU of that type
is free in the region right then. Retry shortly, or create a fresh pod from the
template attached to the volume — the start command self-configures it.

**Stop (manual, safe):**

    bash scripts/runpod_stop.sh          # pre-stop check, confirm, then stop
    bash scripts/runpod_stop.sh --force  # skip checks/prompt

**Stop (automatic):** the idle watcher is **disabled by default for now**. Pass
`--idle` to `runpod_resume.sh` to opt in; once enabled it stops the pod after 30
idle minutes (no GPU load, no heavy job, no attached tmux/SSH). Tune it with
`--idle-min 45` to wait longer. The watcher logs to `/workspace/idle_autostop.log`.

**Keep it awake when you need to:** while the keep-alive file exists, the watcher
never stops the pod (no matter how idle it looks).

    touch /workspace/.keepalive   # pin the pod awake (long think/edit session)
    rm    /workspace/.keepalive   # re-arm auto-stop

## What each script does

| Script | Role |
|--------|------|
| `scripts/runpod_resume.sh` | Idempotent resume; wire as the start command. apt tools, conda hookup, sanity check, optional report server, optional idle watcher (off unless `--idle`). |
| `scripts/idle_autostop.sh` | Background watcher; stops the pod after sustained idle. Off by default (opt in with `runpod_resume.sh --idle`). Needs `RUNPOD_API_KEY`. Honors `/workspace/.keepalive`. |
| `scripts/runpod_start.sh` | Start/resume a stopped pod from your laptop. |
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
