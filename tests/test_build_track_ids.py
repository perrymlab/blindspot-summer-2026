import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from build_track_ids import (  # noqa: E402
    build_track_ids,
    greedy_assign,
    iou_matrix,
    load_annotation_tracks,
    load_matches,
    normalize_camera,
)


def make_export(rows):
    frame = pd.DataFrame(rows, columns=["camera", "frame", "detection_index", "x1", "y1", "x2", "y2"])
    frame["embedding"] = "0.1 0.2 0.3"
    return frame


def test_normalize_camera_variants():
    assert normalize_camera("c01") == normalize_camera("cam01") == normalize_camera("c001") == 1
    # multicam-reid synced clips are named like c01_synced.mp4 -> camera "c01_synced"
    assert normalize_camera("c01_synced") == 1
    assert normalize_camera("S07_c02_synced") == 2
    with pytest.raises(ValueError):
        normalize_camera("nodigits")


def test_load_matches_supported_shapes(tmp_path):
    shapes = [
        {"objects": [{"global_id": 5, "tracks": {"cam01": 12, "cam02": 7}}]},
        [{"global_id": 5, "tracks": {"cam01": 12, "cam02": 7}}],
        {"5": {"cam01": 12, "cam02": 7}},
        [{"global_id": 5, "cam01": 12, "cam02": 7}],
    ]
    for i, shape in enumerate(shapes):
        path = tmp_path / f"matches{i}.json"
        path.write_text(json.dumps(shape))
        assert load_matches(path) == {(1, 12): "5", (2, 7): "5"}


def test_load_matches_multicam_reid_format(tmp_path):
    # Real format from https://github.com/figaone/multicam-reid (.reid/matches.json)
    payload = {
        "version": 1,
        "matches": [
            {"frame": 250, "tracks": {"c01": 12, "c02": 7, "c03": None}},
            {"frame": 300, "tracks": {"c01": 4, "c02": None, "c03": 9}},
        ],
    }
    path = tmp_path / "matches.json"
    path.write_text(json.dumps(payload))
    assert load_matches(path) == {(1, 12): "0", (2, 7): "0", (1, 4): "1", (3, 9): "1"}


def test_load_matches_camera_map(tmp_path):
    payload = {"version": 1, "matches": [{"frame": 1, "tracks": {"cam_north": 12, "cam_east": 7}}]}
    path = tmp_path / "matches.json"
    path.write_text(json.dumps(payload))
    camera_map = {"cam_north": "c01", "cam_east": "c02"}
    assert load_matches(path, camera_map) == {(1, 12): "0", (2, 7): "0"}
    with pytest.raises(ValueError, match="camera-map"):
        load_matches(path)


def test_load_annotation_tracks_multicam_reid_format(tmp_path):
    # Real format: {track_id: {frames: [...], boxes: [[x1,y1,x2,y2],...], ...}}
    payload = {
        "12": {
            "frames": [100, 101],
            "boxes": [[10, 20, 50, 60], [12, 21, 52, 61]],
            "classes": [2, 2],
            "confs": [0.9, 0.88],
            "class_name": "car",
        }
    }
    path = tmp_path / "c01.tracks.json"
    path.write_text(json.dumps(payload))
    tracks = load_annotation_tracks(path)
    assert len(tracks) == 2
    assert tracks.iloc[0].tolist() == [100, 12, 10, 20, 50, 60]
    assert tracks.iloc[1].tolist() == [101, 12, 12, 21, 52, 61]


def test_load_matches_rejects_conflicts(tmp_path):
    path = tmp_path / "matches.json"
    path.write_text(json.dumps({"5": {"c01": 12}, "6": {"c01": 12}}))
    with pytest.raises(ValueError, match="conflict"):
        load_matches(path)


def test_load_annotation_tracks_mot(tmp_path):
    path = tmp_path / "cam01.txt"
    path.write_text("1,12,100,200,50,40,1,-1,-1,-1\n2,12,105,202,50,40,1,-1,-1,-1\n")
    tracks = load_annotation_tracks(path)
    assert list(tracks.columns) == ["frame", "local_id", "x1", "y1", "x2", "y2"]
    assert tracks.iloc[0].tolist() == [1, 12, 100, 200, 150, 240]


def test_iou_and_greedy_assignment():
    a = np.array([[0, 0, 10, 10], [20, 20, 30, 30]], dtype=float)
    b = np.array([[0, 0, 10, 10], [21, 21, 31, 31], [100, 100, 110, 110]], dtype=float)
    iou = iou_matrix(a, b)
    assert iou[0, 0] == pytest.approx(1.0)
    pairs = greedy_assign(iou, threshold=0.3)
    assert {(r, c) for r, c, _ in pairs} == {(0, 0), (1, 1)}


def test_greedy_is_one_to_one():
    # Two detections both overlapping one annotation box: only one may claim it.
    a = np.array([[0, 0, 10, 10], [1, 1, 11, 11]], dtype=float)
    b = np.array([[0, 0, 10, 10]], dtype=float)
    pairs = greedy_assign(iou_matrix(a, b), threshold=0.3)
    assert len(pairs) == 1
    assert pairs[0][:2] == (0, 0)  # exact overlap wins


def test_full_join_with_offsets():
    export = make_export(
        [
            # cam01, export frame 10 == annotation frame 12 (offset +2)
            ("c01", 10, 0, 100, 100, 150, 140),   # matches local track 3 -> global "7"
            ("c01", 10, 1, 400, 400, 450, 440),   # no annotation nearby
            # cam02, offset 0
            ("c02", 5, 0, 200, 200, 260, 250),    # matches local track 9 -> global "7"
            ("c02", 5, 1, 600, 100, 660, 150),    # matches local track 4 -> unmatched globally
        ]
    )
    tracks = {
        1: pd.DataFrame(
            {"frame": [12], "local_id": [3], "x1": [102], "y1": [101], "x2": [149], "y2": [141]}
        ),
        2: pd.DataFrame(
            {
                "frame": [5, 5],
                "local_id": [9, 4],
                "x1": [201, 601],
                "y1": [199, 99],
                "x2": [259, 661],
                "y2": [251, 152],
            }
        ),
    }
    matches = {(1, 3): "7", (2, 9): "7"}
    joined = build_track_ids(export, tracks, matches, offsets={1: 2}, iou_threshold=0.5)

    assert joined.loc[0, "track_id"] == "7"
    assert joined.loc[0, "annotation_track"] == "1:3"
    assert pd.isna(joined.loc[1, "track_id"])
    assert joined.loc[2, "track_id"] == "7"
    # matched to an annotation track that the human never linked across cameras
    assert joined.loc[3, "annotation_track"] == "2:4"
    assert pd.isna(joined.loc[3, "track_id"])
    # same physical vehicle now shares one global id across cameras
    assert joined[joined["track_id"] == "7"]["camera"].tolist() == ["c01", "c02"]


def test_wrong_offset_produces_no_matches():
    export = make_export([("c01", 10, 0, 100, 100, 150, 140)])
    tracks = {1: pd.DataFrame({"frame": [12], "local_id": [3], "x1": [100], "y1": [100], "x2": [150], "y2": [140]})}
    joined = build_track_ids(export, tracks, {(1, 3): "7"}, offsets={1: 0}, iou_threshold=0.5)
    assert joined["track_id"].isna().all()
