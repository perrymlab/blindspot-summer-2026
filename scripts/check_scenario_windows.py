"""Validate data/scenario_windows.csv against footage durations + an alternate.

Read-only diagnostic. For each scenario/camera it ffprobes the source video
(vdo.mp4) and any existing trim (vdo_trim.mp4), then flags the windows most
likely to produce near-empty BoT-SORT exports:

  * OVERRUN       - start+duration runs past the end of the footage
  * START_PAST_END- start is at/after the end of the footage (empty trim)
  * SHORT_TRIM    - an existing vdo_trim.mp4 is far shorter than duration_s
                    (stale/bad trim from an earlier window)
  * MISSING       - no source video found

It also diffs the canonical manifest against an alternate one (default:
``data/edited scenario windows.csv``) so disputed values are easy to see.

Nothing is modified; this only reads files and runs ffprobe.

Usage:
    python scripts/check_scenario_windows.py
    python scripts/check_scenario_windows.py --scenario S03 --scenario S08
    python scripts/check_scenario_windows.py --compare "data/edited scenario windows.csv"
    python scripts/check_scenario_windows.py --data-root /workspace/blindspot_data
"""

from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
import sys
from pathlib import Path

# Reuse the trimmer's parsing + path defaults so this stays in lockstep with it.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from trim_scenarios import default_data_root, default_manifest, parse_start  # noqa: E402

CAMERAS = ("c001", "c002", "c003")
SHORT_TRIM_RATIO = 0.5  # trim shorter than this fraction of duration_s = suspect


def ffprobe_duration(ffprobe: str, path: Path) -> float | None:
    """Return media duration in seconds, or None if it can't be read."""
    if not path.exists():
        return None
    try:
        out = subprocess.run(
            [ffprobe, "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", str(path)],
            check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
    except OSError:
        return None
    text = out.stdout.strip()
    try:
        return float(text)
    except ValueError:
        return None


def read_raw_manifest(path: Path) -> dict[str, dict[str, str]]:
    """Read a manifest into {scenario: {start, duration_s, notes}} keeping blanks."""
    rows: dict[str, dict[str, str]] = {}
    if not path.exists():
        return rows
    with open(path, newline="", encoding="utf-8-sig") as handle:
        for raw in csv.DictReader(handle):
            scenario = (raw.get("scenario") or "").strip()
            if not scenario:
                continue
            rows[scenario] = {
                "start": (raw.get("start") or "").strip(),
                "duration_s": (raw.get("duration_s") or "").strip(),
                "notes": (raw.get("anchor_notes") or "").strip(),
            }
    return rows


def compare_value(canonical: dict[str, str], other: dict[str, str] | None) -> str:
    if other is None:
        return "(no alt row)"
    o_start, o_dur = other["start"], other["duration_s"]
    if not o_start and not o_dur:
        return "alt blank"
    if o_start == canonical["start"] and o_dur == canonical["duration_s"]:
        return "alt agrees"
    return f"alt DIFFERS start={o_start or '-'} dur={o_dur or '-'}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--manifest", type=Path, default=default_manifest())
    parser.add_argument(
        "--compare", type=Path,
        default=Path(__file__).resolve().parents[1] / "data" / "edited scenario windows.csv",
        help="Alternate manifest to diff against (default: data/edited scenario windows.csv).",
    )
    parser.add_argument("--data-root", type=Path, default=default_data_root())
    parser.add_argument("--scenario", action="append", default=None,
                        help="Restrict to one scenario (repeatable).")
    parser.add_argument("--cameras", default=",".join(CAMERAS))
    parser.add_argument("--ffprobe", default=shutil.which("ffprobe") or "ffprobe")
    args = parser.parse_args()

    data_root = args.data_root.expanduser().resolve()
    cameras = [c.strip() for c in args.cameras.split(",") if c.strip()]
    only = set(args.scenario) if args.scenario else None

    canonical = read_raw_manifest(args.manifest)
    alternate = read_raw_manifest(args.compare)
    if not canonical:
        print(f"No rows read from {args.manifest}", file=sys.stderr)
        return 1

    print(f"manifest : {args.manifest}")
    print(f"compare  : {args.compare}  ({'found' if args.compare.exists() else 'MISSING'})")
    print(f"data-root: {data_root}\n")

    suspects: list[str] = []

    for scenario, vals in canonical.items():
        if only is not None and scenario not in only:
            continue

        start_raw, dur_raw = vals["start"], vals["duration_s"]
        diff = compare_value(vals, alternate.get(scenario))

        if not start_raw or not dur_raw:
            print(f"== {scenario} ==  start={start_raw or '-'} dur={dur_raw or '-'}  "
                  f"[manifest row not populated]  {diff}")
            suspects.append(f"{scenario} (unpopulated window)")
            continue

        try:
            start_s = parse_start(start_raw)
            duration_s = float(dur_raw)
        except ValueError as exc:
            print(f"== {scenario} ==  UNPARSEABLE window ({exc})  {diff}")
            suspects.append(f"{scenario} (unparseable)")
            continue

        end_s = start_s + duration_s
        print(f"== {scenario} ==  window [{start_s:.0f}s -> {end_s:.0f}s] "
              f"(start={start_s:.0f}, dur={duration_s:.0f})  {diff}")

        scenario_suspect = False
        for cam in cameras:
            cam_dir = data_root / scenario / cam
            vdo = cam_dir / "vdo.mp4"
            trim = cam_dir / "vdo_trim.mp4"
            src_dur = ffprobe_duration(args.ffprobe, vdo)
            trim_dur = ffprobe_duration(args.ffprobe, trim)

            flags = []
            if src_dur is None:
                flags.append("MISSING vdo.mp4")
                scenario_suspect = True
            else:
                if start_s >= src_dur:
                    flags.append(f"START_PAST_END (video {src_dur:.0f}s)")
                    scenario_suspect = True
                elif end_s > src_dur + 0.5:
                    flags.append(f"OVERRUN by {end_s - src_dur:.0f}s (video {src_dur:.0f}s)")
                    scenario_suspect = True
            if trim_dur is not None and trim_dur < SHORT_TRIM_RATIO * duration_s:
                flags.append(f"SHORT_TRIM {trim_dur:.0f}s (expected ~{duration_s:.0f}s)")
                scenario_suspect = True

            src_txt = f"{src_dur:.0f}s" if src_dur is not None else "?"
            trim_txt = f"{trim_dur:.0f}s" if trim_dur is not None else "none"
            status = "  ".join(flags) if flags else "ok"
            print(f"   {cam}: video={src_txt:>6}  trim={trim_txt:>6}   {status}")

        if scenario_suspect:
            suspects.append(scenario)
        print()

    print("=" * 60)
    if suspects:
        print(f"Suspect scenarios ({len(suspects)}): {', '.join(suspects)}")
        print("Fix the window in data/scenario_windows.csv (or confirm footage), "
              "then re-trim + re-export those scenarios.")
        return 1
    print("All checked windows fit within their footage and have valid trims.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
