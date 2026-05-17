from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from prime_mtmc.detector import DetectorConfig, camera_consistency_scores
from prime_mtmc.metrics import camera_detection_metrics
from prime_mtmc.poison import PoisonConfig, apply_embedding_poison
from prime_mtmc.synthetic import make_synthetic_embeddings


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_poison_changes_only_selected_camera_embeddings() -> None:
    table = make_synthetic_embeddings(cameras=3, tracks=4, observations_per_camera=2, dim=16)
    poisoned = apply_embedding_poison(table, PoisonConfig(cameras=("c01",), epsilon=0.5))

    selected = table.meta["camera"].eq("c01").to_numpy()
    assert_true(
        np.max(np.abs(table.embeddings[selected] - poisoned.embeddings[selected])) > 0.01,
        "selected camera embeddings did not change",
    )
    assert_true(
        np.allclose(table.embeddings[~selected], poisoned.embeddings[~selected]),
        "unselected camera embeddings changed",
    )


def test_detector_flags_strong_poisoning() -> None:
    table = make_synthetic_embeddings(cameras=5, tracks=24, observations_per_camera=3, dim=64)
    poisoned = apply_embedding_poison(
        table, PoisonConfig(cameras=("c01", "c02"), epsilon=1.0, seed=11)
    )

    scores = camera_consistency_scores(poisoned, DetectorConfig(z_threshold=1.0))
    metrics = camera_detection_metrics(scores, {"c01", "c02"})

    assert_true(metrics["recall"] >= 0.5, f"low recall: {metrics}")
    assert_true(
        set(scores["camera"]) == {"c01", "c02", "c03", "c04", "c05"},
        "detector did not score all cameras",
    )


def main() -> None:
    test_poison_changes_only_selected_camera_embeddings()
    test_detector_flags_strong_poisoning()
    print("smoke tests passed")


if __name__ == "__main__":
    main()
