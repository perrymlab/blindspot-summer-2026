Date:7/18/2026
Last name: Page

Scenario:S05
Clean or poisoned:Poisoned
Epsilon (write n/a if this is a clean run):0.1

python scripts/analyze_embedding_export.py --input data/S05_poison_c01-c02_eps0.1_seed7_all-cams_tracked.csv.gz --track-column track_id --scenario S05 --poisoned-cameras c01,c02 --out-dir results/week07/S05_poisoned_eps0.1”

camera  mean_distance  variance  pair_count       z_score  flagged
   c01       0.737441  0.026023        1404     14.927104     True
   c02       0.612388  0.037399        1523      0.674491    False
   c03       0.606737  0.037176        1449      0.000000    False

Camera | clean mean | poisoned mean | drop
-------|------------|---------------|-----
  c01  |0.742828    |0.737441       |0.005387
  c02  |0.616522    |0.612388       |0.004134
  c03  |0.605681    |0.606737       |-0.001056


1. Which cameras were flagged?
   Camera 1 was the only camera to be flagged.

2. Were those the cameras that were actually poisoned (c01 and c02)?
   If not, which camera flagged instead, and why do you think that happened?
   No, camera 1 was not poisoned but most likely flagged because of the high z-score.

3. Did the mean distance drop on c01 and c02 compared to the clean run?
   By how much?
   It dropped by 0.005387 and 0.004134 respectively.

4. If you have run more than one epsilon level for this scenario was the drop bigger at higher epsilon, smaller, or about the same?
   So far this is the only run I have done so I have nothing to compare it to.

5. Did any camera get a z-score of exactly zero, and what does that mean?
   Yes, camera 3 got a z-score of exactly zero meaning it is the reference point for this run.

6. In one sentence, is the detector working correctly in this scenario?
   Why or why not?
   No, I do not think the detector is working correctly in this scenario because it inappropriately flagged a clean camera.

