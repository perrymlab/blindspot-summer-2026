from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .data import EmbeddingTable, cosine_distance


@dataclass(frozen=True)
class DetectorConfig:
    z_threshold: float = 2.0
    min_pairs: int = 3


def camera_consistency_scores(table: EmbeddingTable, config: DetectorConfig) -> pd.DataFrame:
    """Score cameras by cross-camera same-track cosine-distance distribution shift."""

    pair_rows: list[dict[str, object]] = []
    meta = table.meta.reset_index(drop=True)

    for track_id, group in meta.groupby("track_id", sort=False):
        indices_by_camera = {
            str(camera): camera_group.index.to_numpy()
            for camera, camera_group in group.groupby("camera", sort=False)
        }
        cameras = sorted(indices_by_camera)
        for left_pos, left_camera in enumerate(cameras):
            for right_camera in cameras[left_pos + 1 :]:
                left_indices = indices_by_camera[left_camera]
                right_indices = indices_by_camera[right_camera]
                count = min(len(left_indices), len(right_indices))
                if count == 0:
                    continue
                distances = cosine_distance(
                    table.embeddings[left_indices[:count]],
                    table.embeddings[right_indices[:count]],
                )
                for distance in distances:
                    pair_rows.append(
                        {
                            "track_id": track_id,
                            "camera_a": left_camera,
                            "camera_b": right_camera,
                            "distance": float(distance),
                        }
                    )

    if not pair_rows:
        return pd.DataFrame(
            columns=["camera", "mean_distance", "variance", "pair_count", "z_score", "flagged"]
        )

    pairs = pd.DataFrame(pair_rows)
    camera_rows = []
    for camera in sorted(set(pairs["camera_a"]).union(set(pairs["camera_b"]))):
        distances = pairs.loc[
            (pairs["camera_a"] == camera) | (pairs["camera_b"] == camera), "distance"
        ].to_numpy(dtype=np.float64)
        camera_rows.append(
            {
                "camera": camera,
                "mean_distance": float(np.mean(distances)),
                "variance": float(np.var(distances)),
                "pair_count": int(len(distances)),
            }
        )

    scores = pd.DataFrame(camera_rows)
    scores["mean_z_score"] = _robust_z(scores["mean_distance"])
    scores["variance_z_score"] = _robust_z(scores["variance"])
    scores["z_score"] = scores[["mean_z_score", "variance_z_score"]].max(axis=1)
    scores["flagged"] = (scores["z_score"] >= config.z_threshold) & (
        scores["pair_count"] >= config.min_pairs
    )
    return scores.sort_values("camera").reset_index(drop=True)


def _robust_z(values: pd.Series) -> pd.Series:
    values = values.astype(float)
    center = float(values.median())
    mad = float((values - center).abs().median())
    if mad > 0:
        return (values - center).abs() / (1.4826 * mad)
    spread = float(values.std(ddof=0))
    if spread == 0:
        return pd.Series([0.0] * len(values), index=values.index)
    return (values - center).abs() / spread
