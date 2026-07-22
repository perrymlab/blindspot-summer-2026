from __future__ import annotations

import argparse
import re
import sys
import zlib
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

try:
    import cv2
except ImportError:  # pragma: no cover - dependency hint
    cv2 = None

from prime_mtmc.reid import observation_cross_camera_distances, parse_embedding_column

BOX_COLUMNS = {"frame", "x1", "y1", "x2", "y2"}
TRACKED_COLUMNS = BOX_COLUMNS | {"camera", "embedding", "track_id"}
STATUS_COLORS = {
    "OK": (0, 200, 0),
    "WARN": (0, 191, 255),
    "ANOM": (0, 0, 255),
    "UNMATCHED": (128, 128, 128),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Overlay BoT-SORT boxes or cross-camera ReID distances onto a source video."
    )
    parser.add_argument("--csv", required=True, help="Per-camera CSV written by --prime-export-embeddings.")
    parser.add_argument("--video", required=True, help="Source video the CSV was exported from.")
    parser.add_argument("--out", default="runs/embedding_analysis/boxes.mp4", help="Output annotated video.")
    parser.add_argument("--camera", default=None, help="Only draw rows for this result-camera ID.")
    parser.add_argument(
        "--color-by",
        default="detection_index",
        help="Legacy box-mode column used to pick the deterministic box color and label.",
    )
    parser.add_argument(
        "--frame-base",
        type=int,
        default=1,
        help="Frame number assigned to the first video frame (BoT-SORT exports are 1-based).",
    )
    parser.add_argument(
        "--frame-offset",
        type=int,
        default=0,
        help="Extra shift added to the video frame counter before CSV frame matching.",
    )
    parser.add_argument(
        "--annotation-mode",
        choices=("boxes", "reid-distance"),
        default="boxes",
        help="Annotation mode; default boxes preserves the legacy renderer.",
    )
    parser.add_argument(
        "--tracked-csv",
        help="Matching all-camera *_all-cams_tracked.csv[.gz]; required in reid-distance mode.",
    )
    parser.add_argument(
        "--clean-tracked-csv",
        help="Scenario clean all-camera tracked CSV used to calculate clean-reference XCam deltas.",
    )
    parser.add_argument(
        "--reid-iou-threshold",
        type=float,
        default=0.5,
        help="Minimum IoU for the one-to-one ReID fallback match (default: 0.5).",
    )
    parser.add_argument(
        "--warn-threshold",
        type=float,
        default=0.15,
        help="WARN threshold for positive clean-reference delta, or absolute XCam without a reference.",
    )
    parser.add_argument(
        "--anomaly-threshold",
        type=float,
        default=0.30,
        help="ANOM threshold for positive clean-reference delta, or absolute XCam without a reference.",
    )
    parser.add_argument("--scenario", help="Scenario text shown in the ReID HUD.")
    parser.add_argument("--condition", help="Condition text shown in the ReID HUD.")
    parser.add_argument("--epsilon", help="Poison epsilon text shown in the ReID HUD.")
    parser.add_argument("--seed", help="Poison seed text shown in the ReID HUD.")
    return parser.parse_args()


def color_for(value: object) -> tuple[int, int, int]:
    """Deterministic BGR color for a label (stable across runs)."""
    digest = zlib.crc32(str(value).encode("utf-8"))
    return (digest & 255, (digest >> 8) & 255, (digest >> 16) & 255)


def normalize_camera(camera: object) -> str:
    """Normalize c01/c001/cam01-style result IDs to cNN."""
    groups = re.findall(r"\d+", str(camera).strip())
    if not groups:
        raise ValueError(f"cannot extract camera number from {camera!r}")
    return f"c{int(groups[-1]):02d}"


def _validate_columns(frame: pd.DataFrame, required: set[str], label: str) -> None:
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"{label} is missing required columns: {sorted(missing)}")


def _boxes_array(frame: pd.DataFrame) -> np.ndarray:
    return frame[["x1", "y1", "x2", "y2"]].to_numpy(dtype=np.float64)


def iou_matrix(boxes_a: np.ndarray, boxes_b: np.ndarray) -> np.ndarray:
    """Pairwise IoU for XYXY boxes."""
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
    """Return one-to-one descending-IoU matches above threshold."""
    if iou.size == 0:
        return []
    pairs: list[tuple[int, int, float]] = []
    used_rows: set[int] = set()
    used_cols: set[int] = set()
    for flat in np.argsort(iou, axis=None)[::-1]:
        value = float(iou.flat[flat])
        if value < threshold:
            break
        row, col = divmod(int(flat), iou.shape[1])
        if row not in used_rows and col not in used_cols:
            used_rows.add(row)
            used_cols.add(col)
            pairs.append((row, col, value))
    return pairs


