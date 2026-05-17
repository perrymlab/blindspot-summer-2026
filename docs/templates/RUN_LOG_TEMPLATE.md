# Run Log Template

Use this for every real-data or synthetic experiment. Store completed logs in the relevant `experiments/weekXX-topic/` folder. Store only small summaries in `results/weekXX/`.

## Metadata

```text
Date:
Student/researcher:
Branch:
Commit:
Machine:
Python executable:
PyTorch version:
CUDA/CPU:
GPU:
```

## Dataset

```text
Dataset:
Scenario:
Camera IDs:
Dataset path:
Ground truth path:
```

## Weights

```text
Detector weights:
FastReID/OSNet weights:
Other weights:
```

## Command

```bash

```

## Poisoning Settings

```text
Clean or poisoned:
Poisoned cameras:
Perturbation mode: none | random | targeted
Epsilon:
Seed:
Target identity or cluster:
Perturbation before or after feature normalization:
```

## Outputs

```text
Raw output path:
Embedding export path:
Merged embedding table path:
Metrics output path:
Summary output path:
```

## Metrics

```text
IDF1:
HOTA:
MOTA:
IDS:
Detector precision:
Detector recall:
Detector F1:
```

## Notes

```text
What worked:
What failed:
Warnings/errors:
Follow-up needed:
```
