# GPU Cloud Full Test Plan

A single, self-contained runbook for cloning this repo onto a fresh GPU cloud server, installing every dependency, exercising every implemented feature end to end, and recording what work is still outstanding. Read top to bottom; nothing else in `docs/` is required to follow this file.

> Repo: `https://github.com/perrymlab/blindspot-summer-2026`
> Source of truth for related docs (only consult if something here is ambiguous): `docs/setup/PERRY_QUICKSTART.md`, `docs/setup/DOWNLOADS.md`, `docs/botsort-integration/BOTSORT_INTEGRATION.md`, `docs/data/SCENARIO_TRIMMING.md`.

---

## 0. What "full test" covers

Implemented features that this plan exercises:

- **Synthetic pipeline (CPU only)**: `prime_mtmc` package — synthetic embeddings, random/targeted additive poisoning, cross-camera consistency detector, precision/recall/F1 metrics, plus `pytest` and `scripts/smoke_test.py`.
- **Synthetic experiment CLI**: `scripts/run_synthetic_experiment.py` (writes clean/poisoned CSVs and a `summary.csv`).
- **Readiness check**: `scripts/check_research_readiness.py`.
- **Data organization & trimming**: `scripts/organize_blindspot_data.py`, `scripts/trim_scenarios.py`, `scripts/scenario_quicklook.py`, manifest at `data/scenario_windows.csv`.
- **BoT-SORT integration (GPU)**: patched `vendor/BoT-SORT` on branch `prime-reid-poison-export` with PRIME flags `--prime-camera-id`, `--prime-poison-cameras`, `--prime-poison-epsilon`, `--prime-poison-seed`, `--prime-export-embeddings`.
- **Embedding analyzer on real exports**: `scripts/analyze_embedding_export.py`.

Anything not in this list is in section 8 ("Work still outstanding").

---

## 1. Provision the GPU cloud server

Pick any provider (Lambda, RunPod, Paperspace, vast.ai, AWS g5/p3, GCP A100, etc.). Target image:

- **OS**: Ubuntu 22.04 LTS (or 20.04). Linux is what the repo's CI runs against.
- **GPU**: any single CUDA GPU with >= 8 GB VRAM (BoT-SORT + YOLOX-x + FastReID R50). 16 GB is comfortable.
- **CUDA**: 11.8 or 12.1 driver. The matching PyTorch wheel will be installed below.
- **Disk**: at least **80 GB** free. CityFlowV2 (`AICity22_Track1_MTMC_Tracking.zip`) alone is tens of GB.
- **Python**: 3.10 or newer (`python3 --version`). If the image only ships 3.8/3.9, install 3.10 via `deadsnakes` PPA or use `conda`.

Confirm GPU is visible:

```bash
nvidia-smi
```

Install OS-level prerequisites (one shot):

```bash
sudo apt-get update
sudo apt-get install -y git git-lfs python3.10 python3.10-venv python3-pip ffmpeg build-essential
git lfs install
```

`ffmpeg` is required by `scripts/trim_scenarios.py` and `scripts/scenario_quicklook.py`.

---

## 2. Clone the repo and configure git identity

```bash
cd ~
git clone https://github.com/perrymlab/blindspot-summer-2026.git
cd blindspot-summer-2026

# Per-repo identity so commits stamp correctly without touching global git.
git config user.name "Brian"
git config user.email "<your-noreply-email>@users.noreply.github.com"
```

If you plan to push from this server, authenticate with a fine-grained PAT (see `docs/setup/PERRY_QUICKSTART.md`) or `gh auth login`.

---

## 3. Bootstrap the Python environment + smoke test

The repo ships a one-shot bootstrap that creates `.venv`, installs the local package, clones BoT-SORT into `vendor/BoT-SORT`, applies the tracked PRIME patch, and runs the smoke test.

```bash
python3.10 scripts/setup_repo.py
```

What this does (see `@/home/brian/blindspot-summer-2026/scripts/setup_repo.py:43-67`):

1. Creates `.venv/` and `pip install -e .[dev]`.
2. `git clone https://github.com/NirAharon/BoT-SORT.git vendor/BoT-SORT`.
3. Checks out branch `prime-reid-poison-export` from `origin/main` and applies `patches/0001-Add-PRIME-ReID-poison-and-export-hooks.patch` via `git am`.
4. Runs `scripts/smoke_test.py`.

Expected tail of stdout: `smoke tests passed`.

Activate the venv for the rest of the session:

```bash
source .venv/bin/activate
```

---

## 4. Run every CPU-only feature test

These should all pass on the GPU box without any data downloads.

### 4a. Smoke test (already run by setup_repo)

```bash
python scripts/smoke_test.py
```

Pass criterion: prints `smoke tests passed`. Covers poisoning selectivity and detector recall on synthetic data (`@/home/brian/blindspot-summer-2026/scripts/smoke_test.py:21-49`).

