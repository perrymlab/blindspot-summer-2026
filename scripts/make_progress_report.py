"""Build a shareable progress report from finished run_baselines.py batches.

RESEARCHER tool (GPU box, conda `botsort` env, repo root). For every scenario
with outputs in runs/botsort/ it:

  1. Runs the camera-consistency analysis on the clean and poisoned
     *_all-cams.csv exports (detector scores + detection metrics). When a
     ground-truth-joined sibling produced by scripts/build_track_ids.py is
     present next to the merged export (same name + "_tracked.csv", e.g.
     S07_clean_all-cams_tracked.csv), it is used instead and scored on the
     real cross-camera `track_id`. Without it, scores fall back to the
     positional `detection_index` and are labeled SMOKE CHECK ONLY.
  2. Renders annotated bounding-box videos per camera (clean run) from the
     per-camera CSVs + trimmed videos, transcoded to H.264 so they play in
     any browser.
  3. Extracts a few annotated stills per scenario (small, committable).
  4. Writes both REPORT.md (for the repo) and report.html (self-contained-ish,
     for email/Drive -- share the whole report folder or zip it).

Output layout:

    reports/<YYYY-MM-DD>/
        REPORT.md          <- commit this
        stills/*.jpg       <- commit these (small)
        report.html        <- share directly or attach to a Release
        videos/*.mp4       <- DO NOT commit; attach to a GitHub Release
                              (reports/**/videos/ is gitignored)

Usage (after a batch finishes):

    python scripts/make_progress_report.py                 # all scenarios found
    python scripts/make_progress_report.py --scenarios S01
    python scripts/make_progress_report.py --skip-videos   # tables/stills only

Then:
    git add reports/<date>/REPORT.md reports/<date>/stills
    git commit -m "Progress report <date>" && git push
    gh release create report-<date> reports/<date>/videos/*.mp4 reports/<date>/report.html
"""
from __future__ import annotations

import argparse
import base64
import csv
import datetime
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNS_ROOT = REPO_ROOT / "runs" / "botsort"
POISON_RE = re.compile(r"poison_(?P<cams>[a-z0-9-]+)_eps(?P<eps>[\d.]+)_seed(?P<seed>\d+)")


def sh(cmd: List[str]) -> int:
    return subprocess.run(cmd, cwd=str(REPO_ROOT)).returncode


def data_root() -> Path:
    import os
    env = os.environ.get("BLINDSPOT_DATA_ROOT")
    if env:
        return Path(env).expanduser()
    for cand in (Path("/workspace/blindspot_data"), Path.home() / "blindspot_data"):
        if cand.is_dir():
            return cand
    return Path.home() / "blindspot_data"


def read_csv_rows(path: Path) -> List[dict]:
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def md_table(rows: List[dict], columns: Optional[List[str]] = None, floatfmt: int = 3) -> str:
    if not rows:
        return "_no data_\n"
    cols = columns or list(rows[0].keys())
    out = ["| " + " | ".join(cols) + " |", "| " + " | ".join("---" for _ in cols) + " |"]
    for row in rows:
        cells = []
        for col in cols:
            value = str(row.get(col, ""))
            try:
                value = str(round(float(value), floatfmt))
            except ValueError:
                pass
            cells.append(value)
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out) + "\n"


def resolve_join(merged_csv: Path) -> tuple[Path, str, bool]:
    """Prefer the ground-truth-joined export when build_track_ids.py has run.

    build_track_ids.py writes a sibling ``<stem>_tracked.csv`` carrying a real
    cross-camera ``track_id``. When that file exists we analyze it with
    ``track_id`` (valid detection metrics). Otherwise we fall back to the raw
    merged export keyed by ``detection_index`` -- a positional index with no
    cross-camera identity, usable only as a smoke check, never as a result.

    Returns (csv_to_analyze, track_column, is_ground_truth).
    """
    tracked = merged_csv.with_name(f"{merged_csv.stem}_tracked.csv")
    if tracked.exists():
        return tracked, "track_id", True
    return merged_csv, "detection_index", False


def basis_note(is_ground_truth: bool) -> str:
    """Markdown caveat describing what the scores are keyed on."""
    if is_ground_truth:
        return ("_Scores keyed on ground-truth global `track_id` "
                "(joined by `build_track_ids.py`)._\n")
    return ("_SMOKE CHECK ONLY: no `*_tracked.csv` ground-truth join found, so "
            "scores are keyed on `detection_index`, a positional index with no "
            "cross-camera identity. These numbers are NOT valid detection "
            "metrics. Run `build_track_ids.py` to produce a `*_tracked.csv`._\n")


