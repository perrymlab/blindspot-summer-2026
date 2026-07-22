"""Batch-render cross-camera ReID degradation videos from BoT-SORT exports.

Defaults target the Linux pod layout. Rendering is intentionally sequential and
CPU-only: this script only invokes the OpenCV overlay renderer and never reruns
tracking or embedding extraction.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

BOX_COLUMNS = {"frame", "x1", "y1", "x2", "y2"}
TRACKED_COLUMNS = BOX_COLUMNS | {"camera", "embedding", "track_id"}
DEFAULT_SCENARIOS = [f"S{number:02d}" for number in range(1, 9)]


@dataclass(frozen=True)
class RenderJob:
    scenario: str
    result_camera: str
    condition: str
    box_csv: Path
    tracked_csv: Path | None
    clean_tracked_csv: Path | None
    video: Path
    output: Path


def csv_stem(path: Path) -> str:
    name = path.name
    if name.endswith(".csv.gz"):
        return name[:-7]
    if name.endswith(".csv"):
        return name[:-4]
    raise ValueError(f"expected .csv or .csv.gz filename: {path}")


def normalize_result_camera(camera: str) -> str:
    groups = re.findall(r"\d+", camera)
    if not groups:
        raise ValueError(f"invalid camera token: {camera!r}")
    return f"c{int(groups[-1]):02d}"


def video_camera(camera: str) -> str:
    """Map result IDs such as c01/c1/c001 to source-video directories c001."""
    groups = re.findall(r"\d+", camera)
    if not groups:
        raise ValueError(f"invalid camera token: {camera!r}")
    return f"c{int(groups[-1]):03d}"


def parse_per_camera_filename(path: Path) -> tuple[str, str, str] | None:
    """Parse a per-camera export into scenario, result camera, and condition."""
    stem = csv_stem(path)
    if "_all-cams" in stem:
        return None
    match = re.fullmatch(r"(S\d+)_((?:c|cam)\d+)_(.+)", stem)
    if not match:
        return None
    scenario, camera, condition = match.groups()
    return scenario, normalize_result_camera(camera), condition


def find_tracked_csv(directory: Path, scenario: str, condition: str, preferred: Path | None = None) -> Path | None:
    base = f"{scenario}_{condition}_all-cams_tracked"
    extensions = [".csv", ".csv.gz"]
    if preferred is not None and preferred.name.endswith(".csv.gz"):
        extensions.reverse()
    for extension in extensions:
        candidate = directory / f"{base}{extension}"
        if candidate.is_file():
            return candidate
    return None


def output_path(output_root: Path, scenario: str, box_csv: Path) -> Path:
    return output_root / scenario / f"{csv_stem(box_csv)}_reid-distance.mp4"


def condition_metadata(condition: str) -> tuple[str, str | None, str | None]:
    """Return human-readable condition, epsilon, and seed for the HUD."""
    if condition == "clean":
        return "clean", None, None
    match = re.fullmatch(r"(poison_.+)_eps([^_]+)_seed(.+)", condition)
    if not match:
        return condition, None, None
    return match.group(1), match.group(2), match.group(3)


def discover_jobs(
    results_root: Path,
    video_root: Path,
    output_root: Path,
    scenarios: list[str],
    video_name: str,
    experiment_filter: str | None = None,
    camera_filter: str | None = None,
    use_clean_reference: bool = False,
) -> list[RenderJob]:
    jobs: list[RenderJob] = []
    requested_camera = normalize_result_camera(camera_filter) if camera_filter else None
    for scenario in scenarios:
        scenario_dir = results_root / scenario
        if not scenario_dir.is_dir():
            continue
        candidates = sorted(
            [*scenario_dir.glob("*.csv"), *scenario_dir.glob("*.csv.gz")], key=lambda path: path.name
        )
        for box_csv in candidates:
            parsed = parse_per_camera_filename(box_csv)
            if parsed is None:
                continue
            file_scenario, camera, condition = parsed
            if file_scenario != scenario:
                continue
            if requested_camera and camera != requested_camera:
                continue
            if experiment_filter and experiment_filter not in condition and experiment_filter not in box_csv.name:
                continue
            tracked_csv = find_tracked_csv(scenario_dir, scenario, condition, box_csv)
            clean_csv = (
                find_tracked_csv(scenario_dir, scenario, "clean", box_csv) if use_clean_reference else None
            )
            jobs.append(
                RenderJob(
                    scenario=scenario,
                    result_camera=camera,
                    condition=condition,
                    box_csv=box_csv,
                    tracked_csv=tracked_csv,
                    clean_tracked_csv=clean_csv,
                    video=video_root / scenario / video_camera(camera) / video_name,
                    output=output_path(output_root, scenario, box_csv),
                )
            )
    return jobs


def _schema_supported(path: Path, required: set[str]) -> bool:
    try:
        columns = set(pd.read_csv(path, nrows=1).columns)
    except (OSError, ValueError, pd.errors.ParserError):
        return False
    return required.issubset(columns)


def build_command(job: RenderJob, args: argparse.Namespace) -> list[str]:
    condition, epsilon, seed = condition_metadata(job.condition)
    command = [
        sys.executable,
        str(Path(args.repo_root) / "scripts" / "visualize_boxes.py"),
        "--csv",
        str(job.box_csv),
        "--video",
        str(job.video),
        "--out",
        str(job.output),
        "--camera",
        job.result_camera,
        "--annotation-mode",
        "reid-distance",
        "--tracked-csv",
        str(job.tracked_csv),
        "--reid-iou-threshold",
        str(args.reid_iou_threshold),
        "--warn-threshold",
        str(args.warn_threshold),
        "--anomaly-threshold",
        str(args.anomaly_threshold),
        "--scenario",
        job.scenario,
        "--condition",
        condition,
    ]
    if epsilon is not None:
        command.extend(["--epsilon", epsilon])
    if seed is not None:
        command.extend(["--seed", seed])
    if args.clean_reference:
        command.extend(["--clean-tracked-csv", str(job.clean_tracked_csv)])
    return command


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Batch-render CPU-only cross-camera ReID degradation videos.")
    parser.add_argument("--repo-root", default="/workspace/blindspot-summer-2026", help="Repository root containing scripts/.")
    parser.add_argument("--results-root", help="BoT-SORT result root; default is <repo-root>/runs/botsort.")
    parser.add_argument("--video-root", default="/workspace/blindspot_data", help="Source-video root containing S01/c001/vdo_trim.mp4.")
    parser.add_argument("--output-root", help="Output root; default is <repo-root>/results/reid-videos.")
    parser.add_argument("--scenarios", nargs="+", default=DEFAULT_SCENARIOS, help="Scenarios to discover (default: S01 through S08).")
    parser.add_argument("--experiment-filter", help="Only render candidates whose condition or filename contains this text.")
    parser.add_argument("--camera", help="Only render this result camera, e.g. c01.")
    parser.add_argument("--video-name", default="vdo_trim.mp4", help="Video filename below each normalized camera directory.")
    parser.add_argument("--clean-reference", action="store_true", help="Pass each scenario clean tracked CSV for clean-reference deltas.")
    parser.add_argument("--warn-threshold", type=float, default=0.15, help="WARN threshold passed to the visualizer.")
    parser.add_argument("--anomaly-threshold", type=float, default=0.30, help="ANOM threshold passed to the visualizer.")
    parser.add_argument("--reid-iou-threshold", type=float, default=0.5, help="IoU fallback threshold passed to the visualizer.")
    parser.add_argument("--overwrite", action="store_true", help="Render even when the output video already exists.")
    parser.add_argument("--dry-run", action="store_true", help="Discover and validate jobs without encoding videos.")
    parser.add_argument("--fail-fast", action="store_true", help="Stop after the first failed render.")
    parser.add_argument("--allow-partial-success", action="store_true", help="Return zero even if one or more candidate renders fail.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not 0 <= args.reid_iou_threshold <= 1:
        raise SystemExit("--reid-iou-threshold must be between 0 and 1")
    if not 0 <= args.warn_threshold <= args.anomaly_threshold:
        raise SystemExit("thresholds must satisfy 0 <= --warn-threshold <= --anomaly-threshold")

    repo_root = Path(args.repo_root)
    args.repo_root = str(repo_root)
    results_root = Path(args.results_root) if args.results_root else repo_root / "runs" / "botsort"
    video_root = Path(args.video_root)
    output_root = Path(args.output_root) if args.output_root else repo_root / "results" / "reid-videos"
    jobs = discover_jobs(
        results_root,
        video_root,
        output_root,
        args.scenarios,
        args.video_name,
        args.experiment_filter,
        args.camera,
        args.clean_reference,
    )
    rendered = skipped = failed = 0
    for job in jobs:
        if job.tracked_csv is None:
            print(f"SKIP: missing tracked CSV {job.box_csv}")
            skipped += 1
            continue
        if args.clean_reference and job.clean_tracked_csv is None:
            print(f"SKIP: missing clean tracked CSV {job.box_csv}")
            skipped += 1
            continue
        if not job.video.is_file():
            print(f"SKIP: missing source video {job.video}")
            skipped += 1
            continue
        if not _schema_supported(job.box_csv, BOX_COLUMNS) or not _schema_supported(job.tracked_csv, TRACKED_COLUMNS):
            print(f"SKIP: schema unsupported {job.box_csv}")
            skipped += 1
            continue
        if args.clean_reference and not _schema_supported(job.clean_tracked_csv, TRACKED_COLUMNS):
            print(f"SKIP: schema unsupported {job.clean_tracked_csv}")
            skipped += 1
            continue
        if job.output.exists() and not args.overwrite:
            print(f"SKIP: output exists {job.output}")
            skipped += 1
            continue
        command = build_command(job, args)
        print(f"RENDER: {job.box_csv} -> {job.output}")
        if args.dry_run:
            print("  " + " ".join(command))
            rendered += 1
            continue
        try:
            completed = subprocess.run(command, check=False)
        except OSError as exc:
            print(f"FAIL: {job.box_csv}: {exc}")
            failed += 1
        else:
            if completed.returncode:
                print(f"FAIL: {job.box_csv}: visualizer exited {completed.returncode}")
                failed += 1
            else:
                rendered += 1
        if failed and args.fail_fast:
            break

    print(f"Discovered: {len(jobs)}")
    print(f"Rendered: {rendered}")
    print(f"Skipped: {skipped}")
    print(f"Failed: {failed}")
    print(f"Output root: {output_root}")
    if failed and not args.allow_partial_success:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
