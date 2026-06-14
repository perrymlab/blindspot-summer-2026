#!/usr/bin/env bash
# One-shot, idempotent RunPod resume for the blindspot research box.
#
# Designed to be the pod's *container start command* so resume is automatic on
# every start with zero manual steps:
#
#     bash /workspace/blindspot-summer-2026/scripts/runpod_resume.sh --serve
#
# It can also be run by hand after a start. Everything here is safe to run
# repeatedly. It assumes the heavy, persistent state already lives on the
# network volume (/workspace): the repo, the miniforge3 conda install, the
# botsort env, model weights, footage, and runs/. Only the ephemeral container
# bits (apt packages, /root dotfiles) are rebuilt.
#
# What it does:
#   1. apt tools: tmux, ffmpeg, git-lfs, gh.
#   2. Hooks the persistent conda into bash (so `conda activate botsort` works
#      in every shell, including tmux panes).
#   3. Verifies the botsort env + key paths are present (warns, never fails).
#   4. (--serve) starts the reports HTTP server on port 8890.
#   5. (unless --no-idle) starts the idle auto-stop watcher to save money.
#
# Flags:
#   --serve       also start the reports/ HTTP server on port 8890
#   --no-idle     do NOT start the idle auto-stop watcher
#   --idle-min N  idle minutes before auto-stop (default 30)
set -uo pipefail   # NOTE: no -e; resume must finish even if a step warns

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONDA_SH=/workspace/miniforge3/etc/profile.d/conda.sh
SERVE=0
START_IDLE=1
IDLE_MIN=30

while [ $# -gt 0 ]; do
    case "$1" in
        --serve) SERVE=1 ;;
        --no-idle) START_IDLE=0 ;;
        --idle-min) shift; IDLE_MIN="${1:-30}" ;;
        *) echo "unknown flag: $1" ;;
    esac
    shift
done

echo "== 1/5 apt tools =="
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq || echo "   WARN: apt-get update failed (offline?)"
apt-get install -y -qq tmux ffmpeg git-lfs >/dev/null 2>&1 || echo "   WARN: apt install failed"
if ! command -v gh >/dev/null 2>&1; then
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
        -o /usr/share/keyrings/githubcli-archive-keyring.gpg 2>/dev/null && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
        > /etc/apt/sources.list.d/github-cli.list && \
    apt-get update -qq && apt-get install -y -qq gh >/dev/null 2>&1 || echo "   WARN: gh install skipped"
fi
echo "   tmux, ffmpeg, git-lfs, gh ready"

echo "== 2/5 conda shell hookup =="
if [ -f "$CONDA_SH" ]; then
    grep -q "miniforge3/etc/profile.d/conda.sh" ~/.bashrc 2>/dev/null || \
        echo "source $CONDA_SH" >> ~/.bashrc
    grep -q "bashrc" ~/.bash_profile 2>/dev/null || \
        echo '[ -f ~/.bashrc ] && . ~/.bashrc' >> ~/.bash_profile
    # auto-cd into the repo for interactive shells
    grep -q "cd $REPO_ROOT" ~/.bashrc 2>/dev/null || \
        echo "cd $REPO_ROOT 2>/dev/null" >> ~/.bashrc
    echo "   conda hooked into .bashrc/.bash_profile"
else
    echo "   WARN: $CONDA_SH not found -- conda env may need rebuilding"
    echo "   (see docs/setup/RECOVERY.md)"
fi

echo "== 3/5 environment sanity =="
# shellcheck disable=SC1090
[ -f "$CONDA_SH" ] && source "$CONDA_SH" 2>/dev/null
if conda env list 2>/dev/null | grep -q "botsort"; then
    echo "   conda env 'botsort' present"
else
    echo "   WARN: conda env 'botsort' missing -- see docs/setup/RECOVERY.md"
fi
for p in "vendor/BoT-SORT/pretrained" "data" "runs"; do
    if [ -e "$REPO_ROOT/$p" ]; then echo "   ok: $p"; else echo "   WARN: missing $p"; fi
done

echo "== 4/5 report server =="
if [ "$SERVE" = "1" ]; then
    mkdir -p "$REPO_ROOT/reports"
    if pgrep -f "http.server 8890" >/dev/null; then
        echo "   already running on port 8890"
    else
        ( cd "$REPO_ROOT/reports" && nohup python3 -m http.server 8890 --bind 0.0.0.0 \
            > /workspace/report_server.log 2>&1 & )
        echo "   serving reports/ on 8890 (expose it in the RunPod console)"
    fi
else
    echo "   skipped (pass --serve to start it)"
fi

echo "== 5/5 idle auto-stop =="
if [ "$START_IDLE" = "1" ]; then
    if pgrep -f "idle_autostop.sh" >/dev/null; then
        echo "   watcher already running"
    elif ! command -v runpodctl >/dev/null 2>&1 && [ -z "${RUNPOD_API_KEY:-}" ]; then
        echo "   SKIP: no runpodctl and no RUNPOD_API_KEY -- cannot auto-stop"
    else
        nohup bash "$REPO_ROOT/scripts/idle_autostop.sh" --idle-min "$IDLE_MIN" \
            > /workspace/idle_autostop.log 2>&1 &
        echo "   watcher started: stops the pod after ${IDLE_MIN} idle min (log: /workspace/idle_autostop.log)"
    fi
else
    echo "   skipped (--no-idle)"
fi

echo
echo "Resume complete. New shells will auto-activate conda; otherwise:"
echo "  source $CONDA_SH && conda activate botsort"
