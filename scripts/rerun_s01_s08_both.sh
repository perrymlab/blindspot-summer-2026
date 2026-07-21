#!/usr/bin/env bash
# Clean-slate, reversible re-export of S01-S08: clean + two-cam (c01,c02) +
# single-cam (c01), all epsilons (0.1/0.5/1.0), seed 7.
#
# Reversibility: the current S01-S08 export dirs are MOVED (not deleted) to a
# timestamped archive under /workspace. To revert, see the printed restore
# command at the end, or run this script's `revert` mode.
#
# RUNTIME: ~12h (168 tracker runs). Run inside tmux. Published GitHub releases
# are NOT touched by this script — re-publish deliberately afterward if wanted.
#
# Usage (on the pod, from the repo root, inside the botsort env):
#   bash scripts/rerun_s01_s08_both.sh run [S01 S02 ...]   # default: S01..S08
#   bash scripts/rerun_s01_s08_both.sh run S01             # validate one scenario first (~1.5h)
#   bash scripts/rerun_s01_s08_both.sh revert <archive_dir>   # move originals back
#
# Tip: validate on S01 alone before the full ~12h S01-S08 batch.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
BOTSORT_DIR="$REPO_ROOT/runs/botsort"

MODE="${1:-}"

# Scenario list: args after `run` override the default S01..S08.
shift || true
if [ "$#" -gt 0 ] && [ "$MODE" = "run" ]; then
    SCEN=("$@")
else
    SCEN=(S01 S02 S03 S04 S05 S06 S07 S08)
fi
SCEN_CSV="$(IFS=,; echo "${SCEN[*]}")"

if [ "$MODE" = "revert" ]; then
    ARCHIVE="${1:-}"   # after the shift above, archive dir is now $1
    [ -n "$ARCHIVE" ] && [ -d "$ARCHIVE" ] || { echo "usage: $0 revert <archive_dir>"; exit 2; }
    echo "Reverting: removing freshly generated S01-S08 dirs, restoring from $ARCHIVE"
    for s in "${SCEN[@]}"; do
        rm -rf "${BOTSORT_DIR:?}/${s}"
        [ -d "$ARCHIVE/$s" ] && mv "$ARCHIVE/$s" "$BOTSORT_DIR/$s" && echo "  restored $s"
    done
    echo "Revert complete."
    exit 0
fi

[ "$MODE" = "run" ] || { echo "usage: $0 run   (or: $0 revert <archive_dir>)"; exit 2; }

# --- tmux guard: this is a ~12h batch ---
if [ -z "${TMUX:-}" ]; then
    echo "WARNING: not inside tmux; a ~12h batch will die if your SSH drops."
    echo "Do:  tmux new -s rerun   then re-run this inside it."
    read -r -p "Continue anyway? [y/N] " a; case "$a" in y|Y) ;; *) echo Aborted; exit 1;; esac
fi

command -v python >/dev/null || { echo "python not found - did you 'conda activate botsort'?"; exit 1; }

# --- 1. Archive current exports (MOVE = reversible) ---
STAMP="$(date +%Y%m%d_%H%M%S)"
ARCHIVE="/workspace/archive_s01_s08_${STAMP}"
mkdir -p "$ARCHIVE"
echo "== Archiving current S01-S08 exports -> $ARCHIVE"
for s in "${SCEN[@]}"; do
    if [ -d "$BOTSORT_DIR/$s" ]; then
        mv "$BOTSORT_DIR/$s" "$ARCHIVE/$s"
        echo "  moved $s"
    fi
done
echo "Archive complete. REVERT anytime with:"
echo "  bash scripts/rerun_s01_s08_both.sh revert $ARCHIVE"
echo

# --- 2. Full re-export (regenerate from raw video; no --skip-clean) ---
echo "== [1/4] clean baselines"
python scripts/run_baselines.py --scenarios "$SCEN_CSV" --skip-poison --apply

echo "== [2/4] two-cam poison (c01,c02) eps 0.1/0.5/1.0"
python scripts/run_baselines.py --scenarios "$SCEN_CSV" --poison-cameras c01,c02 --epsilons 0.1,0.5,1.0 --skip-clean --apply

echo "== [3/4] single-cam poison (c01) eps 0.1/0.5/1.0"
python scripts/run_baselines.py --scenarios "$SCEN_CSV" --poison-cameras c01 --epsilons 0.1,0.5,1.0 --skip-clean --apply

# --- 3. Ground-truth track-id joins ---
echo "== [4/4] track-id joins (IoU 0.2)"
bash scripts/build_track_ids_all.sh "${SCEN[@]}" -- --iou-threshold 0.2

# --- 4. Validate: every scenario's tracked files should be present & sane ---
echo
echo "== Validation (tracked file sizes; poisoned should be within ~10% of that scenario's clean)"
cd "$BOTSORT_DIR"
for s in "${SCEN[@]}"; do
    ls -lh "${s}/${s}_clean_all-cams_tracked.csv" \
           "${s}/${s}_poison_c01_all-cams_tracked.csv" 2>/dev/null
    ls -lh ${s}/${s}_poison_c01_eps*_all-cams_tracked.csv \
           ${s}/${s}_poison_c01-c02_eps*_all-cams_tracked.csv 2>/dev/null
done | awk '{print $5, $9}'

echo
echo "Done. Fresh S01-S08 set generated. Originals preserved at:"
echo "  $ARCHIVE"
echo "Revert if needed:  bash scripts/rerun_s01_s08_both.sh revert $ARCHIVE"
echo "Publishing releases is a SEPARATE, deliberate step - nothing was uploaded."
