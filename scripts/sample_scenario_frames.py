"""Sample frames from each scenario/camera and auto-triage day vs night.

RESEARCHER tool. The under-detection on S03/S10/S12/S13/S18 turned out to be
night/low-light footage, not a detector-config problem (see docs/STATUS.md
Decisions log 2026-06-19). This script samples a handful of frames per camera,
saves them for eyeballing, and classifies each clip by mean brightness so we
can tell at a glance which scenarios are daytime (usable for ground truth) and
which are dark (smoke-only, like S10).

    # triage every scenario in data/scenario_windows.csv
    python scripts/sample_scenario_frames.py

    # specific scenarios, more frames each
    python scripts/sample_scenario_frames.py S03 S10 S11 --frames 8

Output:
    runs/frame_triage/<scenario>/<scenario>_<cam>_f<NN>.png   <- sampled stills
    runs/frame_triage/brightness.csv                          <- per-camera table

Brightness is mean luma (0-255) over the sampled frames. Defaults: NIGHT < 55,
DUSK < 95, else DAY -- tune with --night-threshold / --dusk-threshold and the
printed values if a clip is misclassified.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import List, Optional

try:
    import cv2
except ImportError as exc:  # pragma: no cover - dependency hint
    raise SystemExit(
        "sample_scenario_frames.py needs OpenCV. Install it into your env:\n"
        "    pip install opencv-python"
    ) from exc

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from run_baselines import (  # noqa: E402
    DEFAULT_CAMERAS, default_data_root, find_video, scenarios_from_manifest, short_cam,
)

REPO_ROOT = SCRIPT_DIR.parent
DEFAULT_OUT_DIR = REPO_ROOT / "runs" / "frame_triage"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("scenarios", nargs="*",
                        help="Scenario ids (e.g. S03 S10). Default: all in scenario_windows.csv.")
    parser.add_argument("--data-root", default=None, help="Override footage root.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR), help="Where to write stills + brightness.csv.")
    parser.add_argument("--frames", type=int, default=5, help="Frames sampled per camera (evenly spaced).")
    parser.add_argument("--night-threshold", type=float, default=55.0, help="Mean luma below this = NIGHT.")
    parser.add_argument("--dusk-threshold", type=float, default=95.0, help="Mean luma below this = DUSK.")
    return parser.parse_args()


def classify(mean_luma: float, night: float, dusk: float) -> str:
    if mean_luma < night:
        return "NIGHT"
    if mean_luma < dusk:
        return "DUSK"
    return "DAY"


def sample_camera(video: Path, n_frames: int, out_dir: Path, prefix: str) -> Optional[float]:
    cap = cv2.VideoCapture(str(video))
    if not cap.isOpened():
        print(f"  WARNING: could not open {video}")
        return None
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
    if total <= 0:
        print(f"  WARNING: no frames reported for {video}")
        cap.release()
        return None

    out_dir.mkdir(parents=True, exist_ok=True)
    targets = [int((i + 1) * total / (n_frames + 1)) for i in range(n_frames)]
    lumas: List[float] = []
    for idx, frame_no in enumerate(targets, start=1):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
        ok, frame = cap.read()
        if not ok or frame is None:
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        lumas.append(float(gray.mean()))
        cv2.imwrite(str(out_dir / f"{prefix}_f{idx:02d}.png"), frame)
    cap.release()
    if not lumas:
        return None
    return sum(lumas) / len(lumas)


def main() -> None:
    args = parse_args()
    data_root = Path(args.data_root).expanduser() if args.data_root else default_data_root()
    out_dir = Path(args.out_dir)
    scenarios = args.scenarios or scenarios_from_manifest()

    rows = []
    for scenario in scenarios:
        print(f"===== {scenario} =====")
        for camera_dir in DEFAULT_CAMERAS:
            cam = short_cam(camera_dir)
            video = find_video(data_root, scenario, camera_dir)
            if video is None:
                print(f"  {cam}: no video -- skip")
                continue
            scene_dir = out_dir / scenario
            mean_luma = sample_camera(video, args.frames, scene_dir, f"{scenario}_{cam}")
            if mean_luma is None:
                print(f"  {cam}: unreadable -- skip")
                continue
            verdict = classify(mean_luma, args.night_threshold, args.dusk_threshold)
            print(f"  {cam}: mean luma {mean_luma:6.1f}  ->  {verdict}   ({video.name})")
            rows.append({"scenario": scenario, "camera": cam,
                         "mean_luma": round(mean_luma, 1), "verdict": verdict,
                         "video": str(video)})

    if not rows:
        print("\nNo cameras sampled.")
        return

    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "brightness.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["scenario", "camera", "mean_luma", "verdict", "video"])
        writer.writeheader()
        writer.writerows(rows)

    print("\n" + "=" * 60)
    tally = {"DAY": [], "DUSK": [], "NIGHT": []}
    for row in rows:
        tally[row["verdict"]].append(f"{row['scenario']}/{row['camera']}")
    for verdict in ("DAY", "DUSK", "NIGHT"):
        members = tally[verdict]
        print(f"{verdict} ({len(members)}): {', '.join(members) if members else '--'}")
    print(f"\nStills + table written under {out_dir}")
    print(f"Brightness table: {csv_path}")


if __name__ == "__main__":
    main()
