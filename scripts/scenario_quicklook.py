"""Render a side-by-side composite frame per scenario for PR review.

For each populated row in ``data/scenario_windows.csv`` this script extracts
one frame from each camera at the midpoint of the trim window
(``start + duration / 2``) and writes a horizontally stacked PNG to
``runs/quicklook/<scenario>.png``. Reviewers (Sabrina) can flip through these
PNGs to confirm that the anchor vehicle described in ``anchor_notes`` really
is visible in all three cameras at the chosen moment, without scrubbing video.

By default the source is each camera's original ``vdo.mp4``. Pass
``--source trim`` to instead read the trimmed ``vdo_trim.mp4`` and sample its
local midpoint.

ffmpeg must be on PATH.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Reuse the manifest loader and start parser from trim_scenarios.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from trim_scenarios import (  # noqa: E402
    DEFAULT_CAMERAS,
    Window,
    default_data_root,
    default_manifest,
    load_manifest,
)


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
        "--out",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "runs" / "quicklook",
        help="Directory to write composite PNGs into.",
    )
    parser.add_argument(
        "--source",
        choices=("original", "trim"),
        default="original",
        help="Read frames from vdo.mp4 (default) or vdo_trim.mp4.",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=1920,
        help="Total composite width in pixels (default: 1920).",
    )
    parser.add_argument(
        "--tile-height",
        type=int,
        default=720,
        help="Per-camera tile height in pixels before hstack (default: 720). "
        "Each input is scaled to this height (preserving aspect ratio) so cameras "
        "with different native resolutions can be stacked.",
    )
    parser.add_argument(
        "--ffmpeg",
        default=shutil.which("ffmpeg") or "ffmpeg",
        help="Path to ffmpeg executable.",
    )
    return parser.parse_args()


def build_quicklook_cmd(
    ffmpeg: str,
    sources: list[Path],
    seek_per_input: list[float],
    width: int,
    tile_height: int,
    out_path: Path,
) -> list[str]:
    cmd = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y"]
    for src, seek in zip(sources, seek_per_input):
        cmd += ["-ss", f"{seek:.3f}", "-i", str(src)]
    n = len(sources)
    scales = ";".join(
        f"[{i}:v]scale=-2:{tile_height}:flags=lanczos[v{i}]" for i in range(n)
    )
    stacked_inputs = "".join(f"[v{i}]" for i in range(n))
    filter_complex = (
        f"{scales};{stacked_inputs}hstack=inputs={n},scale={width}:-2:flags=lanczos"
    )
    cmd += ["-filter_complex", filter_complex, "-frames:v", "1", str(out_path)]
    return cmd


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
        print("No populated manifest rows to render.")
        return 0

    args.out.mkdir(parents=True, exist_ok=True)
    failures = 0

    for window in windows:
        if args.source == "trim":
            src_name = "vdo_trim.mp4"
            seek = window.duration_s / 2.0
        else:
            src_name = "vdo.mp4"
            seek = window.start_s + window.duration_s / 2.0

        sources = [data_root / window.scenario / cam / src_name for cam in cameras]
        missing = [str(p) for p in sources if not p.exists()]
        if missing:
            print(f"  skip {window.scenario}: missing {missing}", file=sys.stderr)
            failures += 1
            continue

        out_path = args.out / f"{window.scenario}.png"
        cmd = build_quicklook_cmd(
            args.ffmpeg,
            sources,
            [seek] * len(sources),
            args.width,
            args.tile_height,
            out_path,
        )
        print(f"  {window.scenario}: midpoint={seek:.3f}s -> {out_path}")
        result = subprocess.run(cmd)
        if result.returncode != 0:
            print(
                f"  FAIL {window.scenario} (ffmpeg exit {result.returncode})",
                file=sys.stderr,
            )
            failures += 1

    if failures:
        print(f"\n{failures} scenario(s) failed.", file=sys.stderr)
        return 1
    print(f"\nDone. Composites written to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
