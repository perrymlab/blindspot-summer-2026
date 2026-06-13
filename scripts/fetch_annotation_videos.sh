#!/usr/bin/env bash
# Fetch scenario videos from the RunPod pod into the multicam-reid
# annotation layout: <dest>/<scenario>/c01.mp4, c02.mp4, c03.mp4
#
# Usage:
#   ./fetch_annotation_videos.sh [scenario ...]        # default: S07 S14 S15
#
# Pod address changes on restart — override via env:
#   POD_HOST=root@1.2.3.4 POD_PORT=12345 ./fetch_annotation_videos.sh S07
#
# Prefers vdo_trim.mp4 (what BoT-SORT processed) and warns if only the raw
# video exists, because raw frames won't line up with the embedding export.
# See docs/data/ANNOTATION_GUIDE.md.
set -euo pipefail

HOST="${POD_HOST:-root@103.196.86.102}"
PORT="${POD_PORT:-17420}"
KEY="${POD_KEY:-$HOME/.ssh/id_ed25519}"
REMOTE_ROOT="${POD_DATA:-/workspace/blindspot_data}"
DEST="${ANNOTATION_DIR:-$HOME/annotation}"

SCENARIOS=("$@")
[ ${#SCENARIOS[@]} -eq 0 ] && SCENARIOS=(S07 S14 S15)

for s in "${SCENARIOS[@]}"; do
  mkdir -p "$DEST/$s"
  for i in 1 2 3; do
    cam="c00$i"
    out="$DEST/$s/c0$i.mp4"
    if [ -s "$out" ]; then
      echo "skip   $out (already present)"
      continue
    fi
    src=""
    for name in vdo_trim.mp4 vdo.mp4; do
      if ssh -p "$PORT" -i "$KEY" "$HOST" "test -f $REMOTE_ROOT/$s/$cam/$name"; then
        src="$REMOTE_ROOT/$s/$cam/$name"
        break
      fi
    done
    if [ -z "$src" ]; then
      echo "WARN   $s/$cam: no video found on pod, skipping"
      continue
    fi
    [ "${src##*/}" = "vdo.mp4" ] && echo "WARN   $s/$cam: only RAW video found (no trim) — frames won't match the BoT-SORT export!"
    echo "fetch  $src -> $out"
    scp -P "$PORT" -i "$KEY" "$HOST:$src" "$out"
  done
done

echo "Done. Annotate with: python -m multicam_reid match $DEST/<scenario>"
