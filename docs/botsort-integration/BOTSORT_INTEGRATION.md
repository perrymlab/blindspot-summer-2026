# BoT-SORT ReID Poisoning Hook

> **Running the tracker?** See the step-by-step
> [BoT-SORT GPU Runbook](BOTSORT_GPU_RUNBOOK.md) for the full researcher
> workflow (conda Python 3.9 env, dependency install, weights, and the exact
> demo commands). This document describes the hook design and contracts.

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

`a7e591afd307a1255bcbf9018e50740b022441b6`

That branch adds PRIME flags in `tools/demo.py` and `tools/mc_demo.py`, plus embedding poisoning/export support in `fast_reid/fast_reid_interfece.py`. It also carries the compatibility fixes required to run the 2021-era FastReID code on a modern stack: `fast_reid/fastreid/data/build.py` replaces the removed `torch._six.string_classes` import with `string_classes = str` (PyTorch 2.x), and `tools/demo.py` replaces the interactive `cv2.waitKey(1)` call with `ch = -1` so the demo runs under headless OpenCV on a GPU server with no display. The PRIME code paths require **Python 3.9** (FastReID imports `collections.Mapping`, removed in Python 3.10).

In a fresh fork/clone of this repository, run `python scripts/setup_repo.py` to recreate the local BoT-SORT checkout and apply the tracked patch from `patches/`.

## Patched Demo Flags

- `--prime-camera-id c01`
- `--prime-poison-cameras c01,c02`
- `--prime-poison-epsilon 0.5`
- `--prime-poison-seed 7`
- `--prime-export-embeddings runs/botsort/c01_embeddings.csv`
- `--prime-classes 2,3,5,7` (restrict a COCO detector to vehicle classes: car/motorcycle/bus/truck)

For the exact, verified-working clean and poisoned commands (with the required
`-f`/`--ckpt` flags and the VeRi vehicle ReID config), see
[BOTSORT_GPU_RUNBOOK.md](BOTSORT_GPU_RUNBOOK.md#6-run-the-tracker-and-export-embeddings).
The `--prime-*` flags layer on top of that base command:

- Clean export: `--prime-camera-id c01 --prime-export-embeddings ../../runs/botsort/clean_c01.csv`
- Poisoned export: add `--prime-poison-cameras c01,c02 --prime-poison-epsilon 0.5`

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
