#!/usr/bin/env bash
# Publish trimmed videos and merged embedding exports into the repo via Git LFS.
#
# RESEARCHER tool. Run from the repo root on the GPU box AFTER a successful
# run_baselines.py batch:
#
#     bash scripts/publish_run_outputs.sh          # stage + report sizes only
#     bash scripts/publish_run_outputs.sh --commit # also git-commit the result
#
# What it does:
#   1. Ensures git-lfs is installed and .gitattributes covers data/trimmed/.
#   2. Gzips every per-scenario *_all-cams.csv from runs/botsort/ into
#      data/exports/S0N/  (LFS-tracked, students pull these).
#   3. Copies every trimmed video from the data root into
#      data/trimmed/S0N/c00K_vdo_trim.mp4  (LFS-tracked).
#   4. Copies run_manifest.csv to data/exports/ (plain git, it is small).
#   5. Prints a size report. LFS free tier is ~1 GiB storage and 1 GiB/month
#      bandwidth for the WHOLE repo -- if the report is large, prefer a
#      GitHub Release (see docs/data/SYNCING_RUN_OUTPUTS.md).
#
# Push afterwards with: git push origin main
# (HTTPS push from the box needs a GitHub personal access token as password.)
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
DATA_ROOT="${BLINDSPOT_DATA_ROOT:-}"
if [ -z "$DATA_ROOT" ]; then
    if [ -d /workspace/blindspot_data ]; then DATA_ROOT=/workspace/blindspot_data
    else DATA_ROOT="$HOME/blindspot_data"; fi
fi
echo "repo:      $REPO_ROOT"
echo "data root: $DATA_ROOT"

# 1. git lfs
if ! command -v git-lfs >/dev/null 2>&1; then
    echo "installing git-lfs..."
    apt-get update -qq && apt-get install -y -qq git-lfs
fi
git lfs install --skip-smudge >/dev/null

if ! grep -q "^data/trimmed/" .gitattributes 2>/dev/null; then
    echo "data/trimmed/**/*.mp4 filter=lfs diff=lfs merge=lfs -text" >> .gitattributes
    git add .gitattributes
    echo "added data/trimmed/ LFS rule to .gitattributes"
fi

# 2. gzip merged exports
count_csv=0
for f in runs/botsort/S*/*_all-cams.csv; do
    [ -e "$f" ] || continue
    s="$(basename "$(dirname "$f")")"
    mkdir -p "data/exports/$s"
    out="data/exports/$s/$(basename "$f").gz"
    gzip -c "$f" > "$out"
    count_csv=$((count_csv + 1))
done
echo "gzipped $count_csv merged CSV(s) into data/exports/"

# 3. trimmed videos
count_vid=0
for v in "$DATA_ROOT"/S*/c0*/vdo_trim.mp4; do
    [ -e "$v" ] || continue
    cam="$(basename "$(dirname "$v")")"
    s="$(basename "$(dirname "$(dirname "$v")")")"
    mkdir -p "data/trimmed/$s"
    cp "$v" "data/trimmed/$s/${cam}_vdo_trim.mp4"
    count_vid=$((count_vid + 1))
done
echo "copied $count_vid trimmed video(s) into data/trimmed/"

# 4. run manifest (small, plain git)
if [ -e runs/botsort/run_manifest.csv ]; then
    cp runs/botsort/run_manifest.csv data/exports/run_manifest.csv
fi

# 5. size report
echo
echo "=== size report ==="
du -sh data/exports data/trimmed 2>/dev/null || true
echo "LFS free tier: ~1 GiB storage, 1 GiB/month bandwidth for the whole repo."
echo "If the totals above threaten that, use a GitHub Release instead:"
echo "  docs/data/SYNCING_RUN_OUTPUTS.md (Alternative: GitHub Release)"
echo

git add data/exports data/trimmed
git status --short -- data/ | head -20

if [ "${1:-}" = "--commit" ]; then
    git commit -m "Publish trimmed videos and merged embedding exports (LFS)"
    echo "Committed. Push with: git push origin main"
else
    echo "Staged only. Review above, then re-run with --commit (or commit manually)."
fi
