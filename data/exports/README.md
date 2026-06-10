# Versioned run exports

Embedding exports that are deliberately kept under version control live here,
tracked with Git LFS (see `docs/data/SYNCING_RUN_OUTPUTS.md`).

- Prefer gzipped CSVs (`*.csv.gz`) to stay within the LFS quota.
- Organize by scenario, e.g. `data/exports/S01/clean_c01.csv.gz`.
- This is for *published* exports only; day-to-day scratch runs stay in the
  gitignored `runs/` directory.