def analyze(input_csv: Path, scenario: str, out_dir: Path, poisoned: str = "",
            track_column: str = "detection_index") -> dict:
    """Run analyze_embedding_export.py; return dict of result tables."""
    cmd = [sys.executable, "scripts/analyze_embedding_export.py",
           "--input", str(input_csv), "--scenario", scenario,
           "--track-column", track_column, "--out-dir", str(out_dir)]
    if poisoned:
        cmd += ["--poisoned-cameras", poisoned]
    code = sh(cmd)
    result = {"ok": code == 0, "scores": [], "metrics": []}
    if (out_dir / "camera_scores.csv").exists():
        result["scores"] = read_csv_rows(out_dir / "camera_scores.csv")
    if (out_dir / "metrics.csv").exists():
        result["metrics"] = read_csv_rows(out_dir / "metrics.csv")
    return result


def render_video(csv_path: Path, video_path: Path, camera: str, out_mp4: Path) -> bool:
    raw = out_mp4.with_suffix(".raw.mp4")
    code = sh([sys.executable, "scripts/visualize_boxes.py",
               "--csv", str(csv_path), "--video", str(video_path),
               "--camera", camera, "--out", str(raw)])
    if code != 0 or not raw.exists():
        return False
    code = sh(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw),
               "-vcodec", "libx264", "-pix_fmt", "yuv420p", "-crf", "28", str(out_mp4)])
    raw.unlink(missing_ok=True)
    return code == 0 and out_mp4.exists()


