# BoT-SORT ReID Poisoning Hook

This project treats embedding-space poisoning as an inference-time intervention on ReID feature vectors. In the upstream BoT-SORT repository, the expected hook point is:

`fast_reid/fast_reid_interfece.py`

Specifically, patch the method that returns one feature vector per detection. The hook should run after model inference and before the features are consumed by the tracker.

## Minimal Hook Shape

```python
features = model_outputs.cpu().numpy()

if poison_config.enabled and current_camera_id in poison_config.cameras:
    features = features + poison_config.epsilon * poison_config.direction
    features = features / np.maximum(np.linalg.norm(features, axis=1, keepdims=True), 1e-12)

return features
```

## Current Clone Status

The upstream repository was cloned to:

`vendor/BoT-SORT`

The cloned commit is:

`251985436d6712aaf682aaaf5f71edb4987224bd`

The local checkout has been patched and committed on branch:

`prime-reid-poison-export`

Patch commit:

`e9dafea0ad85f8bbfb6ad6e7626aa3e31a511285`

That branch adds PRIME flags in `tools/demo.py` and `tools/mc_demo.py`, plus embedding poisoning/export support in `fast_reid/fast_reid_interfece.py`.

In a fresh fork/clone of this repository, run `python scripts/setup_repo.py` to recreate the local BoT-SORT checkout and apply the tracked patch from `patches/`.

## Patched Demo Flags

- `--prime-camera-id c01`
- `--prime-poison-cameras c01,c02`
- `--prime-poison-epsilon 0.5`
- `--prime-poison-seed 7`
- `--prime-export-embeddings runs/botsort/c01_embeddings.csv`

Example shape for a per-camera clean run:

```bash
cd vendor/BoT-SORT
python tools/demo.py video --path <path-to-S01-c001-video> --with-reid --prime-camera-id c01 --prime-export-embeddings ../../runs/botsort/clean_c01.csv
```

Example shape for a poisoned run:

```bash
cd vendor/BoT-SORT
python tools/demo.py video --path <path-to-S01-c001-video> --with-reid --prime-camera-id c01 --prime-poison-cameras c01,c02 --prime-poison-epsilon 0.5 --prime-export-embeddings ../../runs/botsort/poisoned_c01.csv
```

## Required Run Log Fields

- BoT-SORT fork URL and commit hash
- Python, PyTorch, CUDA/CPU mode, and checkpoint path
- Scenario ID and camera IDs
- Whether perturbation is applied before or after feature normalization
- Perturbation mode: `random` or `targeted`
- Epsilon, random seed, and target identity if applicable
- Exact command line for each run

## Detector Input Contract

Export one row per detection with:

- `scenario`
- `camera`
- `frame`
- `track_id`, using the tracker-assigned global ID or ground-truth ID for controlled experiments
- `e0 ... eN`, the ReID embedding vector

The detector in this repository reads that CSV with `EmbeddingTable.from_csv`.

The direct BoT-SORT export writes raw detection-level embeddings. For camera-level detection with this repository, merge those rows with tracker-assigned global IDs or ground-truth IDs, then run:

```bash
python scripts/analyze_embedding_export.py --input runs/botsort/merged_embeddings.csv --track-column track_id --poisoned-cameras c01,c02
```
