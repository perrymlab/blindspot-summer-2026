#!/usr/bin/env bash
# Restore the GPU pod's working environment after a stop/restart.
#
# RunPod containers reset everything outside /workspace on restart: apt
# packages, /root dotfiles, and shell config all vanish. This script puts
# back everything the research workflow needs in one shot:
#
#     bash scripts/pod_bootstrap.sh                # tools + shell hookup
#     bash scripts/pod_bootstrap.sh --serve        # also start the report server
#
# What it does:
#   1. apt tools: tmux, ffmpeg, git-lfs, gh (GitHub CLI).
#   2. Hooks the persistent conda (miniforge3 on /workspace) into bash so
#      `conda activate botsort` works in every shell, including tmux panes.
#   3. (--serve) starts a directory-listing HTTP server on port 8890
#      (8888 is taken by RunPod's bundled JupyterLab) serving
#      ONLY the reports/ folder. Expose port 8890 in the RunPod console to
#      share https://<pod-id>-8890.proxy.runpod.net with the team.
#
# SECURITY: the server has no authentication -- share the URL with the team
# only. It deliberately serves reports/ alone; NEVER serve the repo root
# (.git/config contains the GitHub token).
#
# Not handled here (persisted on /workspace already): conda env, repo clone,
# weights in vendor/BoT-SORT/pretrained/, footage, runs/, reports/.
# Re-check with: python scripts/check_research_readiness.py
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONDA_SH=/workspace/miniforge3/etc/profile.d/conda.sh

echo "== 1/3 apt tools =="
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq tmux ffmpeg git-lfs >/dev/null
if ! command -v gh >/dev/null 2>&1; then
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
        -o /usr/share/keyrings/githubcli-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
        > /etc/apt/sources.list.d/github-cli.list
    apt-get update -qq && apt-get install -y -qq gh >/dev/null
fi
echo "   tmux, ffmpeg, git-lfs, gh installed"

echo "== 2/3 conda shell hookup =="
if [ -f "$CONDA_SH" ]; then
    grep -q "miniforge3/etc/profile.d/conda.sh" ~/.bashrc 2>/dev/null || \
        echo "source $CONDA_SH" >> ~/.bashrc
    grep -q "bashrc" ~/.bash_profile 2>/dev/null || \
        echo '[ -f ~/.bashrc ] && . ~/.bashrc' >> ~/.bash_profile
    echo "   conda hooked into .bashrc/.bash_profile (open a new shell or: source $CONDA_SH)"
else
    echo "   WARNING: $CONDA_SH not found -- conda env may need rebuilding"
    echo "   (see docs/botsort-integration/BOTSORT_GPU_RUNBOOK.md steps 2-4)"
fi

echo "== 3/3 report server =="
if [ "${1:-}" = "--serve" ]; then
    mkdir -p "$REPO_ROOT/reports"
    if pgrep -f "http.server 8890" >/dev/null; then
        echo "   already running on port 8890"
    else
        cd "$REPO_ROOT/reports"
        nohup python3 -m http.server 8890 --bind 0.0.0.0 \
            > /workspace/report_server.log 2>&1 &
        echo "   serving $REPO_ROOT/reports on port 8890 (pid $!)"
        echo "   expose port 8890 in the RunPod console, then share:"
        echo "   https://<pod-id>-8890.proxy.runpod.net"
    fi
else
    echo "   skipped (pass --serve to start it)"
fi

echo
echo "Done. Quick sanity check:"
echo "  source $CONDA_SH && conda activate botsort && python --version   # 3.9.x"