### 4b. Pytest

```bash
pytest -q
```

Pass criterion: green. Covers `tests/test_poison_detector.py`.

### 4c. Synthetic experiment CLI

```bash
python scripts/run_synthetic_experiment.py --out-dir runs/synthetic
```

Pass criterion: prints a summary table to stdout and writes:

- `runs/synthetic/clean_embeddings.csv`
- `runs/synthetic/poisoned_eps_{0.1,0.5,1}.csv`
- `runs/synthetic/scores_clean.csv`, `runs/synthetic/scores_eps_*.csv`
- `runs/synthetic/summary.csv` — should show recall climbing as `epsilon` grows from 0.1 → 1.0 for poisoned cameras `c01,c02`.

Sanity check:

```bash
column -s, -t < runs/synthetic/summary.csv | head
```

### 4d. Analyzer dry run on the synthetic poisoned table

`scripts/analyze_embedding_export.py` was written for the BoT-SORT export schema (`scenario,camera,frame,track_id,embedding`). The synthetic CSV uses the per-dimension `e0..eN` schema instead, so a true round-trip needs a real export (section 6). For now confirm the script imports cleanly:

```bash
python scripts/analyze_embedding_export.py --help
```

### 4e. CI parity check

The `.github/workflows/ci.yml` workflow runs `pytest` on every PR. Re-running locally proves your venv matches CI:

```bash
pytest -q
```

If sections 4a–4e all pass, every CPU-only feature in the repo is verified.

---

## 5. GPU-side dependencies for BoT-SORT

BoT-SORT is **not** installed by `pyproject.toml`; it lives under `vendor/BoT-SORT` and has its own (heavier) deps. Install them into the same `.venv`.

### 5a. PyTorch with CUDA

Match your driver. Examples:

```bash
# CUDA 12.1
pip install torch==2.2.2 torchvision==0.17.2 --index-url https://download.pytorch.org/whl/cu121

# OR CUDA 11.8
pip install torch==2.2.2 torchvision==0.17.2 --index-url https://download.pytorch.org/whl/cu118
```

Verify:

```bash
python -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

### 5b. BoT-SORT requirements

```bash
pip install -r vendor/BoT-SORT/requirements.txt
pip install cython
pip install 'git+https://github.com/cocodataset/cocoapi.git#subdirectory=PythonAPI'
pip install cython_bbox lap

# YOLOX is bundled inside BoT-SORT
pip install -v -e vendor/BoT-SORT
```

If `pip install -v -e vendor/BoT-SORT` complains about a missing `setup.py`, build YOLOX directly:

```bash
pip install -v -e vendor/BoT-SORT/yolox  # only if YOLOX ships its own setup.py path
```

### 5c. FastReID

FastReID is vendored inside BoT-SORT under `vendor/BoT-SORT/fast_reid/`. It typically only needs:

```bash
pip install yacs scikit-learn faiss-cpu termcolor tabulate gdown
```

`gdown` is convenient for the Google Drive weight downloads in section 5e.

### 5d. Sanity check the BoT-SORT checkout

```bash
git -C vendor/BoT-SORT status --short --branch
# expected: "## prime-reid-poison-export"

grep -n "prime-camera-id" vendor/BoT-SORT/tools/demo.py | head
grep -n "PRIME" vendor/BoT-SORT/fast_reid/fast_reid_interfece.py | head
```

Both greps must return matches; that confirms the patch applied.

### 5e. Download model weights

Reference: `docs/setup/DOWNLOADS.md`. Targets and destinations:

```bash
mkdir -p vendor/BoT-SORT/pretrained
cd vendor/BoT-SORT/pretrained

# Detector (ByteTrack/YOLOX MOT17 weights used by demo.py)
gdown 'https://drive.google.com/uc?id=1P4mY0Yyd3PPTybgZkjMYhFri88nTmJX5' -O bytetrack_x_mot17.pth.tar

# Vehicle ReID weights for CityFlowV2 (matches fast_reid/configs/VeRi/sbs_R50-ibn.yml)
wget https://github.com/JDAI-CV/fast-reid/releases/download/v0.1.1/veri_sbs_R50-ibn.pth

cd -
```

If `gdown` hits Google Drive quota, manually download the file and `scp` it to the server.

---

## 6. Real-data run on CityFlowV2 S01

### 6a. Download CityFlowV2

Request access on `https://www.aicitychallenge.org/2022-track1-download/` and download `AICity22_Track1_MTMC_Tracking.zip`. On the GPU server:

```bash
mkdir -p ~/blindspot_data
# scp/wget the zip into ~/blindspot_data/, then:
unzip -q ~/blindspot_data/AICity22_Track1_MTMC_Tracking.zip -d ~/blindspot_data/
```

