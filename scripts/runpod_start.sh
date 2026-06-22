#!/usr/bin/env bash
# Start (resume) a stopped RunPod pod from your LOCAL machine.
# The pod's container start command then runs runpod_resume.sh automatically.
#
# On your laptop, configure runpodctl once:  runpodctl config --apiKey=<key>
# (or set RUNPOD_API_KEY for the GraphQL fallback). RUNPOD_POD_ID or --pod-id
# selects which pod.
#
#   bash scripts/runpod_start.sh                 # start $RUNPOD_POD_ID
#   bash scripts/runpod_start.sh --pod-id abc123
#   bash scripts/runpod_start.sh --gpu-count 2   # request 2 GPUs (graphql path)
set -uo pipefail
POD_ID="${RUNPOD_POD_ID:-}"
GPU_COUNT=1
while [ $# -gt 0 ]; do
    case "$1" in
        --pod-id) shift; POD_ID="${1:-}" ;;
        --gpu-count) shift; GPU_COUNT="${1:-1}" ;;
        *) echo "unknown flag: $1" ;;
    esac
    shift
done
[ -n "$POD_ID" ] || { echo "set RUNPOD_POD_ID or pass --pod-id"; exit 1; }

if command -v runpodctl >/dev/null 2>&1; then
    runpodctl pod start "$POD_ID" 2>/dev/null && exit 0
    runpodctl start pod "$POD_ID" && exit 0
fi
API_KEY="${RUNPOD_API_KEY:-}"
[ -n "$API_KEY" ] || { echo "No runpodctl and no RUNPOD_API_KEY -- start from the RunPod console."; exit 1; }
echo "Resuming pod $POD_ID (gpuCount=$GPU_COUNT)..."
curl -s --max-time 30 "https://api.runpod.io/graphql?api_key=${API_KEY}" \
    -H 'Content-Type: application/json' \
    -d "{\"query\":\"mutation { podResume(input: {podId: \\\"${POD_ID}\\\", gpuCount: ${GPU_COUNT}}) { id desiredStatus } }\"}"
echo
echo "If that errors about GPU availability, the GPU type is temporarily full --"
echo "retry shortly or create a fresh pod from the template attached to the volume."
