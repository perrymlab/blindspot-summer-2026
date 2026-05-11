from __future__ import annotations

import numpy as np
import pandas as pd

from .data import EmbeddingTable, l2_normalize


def make_synthetic_embeddings(
    *,
    scenario: str = "S01",
    cameras: int = 5,
    tracks: int = 32,
    observations_per_camera: int = 4,
    dim: int = 128,
    noise: float = 0.06,
    seed: int = 13,
) -> EmbeddingTable:
    """Create MTMC-like embeddings where same-track vectors cluster across cameras."""

    rng = np.random.default_rng(seed)
    centers = l2_normalize(rng.normal(size=(tracks, dim)))
    rows = []
    vectors = []
    for track_index in range(tracks):
        for camera_index in range(1, cameras + 1):
            camera_bias = rng.normal(scale=noise * 0.4, size=dim)
            for obs_index in range(observations_per_camera):
                rows.append(
                    {
                        "scenario": scenario,
                        "camera": f"c{camera_index:02d}",
                        "frame": obs_index,
                        "track_id": f"veh{track_index:04d}",
                    }
                )
                vectors.append(centers[track_index] + camera_bias + rng.normal(scale=noise, size=dim))
    return EmbeddingTable(pd.DataFrame(rows), l2_normalize(np.vstack(vectors)))
