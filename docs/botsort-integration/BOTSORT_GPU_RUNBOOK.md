# BoT-SORT GPU Runbook

End-to-end procedure for running the patched BoT-SORT tracker on a GPU box to export ReID embeddings (clean and poisoned) as CSVs.

**This doc is for the researcher only.** Students do not run BoT-SORT - they work with the exported CSVs. If you only need to analyze results, see `docs/experiments/STUDENT_EMBEDDING_ANALYSIS.md`.


## Researcher vs. student
| | Researcher | Student |
| --- | --- | --- |
| **Goal** | Run BoT-SORT, export embedding CSVs | Analyze the exported CSVs |
| **Environment** | conda `botsort`, Python 3.9 | project `.venv`, Python 3.12 |
| **Dependencies** | `requirements-botsort-py39.txt` + torch (CUDA) | project `pyproject.toml` |
| **Hardware** | NVIDIA GPU | any laptop |
| **Entry point** | `vendor/BoT-SORT/tools/demo.py` | `scripts/analyze_embedding_export.py` |

If you only need to work with results, stop reading and see the student CSV
workflow doc instead.

---

## 1. Prerequisites on the box

- NVIDIA GPU — confirm driver and CUDA with `nvidia-smi`
- `conda` (Miniconda or Anaconda) and `git`
- Detector and ReID weights (see `docs/setup/DOWNLOADS.md`):
  - `yolox_x.pth` — COCO YOLOX-x vehicle detector
  - `veri_sbs_R50-ibn.pth` — VeRi vehicle ReID weights
- Intersection footage in the standard layout: `<root>/S01/c001/vdo.mp4`, etc.

---

## 2. Create the Python 3.9 environment
**Python 3.9 is mandatory.** FastReID imports `collections.Mapping`, which was removed in Python 3.10+. Any newer version fails at import time.

```bash
conda create -y -n botsort python=3.9
conda activate botsort
python --version   # must say 3.9.x
```

If `python --version` still shows 3.10+ after activating, the vast.ai default `/venv/main` environment is shadowing conda on `PATH`. Fix it:

```bash
deactivate 2>/dev/null
conda deactivate 2>/dev/null
conda activate botsort
which python   # should be /venv/botsort/bin/python
```
---

## 3. Install PyTorch

PyTorch must be installed separately because its wheels come from a CUDA-specific index URL.

```bash
pip install torch==2.5.1 torchvision==0.20.1 --index-url https://download.pytorch.org/whl/cu121
```

Pin these exact versions. A bare `pip install torch torchvision` now resolves to torch 2.11/cu128, which has no Python 3.9 wheels. The `cu121` wheels are verified working on the box's driver/CUDA — CUDA wheels are forward compatible.

Sanity check:

```bash
python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
# expect: 2.5.1+cu121 True
```

---

## 4. Install remaining dependencies

```bash
pip install -r requirements-botsort-py39.txt
```

This file contains the verified BoT-SORT/FastReID dependency set, including required version ceilings for `numpy<1.24` and `scipy<1.11`. See the file header for details.

---

## 5. Set up the patched BoT-SORT checkout

```bash
python scripts/setup_repo.py --skip-venv
```

Use `--skip-venv` because the project package requires Python >=3.10 and will fail to install under the 3.9 env. Without the flag, the script tries to build the project `.venv` first and aborts.

`setup_repo.py` clones BoT-SORT at the pinned commit (`251985436d6712aaf682aaaf5f71edb4987224bd`) and applies the PRIME patch via `git apply`. The patch adds the PRIME export and poison flags, plus py3.9/torch-2.x/headless compatibility fixes (the `torch._six` import and the `cv2.waitKey` GUI call).

**If the patch does not apply, the script hard-fails — do not proceed past it.**

Place the weights where the demo expects them:

```
vendor/BoT-SORT/pretrained/yolox_x.pth
vendor/BoT-SORT/pretrained/veri_sbs_R50-ibn.pth
```
---


## 6. Run the tracker

The demo requires both the YOLOX exp file (`-f`) and the detector checkpoint (`--ckpt`). Omitting either produces a confusing error. Run all commands from inside `vendor/BoT-SORT` so relative paths resolve correctly.

### Batch mode (recommended)

`scripts/run_baselines.py` handles whole scenarios — every camera, clean and poisoned — with self-describing output names, a provenance manifest (`runs/botsort/run_manifest.csv`), and per-scenario merged CSVs ready for student analysis. Run from the **repo root**:

```bash
# Preview the plan without running
python scripts/run_baselines.py --scenarios S01,S02

# Run it
python scripts/run_baselines.py --scenarios S01,S02 --apply

# Run all scenarios with multiple epsilon values
python scripts/run_baselines.py --all --epsilons 0.1,0.5,1.0 --apply
```

Outputs land in `runs/botsort/<scenario>/`, e.g. `S01_c01_clean.csv` and `S01_poison_c01-c02_eps0.5_seed7_all-cams.csv`. The script prefers trimmed videos (`vdo_trim.mp4`), skips already-completed CSVs (resume-friendly), and adds annotated videos with `--save-result`.

The per-camera commands below are the reference for what batch mode runs under the hood, and for one-off debugging.

### Clean run (per camera)

