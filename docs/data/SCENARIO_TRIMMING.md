# Scenario Trimming Workflow

Each scenario in `~/blindspot_data/S0N/` contains three camera videos
(`c001/vdo.mp4`, `c002/vdo.mp4`, `c003/vdo.mp4`) from one intersection.
For research runs we trim each scenario to a **2 to 5 minute window** in which
the same vehicles are visible across all three cameras during the window.
This page explains why and how.

## Why trim

The detector in `src/prime_mtmc/detector.py` scores cameras using
**cross-camera same-`track_id` pairs**: a detection in `c001` is matched to a
detection of the same vehicle in `c002` (and so on), and the cosine distance
between their ReID embeddings becomes one row of evidence. A camera that
contributes **zero co-visible vehicles** in the trim window contributes zero
data to the experiment.

A 2 to 5 minute daylight window at a busy intersection typically yields tens
of co-visible vehicles per camera pair, which is plenty for the per-camera
mean and variance z-score the detector computes. Picking 2 vs. 5 minutes is
a per-scenario judgement: 2 is fine for clearly busy daylight footage, 5 is
safer for low-traffic or twilight scenarios.

## What to commit, what not to commit

- **Commit** the manifest `data/scenario_windows.csv`, which captures the
  window choice and reviewer-readable notes.
- **Do not commit** the trimmed `vdo_trim.mp4` files. They live in
  `~/blindspot_data/` and are reproducible by re-running the trim script
  against the committed manifest.

## Filling in the manifest

`data/scenario_windows.csv` has one row per scenario:

```
scenario,start,duration_s,anchor_notes
S01,00:01:30,180,"red pickup co-visible across all cams ~01:35; ~15 vehicles co-visible during window"
S02,45,300,"low traffic Sunday morning; chose 5 min for sample size"
...
```

Column rules:

- **`scenario`**: scenario folder name, e.g. `S01`.
- **`start`**: window start, measured from the beginning of the source
  `vdo.mp4`. Accepts either plain seconds (`45`, `45.5`) or an HMS string
  (`00:01:30`, `1:30`, `1:30.5`).
- **`duration_s`**: window length in seconds. Aim for 120 to 300.
- **`anchor_notes`**: free text. State (a) at least one specific vehicle that
  is visible in all three cameras within the window, and (b) a rough count of
  total co-visible vehicles during the window. This is what Sabrina reads
  during PR review.

Rows with empty `start` or `duration_s` are skipped by the tooling, so the
manifest can be filled in scenario by scenario as students review footage.

## How to pick a window

1. Open `c001/vdo.mp4`, `c002/vdo.mp4`, `c003/vdo.mp4` for the scenario in
   any video player that displays a time cursor.
2. Scrub forward until you find a moment where the same vehicle is clearly
   visible in all three feeds. Note the timestamp.
3. Pick a window that brackets that moment: typically 30 to 60 seconds
   before the anchor and 60 to 240 seconds after, totalling 2 to 5 minutes.
4. Sanity check: during the window, count how many additional vehicles pass
   through all three cameras. If the count is below ~5, extend the window
   (up to 5 minutes) or pick a different start.
5. Fill in the manifest row.

## Running the tooling

All commands assume the project venv is active.

Dry-run the trim plan against the manifest:

```cmd
python scripts\trim_scenarios.py
```

Apply the trims (writes `vdo_trim.mp4` next to each `vdo.mp4`):

```cmd
python scripts\trim_scenarios.py --apply
```

Restrict to a single scenario while iterating:

```cmd
python scripts\trim_scenarios.py --scenario S01 --apply
```

For sub-second-accurate trims, re-encode instead of stream-copying
(several times slower):

```cmd
python scripts\trim_scenarios.py --apply --reencode
```

Render side-by-side composite PNGs for PR review:

```cmd
python scripts\scenario_quicklook.py
```

Each composite lands in `runs/quicklook/S0N.png` and shows one frame from
each camera at the midpoint of the chosen window. Reviewers can confirm at a
glance that the anchor vehicle named in `anchor_notes` really is present.

## Defaults and overrides

- The data root defaults to `$BLINDSPOT_DATA_ROOT` or `~/blindspot_data`.
- The camera subfolders default to `c001,c002,c003`. Override with
  `--cameras` if a future scenario uses a different layout.
- The ffmpeg executable is taken from `PATH`; override with `--ffmpeg`.

## Suggested PR workflow

1. Branch from `main`.
2. Fill in one or more rows of `data/scenario_windows.csv`.
3. Run the quicklook script and attach a couple of the generated PNGs to the
   PR description.
4. Request review from Sabrina. She approves the window choices by reading
   the manifest diff and the composite images, without needing the videos.
5. After merge, anyone with the raw footage in `~/blindspot_data/` can
   reproduce the trims with `python scripts/trim_scenarios.py --apply`.
