# BoT-SORT GPU Runbook (RESEARCHER)

This runbook is the end-to-end procedure for running the patched BoT-SORT
tracker on a GPU box to export ReID embeddings (clean and poisoned) as CSVs.

It is written for the **researcher** who operates the tracker. **Students do
not run BoT-SORT** -- they consume the exported CSVs. See
[Researcher vs. student](#researcher-vs-student) below.

Everything here was verified on a rented GPU box (RTX 4090, driver 570 /
CUDA 12.8, Ubuntu). Adjust paths/CUDA tags to your box.

---

## Researcher vs. student

| | Researcher (this doc) | Student |
| --- | --- | --- |
| **Goal** | Run BoT-SORT, export embedding CSVs | Analyze the exported CSVs |
| **Env** | conda `botsort`, **Python 3.9** | project `.venv`, Python 3.12 |
| **Deps** | `requirements-botsort-py39.txt` + torch (CUDA) | project `pyproject.toml` |
| **Hardware** | NVIDIA GPU | any laptop |
| **Entry point** | `vendor/BoT-SORT/tools/demo.py` | `scripts/analyze_embedding_export.py` |

If you only need to work with results, stop reading and see the student CSV
workflow doc instead.

---

## 1. Prerequisites on the box

- An NVIDIA GPU. Confirm the driver and CUDA with `nvidia-smi`.
- `conda` (Miniconda/Anaconda) and `git`.
- The detector + ReID weights (see `docs/setup/DOWNLOADS.md`):
  - Detector: `bytetrack_x_mot17.pth.tar`
  - ReID: `mot17_sbs_S50.pth` (or the VeRi vehicle weights for vehicle data)
- The intersection footage arranged in the standard layout
  (`<root>/S01/c001/vdo.mp4`, ...). See `docs/setup/DOWNLOADS.md`.

---

## 2. Create the Python 3.9 environment

**Python 3.9 is mandatory.** FastReID imports `collections.Mapping`, which was
removed in Python 3.10+. Using 3.10/3.11/3.12 fails at import time.

```bash
conda create -y -n botsort python=3.9
conda activate botsort
python --version   # must say 3.9.x
```

If `python --version` still shows 3.10+ after activating, vast.ai's default
`/venv/main` env (auto-activated on every login by the container template) is
shadowing conda on `PATH`. Leave it first, then re-activate:

```bash
deactivate 2>/dev/null        # leave vast.ai's /venv/main if active
conda deactivate 2>/dev/null  # in case conda is also stacked
conda activate botsort
which python                  # should be /venv/botsort/bin/python
```

---

## 3. Install PyTorch (separately, from the CUDA index)

PyTorch is installed on its own because its wheels come from a CUDA-specific
index URL. Do **not** put torch in the requirements file -- that index would
override PyPI for every other package.

```bash
pip install torch==2.5.1 torchvision==0.20.1 --index-url https://download.pytorch.org/whl/cu121
```

Pin these **exact** versions. A bare `pip install torch torchvision` now
resolves to torch 2.11/cu128, which publishes **no Python 3.9 wheels** and will
fail or pull an incompatible build. `cu121` wheels are verified working on the
box's newer driver/CUDA (CUDA wheels are forward compatible). Sanity check:

```bash
python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
```

Expect `True`.

---

## 4. Install the remaining dependencies

```bash
pip install -r requirements-botsort-py39.txt
```

This is the verified BoT-SORT/FastReID dependency set, including the required
`numpy<1.24` and `scipy<1.11` ceilings. See the file's header for why.

---

## 5. Create the patched BoT-SORT checkout

```bash
python scripts/setup_repo.py --skip-venv
```

Use `--skip-venv` here: on the GPU box you run BoT-SORT from this Python 3.9
`botsort` env, and the project `.venv` would fail to install (the project
package requires Python >=3.10). Without `--skip-venv`, the script first tries
to build the project `.venv` from the active 3.9 interpreter and aborts.

`setup_repo.py` clones BoT-SORT at the pinned commit
(`251985436d6712aaf682aaaf5f71edb4987224bd`) and applies the PRIME patch with
`git apply`. The patch adds the PRIME export/poison flags **and** the
py3.9/torch-2.x/headless compatibility fixes (the `torch._six` import and the
`cv2.waitKey` GUI call), so a fresh checkout runs without manual edits.

If the patch does not apply, the script hard-fails with a clear message --
do not proceed past it.

Place the weights where the demo expects them. This project uses the **VeRi
vehicle** ReID model (the footage is vehicles, not people):

```
vendor/BoT-SORT/pretrained/bytetrack_x_mot17.pth.tar   # YOLOX detector
vendor/BoT-SORT/pretrained/veri_sbs_R50-ibn.pth        # VeRi vehicle ReID
```

See `docs/setup/DOWNLOADS.md` for the download links.

---

## 6. Run the tracker and export embeddings

The demo **requires** the YOLOX exp file (`-f`) and detector checkpoint
(`--ckpt`). Omitting them produces a confusing "exp file" error; this is why the
example below is the full command, not the abbreviated form.

Run commands from inside `vendor/BoT-SORT` so the relative `pretrained/` and
`fast_reid/` paths resolve.

The commands below are the exact verified-working invocations from the GPU box.

### Clean run (per camera)

```bash
cd vendor/BoT-SORT
python tools/demo.py video \
  --path /root/blindspot_data/S01/c001/vdo.mp4 \
  -f yolox/exps/example/mot/yolox_x_mix_det.py \
  --ckpt pretrained/bytetrack_x_mot17.pth.tar \
  --with-reid \
  --fast-reid-config fast_reid/configs/VeRi/sbs_R50-ibn.yml \
  --fast-reid-weights pretrained/veri_sbs_R50-ibn.pth \
  --prime-camera-id c01 \
  --prime-export-embeddings ../../runs/botsort/clean_c01.csv \
  --save_result
```

### Poisoned run

Add the poison flags; keep a separate output path:

```bash
python tools/demo.py video \
  --path /root/blindspot_data/S01/c001/vdo.mp4 \
  -f yolox/exps/example/mot/yolox_x_mix_det.py \
  --ckpt pretrained/bytetrack_x_mot17.pth.tar \
  --with-reid \
  --fast-reid-config fast_reid/configs/VeRi/sbs_R50-ibn.yml \
  --fast-reid-weights pretrained/veri_sbs_R50-ibn.pth \
  --prime-camera-id c01 \
  --prime-poison-cameras c01,c02 \
  --prime-poison-epsilon 0.5 \
  --prime-poison-seed 7 \
  --prime-export-embeddings ../../runs/botsort/poisoned_c01.csv \
  --save_result
```

Notes:
- The box is usually **headless** (no display). The patch replaces the demo's
  `cv2.waitKey(1)` GUI call, so it runs without an X server. If you hit any
  other `cv2.imshow`/GUI error, you are on an unpatched checkout -- redo step 5.
- `--save_result` writes an annotated video. The embedding CSV is produced by
  `--prime-export-embeddings` regardless; drop `--save_result` if you only need
  the CSV.
- `--fp16`/`--fuse` are optional speed flags and were **not** used in the
  verified run; add them only if you confirm they don't change the output.
- Repeat per camera (`c001`, `c002`, `c003`) and per scenario, changing
  `--path`, `--prime-camera-id`, and the output CSV name.

---

## 7. Validate the CSV

The exported CSV has one row per detection with the header:

```
camera,frame,detection_index,x1,y1,x2,y2,embedding
```

`embedding` is a space-separated float vector. Quick checks:

```bash
head -1 ../../runs/botsort/clean_c01.csv
wc -l ../../runs/botsort/clean_c01.csv
# embedding dimension of the first data row:
sed -n '2p' ../../runs/botsort/clean_c01.csv | awk -F',' '{print NF" cols; "split($NF,a," ")" dims"}'
```

---

## 8. View the annotated results (boxes + track ids)

When you pass `--save_result`, the demo writes an annotated video with the
bounding boxes and track ids drawn on each frame. YOLOX/BoT-SORT puts it under
`YOLOX_outputs/<exp-name>/track_vis/<timestamp>/`. Since you run from inside
`vendor/BoT-SORT`, locate the newest one with:

```bash
find YOLOX_outputs -name '*.mp4' -printf '%T+ %p\n' | sort | tail
# e.g. YOLOX_outputs/yolox_x_mix_det/track_vis/2026_06_09_18_05_12/vdo.mp4
```

The box is **headless**, so view the video off-box one of two ways:

- **Download and play locally** (from your own machine):

  ```bash
  scp root@<box-host>:/workspace/blindspot-summer-2026/vendor/BoT-SORT/YOLOX_outputs/yolox_x_mix_det/track_vis/<timestamp>/vdo.mp4 .
  ```

  Then open it in VLC / any player.

- **In a Jupyter session on the box** (if the rental provides one): browse to
  the folder and download, or display inline:

  ```python
  from IPython.display import Video
  Video("vendor/BoT-SORT/YOLOX_outputs/yolox_x_mix_det/track_vis/<timestamp>/vdo.mp4")
  ```

Students do not get this video; they redraw boxes from the exported CSV with
`scripts/visualize_boxes.py` (see `docs/experiments/STUDENT_EMBEDDING_ANALYSIS.md`).

---

## 9. Hand off to students

Copy the CSVs out of `runs/botsort/` to wherever students retrieve results.
Do **not** commit CSVs, weights, or videos to git. Record each run's metadata
(see the "Required Run Log Fields" in `BOTSORT_INTEGRATION.md`): fork commit,
Python/PyTorch/CUDA, scenario/camera, epsilon/seed, and the exact command.

Students then analyze the CSVs with `scripts/analyze_embedding_export.py`.

---

## Troubleshooting (lessons from the first run)

| Symptom | Cause | Fix |
| --- | --- | --- |
| `cannot import name 'Mapping' from 'collections'` / `collections.Mapping` | Python 3.10+ | Use Python 3.9 (step 2) |
| `No module named 'torch._six'` | torch 2.x removed `_six` | Use the patched checkout (step 5); fix is in the patch |
| `cv2.imshow`/`waitKey` / `not implemented` GUI error | headless box | Use the patched checkout (step 5); `opencv-python-headless` |
| numpy/scipy `AttributeError` (e.g. `np.float`) | numpy>=1.24 / scipy>=1.11 | The pins in `requirements-botsort-py39.txt` |
| "exp file" / detector error | missing `-f`/`-c` | Pass both, as in step 6 |
| `git am` fails: "empty ident" / "no email" | no git identity for `git am` | `setup_repo.py` now uses `git apply` (no identity needed) |
| Patch did not apply | upstream drift / already applied | Re-run `setup_repo.py --force` |
| `conda activate botsort` but `python --version` is 3.12 | vast.ai's `/venv/main` is shadowing conda on `PATH` | `deactivate` `/venv/main`, then `conda activate botsort` |
| `pip install torch` fails / no matching distribution | torch 2.11/cu128 has no py3.9 wheels | pin `torch==2.5.1 torchvision==0.20.1` (cu121) |
