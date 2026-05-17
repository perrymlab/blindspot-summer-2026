import numpy as np

from prime_mtmc.detector import DetectorConfig, camera_consistency_scores
from prime_mtmc.metrics import camera_detection_metrics
from prime_mtmc.poison import PoisonConfig, apply_embedding_poison
from prime_mtmc.synthetic import make_synthetic_embeddings


def test_poison_changes_only_selected_camera_embeddings():
    table = make_synthetic_embeddings(cameras=3, tracks=4, observations_per_camera=2, dim=16)
    poisoned = apply_embedding_poison(table, PoisonConfig(cameras=("c01",), epsilon=0.5))

    selected = table.meta["camera"].eq("c01").to_numpy()
    assert np.max(np.abs(table.embeddings[selected] - poisoned.embeddings[selected])) > 0.01
    assert np.allclose(table.embeddings[~selected], poisoned.embeddings[~selected])


def test_detector_flags_strong_poisoning():
    table = make_synthetic_embeddings(cameras=5, tracks=24, observations_per_camera=3, dim=64)
    poisoned = apply_embedding_poison(
        table, PoisonConfig(cameras=("c01", "c02"), epsilon=1.0, seed=11)
    )

    scores = camera_consistency_scores(poisoned, DetectorConfig(z_threshold=1.0))
    metrics = camera_detection_metrics(scores, {"c01", "c02"})

    assert metrics["recall"] >= 0.5
    assert set(scores["camera"]) == {"c01", "c02", "c03", "c04", "c05"}
