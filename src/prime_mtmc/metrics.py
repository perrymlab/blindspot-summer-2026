from __future__ import annotations

import pandas as pd


def camera_detection_metrics(
    scores: pd.DataFrame, poisoned_cameras: set[str]
) -> dict[str, float | int]:
    predicted = set(scores.loc[scores["flagged"], "camera"].astype(str))
    truth = {str(camera) for camera in poisoned_cameras}

    tp = len(predicted & truth)
    fp = len(predicted - truth)
    fn = len(truth - predicted)
    tn = max(0, len(set(scores["camera"].astype(str))) - tp - fp - fn)

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }
