# Annotation guide: creating ground-truth vehicle identities

**Audience:** anyone on the team (no prior experience needed).
**Time:** ~45–60 minutes for your first scenario, ~30 after that.
**Why:** docs/data/GROUND_TRUTH.md has the full background. Short version:
the detector needs to know which detection in one camera is *the same car*
as a detection in another camera. No software can supply that label without
being the very thing we're attacking — so a human (you) clicks it in.

The annotation tool is **multicam-reid**: https://github.com/figaone/multicam-reid

---

## 0. One-time setup

You need Python 3.10+ on a machine where a GUI window can open (your laptop,
not the headless pod). A GPU helps but is not required.

```bash
git clone https://github.com/figaone/multicam-reid
cd multicam-reid
pip install -r requirements.txt
```

## 1. Prepare a scenario folder

Make one folder per scenario containing **one video per camera**, named so
the camera number is in the filename — this exact naming lets every later
step work with no extra flags:

```
S07/
├── c01.mp4
├── c02.mp4
└── c03.mp4
```

Copy these from the scenario's footage (e.g. `S07/c001/vdo_trim.mp4` → `c01.mp4`).

> **Which videos?** Use the *same videos BoT-SORT processed* (the trimmed
> ones). That way frame numbers line up automatically and you never have to
> think about offsets. If the scenario's trim windows are broken (see STATUS
> TODO #1) or the cameras are badly out of sync, use the sync path in
> Appendix A instead — but then BoT-SORT must be re-run on the synced clips.

## 2. Start the matcher

```bash
python -m multicam_reid match S07
```

The first time, it will say there are no tracks yet and offer to run
detection + tracking for you. **Say yes.** This takes a few minutes per
video (it's finding all the vehicles so you have boxes to click). It only
happens once — results are cached in a hidden `.reid/` folder inside `S07/`.

Then the matcher window opens: all cameras side by side, gray boxes around
every tracked vehicle.

## 3. Click the matches (the actual work)

For each vehicle that appears in more than one camera:

1. **Click its box in one camera** — it highlights.
2. **Click the same vehicle in the other camera(s).**
3. **Press ENTER** to confirm. The group turns one bright color in all cameras.
4. **Press N** to jump to the next unmatched vehicle. Repeat.

Useful keys (press **H** in the window for the full list):

| Key | What it does |
| --- | --- |
| `SPACE` | play / pause |
| `.` / `,` | step one frame forward / back |
| `→` / `←` | jump 10 frames |
| `W` / `S` | skip ±5 seconds |
| `N` | jump to next unmatched vehicle |
| `ENTER` | confirm the match you're building |
| `BACKSPACE` | clear current selection |
| `Ctrl+Z` | undo |
| `Q` | save and quit |

Tips:

- **Your work saves automatically** every time you press ENTER. You can quit
  and resume any time — just run the same `match` command again.
- A vehicle visible in only one camera needs no match — leave it gray.
- Not sure two blobs are the same car? Scrub a few seconds either way and
  watch the motion. If still unsure, **skip it** — a missing match only costs
  coverage; a wrong match corrupts the ground truth.
- Budget ~1 minute per vehicle. A busy scenario has 20–50 matchable vehicles.

When every cross-camera vehicle has a color, press `Q`. Done — the human part
is over.

## 4. Attach the ground truth to the experiment data

Your clicks are stored in `S07/.reid/matches.json`, and the per-camera boxes
in `S07/.reid/tracks/c01.tracks.json` etc. Now join them onto the BoT-SORT
embedding export (in the blindspot repo):

```bash
python scripts/build_track_ids.py \
  --export runs/botsort/S07/S07_poison_c01-c02_eps0.5_seed7_all-cams.csv \
  --matches /path/to/S07/.reid/matches.json \
  --tracks c01=/path/to/S07/.reid/tracks/c01.tracks.json \
  --tracks c02=/path/to/S07/.reid/tracks/c02.tracks.json \
  --tracks c03=/path/to/S07/.reid/tracks/c03.tracks.json \
  --output runs/botsort/S07/S07_poison_c01-c02_eps0.5_seed7_all-cams_tracked.csv
```

It prints a per-camera **coverage** table. Healthy is roughly 0.3–0.8 (many
detections are vehicles visible in only one camera, which is fine).
**Coverage near 0 means something is wrong** — almost always the annotation
videos and the export came from different timelines. Re-check step 1, or see
Appendix A about offsets.

Run the same command once per export you care about (clean, each epsilon) —
the **same annotation files work for all of them**, because poisoning changes
embeddings, not boxes.

## 5. Analyze with real identities

```bash
python scripts/analyze_embedding_export.py \
  --input runs/botsort/S07/S07_poison_c01-c02_eps0.5_seed7_all-cams_tracked.csv \
  --track-column track_id \
  --poisoned-cameras c01,c02
```

Identical to the old analysis command except `--track-column track_id`
instead of `detection_index`. These numbers are now real and publishable.
Record the coverage figure from step 4 alongside the metrics in your run log.

---

## Appendix A — when the videos are not time-aligned

If the cameras' clips don't show the same moment at the same frame number
(different trim starts, clock drift), do this **before** annotating:

```bash
python -m multicam_reid sync S07
```

Scrub each camera to one recognizable instant (a car crossing a line works
well), press `A` to anchor, `I`/`O` to mark the window you want, `E` to
export. Aligned clips land in `S07/.reid/synced/<segment>/`.

That segment folder is itself a valid project — annotate it directly:

```bash
python -m multicam_reid match S07/.reid/synced/seg_20260612_112209
```

**Crucially:** BoT-SORT must then be re-run on those same synced clips
(`*_synced.mp4`) so the export and the annotation share a timeline, with
offsets 0. This is the recommended way to redo the scenarios with broken trim
windows — it fixes alignment and annotation in one pass.

(`build_track_ids.py` does accept `--offsets`/`--offsets-file` for advanced
cases where the timelines genuinely differ by a known constant, but the
zero-offset path above is simpler and safer. Avoid needing offsets.)

## Appendix B — quality checklist before sharing results

- [ ] Coverage from step 4 recorded in the run log
- [ ] Same annotation files used for the clean and poisoned joins
- [ ] No "cannot extract camera number" warnings (rename videos or pass
      `--camera-map` if your camera names contain no number)
- [ ] `info` agrees with what you think you did:
      `python -m multicam_reid info S07` (cameras, track counts, match count)
- [ ] `.reid/` folder backed up (it *is* the ground truth — copy
      `matches.json` and `tracks/` into the repo under
      `data/annotations/<scenario>/` and commit)