def _unique_key_map(frame: pd.DataFrame, columns: list[str]) -> dict[tuple[object, ...], int]:
    if not set(columns).issubset(frame.columns):
        return {}
    mapping: dict[tuple[object, ...], int] = {}
    duplicates: set[tuple[object, ...]] = set()
    for index, row in frame.iterrows():
        key = tuple(row[column] for column in columns)
        if any(pd.isna(value) for value in key):
            continue
        if key in mapping:
            duplicates.add(key)
        else:
            mapping[key] = int(index)
    for key in duplicates:
        mapping.pop(key, None)
    return mapping


def match_observations(
    boxes: pd.DataFrame, observations: pd.DataFrame, iou_threshold: float
) -> pd.DataFrame:
    """Safely match box rows to one tracked observation, preserving priority order."""
    _validate_columns(boxes, BOX_COLUMNS, "box CSV")
    _validate_columns(observations, BOX_COLUMNS | {"camera"}, "tracked CSV")
    if not 0 <= iou_threshold <= 1:
        raise ValueError("--reid-iou-threshold must be between 0 and 1")

    left = boxes.copy().reset_index(drop=False, names="box_source_index")
    right = observations.copy().reset_index(drop=False, names="tracked_source_index")
    left["_camera"] = left.get("camera", "").map(normalize_camera) if "camera" in left else None
    right["_camera"] = right["camera"].map(normalize_camera)
    left["frame"] = left["frame"].astype(int)
    right["frame"] = right["frame"].astype(int)
    matched: dict[int, tuple[int, str]] = {}
    used_right: set[int] = set()

    def match_unique(columns: list[str], strategy: str) -> None:
        available = right.loc[~right.index.isin(used_right)]
        lookup = _unique_key_map(available, columns)
        for left_index, row in left.loc[~left.index.isin(matched)].iterrows():
            key = tuple(row[column] for column in columns)
            right_index = lookup.get(key)
            if right_index is not None:
                matched[int(left_index)] = (right_index, strategy)
                used_right.add(right_index)

    if "detection_index" in left and "detection_index" in right:
        match_unique(["_camera", "frame", "detection_index"], "detection_index")
    if "track_id" in left and "track_id" in right:
        match_unique(["_camera", "frame", "track_id"], "track_id")
    if "tracker_id" in left and "tracker_id" in right:
        match_unique(["_camera", "frame", "tracker_id"], "tracker_id")

    for (camera, frame), left_group in left.loc[~left.index.isin(matched)].groupby(["_camera", "frame"], dropna=False):
        if camera is None:
            continue
        right_group = right.loc[
            (~right.index.isin(used_right)) & (right["_camera"] == camera) & (right["frame"] == frame)
        ]
        for row_pos, col_pos, _ in greedy_assign(
            iou_matrix(_boxes_array(left_group), _boxes_array(right_group)), iou_threshold
        ):
            box_index = int(left_group.index[row_pos])
            tracked_index = int(right_group.index[col_pos])
            matched[box_index] = (tracked_index, "iou")
            used_right.add(tracked_index)

    rows = []
    for box_index in left.index:
        tracked_index, strategy = matched.get(int(box_index), (None, "unmatched"))
        rows.append(
            {
                "box_index": int(box_index),
                "tracked_index": tracked_index,
                "match_strategy": strategy,
            }
        )
    return pd.DataFrame(rows)


def classify_status(value: float | None, warn_threshold: float, anomaly_threshold: float) -> str:
    if value is None or not np.isfinite(value):
        return "UNMATCHED"
    if value >= anomaly_threshold:
        return "ANOM"
    if value >= warn_threshold:
        return "WARN"
    return "OK"


