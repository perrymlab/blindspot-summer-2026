import numpy as np
import pandas as pd

from prime_mtmc.detector import DetectorConfig, _robust_z, camera_consistency_scores
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
    # Clean cameras must not be flagged: the one-sided z-score keeps sub-median
    # (i.e. cleaner-than-typical) cameras negative instead of treating them as
    # outliers. A two-sided |z| would let them leak in as false positives.
    assert metrics["fp"] == 0
    assert set(scores["camera"]) == {"c01", "c02", "c03", "c04", "c05"}


def test_use_variance_false_flags_on_mean_only():
    table = make_synthetic_embeddings(cameras=5, tracks=24, observations_per_camera=3, dim=64)
    poisoned = apply_embedding_poison(
        table, PoisonConfig(cameras=("c01", "c02"), epsilon=1.0, seed=11)
    )

    scores = camera_consistency_scores(
        poisoned, DetectorConfig(z_threshold=1.0, use_variance=False)
    )
    metrics = camera_detection_metrics(scores, {"c01", "c02"})

    # z_score collapses to the mean-distance z, and the attack is still caught.
    assert np.allclose(scores["z_score"], scores["mean_z_score"])
    assert metrics["recall"] >= 0.5
    assert metrics["fp"] == 0


def test_robust_z_is_one_sided():
    # The fix for the two-sided flag: _robust_z returns a *signed* score, so a
    # camera below the cohort center scores negative (never flagged) even though
    # its magnitude is large. A two-sided |z| would treat it like a high outlier.
    values = pd.Series([0.8, 0.9, 1.0, 1.1, 2.0])
    z = _robust_z(values)
    assert z.iloc[4] > 0          # high outlier -> positive (flaggable)
    assert z.iloc[0] < 0          # low outlier -> negative (never flagged)
    assert abs(z.iloc[0]) > 1.0   # |z| > 1: a two-sided test WOULD have flagged it


def test_detector_assumes_poison_is_a_minority():
    # Documents a *fundamental* limitation (not fixed by the one-sided change):
    # random-mode poison shifts every poisoned camera along the SAME direction,
    # so poisoned cameras stay mutually consistent and the honest minority
    # becomes the high-distance outlier. With poison in the majority (3 of 5),
    # the detector therefore flags the honest cameras and misses the attack.
    # The whole approach assumes the poisoned set is the minority.
    table = make_synthetic_embeddings(cameras=5, tracks=24, observations_per_camera=3, dim=64)
    poisoned = apply_embedding_poison(
        table, PoisonConfig(cameras=("c01", "c02", "c03"), epsilon=1.5, seed=11)
    )

    scores = camera_consistency_scores(poisoned, DetectorConfig(z_threshold=1.0))
    flagged = set(scores.loc[scores["flagged"], "camera"].astype(str))
    metrics = camera_detection_metrics(scores, {"c01", "c02", "c03"})

    assert {"c04", "c05"}.issubset(flagged)  # honest minority misflagged
    assert metrics["recall"] == 0.0          # true attack missed under majority
