from __future__ import annotations

import argparse
import zlib
from pathlib import Path

import pandas as pd

try:
    import cv2
except ImportError as exc:  # pragma: no cover - dependency hint
    raise SystemExit(
        "visualize_boxes.py needs OpenCV. Install it into your env:\n"
        "    pip install opencv-python"
    ) from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Overlay the detection boxes from a BoT-SORT embedding CSV "
        "onto its source video. The CSV carries x1,y1,x2,y2 per detection; this "
        "draws them so you can see what was tracked without re-running BoT-SORT."
    )
    parser.add_argument("--csv", required=True, help="CSV written by --prime-export-embeddings")
    parser.add_argument("--video", required=True, help="Source video the CSV was exported from")
    parser.add_argument("--out", default="runs/embedding_analysis/boxes.mp4", help="Output annotated video")
    parser.add_argument("--camera", default=None, help="Only draw rows for this camera id")
    parser.add_argument(
        "--color-by",
        default="detection_index",
        help="Column used to pick box color/label (use track_id if your CSV has merged ids).",
    )
    parser.add_argument(
        "--frame-base",
        type=int,
        default=1,
        help="Frame number assigned to the FIRST video frame. BoT-SORT exports "
        "are 1-based, so the default is 1.",
    )
    parser.add_argument(
        "--frame-offset",
        type=int,
        default=0,
        help="Extra shift added to the video frame counter before matching the "
        "CSV 'frame' column. Use +/-1 if the boxes look one frame off.",
    )
    return parser.parse_args()


def color_for(value: object) -> tuple[int, int, int]:
    """Deterministic BGR color for a label (stable across runs)."""
    digest = zlib.crc32(str(value).encode("utf-8"))
    return (digest & 255, (digest >> 8) & 255, (digest >> 16) & 255)


def main() -> None:
    args = parse_args()

    df = pd.read_csv(args.csv)
    required = {"frame", "x1", "y1", "x2", "y2"}
    missing = required - set(df.columns)
    if missing:
        raise SystemExit(f"CSV is missing required columns: {sorted(missing)}")

    if args.camera is not None and "camera" in df.columns:
        df = df[df["camera"].astype(str) == str(args.camera)]
    if df.empty:
        raise SystemExit("No rows to draw after filtering. Check --camera / --csv.")

    color_col = args.color_by if args.color_by in df.columns else None
    by_frame = {int(frame): group for frame, group in df.groupby("frame")}

    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        raise SystemExit(f"Could not open video: {args.video}")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(
        str(out_path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height)
    )

    video_frame = args.frame_base
    boxes_drawn = 0
    frames_written = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        rows = by_frame.get(video_frame + args.frame_offset)
        if rows is not None:
            for _, row in rows.iterrows():
                x1, y1, x2, y2 = (
                    int(round(float(row[col]))) for col in ("x1", "y1", "x2", "y2")
                )
                color = color_for(row[color_col]) if color_col else (0, 255, 0)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                if color_col:
                    cv2.putText(
                        frame,
                        str(row[color_col]),
                        (x1, max(0, y1 - 5)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        color,
                        1,
                        cv2.LINE_AA,
                    )
                boxes_drawn += 1
        writer.write(frame)
        frames_written += 1
        video_frame += 1

    cap.release()
    writer.release()

    if boxes_drawn == 0:
        print(
            "WARNING: wrote the video but drew 0 boxes. The CSV 'frame' values "
            "likely do not line up with the video; try --frame-offset 1 or -1, "
            "or confirm this CSV came from this exact video."
        )
    print(f"Wrote {out_path} ({frames_written} frames, {boxes_drawn} boxes drawn)")


if __name__ == "__main__":
    main()
