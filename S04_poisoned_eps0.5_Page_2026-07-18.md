Date:7/18/2026
Last name: Page

Scenario:S04
Clean or poisoned:Poisoned
Epsilon (write n/a if this is a clean run):0.5

python scripts/analyze_embedding_export.py --input data/S04_poison_c01-c02_eps0.5_seed7_all-cams_tracked.csv.gz --track-column track_id --scenario S04 --poisoned-cameras c01,c02 --out-dir results/week07/S04_poisoned_eps0.5”

camera  mean_distance  variance  pair_count       z_score  flagged
   c01       0.559235  0.029339        1669      0.674491    False
   c02       0.550698  0.016962        2443     -0.674491    False
   c03       0.638545  0.023540        1674      6.266436     True

Camera | clean mean | poisoned mean | drop
-------|------------|---------------|-----
  c01  |0.654492    |0.559235       |0.095257
  c02  |0.598198    |0.550698       |0.0475
  c03  |0.597606    |0.638545       |-0.040939

1. Which cameras were flagged?
   Camera 3 was the only camera that was flagged. 

2. Were those the cameras that were actually poisoned (c01 and c02)?
   If not, which camera flagged instead, and why do you think that happened?
   Camera 3 was the only camera that was poisoned and it was the only one to get flagged. 

3. Did the mean distance drop on c01 and c02 compared to the clean run?
   By how much?
   The distance dropped by 0.095257 and 0.0475 respectively.

4. If you have run more than one epsilon level for this scenario was the drop bigger at higher epsilon, smaller, or about the same?
   This epsilon level has a bigger drop than that of the 0.1 epsilon level.

5. Did any camera get a z-score of exactly zero, and what does that mean?
   No, none of the cameras produced a z-score of exactly zero.

6. In one sentence, is the detector working correctly in this scenario?
   Why or why not?
   Yes, I think the detector is working since the only camera that flagged was the only poisoned camera.

