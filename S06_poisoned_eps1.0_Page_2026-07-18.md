Date:7/18/2026
Last name: Page


Scenario:S06
Clean or poisoned:Poisoned
Epsilon (write n/a if this is a clean run):1.0

python scripts/analyze_embedding_export.py --input data/S06_poison_c01-c02_eps1.0_seed7_all-cams_tracked.csv.gz --track-column track_id --scenario S06 --poisoned-cameras c01,c02 --out-dir results/week07/S06_poisoned_eps1.0”

camera  mean_distance  variance  pair_count       z_score  flagged
   c01       0.451228  0.039514        1441      1.061936    False
   c02       0.422272  0.022548        1430      0.000000    False
   c03       0.759276  0.011772         585      7.175646     True


Camera | clean mean | poisoned mean | drop
-------|------------|---------------|-----
  c01  |0.723297    |0.451228       |0.272069
  c02  |0.686841    |0.422272       |0.264569
  c03  |0.673634    |0.759276       |-0.085642

1. Which cameras were flagged?
   Camera 3 was the only camera that flagged on this run.

2. Were those the cameras that were actually poisoned (c01 and c02)?
   If not, which camera flagged instead, and why do you think that happened?
   This camera was poisoned and it was the only camera that flagged.

3. Did the mean distance drop on c01 and c02 compared to the clean run?
   By how much?
   The mean distance dropped by 0.272069 and 0.264569 respectively.

4. If you have run more than one epsilon level for this scenario was the drop bigger at higher epsilon, smaller, or about the same?
   This epsilon level has the biggest drop than either 0.1 or 0.5.

5. Did any camera get a z-score of exactly zero, and what does that mean?
   Yes camera 2 got a z-score of exactly zero meaning it was the reference point for this run.

6. In one sentence, is the detector working correctly in this scenario?
   Why or why not? 
   Yes, I think the detector is working for this scenario since the only camera that flagged was the poisoned camera.




