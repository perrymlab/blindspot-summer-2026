Date:7/18/2026
Last name: Page

Scenario:S04
Clean or poisoned:Poisoned
Epsilon (write n/a if this is a clean run):0.1

python scripts/analyze_embedding_export.py --input data/S04_poison_c01-c02_eps0.1_seed7_all-cams_tracked.csv.gz --track-column track_id --scenario S04 --poisoned-cameras c01,c02 --out-dir results/week07/S04_poisoned_eps0.1”

camera  mean_distance  variance  pair_count       z_score  flagged
   c01       0.647018  0.026860        1669      5.973618     True
   c02       0.593968  0.019266        2443     -0.674491    False
   c03       0.599350  0.028474        1674      0.674491    False

Camera | clean mean | poisoned mean | drop
-------|------------|---------------|-----
  c01  |0.654492    |0.647018       |0.007474
  c02  |0.598198    |0.593968       |0.00423
  c03  |0.597606    |0.599350       |-0.001744

1. Which cameras were flagged?
   Camera 1 was the only camera that was flagged.

2. Were those the cameras that were actually poisoned (c01 and c02)?
   If not, which camera flagged instead, and why do you think that happened?
   Camera 1 was not poisoned but was flagged, I think that was due to the z-score.

3. Did the mean distance drop on c01 and c02 compared to the clean run?
   By how much?
   The distance dropped by 0.007474 and 0.00423 respectively. 

4. If you have run more than one epsilon level for this scenario was the drop bigger at higher epsilon, smaller, or about the same?
   This is the only epsilon level I have ran so far.

5. Did any camera get a z-score of exactly zero, and what does that mean?
   No, none of the cameras produced a z-score of exactly zero.

6. In one sentence, is the detector working correctly in this scenario?
   Why or why not?
   I don't think the detector is working correctly since the only camera that flagged was not the poisoned camera.

