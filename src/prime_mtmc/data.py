from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


REQUIRED_COLUMNS = ("scenario", "camera", "frame", "track_id")


@dataclass(frozen=True)
class EmbeddingTable:
    """A table of detections plus a dense embedding matrix."""

    meta: pd.DataFrame
    embeddings: np.ndarray

    def __post_init__(self) -> None:
        missing = [column for column in REQUIRED_COLUMNS if column not in self.meta.columns]
        if missing:
            raise ValueError(f"missing metadata columns: {', '.join(missing)}")
        if len(self.meta) != len(self.embeddings):
            raise ValueError("metadata row count must match embedding row count")
        if self.embeddings.ndim != 2:
            raise ValueError("embeddings must be a 2D matrix")

    @property
    def dim(self) -> int:
        return int(self.embeddings.shape[1])

    def copy(self) -> "EmbeddingTable":
        return EmbeddingTable(self.meta.copy(), self.embeddings.copy())

    def with_embeddings(self, embeddings: np.ndarray) -> "EmbeddingTable":
        return EmbeddingTable(self.meta.copy(), embeddings)

    def to_csv(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        emb_cols = {f"e{i}": self.embeddings[:, i] for i in range(self.dim)}
        pd.concat([self.meta.reset_index(drop=True), pd.DataFrame(emb_cols)], axis=1).to_csv(
            path, index=False
        )

    @staticmethod
    def from_csv(path: str | Path) -> "EmbeddingTable":
        frame = pd.read_csv(path)
        emb_columns = [column for column in frame.columns if column.startswith("e")]
        if not emb_columns:
            raise ValueError("no embedding columns found; expected e0, e1, ...")
        emb_columns = sorted(emb_columns, key=lambda column: int(column[1:]))
        meta = frame.drop(columns=emb_columns)
        embeddings = frame[emb_columns].to_numpy(dtype=np.float64)
        return EmbeddingTable(meta=meta, embeddings=embeddings)


def l2_normalize(matrix: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    return matrix / np.maximum(norms, eps)


def cosine_distance(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    a_norm = l2_normalize(np.atleast_2d(a))
    b_norm = l2_normalize(np.atleast_2d(b))
    return 1.0 - np.sum(a_norm * b_norm, axis=1)
