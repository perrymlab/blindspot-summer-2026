#!/usr/bin/env python3
"""Tabulate single-camera poison-sweep detector metrics into one combined table.

Reads the joined (`*_all-cams_tracked.csv`) poisoned exports produced by
run_single_cam_sweep.sh, runs the cross-camera embedding-consistency detector
on each, and writes ONE precision/recall/F1 table to results/week06/ (CSV +
markdown), plus a mean-by-epsilon rollup.

Run inside the 'botsort' env, from the repo root:

    python scripts/tabulate_single_cam.py \
        --scenarios S01,S02,S03 --epsilons 0.5 --poison-cameras c01

Each row is one (scenario, epsilon) detector result with the lone poisoned
camera as ground truth. Unlike the Week-06 c01+c02 runs this is a VALID test:
with <50% of cameras poisoned the detector's majority assumption holds.

Mirrors scripts/analyze_embedding_export.py (same detector + metrics), so the
numbers are directly comparable to the per-file analysis.
"""
from __future__ import annotations

import argparse
import datetime
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from prime_mtmc.data import EmbeddingTable, l2_normalize  # noqa: E402
from prime_mtmc.detector import DetectorConfig, camera_consistency_scores  # noqa: E402
from prime_mtmc.metrics import camera_detection_metrics  # noqa: E402


def _fmt(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def df_to_md(df: pd.DataFrame) -> str:
    """Render a DataFrame as a GitHub markdown table without needing `tabulate`."""
    cols = list(df.columns)
    head = "| " + " | ".join(str(c) for c in cols) + " |"
    sep = "| " + " | ".join("---" for _ in cols) + " |"
    body = [
        "| " + " | ".join(_fmt(row[c]) for c in cols) + " |"
        for _, row in df.iterrows()
    ]
    return "\n".join([head, sep, *body])


def find_export(scenario: str, poison_tag: str, eps: str, seed: int) -> Path | None:
    name = f"{scenario}_poison_{poison_tag}_eps{eps}_seed{seed}_all-cams_tracked.csv"
    path = REPO_ROOT / "runs" / "botsort" / scenario / name
    return path if path.exists() else None


def analyze_one(
    path: Path, scenario: str, poisoned: set[str], z_threshold: float, use_variance: bool
) -> dict:
    raw = pd.read_csv(path)
    if "embedding" not in raw.columns or "track_id" not in raw.columns:
        raise ValueError("missing 'embedding' or 'track_id' column")
    raw = raw[raw["track_id"].notna()].copy()
    if raw.empty:
        raise ValueError("no rows with a joined track_id (coverage 0)")
    vectors = np.vstack(
        raw["embedding"].map(lambda v: np.fromstring(str(v), sep=" ")).to_list()
    )
    meta = pd.DataFrame(
        {
            "scenario": scenario,
            "camera": raw["camera"].astype(str),
            "frame": raw["frame"],
            "track_id": raw["track_id"].astype(str),
        }
    )
    table = EmbeddingTable(meta=meta, embeddings=l2_normalize(vectors))
    scores = camera_consistency_scores(
        table, DetectorConfig(z_threshold=z_threshold, use_variance=use_variance)
    )
    metrics = camera_detection_metrics(scores, poisoned)
    flagged = ",".join(sorted(scores.loc[scores["flagged"], "camera"].astype(str)))
    return {
        **metrics,
        "cameras_flagged": flagged or "none",
        "n_cameras": int(scores["camera"].nunique()),
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Tabulate single-cam poison sweep metrics.")
    p.add_argument("--scenarios", required=True, help="Comma-separated scenario ids")
    p.add_argument("--epsilons", default="0.5", help="Comma-separated epsilons (default 0.5)")
    p.add_argument("--poison-cameras", default="c01", help="Poisoned camera id(s) (default c01)")
    p.add_argument("--seed", type=int, default=7)
    p.add_argument("--z-threshold", type=float, default=1.25)
    p.add_argument("--no-variance", dest="use_variance", action="store_false",
                   help="Ignore the noisier variance cue (shrinks false positives).")
    p.add_argument("--out-dir", default=str(REPO_ROOT / "results" / "week06"))
    args = p.parse_args()

    scenarios = [s.strip() for s in args.scenarios.split(",") if s.strip()]
    epsilons = [e.strip() for e in args.epsilons.split(",") if e.strip()]
    poison_list = [c.strip() for c in args.poison_cameras.split(",") if c.strip()]
    poison_tag = "-".join(poison_list)
    poisoned = set(poison_list)

    rows: list[dict] = []
    missing: list[str] = []
    for scenario in scenarios:
        for eps in epsilons:
            path = find_export(scenario, poison_tag, eps, args.seed)
            if path is None:
                missing.append(f"{scenario} eps{eps} (no joined export)")
                continue
            try:
                res = analyze_one(path, scenario, poisoned, args.z_threshold, args.use_variance)
            except Exception as exc:  # noqa: BLE001
                missing.append(f"{scenario} eps{eps} (ERROR: {exc})")
                continue
            rows.append(
                {
                    "scenario": scenario,
                    "epsilon": eps,
                    "poison_cameras": poison_tag,
                    "z_threshold": args.z_threshold,
                    **res,
                }
            )

    if not rows:
        print("No joined exports found -- did the sweep + track-id join run first?")
        if missing:
            print("Missing:\n  " + "\n  ".join(missing))
        sys.exit(1)

    df = pd.DataFrame(rows)
    col_order = [
        "scenario", "epsilon", "poison_cameras", "z_threshold", "n_cameras",
        "tp", "fp", "fn", "tn", "precision", "recall", "f1", "cameras_flagged",
    ]
    df = df[[c for c in col_order if c in df.columns]]

    means = (
        df.groupby("epsilon")[["precision", "recall", "f1"]]
        .mean()
        .round(3)
        .reset_index()
    )

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    date = datetime.date.today().isoformat()
    csv_path = out_dir / f"single_cam_sweep_{date}.csv"
    md_path = out_dir / f"single_cam_sweep_{date}.md"
    df.to_csv(csv_path, index=False)

    variance_state = "on" if args.use_variance else "off"
    with md_path.open("w") as fh:
        fh.write(f"# Single-camera poison sweep — {date}\n\n")
        fh.write(
            f"Poison target: **{poison_tag}** (lone camera; <50% of cameras "
            "poisoned, so the detector's majority assumption holds — unlike the "
            "Week-06 c01+c02 runs, which inverted it). "
            f"z-threshold {args.z_threshold}; variance channel {variance_state}.\n\n"
        )
        fh.write("## Per-scenario\n\n")
        fh.write(df_to_md(df))
        fh.write("\n\n## Mean by epsilon\n\n")
        fh.write(df_to_md(means))
        fh.write("\n")
        if missing:
            fh.write("\n## Missing / failed\n\n")
            for item in missing:
                fh.write(f"- {item}\n")

    print(df.to_string(index=False))
    print("\nMean P/R/F1 by epsilon:")
    print(means.to_string(index=False))
    print(f"\nWrote {csv_path}")
    print(f"Wrote {md_path}")
    if missing:
        print(f"\nWARNING: {len(missing)} missing/failed:\n  " + "\n  ".join(missing))


if __name__ == "__main__":
    main()
