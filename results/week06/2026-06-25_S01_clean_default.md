# Run Log

Store completed logs in `results/week06/` with a filename that includes the scenario and date, for example `S03_clean_2026-06-23.md`. 

## Metadata

```text
Date:6/26/26
Student:Christine
```

## Scenario

```text
Scenario:S01
File used (clean or poisoned): Clean 
Cameras targeted by poison (from filename, e.g. c01,c02):
Epsilon (from filename, e.g. 0.5):
```

## Command (Paste the exact command you ran, including all flags and the full input path)
python scripts/analyze_embedding_export.py \
  --input "data/S01_clean_all-cams_tracked.csv.gz" \
  --track-column track_id \
  --out-dir results/week06/S01_clean 

## Settings (These two settings directly affect your results — if you change either one, start a new run log.)

```text
Track column used (track_id or detection_index): track_id
z-threshold: default
```

## Results 

```text
Camera | mean_distance | variance | pair_count | z_score | flagged
-------|---------------|----------|------------|---------|--------
  c01  |  0.638082     | 0.029832 |    2504    | 1.381494|  True
  c02  |  0.531347     | 0.030225 |    2488    | 0.674491|  False
  c03  |  0.566363     | 0.046934 |    1758    |28.712633|  True
```

## Interpretation 

```text
Which cameras were flagged? camera 1 and camera 3
Were those the cameras the poison was injected into? no
Did mean distance drop on the poisoned cameras compared to clean? this is the baseline to make comparisons to
What does that tell you about whether the detector is working? two cameras were flagged on a clean run suggesting false positives. 
What would you try next (different threshold, different scenario)? I will run the posioned data next to make comparisons
```

## Issues

```text
Anything that looked wrong or surprising: the z-score on camera 3 is really high
Errors or warnings from the script: none
Questions for the team? no
```
