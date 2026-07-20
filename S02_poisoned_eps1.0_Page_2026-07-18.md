Date:7/18/2026
Last name: Page

Scenario:S02
Clean or poisoned:Poisoned
Epsilon (write n/a if this is a clean run):1.0

python scripts/analyze_embedding_export.py --input data/S02_poison_c01-c02_eps1.0_seed7_all-cams_tracked.csv.gz --track-column track_id --scenario S02 --poisoned-cameras c01,c02 --out-dir results/week07/S02_poisoned_eps1.0”

camera  mean_distance  variance  pair_count       z_score  flagged
   c01       0.460469  0.054910        1759      9.911960     True
   c02       0.414502  0.024542        1850      0.000000    False
   c03       0.674278  0.022475        1201      3.137345     True


Camera | clean mean | poisoned mean | drop
-------|------------|---------------|-----
  c01  |0.662492    |0.460469       |0.202023
  c02  |0.577249    |0.414502       |0.162747
  c03  |0.553678    |0.674278       |-0.1206

1. Which cameras were flagged?
   Camera 1 and Camera 3 were flagged.

2. Were those the cameras that were actually poisoned (c01 and c02)?
   If not, which camera flagged instead, and why do you think that happened?
   Camera 3 was poisoned and it was flagged. Camera 1 was not poisoned, but was flagged most likely because of the z-score being so high.

3. Did the mean distance drop on c01 and c02 compared to the clean run?
   By how much?
   The distance dropped by 0.202023 and 0.162747 respectively. 

4. If you have run more than one epsilon level for this scenario was the drop bigger at higher epsilon, smaller, or about the same?
   This epsilon level has the largest drop of all three levels.

5. Did any camera get a z-score of exactly zero, and what does that mean?
   Camera 2 had a z-score of exactly zero, meaning it was the reference point for this scenario.

6. In one sentence, is the detector working correctly in this scenario?
   Why or why not? No, the detector is not working correctly since it incorrectly flagged camera 1 when it had not been poisoned. 
