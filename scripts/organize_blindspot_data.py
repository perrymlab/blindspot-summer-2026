"""Reorganize raw intersection footage into the project's standard layout.

Project convention (CityFlowV2-style, dataset-agnostic):

    <data root>/
        S01/
            c001/vdo.mp4
            c002/vdo.mp4
            c003/vdo.mp4
        S02/
            ...

The data root defaults to ``$BLINDSPOT_DATA_ROOT`` or ``~/blindspot_data`` so
no machine-specific paths land in the repo.

Source layout this script understands (matches the current local capture):

    <source>/video 1/Intersection-Camera-1_*.mp4
             /video 1/Intersection-Camera-2_*.mp4
             /video 1/Intersection-Camera-3_*.mp4
             /video 2/...

Run with ``--apply`` to actually rename. Without it the script only prints
the planned moves (dry run).
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
from pathlib import Path


VIDEO_DIR_RE = re.compile(r"^video\s*(\d+)$", re.IGNORECASE)
CAMERA_FILE_RE = re.compile(r"Intersection-Camera-(\d+)_", re.IGNORECASE)


def default_data_root() -> Path:
    env = os.environ.get("BLINDSPOT_DATA_ROOT")
    if env:
        return Path(env).expanduser()
    return Path.home() / "blindspot_data"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=Path,
        default=default_data_root(),
        help="Folder containing the raw 'video N' subfolders. "
        "Defaults to $BLINDSPOT_DATA_ROOT or ~/blindspot_data.",
    )
    parser.add_argument(
        "--dest",
        type=Path,
        default=None,
        help="Destination data root. Defaults to --source (in-place rename).",
    )
    parser.add_argument(
        "--mode",
        choices=("move", "copy"),
        default="move",
        help="Move (default) or copy files into the new layout.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually perform the operations. Without this flag the script "
        "only prints the planned moves.",
    )
    return parser.parse_args()


def plan_operations(source: Path, dest: Path) -> list[tuple[Path, Path]]:
    ops: list[tuple[Path, Path]] = []
    for entry in sorted(source.iterdir()):
        if not entry.is_dir():
            continue
        match = VIDEO_DIR_RE.match(entry.name)
        if not match:
            continue
        scenario_idx = int(match.group(1))
        scenario_dir = dest / f"S{scenario_idx:02d}"
        for video_file in sorted(entry.iterdir()):
            if video_file.suffix.lower() != ".mp4":
                continue
            cam_match = CAMERA_FILE_RE.search(video_file.name)
            if not cam_match:
                print(f"  skip (no camera tag): {video_file}", file=sys.stderr)
                continue
            cam_idx = int(cam_match.group(1))
            target_dir = scenario_dir / f"c{cam_idx:03d}"
            target = target_dir / "vdo.mp4"
            ops.append((video_file, target))
    return ops


def main() -> int:
    args = parse_args()
    source: Path = args.source.expanduser().resolve()
    dest: Path = (args.dest or args.source).expanduser().resolve()

    if not source.exists():
        print(f"source does not exist: {source}", file=sys.stderr)
        return 1

    ops = plan_operations(source, dest)
    if not ops:
        print(f"no 'video N' folders found in {source}")
        return 0

    verb = "MOVE" if args.mode == "move" else "COPY"
    prefix = "" if args.apply else "[dry run] "
    for src, dst in ops:
        print(f"{prefix}{verb} {src}\n     -> {dst}")

    if not args.apply:
        print(f"\n{len(ops)} planned operation(s). Re-run with --apply to execute.")
        return 0

    for src, dst in ops:
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            print(f"  exists, skipping: {dst}")
            continue
        if args.mode == "move":
            shutil.move(str(src), str(dst))
        else:
            shutil.copy2(str(src), str(dst))

    if args.mode == "move":
        for entry in sorted(source.iterdir()):
            if entry.is_dir() and VIDEO_DIR_RE.match(entry.name):
                try:
                    entry.rmdir()
                except OSError:
                    pass

    print(f"\nDone. {len(ops)} file(s) processed under {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
