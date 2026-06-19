"""Diagnose low annotation-join coverage: why don't export boxes match ground truth.

When build_track_ids.py reports low coverage even though the BoT-SORT export is
detection-rich AND the annotation is dense, the cause is one of:

  * UNDER-DETECTED  - BoT-SORT produced very few boxes on this clip; too little
                      to score against a dense annotation. An export/detector
                      problem, not a join setting.
  * LOOSE BOXES     - the two trackers box the same vehicles but not tightly, so
                      matches collapse at IoU 0.5 but recover at lower IoU.
                      Fix: re-join with a lower --iou-threshold.
  * POOR OVERLAP    - even at low IoU few boxes match a dense annotation: the
                      trackers are boxing largely different vehicles (BoT-SORT a
                      few close/large ones, the annotation many small/distant).
  * COORDINATE MISMATCH - boxes live in different coordinate systems (resolution
                      / letterbox); rare. Fix: rescale before joining.

This is read-only. Per scenario/camera it:
  1. counts export detections vs annotation boxes, plus box sizes and
     coordinate extents (to catch resolution mismatches),
  2. runs the real IoU join at several thresholds (0.5/0.3/0.1/0.05),
  3. classifies the cause and prints a per-camera verdict + tally, and
  4. for UNDER/POOR cameras, adds a secondary "cause:" line that separates the
     daytime explanations -- NIGHT/LOW-LIGHT (objective mean-luma check on the
     source video), DECODE/STREAM (detections confined to an early window then
     stop), SPARSE TRAFFIC (annotation has few boxes/frame), or DISTANT/SMALL
     (annotation boxes far smaller than the few large export boxes).

The brightness check reads the source video (data root via BLINDSPOT_DATA_ROOT
or /workspace/blindspot_data). Pass --no-video to skip it (e.g. off the pod).

Note: a frame-offset sweep is NOT used -- these annotations cover ~every frame,
so frame-number alignment is always ~100% and uninformative.

Auto-discovers the standard layout (data/annotations/<s>/, runs/botsort/<s>/).

Usage:
    python scripts/diagnose_join_offsets.py S11
    python scripts/diagnose_join_offsets.py S03 S08 S09 S10 S11 S12 S13 S18
    python scripts/diagnose_join_offsets.py all
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from build_track_ids import (  # noqa: E402
    build_track_ids, load_annotation_tracks, load_matches, normalize_camera, summarize,
)
from run_baselines import default_data_root, find_video  # noqa: E402

try:
    import cv2  # optional; only needed for the brightness (day/night) check
except ImportError:
    cv2 = None

REPO_ROOT = SCRIPT_DIR.parent
ANNO_DIR = REPO_ROOT / "data" / "annotations"
RUNS_DIR = REPO_ROOT / "runs" / "botsort"

# Mean luma below this is treated as night/low-light (matches sample_scenario_frames).
NIGHT_LUMA = 55.0


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


def box_extents(df: pd.DataFrame) -> dict:
    """Coordinate extents + median box size for a [x1,y1,x2,y2] frame."""
    return {
        "xmax": float(df["x2"].max()), "ymax": float(df["y2"].max()),
        "w": float((df["x2"] - df["x1"]).median()),
        "h": float((df["y2"] - df["y1"]).median()),
    }


def _far(a: float, b: float, ratio: float = 1.3) -> bool:
    lo, hi = min(a, b), max(a, b)
    return lo > 0 and hi / lo > ratio


# A camera with fewer export boxes than this is judged under-detected: there is
# too little for IoU matching to say anything about coordinates or timing.
MIN_DET = 30


def verdict(short: str, n_det: int, n_ann: int, m05: int, m01: int,
            ext_e: dict, ext_a: dict) -> tuple[str, str]:
    """Return (tag, message); tag in UNDER / LOOSE / OK / COORD / PARTIAL / POOR."""
    if n_det < MIN_DET:
        return ("UNDER", f"UNDER-DETECTED -- BoT-SORT produced only {n_det} boxes here "
                f"(vs {n_ann} annotation boxes); too few to score. Export/detector "
                f"problem, not a join setting.")
    if m01 >= max(10, 1.6 * m05) and m01 >= 0.4 * n_det:
        return ("LOOSE", f"LOOSE BOXES -- matches rise {m05}->{m01} when IoU drops "
                f"0.5->0.1; same vehicles, loose boxes. Re-join with --iou-threshold 0.2.")
    if m05 >= 0.5 * n_det:
        return ("OK", f"OK -- {m05}/{n_det} match at IoU 0.5; this camera is fine.")
    if n_det >= 50 and (_far(ext_e["xmax"], ext_a["xmax"]) or _far(ext_e["ymax"], ext_a["ymax"])):
        return ("COORD", f"COORDINATE MISMATCH -- export x<= {ext_e['xmax']:.0f}/"
                f"y<= {ext_e['ymax']:.0f} vs annotation x<= {ext_a['xmax']:.0f}/"
                f"y<= {ext_a['ymax']:.0f}; rescale before joining.")
    if m01 >= 0.3 * n_det:
        return ("PARTIAL", f"PARTIAL -- {m05}/{n_det} at IoU 0.5, {m01}/{n_det} at 0.1; "
                f"a lower --iou-threshold recovers some.")
    return ("POOR", f"POOR OVERLAP -- only {m01}/{n_det} match even at IoU 0.1 despite a "
            f"dense annotation ({n_ann} boxes). BoT-SORT (few, large/close boxes) and the "
            f"annotation (many, small/distant) are largely boxing different vehicles; "
            f"lowering IoU helps little.")


def video_luma_and_frames(video: Path, samples: int = 4) -> tuple[float | None, int | None]:
    """Mean luma (0-255) over a few sampled frames and the clip's frame count.

    Returns (None, None) if OpenCV is unavailable or the video can't be read.
    """
    if cv2 is None or video is None:
        return None, None
    cap = cv2.VideoCapture(str(video))
    if not cap.isOpened():
        return None, None
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
    lumas = []
    if total > 0:
        for i in range(samples):
            cap.set(cv2.CAP_PROP_POS_FRAMES, int((i + 1) * total / (samples + 1)))
            ok, frame = cap.read()
            if ok and frame is not None:
                lumas.append(float(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).mean()))
    cap.release()
    luma = sum(lumas) / len(lumas) if lumas else None
    return luma, (total or None)


def detection_cause(n_det: int, n_ann: int, det: pd.DataFrame, ann: pd.DataFrame,
                    ext_e: dict, ext_a: dict, luma: float | None, clip_hi: int) -> str:
    """Separate *why* a daytime clip under-detects: night vs decode vs sparse vs distant.

    Only meaningful for UNDER/POOR cameras; ordered most-decisive first.
    """
    a_lo, a_hi = int(ann["frame"].min()), int(ann["frame"].max())
    ann_frames = ann["frame"].nunique()
    ann_density = n_ann / max(1, ann_frames)
    det_frames = det["frame"].nunique()
    d_lo, d_hi = int(det["frame"].min()), int(det["frame"].max())
    end = max(clip_hi, a_hi)
    reach = d_hi / max(1, end)

    if luma is not None and luma < NIGHT_LUMA:
        return (f"NIGHT/LOW-LIGHT (mean luma {luma:.0f}) -- COCO YOLOX-x is daytime-biased; "
                f"smoke-only. Confirm with sample_scenario_frames.py.")
    if det_frames < 0.25 * ann_frames and reach < 0.6:
        return (f"DECODE/STREAM? detections only span frames {d_lo}..{d_hi} of ~{end} "
                f"({det_frames} distinct frames) then stop -- the decoder may be feeding "
                f"blank/garbled frames after {d_hi}. Inspect the video / re-trim.")
    if ann_density < 1.0:
        return (f"SPARSE TRAFFIC -- annotation is only ~{ann_density:.1f} boxes/frame; "
                f"genuinely few vehicles, low coverage is expected.")
    area_e = max(1.0, ext_e["w"] * ext_e["h"])
    area_a = max(1.0, ext_a["w"] * ext_a["h"])
    if area_e / area_a > 3.0 and ext_a["w"] < 90:
        return (f"DISTANT/SMALL vehicles -- annotation median {ext_a['w']:.0f}x{ext_a['h']:.0f}px "
                f"vs export {ext_e['w']:.0f}x{ext_e['h']:.0f}px; the detector resolves only "
                f"close/large vehicles. A bigger --tsize may help; not a join setting.")
    luma_note = f" (daytime, luma {luma:.0f})" if luma is not None else ""
    return (f"UNCLEAR{luma_note} -- dense annotation, detections spread across the clip; "
            f"inspect frames with sample_scenario_frames.py.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("scenarios", nargs="+", help="scenario ids or 'all'")
    parser.add_argument("--cov-threshold", type=float, default=0.5,
                        help="IoU used for the reported coverage (default: 0.5); "
                             "the matched-vs-IoU sweep always shows 0.5/0.3/0.1/0.05")
    parser.add_argument("--no-video", action="store_true",
                        help="skip the brightness/day-night check (don't read source videos)")
    args = parser.parse_args()

    data_root = None if args.no_video else default_data_root()

    scenarios = discover_scenarios() if args.scenarios == ["all"] else args.scenarios
    if not scenarios:
        print("No scenarios to diagnose.", file=sys.stderr)
        return 1

    findings: list[tuple[str, str, str]] = []
    sweep_thresholds = sorted({0.5, 0.3, 0.1, 0.05, args.cov_threshold}, reverse=True)

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

            d_lo, d_hi = int(det["frame"].min()), int(det["frame"].max())
            a_lo, a_hi = int(ann["frame"].min()), int(ann["frame"].max())
            ext_e = box_extents(det)
            ext_a = box_extents(ann)

            luma, vframes = (None, None)
            if data_root is not None:
                video = find_video(data_root, scenario, f"c{cam:03d}")
                luma, vframes = video_luma_and_frames(video)
            clip_hi = vframes if vframes else a_hi

            # IoU-threshold sweep at offset 0 (frames already cover ~every annotation
            # frame, so a frame-offset sweep is uninformative here).
            sweep = {thr: join_stats(det, cam, ann, matches, 0, thr) for thr in sweep_thresholds}
            m05 = sweep.get(0.5, sweep[sweep_thresholds[0]])[0]
            m01 = sweep.get(0.1, sweep[sweep_thresholds[-1]])[0]
            cov_g, cov = sweep[args.cov_threshold][1], sweep[args.cov_threshold][2]

            print(f"  {short}: export={n_det} det (frames {d_lo}..{d_hi}, "
                  f"box~{ext_e['w']:.0f}x{ext_e['h']:.0f}, x<= {ext_e['xmax']:.0f} y<= {ext_e['ymax']:.0f})")
            print(f"        annotation={n_ann} boxes ({ann['frame'].nunique()} frames "
                  f"{a_lo}..{a_hi}, box~{ext_a['w']:.0f}x{ext_a['h']:.0f}, "
                  f"x<= {ext_a['xmax']:.0f} y<= {ext_a['ymax']:.0f})")
            print("        matched vs IoU: "
                  + "  ".join(f"@{thr}={sweep[thr][0]}" for thr in sweep_thresholds)
                  + f"   (global@{args.cov_threshold}={cov_g}, cov={cov:.3f})")

            if luma is not None:
                print(f"        brightness: mean luma {luma:.0f} "
                      f"({'NIGHT/LOW-LIGHT' if luma < NIGHT_LUMA else 'daytime'})")

            tag, msg = verdict(short, n_det, n_ann, m05, m01, ext_e, ext_a)
            print(f"        verdict: {msg}")
            if tag in ("UNDER", "POOR"):
                print(f"        cause:   {detection_cause(n_det, n_ann, det, ann, ext_e, ext_a, luma, clip_hi)}")
            findings.append((scenario, short, tag))

    print("\n" + "=" * 60)
    tally = Counter(tag for _, _, tag in findings)
    print("Verdict tally (camera-level): "
          + ", ".join(f"{t}={n}" for t, n in tally.most_common()))

    def group(tag):
        return [f"{s}/{c}" for s, c, t in findings if t == tag]

    recoverable = group("LOOSE") + group("PARTIAL")
    if recoverable:
        print(f"\nRECOVERABLE ({len(recoverable)}): re-join with a lower --iou-threshold "
              f"(~0.2) to recover coverage: " + ", ".join(recoverable))
    poor = group("POOR")
    if poor:
        print(f"\nPOOR OVERLAP ({len(poor)}): trackers box largely different vehicles; "
              f"a lower threshold helps little: " + ", ".join(poor))
    under = group("UNDER")
    if under:
        print(f"\nUNDER-DETECTED ({len(under)}): BoT-SORT emitted too few boxes -- re-run "
              f"detection (lower confidence) or treat as smoke-only: " + ", ".join(under))
    coord = group("COORD")
    if coord:
        print(f"\nCOORDINATE MISMATCH ({len(coord)}): boxes use different coordinate "
              f"systems -- needs rescaling, not a re-join: " + ", ".join(coord))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
