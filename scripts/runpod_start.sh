#!/usr/bin/env bash
# Start (resume) a stopped RunPod pod from your LOCAL machine.
# The pod's container start command then runs runpod_resume.sh automatically,
# so there's no setup once it boots.
#
# Needs (in your local shell, NOT on the pod -- the pod is off):
#   RUNPOD_API_KEY   your RunPod API key
#   RUNPOD_POD_ID    the pod id to start (or pass --pod-id)
#
# Usage:
#   bash scripts/runpod_start.sh                 # start $RUNPOD_POD_ID
#   bash scripts/runpod_start.sh --pod-id abc123 # start a specific pod
#   bash scripts/runpod_start.sh --gpu-count 2   # request 2 GPUs on resume
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

API_KEY="${RUNPOD_API_KEY:-}"
if [ -z "$POD_ID" ]; then echo "set RUNPOD_POD_ID or pass --pod-id"; exit 1; fi

if command -v runpodctl >/dev/null 2>&1; then
    runpodctl start pod "$POD_ID" && exit 0
fi

if [ -z "$API_KEY" ]; then
    echo "No runpodctl and no RUNPOD_API_KEY -- start the pod from the RunPod console."
    exit 1
fi

echo "Resuming pod $POD_ID (gpuCount=$GPU_COUNT)..."
curl -s --max-time 30 "https://api.runpod.io/graphql?api_key=${API_KEY}" \
    -H 'Content-Type: application/json' \
    -d "{\"query\":\"mutation { podResume(input: {podId: \\\"${POD_ID}\\\", gpuCount: ${GPU_COUNT}}) { id desiredStatus } }\"}"
echo
echo "If that returned an error about GPU availability, the GPU type is"
echo "temporarily unavailable -- retry shortly or create a fresh pod from the"
echo "template attached to the volume (start command self-configures it)."
