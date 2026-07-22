import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from prime_mtmc.data import EmbeddingTable
from prime_mtmc.detector import DetectorConfig, camera_consistency_scores
from prime_mtmc.reid import (
    observation_cross_camera_distances,
    parse_embedding_column,
    positional_pair_distances,
)
from render_reid_videos import (
    discover_jobs,
    find_tracked_csv,
    parse_per_camera_filename,
    video_camera,
)
from visualize_boxes import classify_status, match_observations, prepare_reid_annotations


def tracked_rows(rows):
    frame = pd.DataFrame(rows)
    for column in ("x1", "y1", "x2", "y2"):
        if column not in frame:
            frame[column] = 0.0
    return frame


def test_raw_embedding_parser_normalizes_and_rejects_ragged_vectors():
    frame = pd.DataFrame({"embedding": ["3 4", "0 5"]})
    embeddings = parse_embedding_column(frame)
    assert np.allclose(np.linalg.norm(embeddings, axis=1), 1.0)
    with pytest.raises(ValueError, match="does not match"):
        parse_embedding_column(pd.DataFrame({"embedding": ["1 2", "1 2 3"]}))


def test_observation_distances_follow_detector_positional_pairs():
    meta = pd.DataFrame(
        {
            "scenario": ["S01"] * 4,
            "camera": ["c01", "c01", "c02", "c02"],
            "frame": [1, 2, 1, 2],
            "track_id": ["7"] * 4,
        }
    )
    embeddings = np.array([[1, 0], [0, 1], [1, 0], [-1, 0]], dtype=float)
    pairs = positional_pair_distances(meta, embeddings)
    assert pairs["distance"].tolist() == pytest.approx([0.0, 1.0])
    observations = observation_cross_camera_distances(meta, embeddings)
    assert observations["xcam_distance"].tolist() == pytest.approx([0.0, 1.0, 0.0, 1.0])

    scores = camera_consistency_scores(EmbeddingTable(meta, embeddings), DetectorConfig())
    assert scores["mean_distance"].tolist() == pytest.approx([0.5, 0.5])
    assert scores["pair_count"].tolist() == [2, 2]


def test_three_camera_observation_averages_all_pair_contributions():
    meta = pd.DataFrame(
        {
            "camera": ["c01", "c02", "c03"],
            "frame": [1, 1, 1],
            "track_id": [1, 1, 1],
        }
    )
    embeddings = np.array([[1, 0], [0, 1], [-1, 0]], dtype=float)
    observations = observation_cross_camera_distances(meta, embeddings)
    assert observations["xcam_pair_count"].tolist() == [2, 2, 2]
    assert observations["xcam_distance"].tolist() == pytest.approx([1.5, 1.0, 1.5])


def test_observation_without_other_camera_match_is_unscored():
    meta = pd.DataFrame({"camera": ["c01"], "frame": [1], "track_id": [1]})
    observations = observation_cross_camera_distances(meta, np.array([[1.0, 0.0]]))
    assert observations.loc[0, "xcam_pair_count"] == 0
    assert np.isnan(observations.loc[0, "xcam_distance"])


def test_box_matching_prefers_detection_index_then_iou():
    boxes = tracked_rows(
        {
            "camera": ["c01", "c01"],
            "frame": [1, 1],
            "detection_index": [5, 99],
            "x1": [0, 20],
            "y1": [0, 20],
            "x2": [10, 30],
            "y2": [10, 30],
        }
    )
    observations = tracked_rows(
        {
            "camera": ["c001", "c01"],
            "frame": [1, 1],
            "detection_index": [5, 6],
            "x1": [0, 20],
            "y1": [0, 20],
            "x2": [10, 30],
            "y2": [10, 30],
        }
    )
    matches = match_observations(boxes, observations, 0.5)
    assert matches["match_strategy"].tolist() == ["detection_index", "iou"]
    assert matches["tracked_index"].tolist() == [0, 1]