The dataset's `train/S01/c001/vdo.mp4` (and `c002`, `c003`, …) layout already matches what the repo expects. If your local raw footage has a different layout, use:

```bash
python scripts/organize_blindspot_data.py --apply --source <raw-folder> --dest ~/blindspot_data
```

Set the data root for downstream scripts:

```bash
export BLINDSPOT_DATA_ROOT=~/blindspot_data
```

### 6b. Record local paths

```bash
cp docs/setup/LOCAL_PATHS.template.md docs/setup/LOCAL_PATHS.md
# edit docs/setup/LOCAL_PATHS.md and fill in dataset/weights paths.
# This file is .gitignore'd.
```

### 6c. Readiness check

```bash
python scripts/check_research_readiness.py \
  --cityflow-root ~/blindspot_data \
  --detector-weights vendor/BoT-SORT/pretrained/bytetrack_x_mot17.pth.tar \
  --reid-weights vendor/BoT-SORT/pretrained/veri_sbs_R50-ibn.pth
```

Pass criterion: every line prefixed `[PASS]` and final message `Readiness check passed.` (`@/home/brian/blindspot-summer-2026/scripts/check_research_readiness.py:78-130`).

### 6d. Optional — trim scenarios for faster iteration

`data/scenario_windows.csv` already has `S01,0,120,...`. To pre-trim other scenarios you intend to run:

```bash
python scripts/trim_scenarios.py                # dry run
python scripts/trim_scenarios.py --apply        # writes vdo_trim.mp4 next to each vdo.mp4
python scripts/scenario_quicklook.py            # writes runs/quicklook/S0N.png composites
```

Skip this step on the first pass if you only care about S01.

### 6e. Clean per-camera BoT-SORT export

Run once per camera. Use the trimmed video if you produced one.

```bash
mkdir -p runs/botsort

for CAM in c001 c002 c003; do
  python vendor/BoT-SORT/tools/demo.py video \
    --path "$BLINDSPOT_DATA_ROOT/S01/$CAM/vdo.mp4" \
    --with-reid \
    -f vendor/BoT-SORT/yolox/exps/example/mot/yolox_x_mix_det.py \
    -c vendor/BoT-SORT/pretrained/bytetrack_x_mot17.pth.tar \
    --fast-reid-config vendor/BoT-SORT/fast_reid/configs/VeRi/sbs_R50-ibn.yml \
    --fast-reid-weights vendor/BoT-SORT/pretrained/veri_sbs_R50-ibn.pth \
    --prime-camera-id "${CAM/c00/c0}" \
    --prime-export-embeddings "runs/botsort/clean_${CAM}.csv"
done
```

Note: `--prime-camera-id c01` (not `c001`) matches the detector's `c01..cNN` convention used in synthetic data and in `data/scenario_windows.csv`.

Pass criterion: each `runs/botsort/clean_c0X.csv` exists and has one row per detection with columns at minimum `scenario,camera,frame,embedding` (plus a track-id column populated by the tracker).

### 6f. Poisoned per-camera export

Repeat the loop with poisoning enabled on cameras `c01,c02`, sweeping `epsilon ∈ {0.1, 0.5, 1.0}`:

```bash
for EPS in 0.1 0.5 1.0; do
  for CAM in c001 c002 c003; do
    python vendor/BoT-SORT/tools/demo.py video \
      --path "$BLINDSPOT_DATA_ROOT/S01/$CAM/vdo.mp4" \
      --with-reid \
      -f vendor/BoT-SORT/yolox/exps/example/mot/yolox_x_mix_det.py \
      -c vendor/BoT-SORT/pretrained/bytetrack_x_mot17.pth.tar \
      --fast-reid-config vendor/BoT-SORT/fast_reid/configs/VeRi/sbs_R50-ibn.yml \
      --fast-reid-weights vendor/BoT-SORT/pretrained/veri_sbs_R50-ibn.pth \
      --prime-camera-id "${CAM/c00/c0}" \
      --prime-poison-cameras c01,c02 \
      --prime-poison-epsilon $EPS \
      --prime-poison-seed 7 \
      --prime-export-embeddings "runs/botsort/poisoned_eps${EPS}_${CAM}.csv"
  done
done
```

### 6g. Merge per-camera exports → single table with track_ids

