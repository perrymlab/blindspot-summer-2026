#!/usr/bin/env bash
# Copy completed multicam-reid annotation files into the repo and optionally
# upload them to the RunPod pod.
#
# Run this after finishing `python -m multicam_reid match ~/annotation/<scenario>`
# for each scenario. The three output files (matches.json, per-camera tracks)
# are small JSON and belong in version control — they ARE the ground truth.
#
# Usage:
#   ./save_annotations.sh S07            # save one scenario
#   ./save_annotations.sh S07 S14 S15    # save several
#
# Environment overrides (same defaults as fetch_annotation_videos.sh):
#   ANNOTATION_DIR   where multicam-reid wrote its output  (default: ~/annotation)
#   REPO_DIR         path to the blindspot repo on this machine
#                    (default: auto-detected from this script's location)
#   UPLOAD=1         also scp the files to the RunPod pod
#   POD_HOST / POD_PORT / POD_KEY / POD_REPO
#                    pod connection settings (see fetch_annotation_videos.sh)
set -euo pipefail

ANNOTATION_DIR="${ANNOTATION_DIR:-$HOME/annotation}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="${REPO_DIR:-$(dirname "$SCRIPT_DIR")}"

POD_HOST="${POD_HOST:-root@103.196.86.102}"
POD_PORT="${POD_PORT:-17420}"
POD_KEY="${POD_KEY:-$HOME/.ssh/id_ed25519}"
POD_REPO="${POD_REPO:-/workspace/blindspot-summer-2026}"

SCENARIOS=("$@")
[ ${#SCENARIOS[@]} -eq 0 ] && { echo "Usage: $0 <scenario> [scenario ...]"; exit 1; }

for s in "${SCENARIOS[@]}"; do
  reid="$ANNOTATION_DIR/$s/.reid"
  dest="$REPO_DIR/data/annotations/$s"

  if [ ! -f "$reid/matches.json" ]; then
    echo "ERROR  $reid/matches.json not found — has annotation for $s been completed?"
    continue
  fi

  n=$(python3 -c "import json; d=json.load(open('$reid/matches.json')); print(len(d.get('matches', d.get('objects', []))))" 2>/dev/null || echo "?")
  echo "--- $s: $n matches found ---"

  mkdir -p "$dest/tracks"

  cp "$reid/matches.json" "$dest/matches.json"
  echo "  saved matches.json"

  for f in "$reid/tracks"/*.tracks.json; do
    [ -f "$f" ] || continue
    cp "$f" "$dest/tracks/$(basename "$f")"
    echo "  saved tracks/$(basename "$f")"
  done

  if [ -f "$reid/sync.json" ]; then
    cp "$reid/sync.json" "$dest/sync.json"
    echo "  saved sync.json"
  fi

  echo "  -> $dest"

  if [ "${UPLOAD:-0}" = "1" ]; then
    pod_dest="$POD_REPO/data/annotations/$s"
    echo "  uploading to pod: $pod_dest"
    ssh -p "$POD_PORT" -i "$POD_KEY" "$POD_HOST" "mkdir -p $pod_dest/tracks"
    scp -P "$POD_PORT" -i "$POD_KEY" \
      "$dest/matches.json" \
      "$POD_HOST:$pod_dest/matches.json"
    for f in "$dest/tracks"/*.tracks.json; do
      [ -f "$f" ] || continue
      scp -P "$POD_PORT" -i "$POD_KEY" "$f" "$POD_HOST:$pod_dest/tracks/$(basename "$f")"
    done
    echo "  uploaded to pod"
  fi

done

echo ""
echo "Next steps:"
echo "  cd $REPO_DIR"
echo "  git add data/annotations/"
echo "  git commit -m 'Add ground-truth annotations for ${SCENARIOS[*]}'"
echo ""
echo "Then run the join (on the pod or locally wherever the exports are):"
for s in "${SCENARIOS[@]}"; do
  echo "  python scripts/build_track_ids.py \\"
  echo "    --export runs/botsort/$s/<export>_all-cams.csv \\"
  echo "    --matches data/annotations/$s/matches.json \\"
  echo "    --tracks c01=data/annotations/$s/tracks/c01.tracks.json \\"
  echo "             c02=data/annotations/$s/tracks/c02.tracks.json \\"
  echo "             c03=data/annotations/$s/tracks/c03.tracks.json \\"
  echo "    --output runs/botsort/$s/<export>_tracked.csv"
done
echo ""
echo "Add UPLOAD=1 to also push annotation files to the pod:"
echo "  UPLOAD=1 $0 ${SCENARIOS[*]}"
