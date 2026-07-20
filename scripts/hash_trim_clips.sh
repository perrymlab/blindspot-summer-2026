#!/usr/bin/env bash
# Generate or verify SHA256 hashes of the scenario trim clips (vdo_trim.mp4).
#
# Purpose: the team regenerates clips locally from raw captures using
# scripts/trim_scenarios.py + data/scenario_windows.csv instead of downloading
# them. This script proves a regenerated set is byte-identical to the clips
# that produced the published runs.
#
# Usage:
#   bash scripts/hash_trim_clips.sh generate   # on the pod (or wherever the
#                                              # reference clips live); writes
#                                              # data/vdo_trim_hashes.sha256
#   bash scripts/hash_trim_clips.sh verify     # on a laptop after regenerating
#                                              # trims; checks against the file
#
# Data root resolution (same convention as trim_scenarios.py):
#   $BLINDSPOT_DATA_ROOT, else /workspace/blindspot_data, else ~/blindspot_data
#
# After generate: commit data/vdo_trim_hashes.sha256 so everyone can verify.

set -euo pipefail

MODE="${1:-}"
[ -n "$MODE" ] || { echo "usage: $0 [generate|verify]" >&2; exit 2; }

# sha256sum on Linux, shasum -a 256 on macOS
if command -v sha256sum >/dev/null 2>&1; then
    SHA="sha256sum"
elif command -v shasum >/dev/null 2>&1; then
    SHA="shasum -a 256"
else
    echo "ERROR: need sha256sum or shasum on PATH" >&2; exit 1
fi

DATA_ROOT="${BLINDSPOT_DATA_ROOT:-}"
if [ -z "$DATA_ROOT" ]; then
    for candidate in /workspace/blindspot_data "$HOME/blindspot_data"; do
        if [ -d "$candidate" ]; then DATA_ROOT="$candidate"; break; fi
    done
fi
[ -n "$DATA_ROOT" ] && [ -d "$DATA_ROOT" ] || {
    echo "ERROR: no data root found; set BLINDSPOT_DATA_ROOT" >&2; exit 1
}

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HASH_FILE="$REPO_ROOT/data/vdo_trim_hashes.sha256"

cd "$DATA_ROOT"

case "$MODE" in
    generate)
        mapfile -t files < <(find . -type f -name vdo_trim.mp4 | sed 's|^\./||' | sort)
        [ "${#files[@]}" -gt 0 ] || {
            echo "ERROR: no vdo_trim.mp4 under $DATA_ROOT (run trim_scenarios.py first)" >&2
            exit 1
        }
        $SHA "${files[@]}" > "$HASH_FILE"
        echo "Hashed ${#files[@]} clips from $DATA_ROOT"
        echo "Wrote $HASH_FILE"
        # 18 scenarios x 3 cameras = 54 expected; warn, don't fail, if fewer.
        if [ "${#files[@]}" -ne 54 ]; then
            echo "WARNING: expected 54 clips (18 scenarios x 3 cameras), found ${#files[@]}." >&2
        fi
        echo "Next: git add data/vdo_trim_hashes.sha256 && git commit -m 'trim-clip reference hashes' && git push"
        ;;
    verify)
        [ -f "$HASH_FILE" ] || {
            echo "ERROR: $HASH_FILE not found — git pull the repo first" >&2; exit 1
        }
        echo "Verifying clips under $DATA_ROOT against $(basename "$HASH_FILE") ..."
        if $SHA -c "$HASH_FILE"; then
            echo "OK: all clips are byte-identical to the reference set."
        else
            echo "MISMATCH: one or more clips differ or are missing (see lines above)." >&2
            echo "Fix: re-run 'python scripts/trim_scenarios.py --apply' from the raw captures," >&2
            echo "and confirm your raw vdo.mp4 files came from Sabrina's reference set." >&2
            exit 1
        fi
        ;;
    *)
        echo "usage: $0 [generate|verify]" >&2; exit 2
        ;;
esac
