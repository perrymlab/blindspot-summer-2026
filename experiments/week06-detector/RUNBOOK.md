# Week 06 Detector Runbook

Source of truth: `docs/schedules/PRIME_Schedule_new_revised.pdf`.

Goal: run the cross-camera embedding consistency detector on merged embedding tables and report precision, recall, and F1.

## Required Input

`scripts/analyze_embedding_export.py` expects a CSV with:

- `camera`
- `frame`
- a global identity column, usually `track_id`
- `embedding`, as a space-separated vector string

For real detection, do not use detection index as `track_id` except for smoke checks. Merge exported embeddings with tracker/global IDs or ground-truth IDs first.

## Researcher Prerequisites

- Confirm the global ID source.
- Confirm poisoned camera labels for each condition.
- Confirm z-threshold or threshold sweep plan.
- Confirm plot requirements for cosine-distance distributions.

## Example Command

```bash
python scripts/analyze_embedding_export.py --input runs/botsort/merged_embeddings.csv --out-dir runs/embedding_analysis/s01_eps_0_5 --track-column track_id --poisoned-cameras c01,c02 --z-threshold 1.25
```

## Required Outputs

- `normalized_embeddings.csv`
- `camera_scores.csv`
- `metrics.csv`
- Distribution plots if generated separately.

## Required Summary

```text
Scenario,Condition,Epsilon,Poisoned cameras,Threshold,Precision,Recall,F1,Notes
S01,poisoned,0.1,c01;c02,,,,,
S01,poisoned,0.5,c01;c02,,,,,
S01,poisoned,1.0,c01;c02,,,,,
```
