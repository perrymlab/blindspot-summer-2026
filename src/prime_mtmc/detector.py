from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .data import EmbeddingTable, cosine_distance


@dataclass(frozen=True)
class DetectorConfig:
    z_threshold: float = 2.0
    min_pairs: int = 3
    # Whether the variance of a camera's cross-camera distances contributes to
    # the flag (in addition to the mean). Both are treated as one-sided HIGH
    # signals: poisoning inflates a camera's same-track distances *and* tends to
    # spread them (the perturbation lands unevenly across observations after
    # renormalization). The variance cue is weaker/noisier than the mean, so set
    # this False to flag on mean distance alone and shrink the false-positive
    # surface.
    use_variance: bool = True


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
    # One-sided: a camera is suspicious when it sits in the HIGH tail. Both
    # component z-scores are signed, so cameras below the cohort center stay
    # negative and are never flagged. The variance cue is opt-out (see
    # DetectorConfig.use_variance); when disabled we flag on mean distance alone.
    if config.use_variance:
        scores["z_score"] = scores[["mean_z_score", "variance_z_score"]].max(axis=1)
    else:
        scores["z_score"] = scores["mean_z_score"]
    scores["flagged"] = (scores["z_score"] >= config.z_threshold) & (
        scores["pair_count"] >= config.min_pairs
    )
    return scores.sort_values("camera").reset_index(drop=True)


def _robust_z(values: pd.Series) -> pd.Series:
    """Signed robust z-score (median / MAD). Positive => above the cohort center.

    Signed, not absolute, on purpose. Embedding poisoning only *raises* a
    camera's cross-camera distance (and its spread), so the attack signal lives
    entirely in the high tail and the detector flags ``z >= threshold``. A
    two-sided ``|z|`` would also flag an unusually *clean* camera; that misfires
    once poisoned cameras are the majority and drag the median up, turning the
    honest cameras into the apparent outliers. The MAD itself is still built
    from absolute deviations (that is its definition); only the returned score
    keeps its sign.
    """
    values = values.astype(float)
    center = float(values.median())
    mad = float((values - center).abs().median())
    if mad > 0:
        return (values - center) / (1.4826 * mad)
    spread = float(values.std(ddof=0))
    if spread == 0:
        return pd.Series([0.0] * len(values), index=values.index)
    return (values - center) / spread
