"""Trim each scenario's three camera videos to a chosen wall-clock window.

The window for each scenario is read from a manifest CSV
(``data/scenario_windows.csv`` by default) with columns:

    scenario,start,duration_s,anchor_notes

``start`` accepts either plain seconds (``90``, ``90.5``) or an HMS string
(``00:01:30``, ``1:30``, ``1:30.5``). Rows with empty ``start`` or empty
``duration_s`` are skipped with a notice so the manifest can be filled in
incrementally as scenarios are reviewed.

For each populated row this script runs::

    ffmpeg -ss <start> -i <data_root>/<scenario>/<cam>/vdo.mp4
           -t <duration_s> -c copy -an
           <data_root>/<scenario>/<cam>/vdo_trim.mp4

Stream copy (``-c copy``) is fast and lossless but snaps to the nearest
keyframe at the cut points; for sub-second-accurate trims pass
``--reencode``. Originals are never modified.

Default behaviour is a dry run; pass ``--apply`` to actually invoke ffmpeg.
"""

from __future__ import annotations

import argparse
import csv
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


DEFAULT_CAMERAS = ("c001", "c002", "c003")


def default_data_root() -> Path:
    env = os.environ.get("BLINDSPOT_DATA_ROOT")
    if env:
        return Path(env).expanduser()
    for candidate in (Path("/workspace/blindspot_data"), Path.home() / "blindspot_data"):
        if candidate.is_dir():
            return candidate
    return Path.home() / "blindspot_data"


def default_manifest() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "scenario_windows.csv"


def parse_start(value: str) -> float:
    """Parse a manifest ``start`` value into seconds (float)."""
    text = value.strip()
    if not text:
        raise ValueError("empty start value")
    if ":" in text:
        parts = text.split(":")
        if len(parts) == 2:
            hours = 0.0
            minutes, seconds = parts
        elif len(parts) == 3:
            hours, minutes, seconds = parts
        else:
            raise ValueError(f"unrecognized HMS value: {value!r}")
        return float(hours) * 3600 + float(minutes) * 60 + float(seconds)
    return float(text)


@dataclass(frozen=True)
class Window:
    scenario: str
    start_s: float
    duration_s: float
    notes: str


def load_manifest(path: Path, only: set[str] | None) -> list[Window]:
    if not path.exists():
        raise FileNotFoundError(f"manifest not found: {path}")
    rows: list[Window] = []
    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        for raw in reader:
            scenario = (raw.get("scenario") or "").strip()
            if not scenario:
                continue
            if only is not None and scenario not in only:
                continue
            start_raw = (raw.get("start") or "").strip()
            duration_raw = (raw.get("duration_s") or "").strip()
            if not start_raw or not duration_raw:
                print(f"  skip {scenario}: manifest row not populated yet")
                continue
            try:
                start_s = parse_start(start_raw)
                duration_s = float(duration_raw)
            except ValueError as exc:
                print(f"  skip {scenario}: cannot parse window ({exc})", file=sys.stderr)
                continue
            if duration_s <= 0:
                print(f"  skip {scenario}: duration must be positive", file=sys.stderr)
                continue
            rows.append(
                Window(
                    scenario=scenario,
                    start_s=start_s,
                    duration_s=duration_s,
                    notes=(raw.get("anchor_notes") or "").strip(),
                )
            )
    return rows


def build_ffmpeg_cmd(
    ffmpeg: str,
    src: Path,
    dst: Path,
    start_s: float,
    duration_s: float,
    reencode: bool,
) -> list[str]:
    cmd = [
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-ss",
        f"{start_s:.3f}",
        "-i",
        str(src),
        "-t",
        f"{duration_s:.3f}",
        "-an",
    ]
    if reencode:
        cmd += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18"]
    else:
        cmd += ["-c", "copy"]
    cmd.append(str(dst))
    return cmd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=default_manifest())
    parser.add_argument("--data-root", type=Path, default=default_data_root())
    parser.add_argument(
        "--scenario",
        action="append",
        default=None,
        help="Restrict to one scenario (e.g. S01). May be passed multiple times.",
    )
    parser.add_argument(
        "--cameras",
        default=",".join(DEFAULT_CAMERAS),
        help=f"Comma-separated camera subfolders (default: {','.join(DEFAULT_CAMERAS)}).",
    )
    parser.add_argument(
        "--output-suffix",
        default="_trim",
        help="Output filename stem suffix; produces vdo<suffix>.mp4 (default: _trim).",
    )
    parser.add_argument(
        "--reencode",
        action="store_true",
        help="Re-encode for sub-second-accurate trims (slower). Default: stream copy.",
    )
    parser.add_argument(
        "--ffmpeg",
        default=shutil.which("ffmpeg") or "ffmpeg",
        help="Path to ffmpeg executable.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually run ffmpeg. Without this flag, planned commands are printed.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data_root: Path = args.data_root.expanduser().resolve()
    cameras = [item.strip() for item in args.cameras.split(",") if item.strip()]
    only = set(args.scenario) if args.scenario else None

    if shutil.which(args.ffmpeg) is None and not Path(args.ffmpeg).exists():
        print(f"ffmpeg not found: {args.ffmpeg}", file=sys.stderr)
        return 1

    windows = load_manifest(args.manifest, only)
    if not windows:
        print("No populated manifest rows to process.")
        return 0

    planned: list[tuple[Window, str, list[str], Path]] = []
    for window in windows:
        for cam in cameras:
            src = data_root / window.scenario / cam / "vdo.mp4"
            dst = data_root / window.scenario / cam / f"vdo{args.output_suffix}.mp4"
            if not src.exists():
                print(
                    f"  skip {window.scenario}/{cam}: source missing ({src})",
                    file=sys.stderr,
                )
                continue
            cmd = build_ffmpeg_cmd(
                args.ffmpeg, src, dst, window.start_s, window.duration_s, args.reencode
            )
            planned.append((window, cam, cmd, dst))

    if not planned:
        print("Nothing to do after resolving sources.")
        return 0

    prefix = "" if args.apply else "[dry run] "
    for window, cam, cmd, dst in planned:
        print(
            f"{prefix}{window.scenario}/{cam}  "
            f"start={window.start_s:.3f}s dur={window.duration_s:.3f}s -> {dst}"
        )

    if not args.apply:
        print(f"\n{len(planned)} planned operation(s). Re-run with --apply to execute.")
        return 0

    failures = 0
    for window, cam, cmd, dst in planned:
        dst.parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(cmd)
        if result.returncode != 0:
            print(f"  FAIL {window.scenario}/{cam} (ffmpeg exit {result.returncode})", file=sys.stderr)
            failures += 1
        else:
            print(f"  done {window.scenario}/{cam} -> {dst.name}")

    if failures:
        print(f"\n{failures} ffmpeg invocation(s) failed.", file=sys.stderr)
        return 1
    print(f"\nDone. {len(planned)} file(s) written under {data_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
