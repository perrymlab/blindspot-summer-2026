# Local Paths Template

Copy this file to `docs/setup/LOCAL_PATHS.md` on each machine and fill in local paths. Do not commit machine-specific paths.

## Environment

```text
Machine owner:
Operating system:
Python environment method: conda | venv
Python executable:
PyTorch version:
CUDA available: yes | no
GPU model:
```

## Repository

```text
Project repository path:
BoT-SORT path:
BoT-SORT branch:
BoT-SORT commit:
```

## Dataset

```text
CityFlowV2 root:
Scenario S01 path:
Scenario S02 path:
Scenario S03 path:
```

Expected CityFlowV2 layout for this project:

```text
<CityFlowV2 root>/
  S01/
    c001/
    c002/
    c003/
    c004/
    c005/
  S02/
  S03/
```

If the downloaded dataset uses a different layout, document the real layout here and update experiment commands accordingly.

## Model Weights

```text
Object detector weights: vendor/BoT-SORT/pretrained/bytetrack_x_mot17.pth.tar
FastReID/OSNet weights: vendor/BoT-SORT/pretrained/veri_sbs_R50-ibn.pth
Other tracker weights:
```

## Output Locations

Large generated outputs should stay outside git unless Sabrina explicitly approves a small summary file.

```text
Local raw run output root:
Clean baseline output path:
Poisoned run output path:
Merged embedding table path:
```
