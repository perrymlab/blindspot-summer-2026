"""Observation-level cross-camera ReID distance helpers.

The detector scores camera-level distributions of same-identity cosine distances.
This module exposes the same positional pairing rule at observation granularity so
visualization and detector analysis cannot silently use different metrics.
"""

from __future__ import annotations

from collections.abc import Iterator

import numpy as np
import pandas as pd

from .data import cosine_distance, l2_normalize


def parse_embedding_column(frame: pd.DataFrame, column: str = "embedding") -> np.ndarray:
    """Parse one space-separated embedding column into a normalized dense matrix."""
    if column not in frame.columns:
        raise ValueError(f"missing embedding column: {column}")

    vectors: list[np.ndarray] = []
    dimension: int | None = None
    for row_index, value in frame[column].items():
        if pd.isna(value):
            raise ValueError(f"row {row_index}: embedding is missing")
        vector = np.fromstring(str(value), sep=" ", dtype=np.float64)
        if vector.size == 0:
            raise ValueError(f"row {row_index}: embedding is empty or non-numeric")
        if not np.isfinite(vector).all():
            raise ValueError(f"row {row_index}: embedding contains non-finite values")
        if dimension is None:
            dimension = int(vector.size)
        elif vector.size != dimension:
            raise ValueError(
                f"row {row_index}: embedding dimension {vector.size} does not match {dimension}"
            )
        vectors.append(vector)

    if not vectors:
        raise ValueError("no embeddings found")
    return l2_normalize(np.vstack(vectors))


def iter_positional_cross_camera_pairs(meta: pd.DataFrame) -> Iterator[tuple[int, int, object, str, str]]:
    """Yield detector-faithful matched observation positions.

    For each global identity and unordered camera pair, observations are paired
    by their existing CSV order and truncated to the shorter trajectory. The
    yielded positions index ``meta.reset_index(drop=True)`` and the matching
    embedding matrix.
    """
    required = {"camera", "track_id"}
    missing = required - set(meta.columns)
    if missing:
        raise ValueError(f"missing metadata columns: {sorted(missing)}")

    normalized = meta.reset_index(drop=True)
    for track_id, group in normalized.groupby("track_id", sort=False):
        indices_by_camera = {
            str(camera): camera_group.index.to_numpy()
            for camera, camera_group in group.groupby("camera", sort=False)
        }
        cameras = sorted(indices_by_camera)
        for left_position, left_camera in enumerate(cameras):
            for right_camera in cameras[left_position + 1 :]:
                left_indices = indices_by_camera[left_camera]
                right_indices = indices_by_camera[right_camera]
                for left_index, right_index in zip(left_indices, right_indices):
                    yield int(left_index), int(right_index), track_id, left_camera, right_camera


def positional_pair_distances(meta: pd.DataFrame, embeddings: np.ndarray) -> pd.DataFrame:
    """Return one row per detector-style cross-camera pair and its distance."""
    normalized = meta.reset_index(drop=True)
    embeddings = np.asarray(embeddings, dtype=np.float64)
    if embeddings.ndim != 2 or len(normalized) != len(embeddings):
        raise ValueError("metadata row count must match a 2D embedding matrix")

    rows: list[dict[str, object]] = []
    for left_index, right_index, track_id, left_camera, right_camera in iter_positional_cross_camera_pairs(
        normalized
    ):
        distance = float(cosine_distance(embeddings[left_index], embeddings[right_index])[0])
        rows.append(
            {
                "left_index": left_index,
                "right_index": right_index,
                "track_id": track_id,
                "camera_a": left_camera,
                "camera_b": right_camera,
                "distance": distance,
            }
        )
    return pd.DataFrame(
        rows,
        columns=["left_index", "right_index", "track_id", "camera_a", "camera_b", "distance"],
    )


def observation_cross_camera_distances(meta: pd.DataFrame, embeddings: np.ndarray) -> pd.DataFrame:
    """Attach mean detector-style XCam distance and pair count to each observation."""
    normalized = meta.reset_index(drop=True).copy()
    normalized["source_index"] = meta.index.to_numpy()
    pairs = positional_pair_distances(normalized, embeddings)
    sums = np.zeros(len(normalized), dtype=np.float64)
    counts = np.zeros(len(normalized), dtype=np.int64)
    for pair in pairs.itertuples(index=False):
        sums[pair.left_index] += pair.distance
        sums[pair.right_index] += pair.distance
        counts[pair.left_index] += 1
        counts[pair.right_index] += 1

    normalized["xcam_distance"] = np.divide(
        sums,
        counts,
        out=np.full(len(normalized), np.nan, dtype=np.float64),
        where=counts > 0,
    )
    normalized["xcam_pair_count"] = counts
    return normalized