The exports are detection-level. The detector wants one merged CSV per condition. The minimum viable merge is concatenation when the per-camera tracker IDs are already global (BoT-SORT's `mc_demo.py` route) **or** when you accept per-camera IDs and only score statistics that don't require global identity. A quick concat:

```bash
python - <<'PY'
import pandas as pd, glob, os
for tag in ["clean", "poisoned_eps0.1", "poisoned_eps0.5", "poisoned_eps1.0"]:
    paths = sorted(glob.glob(f"runs/botsort/{tag}_c*.csv"))
    if not paths: continue
    df = pd.concat([pd.read_csv(p) for p in paths], ignore_index=True)
    out = f"runs/botsort/{tag}_merged.csv"
    df.to_csv(out, index=False)
    print(out, len(df))
PY
```

A proper global-ID merge is listed in section 8 as outstanding work.

### 6h. Run the analyzer on real exports

```bash
python scripts/analyze_embedding_export.py \
  --input runs/botsort/clean_merged.csv \
  --out-dir runs/embedding_analysis/clean

for EPS in 0.1 0.5 1.0; do
  python scripts/analyze_embedding_export.py \
    --input runs/botsort/poisoned_eps${EPS}_merged.csv \
    --out-dir runs/embedding_analysis/poisoned_eps${EPS} \
    --poisoned-cameras c01,c02
done
```

Pass criterion: each output dir contains `normalized_embeddings.csv`, `camera_scores.csv`, and (for poisoned runs) `metrics.csv` with non-NaN precision/recall/F1.

---

## 7. End-to-end pass/fail checklist

Tick these in order; stop at the first failure and debug.

- [ ] `nvidia-smi` shows the GPU.
- [ ] `python3.10 scripts/setup_repo.py` ends with `smoke tests passed`.
- [ ] `pytest -q` is green.
- [ ] `python scripts/run_synthetic_experiment.py --out-dir runs/synthetic` produces `summary.csv` with recall increasing in epsilon.
- [ ] `torch.cuda.is_available()` is `True`.
- [ ] `git -C vendor/BoT-SORT status` shows branch `prime-reid-poison-export`.
- [ ] `scripts/check_research_readiness.py` reports `Readiness check passed.`.
- [ ] At least one `runs/botsort/clean_c00X.csv` is non-empty after a real BoT-SORT run.
- [ ] At least one poisoned export CSV is non-empty.
- [ ] `scripts/analyze_embedding_export.py` writes `metrics.csv` for a poisoned run.

---

## 8. Work still outstanding (as of this commit)

Sourced from `docs/setup/REAL_DATA_IMPLEMENTATION_PLAN.md`, `docs/setup/IMPLEMENTATION.md`, and the repo `README.md`. Listed in roughly the order they unblock the paper.

### Data pipeline

- **CityFlowV2 ingestion automation.** No script downloads or verifies the dataset; it is a manual `unzip` step. A `scripts/fetch_cityflow.py` (or at least a checksum verifier) would close this.
- **Scenario window manifest.** Only `S01` is filled in `data/scenario_windows.csv`. S02–S18 still need start/duration/anchor notes if those scenarios will be used.

### BoT-SORT integration

- **Global-ID merge.** `tools/demo.py` exports detection-level rows; `scripts/analyze_embedding_export.py` requires a `track_id` column tied to global IDs (or controlled GT IDs). A merge step from `mc_demo.py` outputs (or from CityFlowV2 GT) is missing.
- **Run-log automation.** `docs/botsort-integration/BOTSORT_INTEGRATION.md` lists the required run-log fields, but there is no template-emitter; logs are still hand-written into `experiments/weekXX-*/`.

### Metrics and analysis

- **Real MTMC tracking metrics.** IDF1, HOTA, MOTA, IDS are not computed anywhere in `src/` or `scripts/`. Need to wire in something like `motmetrics` or `TrackEval` against the BoT-SORT MOT-format outputs.
- **Targeted-vs-random poisoning comparison.** `prime_mtmc.poison.PoisonConfig` supports a `target_direction`, but no experiment harness sweeps random vs targeted side by side.
- **Scalability sweep.** No driver script runs the detector across S01/S02/S03 with poisoned-camera count from 1 to N-1.
- **Publication-quality plots.** No plotting code exists; all current outputs are CSVs.

### Repo hygiene / tests

- **Real-export round-trip test.** `tests/test_poison_detector.py` only covers synthetic. A fixture-based test that feeds a tiny merged BoT-SORT CSV through `scripts/analyze_embedding_export.py` would catch schema drift.
- **GPU CI.** CI is CPU-only (`.github/workflows/ci.yml` runs `pytest`). The BoT-SORT path is never exercised in CI.

### Paper

- `paper-draft/` is a stub. Literature review, methods, results, and venue shortlist are all still TODO per `REAL_DATA_IMPLEMENTATION_PLAN.md` Gate 6.

---

## 9. Teardown

When you stop the GPU instance, push or copy out anything you want to keep:

```bash
# Results worth saving (small CSVs only — runs/ is .gitignore'd)
tar czf ~/blindspot_runs_$(date +%F).tgz \
  runs/synthetic runs/embedding_analysis runs/botsort/*.csv
```

Then snapshot or destroy the instance. Raw videos in `~/blindspot_data` and weights in `vendor/BoT-SORT/pretrained` are reproducible from section 5–6 and do not need to be backed up.
