from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from prime_mtmc.detector import DetectorConfig, camera_consistency_scores
from prime_mtmc.metrics import camera_detection_metrics
from prime_mtmc.poison import PoisonConfig, apply_embedding_poison
from prime_mtmc.synthetic import make_synthetic_embeddings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run synthetic PRIME MTMC poisoning experiments.")
    parser.add_argument("--out-dir", default="runs/synthetic", help="Directory for CSV outputs.")
    parser.add_argument("--epsilons", nargs="+", type=float, default=[0.1, 0.5, 1.0])
    parser.add_argument("--poison-cameras", nargs="+", default=["c01", "c02"])
    parser.add_argument("--z-threshold", type=float, default=1.25)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--tracks", type=int, default=32)
    parser.add_argument("--dim", type=int, default=128)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    clean = make_synthetic_embeddings(tracks=args.tracks, dim=args.dim, seed=args.seed)
    clean.to_csv(out_dir / "clean_embeddings.csv")

    summary_rows = []
    detector_config = DetectorConfig(z_threshold=args.z_threshold)
    clean_scores = camera_consistency_scores(clean, detector_config)
    clean_scores.to_csv(out_dir / "scores_clean.csv", index=False)

    for epsilon in args.epsilons:
        poisoned = apply_embedding_poison(
            clean,
            PoisonConfig(cameras=tuple(args.poison_cameras), epsilon=epsilon, seed=args.seed),
        )
        poisoned.to_csv(out_dir / f"poisoned_eps_{epsilon:g}.csv")

        scores = camera_consistency_scores(poisoned, detector_config)
        scores.to_csv(out_dir / f"scores_eps_{epsilon:g}.csv", index=False)
        metrics = camera_detection_metrics(scores, set(args.poison_cameras))
        summary_rows.append(
            {
                "epsilon": epsilon,
                "poisoned_cameras": " ".join(args.poison_cameras),
                "z_threshold": args.z_threshold,
                **metrics,
            }
        )

    summary = pd.DataFrame(summary_rows)
    summary.to_csv(out_dir / "summary.csv", index=False)
    print(summary.to_string(index=False))
    print(f"Wrote outputs to {out_dir}")


if __name__ == "__main__":
    main()
