#!/usr/bin/env bash
# Bring the GPU pod's repo checkout current and verify the env, in one command.
#
#     bash scripts/sync_pod.sh
#
# Idempotent and safe to run repeatedly. It will NOT clobber local work: if the
# working tree is dirty it stops and shows `git status` instead of pulling, so
# uncommitted runs/exports are never lost. Run it from anywhere in the repo.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
CONDA_SH=/workspace/miniforge3/etc/profile.d/conda.sh

# The readiness check needs the research stack (pandas, py3.9) -> botsort env.
if [ -f "$CONDA_SH" ]; then
    # shellcheck disable=SC1090
    source "$CONDA_SH"
    conda activate botsort 2>/dev/null || echo "WARN: could not activate 'botsort' env"
fi

echo "== git sync =="
git fetch origin
if [ -n "$(git status --porcelain)" ]; then
    echo
    echo "Working tree is DIRTY -- refusing to pull so nothing is lost."
    echo "Commit or stash first, then re-run. Current state:"
    git status --short
    exit 1
fi

behind="$(git rev-list --count HEAD..origin/main 2>/dev/null || echo '?')"
echo "  $behind commit(s) behind origin/main"
git pull --ff-only origin main
git log -1 --format='  now at %h %ci %s'

echo
echo "== readiness check =="
python scripts/check_research_readiness.py