def prepare_reid_annotations(args: argparse.Namespace, boxes: pd.DataFrame) -> tuple[pd.DataFrame, Counter[str], str]:
    """Precompute all ReID mode matching and annotation state before video decoding."""
    if not args.tracked_csv:
        raise ValueError("--tracked-csv is required with --annotation-mode reid-distance")
    if not 0 <= args.warn_threshold <= args.anomaly_threshold:
        raise ValueError("thresholds must satisfy 0 <= --warn-threshold <= --anomaly-threshold")

    _validate_columns(boxes, BOX_COLUMNS, "box CSV")
    tracked = pd.read_csv(args.tracked_csv)
    _validate_columns(tracked, TRACKED_COLUMNS, "tracked CSV")
    tracked_metrics = observation_cross_camera_distances(tracked, parse_embedding_column(tracked))
    box_matches = match_observations(boxes, tracked_metrics, args.reid_iou_threshold)
    annotations = boxes.copy().reset_index(drop=True)
    annotations = annotations.join(box_matches.set_index("box_index"))
    annotations["xcam_distance"] = np.nan
    annotations["track_id"] = pd.NA
    annotations["tracker_id"] = pd.NA
    annotations["clean_xcam_distance"] = np.nan
    annotations["delta_xcam"] = np.nan

    for box_index, match in box_matches.set_index("box_index").iterrows():
        tracked_index = match["tracked_index"]
        if pd.isna(tracked_index):
            continue
        row = tracked_metrics.loc[int(tracked_index)]
        annotations.loc[box_index, "xcam_distance"] = row["xcam_distance"]
        annotations.loc[box_index, "track_id"] = row["track_id"]
        if "tracker_id" in tracked_metrics:
            annotations.loc[box_index, "tracker_id"] = row["tracker_id"]

    status_basis = "XCam distance"
    if args.clean_tracked_csv:
        clean = pd.read_csv(args.clean_tracked_csv)
        _validate_columns(clean, TRACKED_COLUMNS, "clean tracked CSV")
        clean_metrics = observation_cross_camera_distances(clean, parse_embedding_column(clean))
        clean_matches = match_observations(tracked_metrics, clean_metrics, args.reid_iou_threshold)
        for tracked_index, match in clean_matches.set_index("box_index").iterrows():
            clean_index = match["tracked_index"]
            if pd.isna(clean_index):
                continue
            clean_value = clean_metrics.loc[int(clean_index), "xcam_distance"]
            target_boxes = annotations.index[annotations["tracked_index"] == int(tracked_index)]
            annotations.loc[target_boxes, "clean_xcam_distance"] = clean_value
            annotations.loc[target_boxes, "delta_xcam"] = (
                annotations.loc[target_boxes, "xcam_distance"] - clean_value
            )
        status_basis = "Delta XCam vs clean"
        annotations["status_score"] = annotations["delta_xcam"]
    else:
        annotations["status_score"] = annotations["xcam_distance"]

    annotations["status"] = annotations["status_score"].map(
        lambda value: classify_status(value, args.warn_threshold, args.anomaly_threshold)
    )
    return annotations, Counter(annotations["match_strategy"]), status_basis


def _display_id(value: object) -> str:
    if pd.isna(value):
        return "?"
    try:
        number = float(value)
        if number.is_integer():
            return str(int(number))
    except (TypeError, ValueError):
        pass
    return str(value)


def _draw_panel(frame: np.ndarray, lines: list[str], origin: tuple[int, int], align_right: bool = False) -> None:
    x, y = origin
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.52
    thickness = 1
    line_height = 19
    widths = [cv2.getTextSize(line, font, scale, thickness)[0][0] for line in lines]
    width = max(widths, default=0)
    if align_right:
        x -= width
    overlay = frame.copy()
    cv2.rectangle(overlay, (max(0, x - 5), max(0, y - 15)), (min(frame.shape[1] - 1, x + width + 5), y + line_height * len(lines)), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.65, frame, 0.35, 0, frame)
    for line_number, line in enumerate(lines):
        cv2.putText(frame, line, (x, y + line_number * line_height), font, scale, (255, 255, 255), thickness, cv2.LINE_AA)


def _draw_reid_box(frame: np.ndarray, row: pd.Series) -> None:
    x1, y1, x2, y2 = (int(round(float(row[column]))) for column in ("x1", "y1", "x2", "y2"))
    status = str(row["status"])
    color = STATUS_COLORS[status]
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
    if status == "UNMATCHED":
        lines = ["UNMATCHED"]
    else:
        first_line = f"GT:{_display_id(row['track_id'])}"
        if not pd.isna(row["tracker_id"]):
            first_line += f"  T:{_display_id(row['tracker_id'])}"
        second_line = f"XCam:{float(row['xcam_distance']):.3f}"
        if np.isfinite(row["delta_xcam"]):
            second_line += f"  Delta:{float(row['delta_xcam']):+.3f}"
        lines = [first_line, f"{second_line}  {status}"]
    top = max(15 + 18 * (len(lines) - 1), y1 - 7 - 18 * (len(lines) - 1))
    _draw_panel(frame, lines, (max(0, x1), top))


