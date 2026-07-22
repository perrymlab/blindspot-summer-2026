"""Visualize the poisoning attack in embedding space (clean vs poisoned).

The attack's effect is cross-camera: it pulls a poisoned camera's embeddings
off the shared manifold so the SAME vehicle no longer matches across cameras.
That is invisible in a single-camera bounding-box video (within-camera tracking
is unaffected) but shows clearly as an embedding projection.

For each ground-truth identity seen on all three cameras, this projects the
2048-d embeddings to 2D (PCA fit on the clean run, same axes applied to both)
and draws two panels: clean and poisoned. Color = identity, marker = camera.
In clean, an identity's three cameras cluster together; under poison, the
poisoned camera's points detach.

Reads the released `_tracked` CSVs (single space-separated `embedding` column
plus `track_id`), same format scripts/analyze_embedding_export.py consumes.

Example:
    python scripts/plot_embedding_projection.py \
      --clean  data/S01_clean_all-cams_tracked.csv.gz \
      --poison data/S01_poison_c01-c02_eps1.0_seed7_all-cams_tracked.csv.gz \
      --scenario S01 --poisoned-cameras c01,c02 --eps 1.0 \
      --out results/week07/viz/S01_embedding_projection.png
"""

from __future__ import annotations

import argparse

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


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--clean", required=True)
    ap.add_argument("--poison", required=True)
    ap.add_argument("--scenario", default="")
    ap.add_argument("--poisoned-cameras", default="c01")
    ap.add_argument("--eps", default="")
    ap.add_argument("--max-identities", type=int, default=8)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    cm, ce = load(args.clean)
    pm, pe = load(args.poison)

    cams = sorted(set(cm["camera"]) | set(pm["camera"]))
    # identities present on ALL cameras in the clean run
    per_id_cams = cm.groupby("track_id")["camera"].nunique()
    covisible = per_id_cams[per_id_cams >= len(cams)].index
    if len(covisible) == 0:
        raise SystemExit("No identity appears on all cameras in the clean run; "
                         "cannot show cross-camera clustering.")
    freq = cm[cm["track_id"].isin(covisible)]["track_id"].value_counts()
    chosen = list(freq.index[: args.max_identities])

    def sub(meta, emb):
        mask = meta["track_id"].isin(chosen).to_numpy()
        return meta[mask].reset_index(drop=True), emb[mask]

    cm, ce = sub(cm, ce)
    pm, pe = sub(pm, pe)

    # PCA fit on clean, same axes applied to both
    mu = ce.mean(axis=0)
    _, _, vt = np.linalg.svd(ce - mu, full_matrices=False)
    comps = vt[:2].T

    def proj(emb):
        return (emb - mu) @ comps

    cp, pp = proj(ce), proj(pe)

    markers = ["o", "s", "^", "D", "v", "P"]
    marker_for = {cam: markers[i % len(markers)] for i, cam in enumerate(cams)}
    palette = plt.cm.tab10(np.linspace(0, 1, max(len(chosen), 1)))
    color_for = {tid: palette[i] for i, tid in enumerate(chosen)}
    poisoned = {c.strip() for c in args.poisoned_cameras.split(",") if c.strip()}

    fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharex=True, sharey=True)
    panels = [
        (axes[0], cm, cp, "Clean"),
        (axes[1], pm, pp, f"Poisoned ({args.poisoned_cameras}"
                          + (f", eps {args.eps}" if args.eps else "") + ")"),
    ]
    for ax, meta, pts, title in panels:
        cam_arr = meta["camera"].to_numpy()
        tid_arr = meta["track_id"].to_numpy()
        for cam in cams:
            for tid in chosen:
                m = (cam_arr == cam) & (tid_arr == tid)
                if m.any():
                    ax.scatter(pts[m, 0], pts[m, 1], c=[color_for[tid]],
                               marker=marker_for[cam], s=22, alpha=0.75,
                               edgecolors="none")
        ax.set_title(title, fontsize=13)
        ax.set_xlabel("PC1"); ax.set_ylabel("PC2")

    # legends: markers = cameras (poisoned marked), colors = identities
    cam_handles = [plt.Line2D([0], [0], marker=marker_for[c], color="gray",
                   linestyle="", markersize=8,
                   label=c + ("  (poisoned)" if c in poisoned else ""))
                   for c in cams]
    axes[0].legend(handles=cam_handles, title="camera", loc="best", fontsize=9)
    fig.suptitle(
        f"{args.scenario} embeddings, PCA (fit on clean) — "
        "same identity's cameras cluster in clean; poisoned camera detaches",
        fontsize=12,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(args.out, dpi=150)
    print(f"Wrote {args.out}  ({len(chosen)} identities, cameras={cams})")


if __name__ == "__main__":
    main()
