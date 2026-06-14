#!/usr/bin/env bash
# Idle auto-stop watcher for a RunPod pod. Stops the pod (GPU billing ends)
# after a sustained idle period, so you stop paying even if you forget to shut
# down. The network volume persists, so runpod_resume.sh brings everything back
# on the next start.
#
# Idle = ALL of:
#   - GPU utilization below --gpu-threshold (default 5%)
#   - no heavy worker process running (python / ffmpeg / botsort)
#   - no attached tmux session and no interactive SSH login
# for --idle-min consecutive minutes (checked once a minute).
#
# Requires (set as pod environment variables in the RunPod template):
#   RUNPOD_API_KEY   your RunPod API key (Account -> Settings -> API Keys)
#   RUNPOD_POD_ID    the pod id; RunPod sets this automatically in most images.
#                    If absent, the script tries the $RUNPOD_POD_ID file/host.
#
# Usage:
#   bash scripts/idle_autostop.sh --idle-min 30 --gpu-threshold 5
set -uo pipefail

IDLE_MIN=30
GPU_THRESHOLD=5
POLL_SECONDS=60

while [ $# -gt 0 ]; do
    case "$1" in
        --idle-min) shift; IDLE_MIN="${1:-30}" ;;
        --gpu-threshold) shift; GPU_THRESHOLD="${1:-5}" ;;
        --poll-seconds) shift; POLL_SECONDS="${1:-60}" ;;
        *) echo "unknown flag: $1" ;;
    esac
    shift
done

POD_ID="${RUNPOD_POD_ID:-$(hostname)}"
API_KEY="${RUNPOD_API_KEY:-}"

if [ -z "$API_KEY" ]; then
    echo "idle_autostop: RUNPOD_API_KEY not set; refusing to run (cannot stop the pod safely)."
    exit 1
fi

log() { echo "$(date -u +%FT%TZ) idle_autostop: $*"; }

gpu_busy() {
    command -v nvidia-smi >/dev/null 2>&1 || return 1   # no GPU -> treat as not busy
    local util
    util=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits 2>/dev/null \
           | tr -d ' ' | sort -nr | head -1)
    [ -n "$util" ] && [ "$util" -ge "$GPU_THRESHOLD" ]
}

worker_busy() {
    # heavy jobs we never want to interrupt
    pgrep -f "run_baselines.py|make_progress_report.py|trim_scenarios.py|ffmpeg|tools/demo.py|train" >/dev/null 2>&1
}

session_active() {
    # attached tmux session?
    if command -v tmux >/dev/null 2>&1 && tmux list-clients >/dev/null 2>&1; then
        [ -n "$(tmux list-clients 2>/dev/null)" ] && return 0
    fi
    # interactive ssh login?
    who 2>/dev/null | grep -q . && return 0
    return 1
}

stop_pod() {
    log "idle for ${IDLE_MIN} min -> stopping pod $POD_ID"
    # Prefer runpodctl if present, else GraphQL API.
    if command -v runpodctl >/dev/null 2>&1; then
        runpodctl stop pod "$POD_ID" && return 0
    fi
    curl -s --max-time 30 "https://api.runpod.io/graphql?api_key=${API_KEY}" \
        -H 'Content-Type: application/json' \
        -d "{\"query\":\"mutation { podStop(input: {podId: \\\"${POD_ID}\\\"}) { id desiredStatus } }\"}" \
        && log "stop request sent"
}

log "watching pod=$POD_ID idle_min=$IDLE_MIN gpu_threshold=${GPU_THRESHOLD}% poll=${POLL_SECONDS}s"
idle_count=0
needed=$(( IDLE_MIN * 60 / POLL_SECONDS ))
[ "$needed" -lt 1 ] && needed=1

while true; do
    if gpu_busy || worker_busy || session_active; then
        if [ "$idle_count" -ne 0 ]; then log "activity detected; idle timer reset"; fi
        idle_count=0
    else
        idle_count=$(( idle_count + 1 ))
        log "idle tick $idle_count/$needed"
        if [ "$idle_count" -ge "$needed" ]; then
            stop_pod
            exit 0
        fi
    fi
    sleep "$POLL_SECONDS"
done
