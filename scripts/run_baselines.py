"""Batch-run clean and poisoned BoT-SORT baselines for one or more scenarios.

RESEARCHER tool (GPU box, conda `botsort` env, Python 3.9). Replaces the
hand-typed per-camera commands in docs/botsort-integration/BOTSORT_GPU_RUNBOOK.md
section 6 with one command per batch:

    # plan only (default; prints every command it would run)
    python scripts/run_baselines.py --scenarios S01,S02

    # actually run
    python scripts/run_baselines.py --scenarios S01,S02 --apply

    # everything in data/scenario_windows.csv, sweep epsilons
    python scripts/run_baselines.py --all --epsilons 0.1,0.5,1.0 --apply

For each scenario it runs every camera twice (clean, poisoned), then merges
the per-camera exports into one per-scenario CSV that
scripts/analyze_embedding_export.py can consume directly (the cross-camera
detector needs all cameras in a single table).

Output layout (intuitive, self-describing names):

    runs/botsort/S01/
        S01_c01_clean.csv
        S01_c02_clean.csv
        S01_c03_clean.csv
        S01_clean_all-cams.csv                      <- hand to students
        S01_c01_poison_c01-c02_eps0.5_seed7.csv
        ...
        S01_poison_c01-c02_eps0.5_seed7_all-cams.csv <- hand to students
    runs/botsort/run_manifest.csv                    <- one row per run (provenance)

Every run is also appended to run_manifest.csv with the exact command,
scenario, camera, mode, epsilon, seed, poison set, video path, exit code, and
timestamp -- the fields the run log requires.

Notes:
- Prefers the trimmed video (vdo_trim.mp4) and falls back to vdo.mp4 with a
  warning. Trim first: scripts/trim_scenarios.py (see docs/data/SCENARIO_TRIMMING.md).
- Skips runs whose output CSV already exists (resume-friendly); use
  --overwrite to redo them.
- Must be run from the repo root on the GPU box, with the patched checkout in
  vendor/BoT-SORT and weights in vendor/BoT-SORT/pretrained/ (runbook steps 1-5).
"""
from __future__ import annotations

import argparse
import csv
import datetime
import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
BOT_SORT_DIR = REPO_ROOT / "vendor" / "BoT-SORT"
DEFAULT_OUT_ROOT = REPO_ROOT / "runs" / "botsort"
DEFAULT_CAMERAS = ("c001", "c002", "c003")
MANIFEST_FIELDS = [
    "timestamp",
    "scenario",
    "camera",
    "mode",
    "poison_cameras",
    "epsilon",
    "seed",
    "video",
    "output_csv",
    "returncode",
    "command",
]


def short_cam(camera_dir: str) -> str:
    """Map a camera folder name like c001 to the export id c01."""
    return "c" + str(int(camera_dir.lstrip("c"))).zfill(2)


def default_data_root() -> Path:
    env = os.environ.get("BLINDSPOT_DATA_ROOT")
    if env:
        return Path(env).expanduser()
    for candidate in (Path("/workspace/blindspot_data"), Path.home() / "blindspot_data"):
        if candidate.is_dir():
            return candidate
    return Path.home() / "blindspot_data"


def scenarios_from_manifest() -> List[str]:
    manifest = REPO_ROOT / "data" / "scenario_windows.csv"
    with open(manifest, newline="", encoding="utf-8-sig") as handle:
        return [row["scenario"].strip() for row in csv.DictReader(handle) if row.get("scenario", "").strip()]


def find_video(data_root: Path, scenario: str, camera_dir: str) -> Optional[Path]:
    trimmed = data_root / scenario / camera_dir / "vdo_trim.mp4"
    raw = data_root / scenario / camera_dir / "vdo.mp4"
    if trimmed.exists():
        return trimmed
    if raw.exists():
        print(f"  WARNING: no trimmed video for {scenario}/{camera_dir}; "
              f"falling back to full {raw.name}. Trim first for comparable runs.")
        return raw
    return None


def poison_tag(poison_cameras: List[str], epsilon: float, seed: int) -> str:
    return "poison_{}_eps{}_seed{}".format("-".join(poison_cameras), epsilon, seed)


