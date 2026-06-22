#!/usr/bin/env bash
# Safe manual stop: run a pre-stop check, then stop the pod.
# Uses runpodctl (preinstalled on the pod, pod-scoped key) -> no API key needed
# on the pod. Network volume persists; runpod_resume.sh restores on next start.
#   bash scripts/runpod_stop.sh          # check, confirm, then stop
#   bash scripts/runpod_stop.sh --force  # skip the confirmation prompt
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FORCE=0
[ "${1:-}" = "--force" ] && FORCE=1

bash "$REPO_ROOT/scripts/prestop_check.sh"; rc=$?
if [ "$rc" -ne 0 ] && [ "$FORCE" -ne 1 ]; then
    echo; echo "Pre-stop check raised warnings above. Re-run with --force to stop anyway."
    exit 1
fi
if [ "$FORCE" -ne 1 ]; then
    read -r -p "Stop the pod now? [y/N] " ans
    case "$ans" in y|Y|yes|YES) ;; *) echo "aborted"; exit 1 ;; esac
fi

POD_ID="${RUNPOD_POD_ID:-$(hostname)}"
API_KEY="${RUNPOD_API_KEY:-}"
if command -v runpodctl >/dev/null 2>&1; then
    runpodctl pod stop "$POD_ID" 2>/dev/null && exit 0
    runpodctl stop pod "$POD_ID" && exit 0
fi
if [ -n "$API_KEY" ]; then
    curl -s --max-time 30 "https://api.runpod.io/graphql?api_key=${API_KEY}" \
        -H 'Content-Type: application/json' \
        -d "{\"query\":\"mutation { podStop(input: {podId: \\\"${POD_ID}\\\"}) { id desiredStatus } }\"}"; echo
else
    echo "No runpodctl and no RUNPOD_API_KEY -- stop the pod from the RunPod console."; exit 1
fi
