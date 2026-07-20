Date:7/18/2026
Last name:Page

Scenario:S03
Clean or poisoned:Poisoned
Epsilon (write n/a if this is a clean run):1.0

python scripts/analyze_embedding_export.py --input data/S03_poison_c01-c02_eps1.0_seed7_all-cams_tracked.csv.gz --track-column track_id --scenario S03 --poisoned-cameras c01,c02 --out-dir results/week07/S03_poisoned_eps1.0”

camera  mean_distance  variance  pair_count       z_score  flagged
   c01       0.476642  0.054537         370      0.674491    False
   c02       0.487437  0.043034         431      0.000000    False
   c03       0.751219  0.012817         291     16.480894     True

Camera | clean mean | poisoned mean | drop
-------|------------|---------------|-----
  c01  |0.686541    |0.476642       |0.209899
  c02  |0.645078    |0.487437       |0.157641
  c03  |0.665963    |0.751219       |-0.085256

1. Which cameras were flagged?
   Camera 3 was the only camera that was flagged.

2. Were those the cameras that were actually poisoned (c01 and c02)?
   If not, which camera flagged instead, and why do you think that happened?
   Yes, it was the only camera that was poisoned.

3. Did the mean distance drop on c01 and c02 compared to the clean run?
   By how much? The mean distance dropped by 0.209899 and 0.157641 respectively. 

4. If you have run more than one epsilon level for this scenario was the drop bigger at higher epsilon, smaller, or about the same?
   Out of all three epsilon levels this one has the biggest drops.

5. Did any camera get a z-score of exactly zero, and what does that mean?
   Yes, camera 2 has a z-score of exactly zero meaning it is the reference point for this scenario.

6. In one sentence, is the detector working correctly in this scenario?
   Why or why not?
   Yes, I think the detector is working because the only camera that was flagged was the only poisoned camera.


