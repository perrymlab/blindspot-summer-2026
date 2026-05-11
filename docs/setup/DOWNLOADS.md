# Required Downloads

This document lists external data and model artifacts needed for the project. Do not commit downloaded datasets, model weights, videos, or raw tracker outputs to git.

## CityFlowV2 / AI City 2022 Track 1

Use the official AI City Challenge page:

- `https://www.aicitychallenge.org/2022-track1-download/`

Direct file link from the official page:

- `https://drive.google.com/file/d/13wNJpS_Oaoe-7y5Dzexg_Ol7bKu1OWuC/view?usp=sharing`

Dataset name:

- `AICity22_Track1_MTMC_Tracking.zip`

Project use:

- CityFlowV2 multi-camera tracking data.
- Schedule target: Scenario S01 first, then S02/S03 for scalability.

License note:

- The AI City page states that clicking the download link means accepting the data license agreement.

After download:

1. Extract the dataset outside the git repository.
2. Record the local path in an untracked copy of `docs/setup/LOCAL_PATHS.md`.
3. Run the readiness check with the chosen local path.

```bash
python scripts/check_research_readiness.py --cityflow-root <path-to-CityFlowV2> --detector-weights <path-to-detector-weights> --reid-weights <path-to-reid-weights>
```

## BoT-SORT

The repository setup script clones BoT-SORT automatically:

```bash
python scripts/setup_repo.py
```

Default upstream:

- `https://github.com/NirAharon/BoT-SORT.git`

Local path:

- `vendor/BoT-SORT`

The local checkout is ignored by git. The PRIME patch is tracked in:

- `patches/0001-Add-PRIME-ReID-poison-and-export-hooks.patch`

## Detector Weights

Required for real BoT-SORT runs.

BoT-SORT's demo examples use the ByteTrack/YOLOX MOT17 detector checkpoint:

- `bytetrack_x_mot17.pth.tar`
- `https://drive.google.com/file/d/1P4mY0Yyd3PPTybgZkjMYhFri88nTmJX5/view?usp=sharing`

Expected local location:

- `vendor/BoT-SORT/pretrained/bytetrack_x_mot17.pth.tar`

Record the local path in:

- `docs/setup/LOCAL_PATHS.md`

Do not commit the weight file.

## FastReID / OSNet Weights

There are two related but different needs:

1. BoT-SORT-ReID experiment weights.
2. Week 1 OSNet/ReID teaching-demo weights.

### BoT-SORT-ReID Weights

The patched BoT-SORT checkout uses FastReID through:

- `vendor/BoT-SORT/fast_reid/fast_reid_interfece.py`

BoT-SORT's README says trained ReID models should be stored in:

- `vendor/BoT-SORT/pretrained/`

BoT-SORT lists these ReID downloads:

- MOT17-SBS-S50: `https://drive.google.com/file/d/1QZFWpoa80rqo7O-HXmlss8J8CnS7IUsN/view?usp=sharing`
- MOT20-SBS-S50: `https://drive.google.com/file/d/1KqPQyj6MFyftliBHEIER7m_OrGpcrJwi/view?usp=sharing`

These are person/MOT ReID weights from the BoT-SORT project. They are useful for reproducing BoT-SORT's MOT17/MOT20 setup, but Sabrina should decide whether they are appropriate for CityFlowV2 vehicle tracking.

### Vehicle ReID Weights For CityFlowV2

Because CityFlowV2 is a vehicle tracking dataset, the more natural FastReID source is the FastReID vehicle model zoo.

The local BoT-SORT checkout includes a VeRi vehicle config:

- `vendor/BoT-SORT/fast_reid/configs/VeRi/sbs_R50-ibn.yml`

FastReID's model zoo lists the matching VeRi model:

- `veri_sbs_R50-ibn.pth`
- `https://github.com/JDAI-CV/fast-reid/releases/download/v0.1.1/veri_sbs_R50-ibn.pth`

Recommended starting point for this project:

- Config: `vendor/BoT-SORT/fast_reid/configs/VeRi/sbs_R50-ibn.yml`
- Weights: `veri_sbs_R50-ibn.pth`
- Expected local location: `vendor/BoT-SORT/pretrained/veri_sbs_R50-ibn.pth`

### OSNet Demo Weights

The schedule asks Sabrina to demonstrate OSNet/ReID embeddings on two crop images during Week 1. That can be a teaching demo separate from the BoT-SORT real-data run.

Use the torchreid/deep-person-reid model zoo for OSNet demo weights:

- `https://kaiyangzhou.github.io/deep-person-reid/MODEL_ZOO`

For the project experiments, keep the production BoT-SORT/FastReID weight choice documented separately from the Week 1 OSNet demo choice.

Record the local path in:

- `docs/setup/LOCAL_PATHS.md`

Do not commit the weight file.

## Local Path Tracking

Each machine should keep a private local path file:

```bash
copy docs\setup\LOCAL_PATHS.template.md docs\setup\LOCAL_PATHS.md
```

`docs/setup/LOCAL_PATHS.md` is ignored by git because it contains machine-specific paths.
