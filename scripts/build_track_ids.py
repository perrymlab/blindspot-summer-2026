"""Join ground-truth global identities onto BoT-SORT embedding exports.

This closes STATUS TODO #4. BoT-SORT runs per camera, so its exports
(`camera,frame,detection_index,x1,y1,x2,y2,embedding`) carry no cross-camera
identity. Ground truth comes from the multicam-reid annotation workflow:

1. `sync`  -> per-camera frame offsets onto a shared reference timeline.
2. `track` -> per-camera annotation tracks (local track ids + boxes per frame).
3. `match` -> `matches.json`: global object id -> {camera: local track id}.

This script joins those annotation tracks onto the BoT-SORT export by
per-frame box IoU (the two trackers are separate runs, so boxes only roughly
agree), then replaces the local annotation track id with the global id from
`matches.json` and writes a `track_id` column the detector can trust:

    python scripts/analyze_embedding_export.py --input <output> --track-column track_id

See docs/data/GROUND_TRUTH.md for the full methodology.

Usage:
    python scripts/build_track_ids.py \
        --export runs/botsort/S01/S01_poison_c01-c02_eps0.5_seed7_all-cams.csv \
        --matches annotations/S01/matches.json \
        --tracks c01=annotations/S01/cam01_tracks.txt \
        --tracks c02=annotations/S01/cam02_tracks.txt \
        --tracks c03=annotations/S01/cam03_tracks.txt \
        --offsets c01=0,c02=-12,c03=31 \
        --output runs/botsort/S01/S01_poison_..._all-cams_tracked.csv

Frame offset convention: annotation_frame = export_frame + offset[camera].
If annotation ran on the same trimmed videos as BoT-SORT, all offsets are 0.
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

def normalize_camera(camera: object) -> int:
    match = re.search(r"(\d+)\s*$", str(camera).strip())
    if not match:
        raise ValueError(f"cannot extract camera number from {camera!r}")
    return int(match.group(1))


# ---------------------------------------------------------------------------
# matches.json parsing (schema-tolerant)
# ---------------------------------------------------------------------------

def load_matches(path: Path) -> dict[tuple[int, int], str]:
    """Return {(camera_number, local_track_id): global_id}.

    Accepts the common shapes:
      {"objects": [{"global_id": 5, "tracks": {"cam01": 12, "cam02": 7}}, ...]}
      [{"global_id": 5, "tracks": {...}}, ...]
      {"5": {"cam01": 12, "cam02": 7}, ...}
      [{"global_id": 5, "cam01": 12, "cam02": 7}, ...]
    """
    raw = json.loads(Path(path).read_text())
    if isinstance(raw, dict) and isinstance(raw.get("objects"), list):
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
                if k not in {"global_id", "id", "label", "notes"} and not isinstance(v, (list, dict))
            }
        else:
            raise ValueError(f"unrecognized matches.json entry for global id {global_id!r}")
        for camera, local_id in cam_map.items():
            if local_id is None:
                continue
            key = (normalize_camera(camera), int(local_id))
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

    MOT format: frame,track_id,x,y,w,h[,conf,...]  (x,y = top-left).
    JSON format: [{"frame": f, "track_id": t, "x1": .., "y1": .., "x2": .., "y2": ..}, ...]
    """
    path = Path(path)
    if path.suffix.lower() == ".json":
        rows = json.loads(path.read_text())
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

def parse_key_value_pairs(values: list[str]) -> dict[int, str]:
    out: dict[int, str] = {}
    for item in values:
        for pair in item.split(","):
            pair = pair.strip()
            if not pair:
                continue
            key, _, value = pair.partition("=")
            if not value:
                raise ValueError(f"expected key=value, got {pair!r}")
            out[normalize_camera(key)] = value
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
                        help="JSON file {camera: offset} (e.g. from the sync step)")
    parser.add_argument("--iou-threshold", type=float, default=0.5)
    parser.add_argument("--keep-all", action="store_true",
                        help="keep rows without a global id (track_id left empty); "
                             "default drops them so the output is detector-ready")
    parser.add_argument("--output", required=True, help="output CSV path")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    export = pd.concat([pd.read_csv(p) for p in args.export], ignore_index=True)
    matches = load_matches(Path(args.matches))
    tracks_by_camera = {
        cam: load_annotation_tracks(Path(path))
        for cam, path in parse_key_value_pairs(args.tracks).items()
    }

    offsets: dict[int, int] = {}
    if args.offsets_file:
        offsets.update(
            {normalize_camera(k): int(v) for k, v in json.loads(Path(args.offsets_file).read_text()).items()}
        )
    if args.offsets:
        offsets.update({k: int(v) for k, v in parse_key_value_pairs([args.offsets]).items()})

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
