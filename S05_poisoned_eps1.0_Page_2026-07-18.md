Date:7/18/2026
Last name: Page

Scenario:S05
Clean or poisoned:Poisoned
Epsilon (write n/a if this is a clean run):1.0

python scripts/analyze_embedding_export.py --input data/S05_poison_c01-c02_eps1.0_seed7_all-cams_tracked.csv.gz --track-column track_id --scenario S05 --poisoned-cameras c01,c02 --out-dir results/week07/S05_poisoned_eps1.0”

camera  mean_distance  variance  pair_count       z_score  flagged
   c01       0.573948  0.057832        1404      2.790982     True
   c02       0.504464  0.026675        1523      0.000000    False
   c03       0.713041  0.019145        1449      1.350185     True

Camera | clean mean | poisoned mean | drop
-------|------------|---------------|-----
  c01  |0.742828    |0.573948       |0.16888
  c02  |0.616522    |0.504464       |0.112058
  c03  |0.605681    |0.713041       |-0.10736


1. Which cameras were flagged?
   Camera 1 and camera 3 were both flagged.

2. Were those the cameras that were actually poisoned (c01 and c02)?
   If not, which camera flagged instead, and why do you think that happened?
   Camera 3 was poisoned, but camera 1 was not and it most likely flagged because it has the highest z-score for this run.

3. Did the mean distance drop on c01 and c02 compared to the clean run?
   By how much?
   The mean distance dropped by 0.16888 and 0.112058 respectively.

4. If you have run more than one epsilon level for this scenario was the drop bigger at higher epsilon, smaller, or about the same?
   This epsilon level had the biggest drop out of all three epsilon levels.

5. Did any camera get a z-score of exactly zero, and what does that mean?
   Yes, camera 2 produced a z-score of exactly zero meaning it is the reference point for this run.

6. In one sentence, is the detector working correctly in this scenario?
   Why or why not?
   No, I do not think the detector is working correctly in this scenario since it flagged a clean camera. 