def build_command(video: Path, camera_id: str, out_csv: Path,
                  poison_cameras: List[str], epsilon: Optional[float], seed: int,
                  save_result: bool) -> List[str]:
    cmd = [
        sys.executable, "tools/demo.py", "video",
        "--path", str(video),
        "-f", "yolox/exps/default/yolox_x.py",
        "--ckpt", "pretrained/yolox_x.pth",
        "--prime-classes", "2,3,5,7",
        "--aspect_ratio_thresh", "10",
        "--with-reid",
        "--fast-reid-config", "fast_reid/configs/VeRi/sbs_R50-ibn.yml",
        "--fast-reid-weights", "pretrained/veri_sbs_R50-ibn.pth",
        "--prime-camera-id", camera_id,
        "--prime-export-embeddings", str(out_csv),
    ]
    if epsilon is not None:
        cmd += [
            "--prime-poison-cameras", ",".join(poison_cameras),
            "--prime-poison-epsilon", str(epsilon),
            "--prime-poison-seed", str(seed),
        ]
    if save_result:
        cmd.append("--save_result")
    return cmd


def append_manifest(out_root: Path, row: dict) -> None:
    manifest = out_root / "run_manifest.csv"
    new_file = not manifest.exists()
    with open(manifest, "a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=MANIFEST_FIELDS)
        if new_file:
            writer.writeheader()
        writer.writerow(row)


def merge_camera_csvs(per_camera: List[Path], merged: Path) -> bool:
    """Concatenate per-camera exports (same header) into one scenario CSV."""
    existing = [path for path in per_camera if path.exists()]
    if len(existing) != len(per_camera):
        missing = [str(p.name) for p in per_camera if not p.exists()]
        print(f"  WARNING: not merging {merged.name}; missing {', '.join(missing)}")
        return False
    with open(merged, "w", encoding="utf-8") as out:
        for index, path in enumerate(existing):
            with open(path, encoding="utf-8") as src:
                header = src.readline()
                if index == 0:
                    out.write(header)
                for line in src:
                    out.write(line)
    print(f"  merged -> {merged}")
    return True


def tracked_path(merged: Path) -> Path:
    """Ground-truth-joined sibling of a merged export (build_track_ids output).

    Must match the name make_progress_report.resolve_join() looks for so the
    report auto-prefers it: ``<merged_stem>_tracked.csv``.
    """
    return merged.with_name(f"{merged.stem}_tracked.csv")


def print_ground_truth_handoff(merged_files: List[Path]) -> None:
    """Print the build_track_ids.py command for each merged export.

    A merged ``*_all-cams.csv`` is keyed only on ``detection_index`` (a
    positional, per-frame index with no cross-camera identity), so it is a
    smoke-check input, not a result. Joining ground-truth annotations produces
    a ``*_tracked.csv`` with a real global ``track_id`` that the detector and
    make_progress_report.py can trust.
    """
    if not merged_files:
        return
    print("\nNext: join ground-truth global track ids (analysis/reporting must be")
    print("keyed on track_id, not the positional detection_index in the merged")
    print("CSV). For each scenario with completed annotations under")
    print("data/annotations/<scenario>/ (see scripts/save_annotations.sh):")
    for merged in merged_files:
        scenario = merged.parent.name
        ann = REPO_ROOT / "data" / "annotations" / scenario
        tracked = tracked_path(merged)
        print(f"\n  python scripts/build_track_ids.py \\")
        print(f"    --export {merged} \\")
        print(f"    --matches {ann}/matches.json \\")
        print(f"    --tracks c01={ann}/tracks/c01.tracks.json \\")
        print(f"             c02={ann}/tracks/c02.tracks.json \\")
        print(f"             c03={ann}/tracks/c03.tracks.json \\")
        print(f"    --output {tracked}")
    print("\nmake_progress_report.py auto-prefers these *_tracked.csv files when present.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    which = parser.add_mutually_exclusive_group(required=True)
    which.add_argument("--scenarios", help="Comma-separated scenario ids, e.g. S01,S02")
    which.add_argument("--all", action="store_true",
                       help="All scenarios listed in data/scenario_windows.csv")
    parser.add_argument("--data-root", type=Path, default=default_data_root(),
                        help="Footage root (default: $BLINDSPOT_DATA_ROOT, else /workspace/blindspot_data if present, else ~/blindspot_data)")
    parser.add_argument("--out-root", type=Path, default=DEFAULT_OUT_ROOT,
                        help="Output root (default: runs/botsort)")
    parser.add_argument("--cameras", default=",".join(DEFAULT_CAMERAS),
                        help="Camera subfolders (default: c001,c002,c003)")
    parser.add_argument("--poison-cameras", default="c01,c02",
                        help="Short camera ids to poison (default: c01,c02)")
    parser.add_argument("--epsilons", default="0.5",
                        help="Comma-separated poison epsilons; one poisoned pass per value (default: 0.5)")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--skip-clean", action="store_true", help="Only run poisoned passes")
    parser.add_argument("--skip-poison", action="store_true", help="Only run clean passes")
    parser.add_argument("--save-result", action="store_true",
                        help="Also write annotated videos (slower, big files)")
    parser.add_argument("--overwrite", action="store_true",
                        help="Re-run even if the output CSV already exists")
    parser.add_argument("--apply", action="store_true",
                        help="Actually run. Without this flag, prints the plan only.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not (BOT_SORT_DIR / "tools" / "demo.py").exists():
        sys.exit("vendor/BoT-SORT not found or unpatched; run scripts/setup_repo.py --skip-venv first.")

    scenarios = scenarios_from_manifest() if args.all else \
        [item.strip() for item in args.scenarios.split(",") if item.strip()]
    cameras = [item.strip() for item in args.cameras.split(",") if item.strip()]
    poison_cameras = [item.strip() for item in args.poison_cameras.split(",") if item.strip()]
    epsilons = [float(item) for item in args.epsilons.split(",") if item.strip()]

    # condition -> (label used in filenames, epsilon or None for clean)
    conditions = []
    if not args.skip_clean:
        conditions.append(("clean", None))
    if not args.skip_poison:
        for epsilon in epsilons:
            conditions.append((poison_tag(poison_cameras, epsilon, args.seed), epsilon))

    failures = 0
    merged_files: List[Path] = []
    for scenario in scenarios:
        print(f"\n=== {scenario} ===")
        scenario_dir = args.out_root / scenario
        for label, epsilon in conditions:
            per_camera_csvs = []
            for camera_dir in cameras:
                camera_id = short_cam(camera_dir)
                video = find_video(args.data_root, scenario, camera_dir)
                out_csv = scenario_dir / f"{scenario}_{camera_id}_{label}.csv"
                per_camera_csvs.append(out_csv)
                if video is None:
                    print(f"  SKIP {out_csv.name}: no video at "
                          f"{args.data_root / scenario / camera_dir}")
                    failures += 1
                    continue
                if out_csv.exists() and not args.overwrite:
                    print(f"  SKIP {out_csv.name}: already exists (use --overwrite to redo)")
                    continue
                command = build_command(video, camera_id, out_csv, poison_cameras,
                                        epsilon, args.seed, args.save_result)
                printable = " ".join(shlex.quote(part) for part in command)
                if not args.apply:
                    print(f"  PLAN {out_csv.name}\n       {printable}")
                    continue
                scenario_dir.mkdir(parents=True, exist_ok=True)
                print(f"  RUN  {out_csv.name}")
                result = subprocess.run(command, cwd=str(BOT_SORT_DIR))
                append_manifest(args.out_root, {
                    "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
                    "scenario": scenario,
                    "camera": camera_id,
                    "mode": "clean" if epsilon is None else "poisoned",
                    "poison_cameras": "" if epsilon is None else ",".join(poison_cameras),
                    "epsilon": "" if epsilon is None else epsilon,
                    "seed": args.seed,
                    "video": str(video),
                    "output_csv": str(out_csv),
                    "returncode": result.returncode,
                    "command": printable,
                })
                if result.returncode != 0:
                    print(f"  FAIL {out_csv.name} (exit {result.returncode}); continuing")
                    failures += 1
            if args.apply:
                merged = scenario_dir / f"{scenario}_{label}_all-cams.csv"
                if not merged.exists() or args.overwrite:
                    merge_camera_csvs(per_camera_csvs, merged)
                if merged.exists():
                    merged_files.append(merged)

    if not args.apply:
        print("\nPlan only. Re-run with --apply to execute.")
        return 0

    print_ground_truth_handoff(merged_files)

    if failures:
        print(f"\nDone with {failures} failure(s); see messages above and run_manifest.csv.")
        return 1
    print("\nAll runs completed. Hand students the *_tracked.csv (after the join "
          "above) or the *_all-cams.csv smoke inputs, plus run_manifest.csv rows.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
