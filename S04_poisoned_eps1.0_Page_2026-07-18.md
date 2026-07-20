Date:7/18/2026
Last name: Page

Scenario:S04
Clean or poisoned:Poisoned
Epsilon (write n/a if this is a clean run):1.0

python scripts/analyze_embedding_export.py --input data/S04_poison_c01-c02_eps1.0_seed7_all-cams_tracked.csv.gz --track-column track_id --scenario S04 --poisoned-cameras c01,c02 --out-dir results/week07/S04_poisoned_eps1.0”

camera  mean_distance  variance  pair_count       z_score  flagged
   c01       0.436199  0.053768        1669      0.674491    False
   c02       0.497361  0.043561        2443      0.000000    False
   c03       0.712045  0.015353        1674      2.367534     True

Camera | clean mean | poisoned mean | drop
-------|------------|---------------|-----
  c01  |0.654492    |0.436199       |0.218293
  c02  |0.598198    |0.497361       |0.100837
  c03  |0.597606    |0.712045       |-0.114439

1. Which cameras were flagged?
   Camera 3 was the only camera that was flagged.

2. Were those the cameras that were actually poisoned (c01 and c02)?
   If not, which camera flagged instead, and why do you think that happened?
   Camera 3 was the only poisoned canera, and it was also the only one to be flagged. 

3. Did the mean distance drop on c01 and c02 compared to the clean run?
   By how much?
   The mean distance dropped by 0.218293 and 0.100837 respectively.

4. If you have run more than one epsilon level for this scenario was the drop bigger at higher epsilon, smaller, or about the same?
   This epsilon level had the biggest drop out of all three epsilon levels. 

5. Did any camera get a z-score of exactly zero, and what does that mean?
   Yes, camera 2 produced a z-score of exactly zero meaning it is the reference point for this run.

6. In one sentence, is the detector working correctly in this scenario?
   Why or why not?
   Yes, I think the detector is working correctly since the only flagged camera was the poisoned camera.

