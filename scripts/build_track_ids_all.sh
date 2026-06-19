#!/usr/bin/env bash
# Batch wrapper around scripts/build_track_ids.py.
#
# Joins ground-truth global identities onto EVERY BoT-SORT export for one or
# more scenarios, using the standard repo layout so you don't type the flags
# per export:
#   annotations : data/annotations/<scenario>/matches.json
#                 data/annotations/<scenario>/tracks/<cam>.tracks.json
#   exports     : runs/botsort/<scenario>/*_all-cams.csv   (skips *_tracked.csv)
#   output      : <export>_all-cams.csv -> <export>_all-cams_tracked.csv
#
# Run it inside the env that has pandas (the 'botsort' conda env is fine).
#
# Usage:
#   bash scripts/build_track_ids_all.sh S07              # one scenario
#   bash scripts/build_track_ids_all.sh S07 S14 S15      # several
#   bash scripts/build_track_ids_all.sh all              # every annotated scenario
#
# Pass extra build_track_ids.py options after a `--` separator (applied to
# every join):
#   bash scripts/build_track_ids_all.sh all -- --iou-threshold 0.4
#   bash scripts/build_track_ids_all.sh S07 -- --offsets c02=-1
#
# Override the interpreter with PYTHON=... if needed (default: python).

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
ANNO_DIR="$REPO_ROOT/data/annotations"
RUNS_DIR="$REPO_ROOT/runs/botsort"
PY="${PYTHON:-python}"

# Split args at `--`: before = scenarios (or `all`), after = passthrough opts.
SCENARIOS=()
PASSTHRU=()
seen_sep=0
for a in "$@"; do
  if [ "$seen_sep" -eq 1 ]; then PASSTHRU+=("$a"); continue; fi
  if [ "$a" = "--" ]; then seen_sep=1; continue; fi
  SCENARIOS+=("$a")
done

if [ ${#SCENARIOS[@]} -eq 0 ]; then
  echo "Usage: $0 <scenario|all> [scenario ...] [-- build_track_ids.py opts]"
  exit 1
fi

# `all` -> discover every scenario that has a matches.json (bash 3.2-safe).
if [ ${#SCENARIOS[@]} -eq 1 ] && { [ "${SCENARIOS[0]}" = "all" ] || [ "${SCENARIOS[0]}" = "--all" ]; }; then
  SCENARIOS=()
  while IFS= read -r s; do
    [ -n "$s" ] && SCENARIOS+=("$s")
  done < <(
    for d in "$ANNO_DIR"/*/matches.json; do
      [ -f "$d" ] || continue
      basename "$(dirname "$d")"
    done | sort
  )
  if [ ${#SCENARIOS[@]} -eq 0 ]; then
    echo "No annotations found under $ANNO_DIR (looked for */matches.json)."
    exit 1
  fi
  echo "Discovered annotated scenarios: ${SCENARIOS[*]}"
fi

joins=0
fails=0
skips=0

for s in "${SCENARIOS[@]}"; do
  matches="$ANNO_DIR/$s/matches.json"
  tracks_dir="$ANNO_DIR/$s/tracks"
  scen_runs="$RUNS_DIR/$s"

  echo
  echo "===== $s ====="

  if [ ! -f "$matches" ]; then
    echo "  SKIP: no annotations ($matches not found)"; skips=$((skips+1)); continue
  fi
  if [ ! -d "$tracks_dir" ]; then
    echo "  SKIP: no tracks dir ($tracks_dir)"; skips=$((skips+1)); continue
  fi

  # --tracks CAM=PATH built from <cam>.tracks.json filenames.
  track_args=()
  for tf in "$tracks_dir"/*.tracks.json; do
    [ -f "$tf" ] || continue
    base="$(basename "$tf")"
    cam="${base%.tracks.json}"
    track_args+=("$cam=$tf")
  done
  if [ ${#track_args[@]} -eq 0 ]; then
    echo "  SKIP: no *.tracks.json in $tracks_dir"; skips=$((skips+1)); continue
  fi

  if [ ! -d "$scen_runs" ]; then
    echo "  SKIP: no exports dir ($scen_runs)"; skips=$((skips+1)); continue
  fi

  # Exports to join: *_all-cams.csv, excluding already-joined *_tracked.csv.
  exports=()
  for ex in "$scen_runs"/*_all-cams.csv; do
    [ -f "$ex" ] || continue
    case "$ex" in *_tracked.csv) continue ;; esac
    exports+=("$ex")
  done
  if [ ${#exports[@]} -eq 0 ]; then
    echo "  SKIP: no *_all-cams.csv exports in $scen_runs"; skips=$((skips+1)); continue
  fi

  echo "  cameras: ${track_args[*]}"
  echo "  exports: ${#exports[@]}"

  for ex in "${exports[@]}"; do
    out="${ex%.csv}_tracked.csv"
    echo
    echo "  -> $(basename "$ex")"
    if "$PY" "$SCRIPT_DIR/build_track_ids.py" \
        --export "$ex" \
        --matches "$matches" \
        --tracks "${track_args[@]}" \
        --output "$out" \
        ${PASSTHRU[@]+"${PASSTHRU[@]}"}; then
      joins=$((joins+1))
    else
      echo "  ERROR: join failed for $ex"
      fails=$((fails+1))
    fi
  done
done

echo
echo "Done: $joins join(s) written, $skips scenario(s) skipped, $fails failure(s)."
[ "$fails" -eq 0 ]
