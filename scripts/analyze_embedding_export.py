from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from prime_mtmc.data import EmbeddingTable, l2_normalize
from prime_mtmc.detector import DetectorConfig, camera_consistency_scores
from prime_mtmc.metrics import camera_detection_metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze exported BoT-SORT ReID embeddings.")
    parser.add_argument("--input", required=True, help="CSV written by --prime-export-embeddings")
    parser.add_argument("--out-dir", default="runs/embedding_analysis")
    parser.add_argument("--scenario", default="S01")
    parser.add_argument(
        "--track-column",
        default="track_id",
        help="Column containing global track ids. Use detection_index only for smoke checks.",
    )
    parser.add_argument("--poisoned-cameras", default="", help="Comma-separated poisoned camera ids")
    parser.add_argument("--z-threshold", type=float, default=1.25)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    raw = pd.read_csv(args.input)
    if "embedding" not in raw.columns:
        raise ValueError("input must contain an embedding column")
    if args.track_column not in raw.columns:
        raise ValueError(
            f"input does not contain {args.track_column!r}. "
            "For real detection, merge exported embeddings with tracker/global ids first."
        )

    vectors = np.vstack(
        raw["embedding"].map(lambda value: np.fromstring(str(value), sep=" ")).to_list()
    )
    meta = pd.DataFrame(
        {
            "scenario": args.scenario,
            "camera": raw["camera"].astype(str),
            "frame": raw["frame"],
            "track_id": raw[args.track_column].astype(str),
        }
    )
    table = EmbeddingTable(meta=meta, embeddings=l2_normalize(vectors))
    normalized_path = out_dir / "normalized_embeddings.csv"
    table.to_csv(normalized_path)

    scores = camera_consistency_scores(table, DetectorConfig(z_threshold=args.z_threshold))
    scores.to_csv(out_dir / "camera_scores.csv", index=False)

    poisoned = {camera.strip() for camera in args.poisoned_cameras.split(",") if camera.strip()}
    if poisoned:
        metrics = camera_detection_metrics(scores, poisoned)
        pd.DataFrame([metrics]).to_csv(out_dir / "metrics.csv", index=False)
        print(pd.DataFrame([metrics]).to_string(index=False))
    print(scores.to_string(index=False))
    print(f"Wrote outputs to {out_dir}")


if __name__ == "__main__":
    main()