def test_box_matching_keeps_ambiguous_identity_unmatched():
    boxes = tracked_rows({"camera": ["c01"], "frame": [1], "track_id": [7], "x1": [100], "y1": [100], "x2": [110], "y2": [110]})
    observations = tracked_rows(
        {"camera": ["c01", "c01"], "frame": [1, 1], "track_id": [7, 7], "x1": [0, 20], "y1": [0, 20], "x2": [10, 30], "y2": [10, 30]}
    )
    matches = match_observations(boxes, observations, 0.5)
    assert matches.loc[0, "match_strategy"] == "unmatched"


def test_status_thresholds_and_unmatched():
    assert classify_status(0.1, 0.15, 0.3) == "OK"
    assert classify_status(0.2, 0.15, 0.3) == "WARN"
    assert classify_status(0.3, 0.15, 0.3) == "ANOM"
    assert classify_status(None, 0.15, 0.3) == "UNMATCHED"


def test_clean_reference_delta_drives_poison_status(tmp_path):
    boxes = tracked_rows(
        {
            "camera": ["c01"],
            "frame": [1],
            "detection_index": [0],
            "x1": [0],
            "y1": [0],
            "x2": [10],
            "y2": [10],
        }
    )
    current = tracked_rows(
        {
            "camera": ["c01", "c02"],
            "frame": [1, 1],
            "detection_index": [0, 0],
            "embedding": ["0 1", "1 0"],
            "track_id": [7, 7],
            "x1": [0, 0],
            "y1": [0, 0],
            "x2": [10, 10],
            "y2": [10, 10],
        }
    )
    clean = current.copy()
    clean["embedding"] = ["1 0", "1 0"]
    current_path = tmp_path / "current.csv"
    clean_path = tmp_path / "clean.csv"
    current.to_csv(current_path, index=False)
    clean.to_csv(clean_path, index=False)
    args = SimpleNamespace(
        tracked_csv=current_path,
        clean_tracked_csv=clean_path,
        reid_iou_threshold=0.5,
        warn_threshold=0.15,
        anomaly_threshold=0.3,
    )
    annotations, _, basis = prepare_reid_annotations(args, boxes)
    assert basis == "Delta XCam vs clean"
    assert annotations.loc[0, "xcam_distance"] == pytest.approx(1.0)
    assert annotations.loc[0, "delta_xcam"] == pytest.approx(1.0)
    assert annotations.loc[0, "status"] == "ANOM"


def test_filename_pairing_and_camera_normalization(tmp_path):
    scenario = tmp_path / "S01"
    scenario.mkdir()
    box = scenario / "S01_c01_poison_c01-c02_eps0.5_seed7.csv.gz"
    box.touch()
    tracked = scenario / "S01_poison_c01-c02_eps0.5_seed7_all-cams_tracked.csv.gz"
    tracked.touch()
    (scenario / "S01_clean_all-cams_tracked.csv").touch()
    assert parse_per_camera_filename(box) == ("S01", "c01", "poison_c01-c02_eps0.5_seed7")
    assert parse_per_camera_filename(tracked) is None
    assert find_tracked_csv(scenario, "S01", "poison_c01-c02_eps0.5_seed7", box) == tracked
    assert video_camera("c01") == video_camera("c1") == video_camera("c001") == "c001"


def test_discovery_excludes_all_camera_files_and_maps_video_directory(tmp_path):
    results = tmp_path / "runs"
    videos = tmp_path / "videos"
    output = tmp_path / "output"
    scenario = results / "S01"
    scenario.mkdir(parents=True)
    box = scenario / "S01_c01_clean.csv"
    box.touch()
    (scenario / "S01_clean_all-cams_tracked.csv").touch()
    (scenario / "S01_clean_all-cams.csv").touch()
    jobs = discover_jobs(results, videos, output, ["S01"], "vdo_trim.mp4", use_clean_reference=True)
    assert len(jobs) == 1
    assert jobs[0].box_csv == box
    assert jobs[0].video == videos / "S01" / "c001" / "vdo_trim.mp4"
    assert jobs[0].output == output / "S01" / "S01_c01_clean_reid-distance.mp4"