```bash
cd vendor/BoT-SORT
python tools/demo.py video \
  --path /workspace/blindspot_data/S01/c001/vdo.mp4 \
  -f yolox/exps/default/yolox_x.py \
  --ckpt pretrained/yolox_x.pth \
  --prime-classes 2,3,5,7 \
  --aspect_ratio_thresh 10 \
  --with-reid \
  --fast-reid-config fast_reid/configs/VeRi/sbs_R50-ibn.yml \
  --fast-reid-weights pretrained/veri_sbs_R50-ibn.pth \
  --prime-camera-id c01 \
  --prime-export-embeddings ../../runs/botsort/S01/S01_c01_clean.csv \
  --save_result
```

### Poisoned run (per camera)

```bash
python tools/demo.py video \
  --path /workspace/blindspot_data/S01/c001/vdo.mp4 \
  -f yolox/exps/default/yolox_x.py \
  --ckpt pretrained/yolox_x.pth \
  --prime-classes 2,3,5,7 \
  --aspect_ratio_thresh 10 \
  --with-reid \
  --fast-reid-config fast_reid/configs/VeRi/sbs_R50-ibn.yml \
  --fast-reid-weights pretrained/veri_sbs_R50-ibn.pth \
  --prime-camera-id c01 \
  --prime-poison-cameras c01,c02 \
  --prime-poison-epsilon 0.5 \
  --prime-poison-seed 7 \
  --prime-export-embeddings ../../runs/botsort/S01/S01_c01_poison_c01-c02_eps0.5_seed7.csv \
  --save_result
```

**Notes:**

- **Use the COCO YOLOX-x detector, not the MOT17 detector.** This is a vehicle project. The MOT17 detector (`bytetrack_x_mot17.pth.tar`) is trained on pedestrians and finds almost nothing on vehicle footage (~8 detections in 6000 frames). Use `-f yolox/exps/default/yolox_x.py` with `--prime-classes 2,3,5,7` (COCO car/motorcycle/bus/truck).
- **`--aspect_ratio_thresh 10`** keeps wide vehicle bounding boxes. The default (`1.6`) is tuned for upright pedestrians and silently drops wide boxes from the visualization. The embedding CSV export is unaffected either way.
- **Annotated video output path** changes with the exp file. With the COCO exp, the video lands under `YOLOX_outputs/yolox_x/track_vis/<timestamp>/` (not `yolox_x_mix_det`).
- **The box is headless.** The patch replaces the `cv2.waitKey(1)` GUI call so the demo runs without an X server. If you hit a `cv2.imshow` or GUI error, you are on an unpatched checkout — redo step 5.
- **`--save_result`** writes an annotated video. The embedding CSV is produced by `--prime-export-embeddings` regardless; drop `--save_result` if you only need the CSV.
- **`--fp16`/`--fuse`** are optional speed flags and were not used in the verified run. Add them only if you confirm they don't change the output.
- Repeat for each camera (`c001`, `c002`, `c003`) and each scenario, updating `--path`, `--prime-camera-id`, and the output CSV name.

---

## 7. Validate the CSV

The exported CSV has one row per detection:

```
camera,frame,detection_index,x1,y1,x2,y2,embedding
```

`embedding` is a space-separated float vector. Quick checks:

```bash
# Check the header
head -1 ../../runs/botsort/S01/S01_c01_clean.csv

# Check the row count
wc -l ../../runs/botsort/S01/S01_c01_clean.csv

# Check the embedding dimension of the first data row
sed -n '2p' ../../runs/botsort/S01/S01_c01_clean.csv \
  | awk -F',' '{print NF" cols; "split($NF,a," ")" dims"}'
```

---

## 8. View the annotated video

When `--save_result` is passed, the demo writes an annotated video under `YOLOX_outputs/<exp-name>/track_vis/<timestamp>/`. Find the newest one:

```bash
find YOLOX_outputs -name '*.mp4' -printf '%T+ %p\n' | sort | tail
```

The box is headless, so view off-box:

**Download and play locally** (from your own machine):

```bash
scp root@<box-host>:/workspace/blindspot-summer-2026/vendor/BoT-SORT/YOLOX_outputs/yolox_x/track_vis/<timestamp>/vdo.mp4 .
```

Open in VLC or any player.

**In a Jupyter session on the box:** The demo writes with OpenCV's `mp4v` codec, which browsers cannot play inline. Transcode to H.264 first:

```bash
ffmpeg -i vdo.mp4 -vcodec libx264 -pix_fmt yuv420p vdo_h264.mp4
```

```python
from IPython.display import Video
Video("vdo_h264.mp4", embed=True)
```
---

## 9. What to hand off to students

Give students the per-scenario **merged** files (`*_all-cams.csv`) — the cross-camera detector needs all cameras in one table. Per-camera files are for debugging. If you used batch mode, `runs/botsort/run_manifest.csv` already has each run's metadata; copy the relevant rows into the run log.

Do not commit raw CSVs, weights, or videos to git — `runs/` is gitignored. To version an export or preserve it off the ephemeral box, see `docs/data/SYNCING_RUN_OUTPUTS.md`.

Record each run's metadata in the run log: fork commit, Python/PyTorch/CUDA versions, scenario/camera, epsilon/seed, and the exact command used.
---
