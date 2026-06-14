#!/usr/bin/env bash
# Pre-stop safety check: confirm nothing important is only on the ephemeral
# container disk before you stop/terminate the pod. Exits non-zero if it finds
# something worth looking at. Read-only; never changes anything.
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
warn=0
say()  { echo "  $*"; }
bad()  { echo "  ! $*"; warn=1; }

echo "== pre-stop check =="

# 1. Repo must live on the network volume (/workspace), not the container disk.
case "$REPO_ROOT" in
    /workspace/*) say "repo is on /workspace (persistent): $REPO_ROOT" ;;
    *) bad "repo is NOT under /workspace -- it will be WIPED on stop: $REPO_ROOT" ;;
esac

# 2. Uncommitted / unpushed git work.
if command -v git >/dev/null 2>&1 && git -C "$REPO_ROOT" rev-parse >/dev/null 2>&1; then
    if [ -n "$(git -C "$REPO_ROOT" status --porcelain)" ]; then
        bad "uncommitted changes in the repo (git status):"
        git -C "$REPO_ROOT" --no-pager status --short | sed 's/^/      /'
    else
        say "git working tree clean"
    fi
    ahead=$(git -C "$REPO_ROOT" rev-list --count @{u}..HEAD 2>/dev/null || echo 0)
    [ "${ahead:-0}" != "0" ] && bad "$ahead commit(s) not pushed to origin"
fi

# 3. Run outputs present but not synced (heuristic: runs/ has CSVs).
if ls "$REPO_ROOT"/runs/botsort/*/*.csv >/dev/null 2>&1; then
    say "run outputs exist in runs/botsort/ -- confirm they're on /workspace or pulled off-box"
fi

# 4. Heavy job still running?
if pgrep -f "run_baselines.py|make_progress_report.py|tools/demo.py|ffmpeg|train" >/dev/null 2>&1; then
    bad "a heavy job appears to be RUNNING -- stopping now would kill it:"
    pgrep -af "run_baselines.py|make_progress_report.py|tools/demo.py|ffmpeg|train" | sed 's/^/      /'
fi

echo
if [ "$warn" -eq 0 ]; then
    echo "OK -- safe to stop."
else
    echo "Review the ! lines above before stopping."
fi
exit "$warn"
