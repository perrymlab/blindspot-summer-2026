# Run Log

Store completed logs in `results/week06/` with a filename that includes the scenario and date, for example `S03_clean_2026-06-23.md`. 

## Metadata

```text
Date:6/26/26
Student:Christine
```

## Scenario

```text
Scenario:S04
File used (clean or poisoned):Clean
Cameras targeted by poison (from filename, e.g. c01,c02):n/a
Epsilon (from filename, e.g. 0.5):n/a
```

## Command (Paste the exact command you ran, including all flags and the full input path)
python scripts/analyze_embedding_export.py \
  --input "data/S04_clean_all-cams_tracked.csv.gz" \                     
  --track-column track_id \
  --out-dir results/week06/S04_clean
```bash

```

## Settings (These two settings directly affect your results — if you change either one, start a new run log.)

```text
Track column used (track_id or detection_index):track_id
z-threshold:default
```

## Results 

```text
Camera | mean_distance | variance | pair_count | z_score | flagged
-------|---------------|----------|------------|---------|--------
  c01  |  0.654492     |0.026936  |    1669    |64.187892|True 
  c02  |  0.598198     |0.019754  |    2443    |2.840194 |True
  c03  |  0.597606     |0.028641  |    1674    |0.674491 |False
```

## Interpretation 

```text
Which cameras were flagged?Camera 3
Were those the cameras the poison was injected into? No this was a clean run
Did mean distance drop on the poisoned cameras compared to clean?N/A
What does that tell you about whether the detector is working?N/A
What would you try next (different threshold, different scenario)?Next I will run the poisoned data
```

## Issues

```text
Anything that looked wrong or surprising:Camera 1 has a very high z-score
Errors or warnings from the script:No
Questions for the team?None
```
