Date:7/18/2026
Last name: Page

Scenario:S07
Clean or poisoned:Poisoned
Epsilon (write n/a if this is a clean run):0.1

python scripts/analyze_embedding_export.py --input data/S07_poison_c01-c02_eps0.1_seed7_all-cams_tracked.csv.gz --track-column track_id --scenario S07 --poisoned-cameras c01,c02 --out-dir results/week07/S07_poisoned_eps0.1”

camera  mean_distance  variance  pair_count      z_score  flagged
   c01       0.600019  0.021779        2262      1.07633    False
   c02       0.542911  0.023852        2316     29.36170     True
   c03       0.564912  0.021826        1940      0.00000    False

Camera | clean mean | poisoned mean | drop
-------|------------|---------------|-----
  c01  |0.603676    |0.600019       |0.003657
  c02  |0.546259    |0.542911       |0.003348
  c03  |0.563952    |0.564912       |-0.00096


1. Which cameras were flagged?
   Camera 2 was the only camera to flag for this run.

2. Were those the cameras that were actually poisoned (c01 and c02)?
   If not, which camera flagged instead, and why do you think that happened?
   Camera 2 was not poisoned but most likely flagged because of its high z-score.

3. Did the mean distance drop on c01 and c02 compared to the clean run?
   By how much?
   The mean distance dropped by 0.003657 and 0.003348 respectively.

4. If you have run more than one epsilon level for this scenario was the drop bigger at higher epsilon, smaller, or about the same?
   This is the first epsilon level run so there is nothing to compare it to.

5. Did any camera get a z-score of exactly zero, and what does that mean?
   Yes camera 3 got a z-score of exactly zero meaning it was the reference point for this scenario.

6. In one sentence, is the detector working correctly in this scenario?
   Why or why not?
  No I do not think the detector is working since it incorrectly flagged a clean camera and did not flag the poisoned camera. 


