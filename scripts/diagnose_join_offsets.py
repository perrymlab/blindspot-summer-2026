"""Diagnose low annotation-join coverage: sync-offset vs sparse annotation.

When build_track_ids.py reports low coverage even though the BoT-SORT export is
detection-rich, the cause is one of:

  * SYNC OFFSET     - the annotation and the export ran on slightly different
                      timelines, so boxes that should match are a few frames
                      apart. Fixable with build_track_ids.py --offsets.
  * SPARSE ANNOTATION - the annotator labeled far fewer boxes than the detector
                      produced, so most detections have nothing to match.
                      Needs more annotation, not a code fix.
  * SPATIAL MISMATCH- frames align and boxes exist, but they don't overlap
                      (resolution/scale mismatch or wrong camera mapping).
                      Try a lower --iou-threshold or --camera-map.

This is read-only. Per scenario/camera it:
  1. counts export detections vs annotation boxes and their frame ranges,
  2. sweeps a frame offset to find the alignment that maximizes frame overlap
     (cheap, no IoU), then
  3. runs the real IoU join at offset 0 and at the best offset and compares
     matched / coverage,
and prints a verdict + the --offsets string to use if a sync offset helps.

Auto-discovers the standard layout (data/annotations/<s>/, runs/botsort/<s>/).

Usage:
    python scripts/diagnose_join_offsets.py S11
    python scripts/diagnose_join_offsets.py S03 S08 S09 S10 S11 S12 S13 S18
    python scripts/diagnose_join_offsets.py all --offset-range 50
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from build_track_ids import (  # noqa: E402
    build_track_ids, load_annotation_tracks, load_matches, normalize_camera, summarize,
)

REPO_ROOT = SCRIPT_DIR.parent
ANNO_DIR = REPO_ROOT / "data" / "annotations"
RUNS_DIR = REPO_ROOT / "runs" / "botsort"


def discover_scenarios() -> list[str]:
    out = []
    for matches in sorted(ANNO_DIR.glob("*/matches.json")):
        out.append(matches.parent.name)
    return out


def pick_export(scenario: str) -> Path | None:
    """Prefer the clean all-cams export; else any non-tracked *_all-cams.csv."""
    clean = RUNS_DIR / scenario / f"{scenario}_clean_all-cams.csv"
    if clean.exists():
        return clean
    for csv in sorted((RUNS_DIR / scenario).glob("*_all-cams.csv")):
        if not csv.name.endswith("_tracked.csv"):
            return csv
    return None


def join_stats(det: pd.DataFrame, cam: int, ann: pd.DataFrame,
               matches, offset: int, iou: float) -> tuple[int, int, float]:
    """Return (matched_to_annotation, with_global_id, coverage) for one camera."""
    joined = build_track_ids(det, {cam: ann}, matches, {cam: offset}, iou)
    summary = summarize(joined)
    if summary.empty:
        return 0, 0, 0.0
    row = summary.iloc[0]
    return int(row["matched_to_annotation"]), int(row["with_global_id"]), float(row["coverage"])


def best_overlap_offset(det_frames: np.ndarray, ann_frames: np.ndarray,
                        rng: int) -> tuple[int, int]:
    """Offset (in [-rng, rng]) maximizing how many det frames land on an ann frame."""
    ann_set = set(int(f) for f in ann_frames)
    if not ann_set or det_frames.size == 0:
        return 0, 0
    best_o, best_count = 0, -1
    for o in range(-rng, rng + 1):
        shifted = det_frames + o
        count = int(np.count_nonzero(np.isin(shifted, list(ann_set))))
        if count > best_count or (count == best_count and abs(o) < abs(best_o)):
            best_o, best_count = o, count
    return best_o, best_count


def verdict(short: str, n_det: int, n_ann: int, overlap: int, base_matched: int,
            best_o: int, best_matched: int) -> str:
    gain = best_matched - base_matched
    if best_o != 0 and best_matched >= max(10, 2 * base_matched) and gain >= 0.1 * n_det:
        return (f"SYNC OFFSET -- shifting this camera by {best_o:+d} frames raises "
                f"matches {base_matched}->{best_matched}. Re-join with "
                f"--offsets {short}={best_o}")
    if overlap >= 0.5 * n_det and best_matched < 0.3 * n_det:
        if n_ann < 0.5 * n_det:
            return (f"SPARSE ANNOTATION -- only {n_ann} annotation boxes vs {n_det} "
                    f"detections; most detections have nothing to match. Annotate more "
                    f"or accept as smoke-only.")
        return (f"SPATIAL MISMATCH -- frames align ({overlap}/{n_det} overlap) and "
                f"{n_ann} ann boxes exist, but boxes don't overlap. Try a lower "
                f"--iou-threshold or check --camera-map / resolution.")
    if overlap < 0.3 * n_det:
        return (f"NO FRAME OVERLAP -- even the best offset lands only {overlap}/{n_det} "
                f"detections on an annotation frame; annotation likely covers a "
                f"different time span than this export.")
    return (f"PARTIAL -- best matches {best_matched}/{n_det} at offset {best_o:+d}; "
            f"borderline, inspect manually.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("scenarios", nargs="+", help="scenario ids or 'all'")
    parser.add_argument("--offset-range", type=int, default=30,
                        help="sweep frame offsets in [-N, N] (default: 30)")
    parser.add_argument("--iou-threshold", type=float, default=0.5)
    args = parser.parse_args()

    scenarios = discover_scenarios() if args.scenarios == ["all"] else args.scenarios
    if not scenarios:
        print("No scenarios to diagnose.", file=sys.stderr)
        return 1

    recommended: dict[str, dict[str, int]] = {}

    for scenario in scenarios:
        print(f"\n===== {scenario} =====")
        matches_path = ANNO_DIR / scenario / "matches.json"
        tracks_dir = ANNO_DIR / scenario / "tracks"
        export_path = pick_export(scenario)

        if not matches_path.exists() or not tracks_dir.is_dir():
            print(f"  SKIP: missing annotations under {ANNO_DIR / scenario}")
            continue
        if export_path is None:
            print(f"  SKIP: no *_all-cams.csv export under {RUNS_DIR / scenario}")
            continue

        print(f"  export: {export_path.name}")
        export = pd.read_csv(export_path)
        export["_cam_num"] = export["camera"].map(normalize_camera)
        matches = load_matches(matches_path)

        tracks = {}
        for tf in sorted(tracks_dir.glob("*.tracks.json")):
            cam = normalize_camera(tf.stem)
            tracks[cam] = load_annotation_tracks(tf)

        for cam in sorted(tracks):
            short = f"c{cam:02d}"
            det = export[export["_cam_num"] == cam].drop(columns=["_cam_num"])
            ann = tracks[cam]
            n_det = len(det)
            n_ann = len(ann)
            if n_det == 0:
                print(f"  {short}: no detections in export -- skip")
                continue

            det_frames = det["frame"].astype(int).to_numpy()
            ann_frames = ann["frame"].astype(int).to_numpy()
            d_lo, d_hi = int(det_frames.min()), int(det_frames.max())
            a_lo, a_hi = int(ann_frames.min()), int(ann_frames.max())

            best_o, overlap = best_overlap_offset(det_frames, ann_frames, args.offset_range)

            base_m, base_g, base_cov = join_stats(det, cam, ann, matches, 0, args.iou_threshold)
            if best_o != 0:
                best_m, best_g, best_cov = join_stats(det, cam, ann, matches, best_o, args.iou_threshold)
            else:
                best_m, best_g, best_cov = base_m, base_g, base_cov

            print(f"  {short}: export={n_det} det (frames {d_lo}..{d_hi}), "
                  f"annotation={n_ann} boxes ({ann['frame'].nunique()} frames {a_lo}..{a_hi})")
            print(f"        frame-overlap best offset {best_o:+d} "
                  f"({overlap}/{n_det} det land on an ann frame)")
            print(f"        IoU join @0     : matched={base_m} global={base_g} cov={base_cov:.3f}")
            if best_o != 0:
                print(f"        IoU join @{best_o:+d}: matched={best_m} global={best_g} cov={best_cov:.3f}")

            v = verdict(short, n_det, n_ann, overlap, base_m, best_o, best_m)
            print(f"        verdict: {v}")

            if v.startswith("SYNC OFFSET"):
                recommended.setdefault(scenario, {})[short] = best_o

    print("\n" + "=" * 60)
    if recommended:
        print("Recommended re-joins with sync offsets:")
        for scenario, offs in recommended.items():
            off_str = ",".join(f"{c}={o}" for c, o in offs.items())
            print(f"  python scripts/build_track_ids.py --export "
                  f"runs/botsort/{scenario}/{scenario}_clean_all-cams.csv \\")
            print(f"      --matches data/annotations/{scenario}/matches.json \\")
            print(f"      --tracks c01=... c02=... c03=... --offsets {off_str} \\")
            print(f"      --output runs/botsort/{scenario}/{scenario}_clean_all-cams_tracked.csv")
    else:
        print("No camera was improved by a frame offset -- low coverage is from sparse "
              "annotation or spatial mismatch, not sync. See per-camera verdicts above.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
