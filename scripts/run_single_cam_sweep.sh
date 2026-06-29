#!/usr/bin/env bash
# End-to-end single-camera poison sweep on the 14 usable scenarios, in one shot:
#
#   1. run_baselines.py        -> poisoned exports (clean baselines reused; --skip-clean)
#   2. build_track_ids_all.sh  -> join real global track_id onto each export (IoU 0.2)
#   3. tabulate_single_cam.py  -> one combined P/R/F1 table in results/week06/
#
# WHY: every Week-06 poisoned run poisoned c01+c02 (2 of 3 = majority), which
# inverts the detector's "most cameras are clean" assumption and makes it flag
# the lone CLEAN camera. Poisoning only ONE camera keeps <50% poisoned, so this
# is the first VALID test of detector performance.
#
# Run inside the 'botsort' conda env, from the repo root, in a tmux session
# (this is an ~8-10h batch: 14 scenarios x 3 cameras x N epsilons). Every step
# is resume-friendly -- re-running skips finished exports/joins.
#
# Usage:
#   bash scripts/run_single_cam_sweep.sh                 # eps 0.5 only
#   bash scripts/run_single_cam_sweep.sh 0.1,0.5,1.0     # full epsilon sweep
#   POISON_CAM=c02 bash scripts/run_single_cam_sweep.sh  # poison a different lone cam
#   JOIN_IOU=0.3  bash scripts/run_single_cam_sweep.sh   # override join IoU (default 0.2)
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

EPSILONS="${1:-0.5}"
POISON_CAM="${POISON_CAM:-c01}"
JOIN_IOU="${JOIN_IOU:-0.2}"
SCENARIOS="S01,S02,S03,S04,S05,S06,S07,S08,S11,S13,S14,S15,S16,S17"
SCEN_SPACE="${SCENARIOS//,/ }"

# tmux guard -- an 8-10h batch dies with the SSH session if it isn't detached.
if [ -z "${TMUX:-}" ]; then
    echo "WARNING: not inside tmux. This batch (~8-10h) will die if your SSH drops."
    echo "Recommended:  tmux new -s sweep   then re-run this script inside it."
    read -r -p "Continue anyway? [y/N] " ans
    case "$ans" in
        y|Y) ;;
        *) echo "Aborted."; exit 1 ;;
    esac
fi

echo "============================================================"
echo " single-cam sweep | poison=$POISON_CAM | eps={$EPSILONS} | join IoU=$JOIN_IOU"
echo " scenarios: $SCENARIOS"
echo "============================================================"

echo
echo "== 1/3 baselines (poisoned exports) =="
python scripts/run_baselines.py \
    --scenarios "$SCENARIOS" \
    --poison-cameras "$POISON_CAM" \
    --epsilons "$EPSILONS" \
    --skip-clean --apply

echo
echo "== 2/3 join ground-truth global track_id =="
bash scripts/build_track_ids_all.sh $SCEN_SPACE -- --iou-threshold "$JOIN_IOU"

echo
echo "== 3/3 tabulate detector metrics =="
python scripts/tabulate_single_cam.py \
    --scenarios "$SCENARIOS" \
    --epsilons "$EPSILONS" \
    --poison-cameras "$POISON_CAM"

echo
echo "Done. Combined table + markdown summary written under results/week06/."
echo "Compare against the c01+c02 majority-poison table in results/week06/README.md."
