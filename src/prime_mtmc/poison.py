from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .data import EmbeddingTable, l2_normalize


@dataclass(frozen=True)
class PoisonConfig:
    cameras: tuple[str, ...]
    epsilon: float
    seed: int = 7
    mode: str = "random"
    target_track_id: str | None = None
    renormalize: bool = True


def apply_embedding_poison(table: EmbeddingTable, config: PoisonConfig) -> EmbeddingTable:
    """Apply an additive embedding perturbation to selected camera rows."""

    if config.epsilon < 0:
        raise ValueError("epsilon must be non-negative")
    embeddings = table.embeddings.copy()
    camera_mask = table.meta["camera"].astype(str).isin(config.cameras).to_numpy()
    if not camera_mask.any() or config.epsilon == 0:
        return table.with_embeddings(l2_normalize(embeddings) if config.renormalize else embeddings)

    direction = _perturbation_direction(table, config)
    embeddings[camera_mask] = embeddings[camera_mask] + config.epsilon * direction
    if config.renormalize:
        embeddings = l2_normalize(embeddings)
    return table.with_embeddings(embeddings)


def _perturbation_direction(table: EmbeddingTable, config: PoisonConfig) -> np.ndarray:
    if config.mode == "random":
        rng = np.random.default_rng(config.seed)
        direction = rng.normal(size=table.dim)
    elif config.mode == "targeted":
        if config.target_track_id is None:
            raise ValueError("target_track_id is required for targeted poisoning")
        target_mask = table.meta["track_id"].astype(str).eq(str(config.target_track_id)).to_numpy()
        if not target_mask.any():
            raise ValueError(f"target_track_id not found: {config.target_track_id}")
        direction = table.embeddings[target_mask].mean(axis=0)
    else:
        raise ValueError(f"unknown poison mode: {config.mode}")
    norm = np.linalg.norm(direction)
    if norm == 0:
        raise ValueError("perturbation direction has zero norm")
    return direction / norm
