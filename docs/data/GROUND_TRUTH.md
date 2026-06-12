# Ground-truth cross-camera identity (closes STATUS TODO #4)

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

1. **Sync.** Estimate a constant per-camera frame offset onto a shared
   reference timeline (multicam-reid `sync` step). Save as
   `annotations/<scenario>/sync.json`, e.g. `{"cam01": 0, "cam02": -12, "cam03": 31}`.
   Convention used throughout: `annotation_frame = export_frame + offset[camera]`.
   If annotation runs on the *same trimmed videos* BoT-SORT consumed, offsets
   are all 0. Sync also matters upstream: trim windows must cover the same
   real-world interval in every camera, or vehicles aren't co-visible
   (see STATUS TODO #1 — re-trim on the synced timeline).
2. **Per-camera tracks.** The annotation toolkit's tracker (ByteTrack) gives
   the annotator boxes to click. These tracks are *scaffolding only* — they are
   never poisoned or analyzed. Save per camera as MOT text
   (`frame,track_id,x,y,w,h,...`) or JSON.
3. **Match.** A human clicks the same vehicle across cameras, producing
   `matches.json`: global object id → `{camera: local_track_id}`. Budget
   ~1 minute per object; a busy window has 20–50 co-visible vehicles, so plan
   20–50 min/scenario. Don't annotate all 18 scenarios — pick a few
   well-synced, vehicle-rich ones (S07, S14, S15) and do them thoroughly.
4. **Join.** Two separate tracking runs (BoT-SORT vs. the annotation tracker)
   never share track ids, so `scripts/build_track_ids.py` aligns them by box
   IoU per (camera, frame), greedily one-to-one, then replaces the local
   annotation id with the global id from `matches.json`:

   ```bash
   python scripts/build_track_ids.py \
     --export runs/botsort/S07/S07_poison_c01-c02_eps0.5_seed7_all-cams.csv \
     --matches annotations/S07/matches.json \
     --tracks c01=annotations/S07/cam01_tracks.txt \
              c02=annotations/S07/cam02_tracks.txt \
              c03=annotations/S07/cam03_tracks.txt \
     --offsets-file annotations/S07/sync.json \
     --output runs/botsort/S07/S07_poison_c01-c02_eps0.5_seed7_all-cams_tracked.csv
   ```

   Camera naming is normalized by trailing number (`c01` ≡ `cam01` ≡ `c001`).
   Default IoU threshold 0.5; rows without a global id are dropped unless
   `--keep-all`. The script prints per-camera coverage — if it's near zero,
   suspect a wrong offset (a deliberate test confirms wrong offsets yield no
   matches rather than wrong matches).
5. **Analyze.** The detector is unchanged; it finally gets honest input:

   ```bash
   python scripts/analyze_embedding_export.py \
     --input ..._all-cams_tracked.csv --track-column track_id \
     --poisoned-cameras c01,c02
   ```

## File layout

```
annotations/<scenario>/
  sync.json          # {camera: frame offset}
  cam0N_tracks.txt   # MOT per-camera annotation tracks
  matches.json       # global id -> {camera: local track id}
```

`matches.json` parsing is schema-tolerant; supported shapes include
`{"objects": [{"global_id": 5, "tracks": {"cam01": 12}}]}`,
a top-level list, and `{"5": {"cam01": 12}}`.

## Caveats

- The join is greedy one-to-one per frame, not Hungarian; with IoU ≥ 0.5 on
  vehicle boxes the difference is negligible, and it avoids a scipy dependency.
- Run the join once per export (clean and each poison config) with the *same*
  annotation files — poisoning perturbs embeddings, not boxes, so the same
  ground truth applies.
- Detections the annotation tracker missed (or the human didn't link) drop
  out. Report coverage alongside metrics; it's part of the methodology.
- Validated by `tests/test_build_track_ids.py` plus a synthetic end-to-end run
  (3 cameras, known offsets, poisoned c02 → detector P/R = 1.0 on `track_id`).