def extract_stills(video: Path, dest_dir: Path, stem: str, count: int = 3) -> List[Path]:
    """Pull `count` evenly spaced frames from an annotated video."""
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(video)],
        capture_output=True, text=True)
    try:
        duration = float(probe.stdout.strip())
    except ValueError:
        return []
    stills = []
    for index in range(count):
        ts = duration * (index + 0.5) / count
        out = dest_dir / f"{stem}_t{int(ts):03d}s.jpg"
        code = sh(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(ts),
                   "-i", str(video), "-frames:v", "1", "-q:v", "4", str(out)])
        if code == 0 and out.exists():
            stills.append(out)
    return stills


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--scenarios", default="",
                        help="Comma-separated subset, e.g. S01,S02 (default: all found)")
    parser.add_argument("--skip-videos", action="store_true",
                        help="Tables and report only; no video rendering")
    parser.add_argument("--out-dir", type=Path, default=None,
                        help="Report folder (default: reports/<today>)")
    args = parser.parse_args()

    today = datetime.date.today().isoformat()
    report_dir = args.out_dir or (REPO_ROOT / "reports" / today)
    stills_dir = report_dir / "stills"
    videos_dir = report_dir / "videos"
    work_dir = report_dir / ".analysis"
    for d in (report_dir, stills_dir, videos_dir, work_dir):
        d.mkdir(parents=True, exist_ok=True)

    wanted = {s.strip() for s in args.scenarios.split(",") if s.strip()}
    scenario_dirs = sorted(p for p in RUNS_ROOT.glob("S*") if p.is_dir()
                           and (not wanted or p.name in wanted))
    if not scenario_dirs:
        sys.exit("No scenario outputs found under runs/botsort/.")

    md = [f"# Blindspot progress report — {today}", ""]
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=str(REPO_ROOT),
                          capture_output=True, text=True).stdout.strip()
    md += [f"Repo commit: `{head}`. Produced by `scripts/make_progress_report.py` "
           f"from `runs/botsort/` (see `run_manifest.csv` for full provenance).", ""]
    html_parts = []

    for sdir in scenario_dirs:
        scenario = sdir.name
        print(f"=== {scenario} ===")
        md += [f"## {scenario}", ""]

        clean_all = sorted(sdir.glob(f"{scenario}_clean_all-cams.csv"))
        poison_all = sorted(sdir.glob(f"{scenario}_poison_*_all-cams.csv"))

        if clean_all:
            csv_in, track_col, is_gt = resolve_join(clean_all[0])
            res = analyze(csv_in, scenario, work_dir / f"{scenario}_clean",
                          track_column=track_col)
            md += ["### Clean run — camera consistency scores", "",
                   basis_note(is_gt),
                   md_table(res["scores"], ["camera", "mean_distance", "pair_count",
                                            "z_score", "flagged"]), ""]
        for pcsv in poison_all:
            match = POISON_RE.search(pcsv.name)
            cams = match.group("cams").replace("-", ",") if match else ""
            label = match.group(0) if match else pcsv.stem
            csv_in, track_col, is_gt = resolve_join(pcsv)
            res = analyze(csv_in, scenario, work_dir / f"{scenario}_{label}",
                          poisoned=cams, track_column=track_col)
            md += [f"### Poisoned run (`{label}`) — scores and detection", "",
                   basis_note(is_gt),
                   md_table(res["scores"], ["camera", "mean_distance", "pair_count",
                                            "z_score", "flagged"]), ""]
            if res["metrics"]:
                md += [md_table(res["metrics"], ["tp", "fp", "fn", "precision",
                                                 "recall", "f1"]), ""]

        if not args.skip_videos:
            droot = data_root()
            for cam_csv in sorted(sdir.glob(f"{scenario}_c0?_clean.csv")):
                cam = cam_csv.stem.split("_")[1]              # c01
                cam_dir = "c" + cam[1:].zfill(3)              # c001
                video = droot / scenario / cam_dir / "vdo_trim.mp4"
                if not video.exists():
                    video = droot / scenario / cam_dir / "vdo.mp4"
                if not video.exists():
                    print(f"  no source video for {scenario}/{cam_dir}; skipping render")
                    continue
                out_mp4 = videos_dir / f"{scenario}_{cam}_clean_boxes.mp4"
                print(f"  rendering {out_mp4.name} ...")
                if render_video(cam_csv, video, cam, out_mp4):
                    stills = extract_stills(out_mp4, stills_dir, f"{scenario}_{cam}")
                    for still in stills:
                        md += [f"![{still.stem}](stills/{still.name})"]
                    md += [f"", f"Full clip: `videos/{out_mp4.name}` "
                           f"(attached to the GitHub Release for this report)", ""]

    report_md = report_dir / "REPORT.md"
    report_md.write_text("\n".join(md), encoding="utf-8")

    # Self-contained-ish HTML: markdown content with stills inlined as base64,
    # videos referenced relatively (share the folder or zip it).
    html_body = "\n".join(md)
    html_body = html_body.replace("\n## ", "\n<h2>").replace("\n### ", "\n<h3>")
    inline = []
    for line in html_body.splitlines():
        match = re.match(r"!\[(.*?)\]\(stills/(.*?)\)", line.strip())
        if match:
            img = stills_dir / match.group(2)
            b64 = base64.b64encode(img.read_bytes()).decode()
            inline.append(f'<img alt="{match.group(1)}" style="max-width:480px;margin:4px" '
                          f'src="data:image/jpeg;base64,{b64}">')
        elif line.startswith("|"):
            inline.append(f"<tt>{line}</tt><br>")
        elif line.startswith("<h"):
            tag = line[:3]
            inline.append(f"{line}</{tag[1:]}>" if not line.endswith(">") else line)
        else:
            inline.append(f"<p>{line}</p>" if line.strip() else "")
    # Embed videos as base64 data URIs so report.html works as a SINGLE
    # downloaded file (GitHub serves release assets as downloads; relative
    # video paths would be dead links). Cap total embedded size to keep the
    # file mailable; clips over budget fall back to a named reference.
    embed_budget = 80 * 1024 * 1024  # ~80 MB of raw video -> ~107 MB html
    embedded = 0
    for v in sorted(videos_dir.glob("*.mp4")):
        size = v.stat().st_size
        if embedded + size <= embed_budget:
            b64 = base64.b64encode(v.read_bytes()).decode()
            inline.append(f"<h3>{v.stem}</h3>"
                          f"<video controls width=640 src='data:video/mp4;base64,{b64}'></video>")
            embedded += size
        else:
            inline.append(f"<h3>{v.stem}</h3><p>(clip too large to embed -- "
                          f"download <tt>{v.name}</tt> from the GitHub Release)</p>")
    (report_dir / "report.html").write_text(
        "<html><meta charset='utf-8'><body style='font-family:sans-serif;max-width:900px;margin:auto'>"
        + "\n".join(inline) + "</body></html>", encoding="utf-8")

    shutil.rmtree(work_dir, ignore_errors=True)
    print(f"\nReport written to {report_dir}")
    print("Next steps:")
    print(f"  git add reports/{report_dir.name}/REPORT.md reports/{report_dir.name}/stills")
    print(f"  git commit -m 'Progress report {report_dir.name}' && git push")
    print(f"  gh release create report-{report_dir.name} reports/{report_dir.name}/videos/*.mp4 "
          f"reports/{report_dir.name}/report.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
