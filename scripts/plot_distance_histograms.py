"""Visualize the poisoning attack as cross-camera distance distributions.

This plots the exact quantity the detector scores: for each camera, the cosine
distances between that camera's embeddings and other cameras' embeddings of the
SAME ground-truth identity. Poisoning a camera shifts its distribution to the
right (its same-vehicle matches get farther apart across cameras); unpoisoned
cameras stay put. Unlike the 2D projection, this is guaranteed to show the
effect because it is the measured signal itself.

Reads the released `_tracked` CSVs (space-separated `embedding` + `track_id`).

Example:
    python scripts/plot_distance_histograms.py \
      --clean  runs/botsort/S01/S01_clean_all-cams_tracked.csv \
      --poison runs/botsort/S01/S01_poison_c01_eps1.0_seed7_all-cams_tracked.csv \
      --scenario S01 --poisoned-cameras c01 --eps 1.0 \
      --out results/week07/viz/S01_distance_hist.png
"""

from __future__ import annotations

import argparse
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def load(path: str):
    raw = pd.read_csv(path)
    if "embedding" not in raw.columns:
        raise SystemExit(f"{path}: no 'embedding' column (use a _tracked export)")
    emb = np.array(
        raw["embedding"].map(lambda v: np.fromstring(str(v), sep=" ")).to_list(),
        dtype=float,
    )
    emb = emb / np.maximum(np.linalg.norm(emb, axis=1, keepdims=True), 1e-12)
    meta = pd.DataFrame({
        "camera": raw["camera"].astype(str),
        "track_id": raw["track_id"].astype(str),
    })
    return meta, emb


def per_camera_distances(meta: pd.DataFrame, emb: np.ndarray) -> dict:
    """Cross-camera same-identity cosine distances, assigned to each camera.

    Mirrors detector.py: pair cameras within a track, take min(count) rows in
    order, cosine distance = 1 - dot (embeddings are L2-normalized).
    """
    per_cam = defaultdict(list)
    df = meta.copy()
    df["idx"] = np.arange(len(df))
    for _, g in df.groupby("track_id", sort=False):
        cams = {c: sub["idx"].to_numpy() for c, sub in g.groupby("camera", sort=False)}
        clist = sorted(cams)
        for i, ca in enumerate(clist):
            for cb in clist[i + 1:]:
                ia, ib = cams[ca], cams[cb]
                n = min(len(ia), len(ib))
                if n == 0:
                    continue
                a, b = emb[ia[:n]], emb[ib[:n]]
                d = 1.0 - np.sum(a * b, axis=1)
                per_cam[ca].extend(d.tolist())
                per_cam[cb].extend(d.tolist())
    return per_cam


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--clean", required=True)
    ap.add_argument("--poison", required=True)
    ap.add_argument("--scenario", default="")
    ap.add_argument("--poisoned-cameras", default="c01")
    ap.add_argument("--eps", default="")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    cm, ce = load(args.clean)
    pm, pe = load(args.poison)
    clean_d = per_camera_distances(cm, ce)
    pois_d = per_camera_distances(pm, pe)

    cams = sorted(set(clean_d) | set(pois_d))
    poisoned = {c.strip() for c in args.poisoned_cameras.split(",") if c.strip()}

    fig, axes = plt.subplots(1, len(cams), figsize=(5 * len(cams), 4.2),
                             sharex=True, sharey=True)
    if len(cams) == 1:
        axes = [axes]
    bins = np.linspace(0.0, 1.0, 41)
    for ax, cam in zip(axes, cams):
        c = np.array(clean_d.get(cam, []))
        p = np.array(pois_d.get(cam, []))
        ax.hist(c, bins=bins, alpha=0.55, label="clean", color="#4c78a8", density=True)
        ax.hist(p, bins=bins, alpha=0.55, label="poisoned", color="#e45756", density=True)
        if len(c):
            ax.axvline(c.mean(), color="#4c78a8", ls="--", lw=1.5)
        if len(p):
            ax.axvline(p.mean(), color="#e45756", ls="--", lw=1.5)
        tag = "  (POISONED)" if cam in poisoned else ""
        dm = (p.mean() - c.mean()) if (len(c) and len(p)) else float("nan")
        ax.set_title(f"{cam}{tag}\nmean {c.mean():.3f} -> {p.mean():.3f}  (Δ{dm:+.3f})"
                     if (len(c) and len(p)) else f"{cam}{tag}", fontsize=11)
        ax.set_xlabel("cross-camera cosine distance")
        ax.legend(fontsize=9)
    axes[0].set_ylabel("density")
    fig.suptitle(
        f"{args.scenario}: cross-camera same-identity distance, clean vs poisoned"
        + (f" (eps {args.eps})" if args.eps else "")
        + " — the poisoned camera's distribution shifts right",
        fontsize=12,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    fig.savefig(args.out, dpi=150)
    print(f"Wrote {args.out}  cameras={cams}")
    for cam in cams:
        c = np.array(clean_d.get(cam, [])); p = np.array(pois_d.get(cam, []))
        if len(c) and len(p):
            print(f"  {cam}: clean {c.mean():.3f}  poisoned {p.mean():.3f}  "
                  f"delta {p.mean()-c.mean():+.3f}  (n={len(c)}/{len(p)})")


if __name__ == "__main__":
    main()
