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
# Override: while the keep-alive file exists (default /workspace/.keepalive),
# the pod is never stopped, regardless of idle state.
#   touch /workspace/.keepalive   # pin the pod awake
#   rm    /workspace/.keepalive   # re-arm auto-stop
#
# Stopping: prefers runpodctl, which every RunPod pod ships with, already
# configured with a pod-scoped key -- so on the pod NO api key is needed.
# Falls back to the GraphQL API (needs RUNPOD_API_KEY) only if runpodctl is
# absent. RUNPOD_POD_ID is set automatically on most images.
set -uo pipefail

IDLE_MIN=30
GPU_THRESHOLD=5
POLL_SECONDS=60
KEEPALIVE_FILE="/workspace/.keepalive"

while [ $# -gt 0 ]; do
    case "$1" in
        --idle-min) shift; IDLE_MIN="${1:-30}" ;;
        --gpu-threshold) shift; GPU_THRESHOLD="${1:-5}" ;;
        --poll-seconds) shift; POLL_SECONDS="${1:-60}" ;;
        --keepalive-file) shift; KEEPALIVE_FILE="${1:-/workspace/.keepalive}" ;;
        *) echo "unknown flag: $1" ;;
    esac
    shift
done

POD_ID="${RUNPOD_POD_ID:-$(hostname)}"
API_KEY="${RUNPOD_API_KEY:-}"

if ! command -v runpodctl >/dev/null 2>&1 && [ -z "$API_KEY" ]; then
    echo "idle_autostop: need runpodctl (preinstalled on the pod) or RUNPOD_API_KEY; refusing to run."
    exit 1
fi

log() { echo "$(date -u +%FT%TZ) idle_autostop: $*"; }

gpu_busy() {
    command -v nvidia-smi >/dev/null 2>&1 || return 1
    local util
    util=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits 2>/dev/null \
           | tr -d ' ' | sort -nr | head -1)
    [ -n "$util" ] && [ "$util" -ge "$GPU_THRESHOLD" ]
}

worker_busy() {
    pgrep -f "run_baselines.py|make_progress_report.py|trim_scenarios.py|ffmpeg|tools/demo.py|train" >/dev/null 2>&1
}

session_active() {
    if command -v tmux >/dev/null 2>&1 && tmux list-clients >/dev/null 2>&1; then
        [ -n "$(tmux list-clients 2>/dev/null)" ] && return 0
    fi
    who 2>/dev/null | grep -q . && return 0
    return 1
}

stop_pod() {
    log "idle for ${IDLE_MIN} min -> stopping pod $POD_ID"
    if command -v runpodctl >/dev/null 2>&1; then
        runpodctl pod stop "$POD_ID" 2>/dev/null && return 0   # modern syntax
        runpodctl stop pod "$POD_ID" && return 0               # legacy fallback
    fi
    [ -n "$API_KEY" ] || { log "no runpodctl and no API key; cannot stop"; return 1; }
    curl -s --max-time 30 "https://api.runpod.io/graphql?api_key=${API_KEY}" \
        -H 'Content-Type: application/json' \
        -d "{\"query\":\"mutation { podStop(input: {podId: \\\"${POD_ID}\\\"}) { id desiredStatus } }\"}" \
        && log "stop request sent (graphql)"
}

log "watching pod=$POD_ID idle_min=$IDLE_MIN gpu_threshold=${GPU_THRESHOLD}% poll=${POLL_SECONDS}s keepalive=$KEEPALIVE_FILE"
idle_count=0
needed=$(( IDLE_MIN * 60 / POLL_SECONDS ))
[ "$needed" -lt 1 ] && needed=1

while true; do
    if [ -f "$KEEPALIVE_FILE" ]; then
        if [ "$idle_count" -ne 0 ]; then log "keepalive present; idle timer reset"; fi
        idle_count=0
    elif gpu_busy || worker_busy || session_active; then
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
