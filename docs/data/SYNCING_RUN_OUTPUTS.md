# Syncing run outputs

`runs/` is **gitignored** -- it is scratch space on the GPU box and is never
committed directly. When a run finishes you have two separate jobs:

1. **Preserve the heavy artifacts** (embedding CSVs, annotated videos) somewhere
   durable, because the GPU box is ephemeral (see `docs/setup/RECOVERY.md`).
2. **Record provenance in git**: a run log (`docs/templates/RUN_LOG_TEMPLATE.md`)
   plus, if you want, the export itself under version control.

This doc covers option 2 when you want the CSV **versioned in the repo**.

## When to version in git vs not

| Artifact | Recommendation |
| --- | --- |
| Small summary tables / metrics | Commit normally to `results/weekXX/` (no LFS). |
| Embedding CSVs you want versioned | **Git LFS**, gzipped, under `data/exports/` (below). |
| Very large CSVs / annotated videos | **GitHub Release** or external storage -- do not put in LFS. |

> **LFS quota:** GitHub's free tier is ~1 GiB storage + 1 GiB/month bandwidth.
> Full embedding CSVs are large (every detection row is a ~2048-dim float vector
> as text). Always **gzip** before committing -- it shrinks them ~5-10x and
> `pandas.read_csv` reads `.csv.gz` directly, so analysis is unchanged.

## One-time setup (per machine)

```bash
git lfs install
```

`.gitattributes` already tracks `data/exports/**/*.csv`, `*.csv.gz`, `*.npy`,
and `*.npz` with LFS. Nothing else is converted (small CSVs like
`data/scenario_windows.csv` stay as normal git objects).

## Publishing a finished export

```bash
# 1. gzip the export (keep the original in runs/)
mkdir -p data/exports/S01
gzip -c runs/botsort/S01/S01_clean_all-cams.csv > data/exports/S01/S01_clean_all-cams.csv.gz

# 2. commit it (LFS handles the binary blob automatically)
git add data/exports/S01/S01_clean_all-cams.csv.gz
git commit -m "Add S01 c01 clean embedding export"
git push
```

Consumers pull it with a normal clone (Git LFS fetches the blob):

```bash
git lfs install        # once
git clone <repo>       # or: git lfs pull  in an existing clone
# read directly, gz is transparent:
python scripts/analyze_embedding_export.py --input data/exports/S01/S01_clean_all-cams.csv.gz ...
```

## Alternative: GitHub Release (no LFS quota)

For exports too large for the LFS budget, or for videos, attach them to a
tagged Release instead:

```bash
# requires the GitHub CLI (gh) authenticated
gh release create runs-2026-06-10 \
  runs/botsort/S01/S01_clean_all-cams.csv.gz \
  --title "Run outputs 2026-06-10" --notes "S01 clean export"
# add more files later:
gh release upload runs-2026-06-10 runs/botsort/S01/S01_poison_c01-c02_eps0.5_seed7_all-cams.csv.gz
```

Releases allow up to 2 GiB per file and do **not** count against LFS storage.
They are not versioned per-commit, so record the release tag and file name in
the run log's **Outputs** section.

## Either way: record it in the run log

Copy `docs/templates/RUN_LOG_TEMPLATE.md` into the relevant
`experiments/weekXX-topic/` folder and fill the **Outputs** section with the
exact location (LFS path or release tag) so the export can always be found or
regenerated.
