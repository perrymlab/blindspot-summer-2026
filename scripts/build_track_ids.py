"""Join ground-truth global identities onto BoT-SORT embedding exports.

This closes STATUS TODO #4. BoT-SORT runs per camera, so its exports
(`camera,frame,detection_index,x1,y1,x2,y2,embedding`) carry no cross-camera
identity. Ground truth comes from the multicam-reid annotation toolkit
(https://github.com/figaone/multicam-reid):

1. `sync`  -> aligned per-camera clips (`.reid/synced/<segment>/`).
2. `track` -> per-camera annotation tracks (`.reid/tracks/<cam>.tracks.json`).
3. `match` -> `.reid/matches.json`: one entry per physical object, mapping
              each camera name to the local track id it gave that object.

This script joins those annotation tracks onto the BoT-SORT export by
per-frame box IoU (the two trackers are separate runs, so boxes only roughly
agree), then replaces the local annotation track id with a global id from
`matches.json` and writes a `track_id` column the detector can trust:

    python scripts/analyze_embedding_export.py --input <output> --track-column track_id

See docs/data/GROUND_TRUTH.md (methodology) and docs/data/ANNOTATION_GUIDE.md
(step-by-step walkthrough).

Usage (recommended path: BoT-SORT and annotation both ran on the same synced
clips, so no offsets are needed):

    python scripts/build_track_ids.py \
        --export runs/botsort/S07/S07_poison_c01-c02_eps0.5_seed7_all-cams.csv \
        --matches footage/S07/.reid/matches.json \
        --tracks c01=footage/S07/.reid/tracks/c01.tracks.json \
        --tracks c02=footage/S07/.reid/tracks/c02.tracks.json \
        --tracks c03=footage/S07/.reid/tracks/c03.tracks.json \
        --output runs/botsort/S07/S07_poison_..._all-cams_tracked.csv

Camera names are matched by their trailing number (`c01` == `cam01` == `c001`).
For non-numeric camera names, map them explicitly:
    --camera-map cam_north=c01,cam_east=c02,cam_west=c03

Frame offset convention: annotation_frame = export_frame + offset[camera].
Only needed when annotation and BoT-SORT ran on different timelines.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

EXPORT_COLUMNS = {"camera", "frame", "x1", "y1", "x2", "y2"}


# ---------------------------------------------------------------------------
# Camera-id normalization: "c01", "cam01", "c001", "1" all -> 1
# ---------------------------------------------------------------------------

def normalize_camera(camera: object, camera_map: dict[str, str] | None = None) -> int:
    name = str(camera).strip()
    if camera_map:
        name = camera_map.get(name, camera_map.get(name.lower(), name))
    digit_groups = re.findall(r"\d+", str(name))
    if not digit_groups:
        raise ValueError(
            f"cannot extract camera number from {camera!r}. "
            "For non-numeric camera names pass --camera-map, e.g. "
            "--camera-map cam_north=c01,cam_east=c02"
        )
    # Last digit group, so "c01" == "cam01" == "c001" == "c01_synced" == 1.
    return int(digit_groups[-1])


# ---------------------------------------------------------------------------
# matches.json parsing (schema-tolerant)
# ---------------------------------------------------------------------------

def load_matches(path: Path, camera_map: dict[str, str] | None = None) -> dict[tuple[int, int], str]:
    """Return {(camera_number, local_track_id): global_id}.

    Primary format — multicam-reid `.reid/matches.json`
    (https://github.com/figaone/multicam-reid):
      {"version": 1, "matches": [
        {"frame": 250, "tracks": {"cam_north": 12, "cam_east": 7, "cam_west": null}},
        ...]}
    Each entry is one physical object; entry index becomes the global id.
    `null` means "not visible / not linked in that camera" and is skipped.

    Also accepted for flexibility:
      {"objects": [{"global_id": 5, "tracks": {"cam01": 12, "cam02": 7}}, ...]}
      [{"global_id": 5, "tracks": {...}}, ...]
      {"5": {"cam01": 12, "cam02": 7}, ...}
      [{"global_id": 5, "cam01": 12, "cam02": 7}, ...]
    """
    raw = json.loads(Path(path).read_text())
    if isinstance(raw, dict) and isinstance(raw.get("matches"), list):
        entries = [(e.get("global_id", e.get("id", i)), e) for i, e in enumerate(raw["matches"])]
    elif isinstance(raw, dict) and isinstance(raw.get("objects"), list):
        entries = [(e.get("global_id", e.get("id", i)), e) for i, e in enumerate(raw["objects"])]
    elif isinstance(raw, list):
        entries = [(e.get("global_id", e.get("id", i)), e) for i, e in enumerate(raw)]
    elif isinstance(raw, dict):
        entries = list(raw.items())
    else:
        raise ValueError(f"unrecognized matches.json structure in {path}")

    mapping: dict[tuple[int, int], str] = {}
    for global_id, entry in entries:
        if isinstance(entry, dict):
            cam_map = entry.get("tracks") or entry.get("cameras") or {
                k: v for k, v in entry.items()
                if k not in {"global_id", "id", "label", "notes", "frame", "version"}
                and not isinstance(v, (list, dict))
            }
        else:
            raise ValueError(f"unrecognized matches.json entry for global id {global_id!r}")
        for camera, local_id in cam_map.items():
            if local_id is None:
                continue
            key = (normalize_camera(camera, camera_map), int(local_id))
            if key in mapping and mapping[key] != str(global_id):
                raise ValueError(
                    f"conflict: camera-track {key} assigned to global ids "
                    f"{mapping[key]!r} and {global_id!r}"
                )
            mapping[key] = str(global_id)
    if not mapping:
        raise ValueError(f"no (camera, track) -> global id pairs found in {path}")
    return mapping


# ---------------------------------------------------------------------------
# Annotation track loading (MOT txt or JSON)
# ---------------------------------------------------------------------------

def load_annotation_tracks(path: Path) -> pd.DataFrame:
    """Return DataFrame [frame, local_id, x1, y1, x2, y2] for one camera.

    Primary format — multicam-reid `.reid/tracks/<cam>.tracks.json`:
      {"12": {"frames": [100, 101], "boxes": [[x1,y1,x2,y2], ...], ...}, ...}
    (top-level key = local track id; frames/boxes are parallel lists).

    Also accepted:
      MOT text: frame,track_id,x,y,w,h[,conf,...]  (x,y = top-left)
      JSON list: [{"frame": f, "track_id": t, "x1": .., "y1": .., ...}, ...]
    """
    path = Path(path)
    if path.suffix.lower() == ".json":
        rows = json.loads(path.read_text())
        if isinstance(rows, dict):
            records = []
            for local_id, track in rows.items():
                for f, box in zip(track["frames"], track["boxes"]):
                    records.append(
                        {
                            "frame": int(f),
                            "track_id": int(local_id),
                            "x1": box[0],
                            "y1": box[1],
                            "x2": box[2],
                            "y2": box[3],
                        }
                    )
            if not records:
                raise ValueError(f"{path}: no track boxes found")
            rows = records
        frame = pd.DataFrame(rows)
        if {"x", "y", "w", "h"}.issubset(frame.columns):
            frame["x1"] = frame["x"]
            frame["y1"] = frame["y"]
            frame["x2"] = frame["x"] + frame["w"]
            frame["y2"] = frame["y"] + frame["h"]
        frame = frame.rename(columns={"track": "track_id", "id": "track_id"})
        out = frame[["frame", "track_id", "x1", "y1", "x2", "y2"]].copy()
    else:
        mot = pd.read_csv(path, header=None)
        if mot.shape[1] < 6:
            raise ValueError(f"{path}: expected MOT columns frame,track_id,x,y,w,h[,...]")
        out = pd.DataFrame(
            {
                "frame": mot[0],
                "track_id": mot[1],
                "x1": mot[2],
                "y1": mot[3],
                "x2": mot[2] + mot[4],
                "y2": mot[3] + mot[5],
            }
        )
    out = out.rename(columns={"track_id": "local_id"})
    out["frame"] = out["frame"].astype(int)
    out["local_id"] = out["local_id"].astype(int)
    return out


# ---------------------------------------------------------------------------
# IoU matching
# ---------------------------------------------------------------------------

def iou_matrix(boxes_a: np.ndarray, boxes_b: np.ndarray) -> np.ndarray:
    """Pairwise IoU between (N,4) and (M,4) arrays of [x1,y1,x2,y2]."""
    a = boxes_a[:, None, :]
    b = boxes_b[None, :, :]
    inter_w = np.clip(np.minimum(a[..., 2], b[..., 2]) - np.maximum(a[..., 0], b[..., 0]), 0, None)
    inter_h = np.clip(np.minimum(a[..., 3], b[..., 3]) - np.maximum(a[..., 1], b[..., 1]), 0, None)
    inter = inter_w * inter_h
    area_a = np.clip(a[..., 2] - a[..., 0], 0, None) * np.clip(a[..., 3] - a[..., 1], 0, None)
    area_b = np.clip(b[..., 2] - b[..., 0], 0, None) * np.clip(b[..., 3] - b[..., 1], 0, None)
    union = area_a + area_b - inter
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(union > 0, inter / union, 0.0)


def greedy_assign(iou: np.ndarray, threshold: float) -> list[tuple[int, int, float]]:
    """One-to-one greedy assignment by descending IoU. Returns (row, col, iou)."""
    pairs = []
    order = np.argsort(iou, axis=None)[::-1]
    used_rows: set[int] = set()
    used_cols: set[int] = set()
    n_cols = iou.shape[1]
    for flat in order:
        value = iou.flat[flat]
        if value < threshold:
            break
        row, col = divmod(int(flat), n_cols)
        if row in used_rows or col in used_cols:
            continue
        used_rows.add(row)
        used_cols.add(col)
        pairs.append((row, col, float(value)))
    return pairs


# ---------------------------------------------------------------------------
# Main join
# ---------------------------------------------------------------------------

def build_track_ids(
    export: pd.DataFrame,
    tracks_by_camera: dict[int, pd.DataFrame],
    matches: dict[tuple[int, int], str],
    offsets: dict[int, int],
    iou_threshold: float = 0.5,
) -> pd.DataFrame:
    """Return the export with track_id / annotation_track / match_iou columns."""
    missing = EXPORT_COLUMNS - set(export.columns)
    if missing:
        raise ValueError(f"export is missing columns: {sorted(missing)}")

    export = export.copy()
    export["_cam_num"] = export["camera"].map(normalize_camera)
    export["track_id"] = pd.NA
    export["annotation_track"] = pd.NA
    export["match_iou"] = np.nan

    # Index annotation boxes by (camera, frame) for fast lookup.
    annotation_index: dict[int, dict[int, pd.DataFrame]] = {
        cam: {int(f): grp for f, grp in tracks.groupby("frame")}
        for cam, tracks in tracks_by_camera.items()
    }

    for (cam, frame), group in export.groupby(["_cam_num", "frame"]):
        per_frame = annotation_index.get(cam, {})
        annotation = per_frame.get(int(frame) + offsets.get(cam, 0))
        if annotation is None or annotation.empty:
            continue
        det_boxes = group[["x1", "y1", "x2", "y2"]].to_numpy(dtype=float)
        ann_boxes = annotation[["x1", "y1", "x2", "y2"]].to_numpy(dtype=float)
        for det_pos, ann_pos, iou in greedy_assign(iou_matrix(det_boxes, ann_boxes), iou_threshold):
            export_idx = group.index[det_pos]
            local_id = int(annotation["local_id"].iloc[ann_pos])
            export.loc[export_idx, "annotation_track"] = f"{cam}:{local_id}"
            export.loc[export_idx, "match_iou"] = iou
            global_id = matches.get((cam, local_id))
            if global_id is not None:
                export.loc[export_idx, "track_id"] = global_id

    return export.drop(columns=["_cam_num"])


def summarize(joined: pd.DataFrame) -> pd.DataFrame:
    summary = (
        joined.assign(
            matched=joined["annotation_track"].notna(),
            global_assigned=joined["track_id"].notna(),
        )
        .groupby("camera")
        .agg(
            detections=("frame", "size"),
            matched_to_annotation=("matched", "sum"),
            with_global_id=("global_assigned", "sum"),
            global_ids=("track_id", "nunique"),
        )
        .reset_index()
    )
    summary["coverage"] = (summary["with_global_id"] / summary["detections"]).round(3)
    return summary


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_key_value_pairs(
    values: list[str], camera_map: dict[str, str] | None = None
) -> dict[int, str]:
    out: dict[int, str] = {}
    for item in values:
        for pair in item.split(","):
            pair = pair.strip()
            if not pair:
                continue
            key, _, value = pair.partition("=")
            if not value:
                raise ValueError(f"expected key=value, got {pair!r}")
            out[normalize_camera(key, camera_map)] = value
    return out


def parse_camera_map(value: str) -> dict[str, str]:
    """Parse 'cam_north=c01,cam_east=c02' into {'cam_north': 'c01', ...}."""
    out: dict[str, str] = {}
    for pair in value.split(","):
        pair = pair.strip()
        if not pair:
            continue
        key, _, mapped = pair.partition("=")
        if not mapped:
            raise ValueError(f"expected name=camera, got {pair!r}")
        out[key.strip()] = mapped.strip()
    return out


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--export", required=True, nargs="+",
                        help="BoT-SORT export CSV(s) (merged all-cams or one per camera)")
    parser.add_argument("--matches", required=True, help="matches.json from annotation")
    parser.add_argument("--tracks", required=True, nargs="+", metavar="CAM=PATH",
                        help="per-camera annotation tracks (MOT txt or JSON), e.g. c01=cam01.txt")
    parser.add_argument("--offsets", default="",
                        help="per-camera frame offsets, e.g. c01=0,c02=-12 "
                             "(annotation_frame = export_frame + offset); default all 0")
    parser.add_argument("--offsets-file", default="",
                        help="JSON file {camera: offset}, or a multicam-reid "
                             "sync.json (its 'offsets' key is used). NOT needed "
                             "when BoT-SORT and annotation ran on the same "
                             "synced clips — leave offsets at 0 then.")
    parser.add_argument("--camera-map", default="",
                        help="map annotation camera names to export camera ids "
                             "when names have no number, e.g. "
                             "cam_north=c01,cam_east=c02,cam_west=c03")
    parser.add_argument("--iou-threshold", type=float, default=0.5)
    parser.add_argument("--keep-all", action="store_true",
                        help="keep rows without a global id (track_id left empty); "
                             "default drops them so the output is detector-ready")
    parser.add_argument("--output", required=True, help="output CSV path")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    camera_map = parse_camera_map(args.camera_map) if args.camera_map else None

    export = pd.concat([pd.read_csv(p) for p in args.export], ignore_index=True)
    matches = load_matches(Path(args.matches), camera_map)
    tracks_by_camera = {
        cam: load_annotation_tracks(Path(path))
        for cam, path in parse_key_value_pairs(args.tracks, camera_map).items()
    }

    offsets: dict[int, int] = {}
    if args.offsets_file:
        offsets_raw = json.loads(Path(args.offsets_file).read_text())
        if isinstance(offsets_raw, dict) and isinstance(offsets_raw.get("offsets"), dict):
            offsets_raw = offsets_raw["offsets"]  # multicam-reid sync.json
        offsets.update(
            {normalize_camera(k, camera_map): int(v) for k, v in offsets_raw.items()}
        )
    if args.offsets:
        offsets.update(
            {k: int(v) for k, v in parse_key_value_pairs([args.offsets], camera_map).items()}
        )

    joined = build_track_ids(export, tracks_by_camera, matches, offsets, args.iou_threshold)

    summary = summarize(joined)
    print(summary.to_string(index=False))

    total = len(joined)
    if not args.keep_all:
        joined = joined[joined["track_id"].notna()]
        print(f"Kept {len(joined)}/{total} detections with a ground-truth global id "
              f"(--keep-all to keep the rest).")

    if joined.empty:
        print("WARNING: no detections received a global id. Check --offsets (sync), "
              "camera naming, and --iou-threshold.", file=sys.stderr)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    joined.to_csv(out_path, index=False)
    print(f"Wrote {out_path}")
    print("Next: python scripts/analyze_embedding_export.py "
          f"--input {out_path} --track-column track_id")


if __name__ == "__main__":
    main()
