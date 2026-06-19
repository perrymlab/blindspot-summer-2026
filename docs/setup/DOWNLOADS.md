# Required Downloads

This document lists external data and model artifacts needed for the project. Do not commit datasets, model weights, videos, or raw tracker outputs to git.

> Rebuilding a GPU box from scratch (e.g. after a cloud instance was wiped)?
> See `docs/setup/RECOVERY.md` for the full recovery checklist.

## Intersection Footage (`blindspot_data`)

The project runs on locally captured multi-camera intersection footage,
**not** the public CityFlowV2 / AI City Challenge dataset. Sabrina is the
source of truth for the raw videos; ask her how to obtain or sync them onto
your machine.

Once you have the raw captures, the project tooling expects them arranged
on disk in this layout (the layout itself is borrowed from CityFlowV2 so
that future external data could plug in without changing the code):

```
<data root>/
    S01/c001/vdo.mp4
    S01/c002/vdo.mp4
    S01/c003/vdo.mp4
    S02/...
    ...
```

Default data root:

- `~/blindspot_data` on macOS/Linux
- `C:\Users\<you>\blindspot_data` on Windows
- `/workspace/blindspot_data` on a GPU box (persistent volume; auto-detected)
- override with the `BLINDSPOT_DATA_ROOT` environment variable

Workflow:

1. Place or symlink the raw captures somewhere outside the git repository.
2. If they did not already arrive in the layout above, normalize them with
   `python scripts/organize_blindspot_data.py --apply` (dry-run first
   without `--apply`).
3. Pick a 2-5 minute trim window per scenario and record it in
   `data/scenario_windows.csv`. See
   `docs/data/SCENARIO_TRIMMING.md` for the full workflow.
4. Run the readiness check:

```bash
python scripts/check_research_readiness.py
```

The data root and both weight paths auto-detect: the data root from
`$BLINDSPOT_DATA_ROOT` / `/workspace/blindspot_data`, and the weights from
`vendor/BoT-SORT/pretrained/` (`yolox_x.pth` detector, `veri_sbs_R50-ibn.pth`
ReID). Override only if they live elsewhere:

```bash
python scripts/check_research_readiness.py \
  --data-root <data root> \
  --detector-weights <path-to-detector-weights> \
  --reid-weights <path-to-reid-weights>
```

Run this inside the researcher `botsort` conda env (Python 3.9). The old
`--cityflow-root` flag still works as a deprecated alias for `--data-root`.

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

### Use the COCO YOLOX-x detector (vehicles)

This project tracks **vehicles**. Use the COCO-pretrained YOLOX-x detector,
which emits `car`/`motorcycle`/`bus`/`truck` boxes, and restrict it to those
classes with the patched `--prime-classes` flag.

- Weights: `yolox_x.pth`
- `https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_x.pth`
- Exp file (already in the checkout): `vendor/BoT-SORT/yolox/exps/default/yolox_x.py` (COCO, 80 classes)
- COCO vehicle class ids: `2` car, `3` motorcycle, `5` bus, `7` truck → pass `--prime-classes 2,3,5,7`

Expected local location:

- `vendor/BoT-SORT/pretrained/yolox_x.pth`

See the runbook for the full demo command:
`docs/botsort-integration/BOTSORT_GPU_RUNBOOK.md`.

### Why not the MOT17 detector

BoT-SORT's demo examples use the ByteTrack/YOLOX **MOT17** checkpoint
(`bytetrack_x_mot17.pth.tar`), which is a single-class **pedestrian** detector.
On intersection vehicle footage it barely fires — a baseline run produced only
~8 detections across 6000 frames — so the annotated video looked empty and the
embedding export was nearly empty. It is the wrong detector for this project and
should not be used for vehicle runs.

- `bytetrack_x_mot17.pth.tar` (pedestrians — **do not use for vehicle runs**)
- `https://drive.google.com/file/d/1P4mY0Yyd3PPTybgZkjMYhFri88nTmJX5/view?usp=sharing`

Record the local detector path in:

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
cp docs/setup/LOCAL_PATHS.template.md docs/setup/LOCAL_PATHS.md
```

`docs/setup/LOCAL_PATHS.md` is ignored by git because it contains machine-specific paths.
