# Run Log

Store completed logs in `results/week06/` with a filename that includes the scenario and date, for example `S03_clean_2026-06-23.md`. 

## Metadata

```text
Date:6/26/26
Student:Christine
```

## Scenario

```text
Scenario: S01 
File used (clean or poisoned):poisoned
Cameras targeted by poison (from filename, e.g. c01,c02):c01 c02
Epsilon (from filename, e.g. 0.5):0.5
```

## Command (Paste the exact command you ran, including all flags and the full input path)
python scripts/analyze_embedding_export.py \
  --input "data/S01_poison_c01-c02_eps0.5_seed7_all-cams_tracked.csv.gz" \
  --track-column track_id \
  --poisoned-cameras c01,c02 \
  --out-dir results/week06/S01_poisoned

```bash

```

## Settings (These two settings directly affect your results — if you change either one, start a new run log.)

```text
Track column used (track_id or detection_index):track_id
z-threshold: default
```

## Results 

```text
Camera | mean_distance | variance | pair_count | z_score | flagged
-------|---------------|----------|------------|---------|--------
  c01  |  0.565672     |0.035538  |    2504    |0.000000 | False
  c02  |  0.470289     |0.015035  |    2488    |10.023294| True
  c03  |  0.609014     |0.036918  |    1758    |0.674491 | False
```

## Interpretation 

```text
Which cameras were flagged?c02
Were those the cameras the poison was injected into?it was one of the two poisoned cameras
Did mean distance drop on the poisoned cameras compared to clean?yes it dropped for both poisoned cameras
What does that tell you about whether the detector is working? it tells me that it picked up on camera 2 and not camera 1, so it is kind of working
What would you try next (different threshold, different scenario)? I'm going to run at a different threshold.
```

## Issues

```text
Anything that looked wrong or surprising: no
Errors or warnings from the script: the z-score for camera 2 was kind of high
Questions for the team? none

```
