# Ground-truth cross-camera identity (closes STATUS TODO #4)

> **Just want to annotate?** Follow the step-by-step walkthrough in
> [ANNOTATION_GUIDE.md](ANNOTATION_GUIDE.md). This document is the
> methodology and format reference behind it.
>
> Annotation toolkit: **multicam-reid** — https://github.com/figaone/multicam-reid

## Why

The detector compares ReID embeddings of *the same physical vehicle* across
cameras and flags the camera whose embeddings are inconsistent. BoT-SORT runs
per camera; its export (`camera,frame,detection_index,x1,y1,x2,y2,embedding`)
carries no cross-camera identity. Until now we ran the analysis with
`--track-column detection_index`, which pairs the Nth detection in one camera
with the Nth in another — fictional correspondences. The structural
poisoned-pair pattern survives, but every identity-level number (z-scores,
precision/recall) is a placeholder. We cannot use a cross-camera ReID tracker
to supply the link, because that is the system under attack (circular). The
link has to come from a human.

## Workflow

```
sync  →  annotate/track  →  match  →  build_track_ids.py  →  analyze
(per-camera     (per-camera      (human links     (IoU join onto    (--track-column
frame offsets)  local tracks)    tracks across    BoT-SORT export)   track_id)
                                 cameras)
```

1. **Sync (only if needed).** `python -m multicam_reid sync <folder>` aligns
   the cameras interactively and exports equal-length clips to
   `.reid/synced/<segment>/`. **Recommended workflow: make offsets a
   non-problem** — annotate the *same videos BoT-SORT processed* (offsets all
   0), or sync first and re-run BoT-SORT on the synced clips. Sync also
   matters upstream: trim windows must cover the same real-world interval in
   every camera, or vehicles aren't co-visible (see STATUS TODO #1 — the
   sync-then-rerun path fixes both at once).
2. **Per-camera tracks.** `python -m multicam_reid track <folder>` (or let
   `match` auto-run it) writes `.reid/tracks/<cam>.tracks.json` per camera.
   These tracks give the annotator boxes to click — *scaffolding only*, never
   poisoned or analyzed.
3. **Match.** `python -m multicam_reid match <folder>` opens the clicking UI;
   a human links the same vehicle across cameras, producing
   `.reid/matches.json` (auto-saved on every confirm). Budget ~1 minute per
   object; a busy window has 20–50 co-visible vehicles, so plan 20–50
   min/scenario. The original guidance was to annotate just a few well-synced,
   vehicle-rich scenarios; in practice all 18 were annotated and 14 (S01–S08, S11,
   S13–S17) are joined and published (`exports-2026-06-20`). When extending to new
   footage, still prioritize well-synced, vehicle-rich windows.
4. **Join.** Two separate tracking runs (BoT-SORT vs. the annotation tracker)
   never share track ids, so `scripts/build_track_ids.py` aligns them by box
   IoU per (camera, frame), greedily one-to-one, then replaces the local
   annotation id with a global id from `matches.json`:

   ```bash
   python scripts/build_track_ids.py \
     --export runs/botsort/S07/S07_poison_c01-c02_eps0.5_seed7_all-cams.csv \
     --matches footage/S07/.reid/matches.json \
     --tracks c01=footage/S07/.reid/tracks/c01.tracks.json \
              c02=footage/S07/.reid/tracks/c02.tracks.json \
              c03=footage/S07/.reid/tracks/c03.tracks.json \
     --output runs/botsort/S07/S07_poison_c01-c02_eps0.5_seed7_all-cams_tracked.csv
   ```

   Camera naming is normalized by the last number in the name
   (`c01` ≡ `cam01` ≡ `c001` ≡ `c01_synced`); for nameless cameras pass
   `--camera-map cam_north=c01,...`. Default IoU threshold 0.5; rows without
   a global id are dropped unless `--keep-all`. The script prints per-camera
   coverage — near zero means a timeline mismatch (a deliberate test confirms
   wrong offsets yield no matches rather than wrong matches). For the rare
   case of genuinely different timelines, `--offsets c01=0,c02=-12` or
   `--offsets-file sync.json` applies
   `annotation_frame = export_frame + offset[camera]`.
5. **Analyze.** The detector is unchanged; it finally gets honest input:

   ```bash
   python scripts/analyze_embedding_export.py \
     --input ..._all-cams_tracked.csv --track-column track_id \
     --poisoned-cameras c01,c02
   ```

## File formats (verified against the toolkit)

The toolkit stores everything in a hidden `.reid/` folder next to the videos.
Commit the annotation work into the repo as
`data/annotations/<scenario>/{matches.json, tracks/, sync.json}`.

`matches.json` — one entry per physical object; the entry index becomes the
global id; `null` = not visible/linked in that camera:

```json
{"version": 1, "matches": [
  {"frame": 250, "tracks": {"c01": 12, "c02": 7, "c03": null}}
]}
```

`tracks/<cam>.tracks.json` — top-level key is the local track id; `frames`
and `boxes` are parallel lists, boxes are `[x1, y1, x2, y2]` in pixels:

```json
{"12": {"frames": [100, 101], "boxes": [[651, 223, 705, 261], [654, 224, 708, 262]],
        "classes": [2, 2], "confs": [0.91, 0.88], "class_name": "car"}}
```

`sync.json` — `--offsets-file` reads its `offsets` key directly:

```json
{"version": 1, "reference": "c01",
 "offsets": {"c01": 0, "c02": -12, "c03": 5}, "segments": ["..."]}
```

The parser is additionally tolerant of MOT text tracks
(`frame,track_id,x,y,w,h,...`), JSON row lists, and several legacy
matches.json shapes — see docstrings in `scripts/build_track_ids.py`.

## Caveats

- The join is greedy one-to-one per frame, not Hungarian; with IoU ≥ 0.5 on
  vehicle boxes the difference is negligible, and it avoids a scipy dependency.
- Run the join once per export (clean and each poison config) with the *same*
  annotation files — poisoning perturbs embeddings, not boxes, so the same
  ground truth applies.
- Detections the annotation tracker missed (or the human didn't link) drop
  out. Report coverage alongside metrics; it's part of the methodology.
- Validated by `tests/test_build_track_ids.py` (including the toolkit's exact
  file formats) plus synthetic end-to-end runs: 3 cameras, poisoned camera
  flagged with detector P/R = 1.0 on `track_id`, null-camera entries correctly
  reduce coverage rather than corrupting matches.