def render_boxes(args: argparse.Namespace, df: pd.DataFrame) -> None:
    color_col = args.color_by if args.color_by in df.columns else None
    by_frame = {int(frame): group for frame, group in df.groupby("frame")}
    _render_video(args, by_frame, color_col=color_col)


def render_reid_distance(args: argparse.Namespace, annotations: pd.DataFrame, status_basis: str) -> None:
    by_frame = {int(frame): group for frame, group in annotations.groupby("frame")}
    _render_video(args, by_frame, status_basis=status_basis)


def _render_video(
    args: argparse.Namespace,
    by_frame: dict[int, pd.DataFrame],
    *,
    color_col: str | None = None,
    status_basis: str | None = None,
) -> None:
    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        raise SystemExit(f"Could not open video: {args.video}")
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(str(out_path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
    if not writer.isOpened():
        cap.release()
        raise SystemExit(f"Could not open output video writer: {out_path}")

    video_frame = args.frame_base
    boxes_drawn = 0
    frames_written = 0
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            rows = by_frame.get(video_frame + args.frame_offset)
            if rows is not None:
                if status_basis is None:
                    for _, row in rows.iterrows():
                        x1, y1, x2, y2 = (int(round(float(row[col]))) for col in ("x1", "y1", "x2", "y2"))
                        color = color_for(row[color_col]) if color_col else (0, 255, 0)
                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                        if color_col:
                            cv2.putText(frame, str(row[color_col]), (x1, max(0, y1 - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)
                        boxes_drawn += 1
                else:
                    for _, row in rows.iterrows():
                        _draw_reid_box(frame, row)
                        boxes_drawn += 1
                    matched = rows[rows["status"] != "UNMATCHED"]
                    value_column = "delta_xcam" if "Delta" in status_basis else "xcam_distance"
                    mean_value = matched[value_column].mean()
                    left_lines = [
                        f"Scenario: {args.scenario or '-'}",
                        f"Camera: {args.camera or '-'}",
                        f"Condition: {args.condition or '-'}",
                        f"Epsilon: {args.epsilon or '-'}",
                        f"Seed: {args.seed or '-'}",
                        f"Frame: {video_frame + args.frame_offset}",
                    ]
                    right_lines = [
                        f"Vehicles: {len(rows)}",
                        f"Warnings: {(rows['status'] == 'WARN').sum()}",
                        f"Anomalies: {(rows['status'] == 'ANOM').sum()}",
                        f"Unmatched: {(rows['status'] == 'UNMATCHED').sum()}",
                        f"Mean {'Delta ' if 'Delta' in status_basis else ''}XCam: {mean_value:+.3f}" if np.isfinite(mean_value) else "Mean XCam: n/a",
                        f"Status: {status_basis}",
                    ]
                    _draw_panel(frame, left_lines, (10, 25))
                    _draw_panel(frame, right_lines, (width - 10, 25), align_right=True)
            writer.write(frame)
            frames_written += 1
            video_frame += 1
    finally:
        cap.release()
        writer.release()

    if boxes_drawn == 0:
        print("WARNING: wrote the video but drew 0 boxes. Check --frame-offset and that the CSV belongs to this video.")
    print(f"Wrote {out_path} ({frames_written} frames, {boxes_drawn} boxes drawn)")


def main() -> None:
    args = parse_args()
    if cv2 is None:
        raise SystemExit(
            "visualize_boxes.py needs OpenCV to render videos. Install it into your env:\n"
            "    pip install opencv-python"
        )
    boxes = pd.read_csv(args.csv)
    try:
        _validate_columns(boxes, BOX_COLUMNS, "CSV")
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    if args.camera is not None and "camera" in boxes.columns:
        boxes = boxes[boxes["camera"].astype(str) == str(args.camera)]
    if boxes.empty:
        raise SystemExit("No rows to draw after filtering. Check --camera / --csv.")

    try:
        if args.annotation_mode == "boxes":
            render_boxes(args, boxes)
        else:
            annotations, strategies, status_basis = prepare_reid_annotations(args, boxes)
            print("ReID matching:", ", ".join(f"{name}={count}" for name, count in sorted(strategies.items())))
            render_reid_distance(args, annotations, status_basis)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()
