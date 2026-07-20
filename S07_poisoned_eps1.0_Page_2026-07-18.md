Date:7/18/2026
Last name: Page

Scenario:S07
Clean or poisoned:Poisoned
Epsilon (write n/a if this is a clean run):1.0

python scripts/analyze_embedding_export.py --input data/S07_poison_c01-c02_eps1.0_seed7_all-cams_tracked.csv.gz --track-column track_id --scenario S07 --poisoned-cameras c01,c02 --out-dir results/week07/S07_poisoned_eps1.0”

camera  mean_distance  variance  pair_count       z_score  flagged
   c01       0.473190  0.054717        2262      0.674491    False
   c02       0.437783  0.037264        2316      0.000000    False
   c03       0.681828  0.011495        1940      3.974516     True

Camera | clean mean | poisoned mean | drop
-------|------------|---------------|-----
  c01  |0.603676    |0.473190       |0.130486
  c02  |0.546259    |0.437783       |0.108476
  c03  |0.563952    |0.681828       |-0.117876

1. Which cameras were flagged?
   Camera 3 was the only camera to flag in this run.

2. Were those the cameras that were actually poisoned (c01 and c02)?
   If not, which camera flagged instead, and why do you think that happened?
   Yes it was the camera that was actually poisoned. 

3. Did the mean distance drop on c01 and c02 compared to the clean run?
   By how much?
   It dropped by 0.130486 and 0.108476 respectively.

4. If you have run more than one epsilon level for this scenario was the drop bigger at higher epsilon, smaller, or about the same?
   This epsilon level has the biggest drop out of all three epsilon levels.

5. Did any camera get a z-score of exactly zero, and what does that mean?
   Yes, camera 2 got a z-score of exactly zero meaning it is the reference point for this run.

6. In one sentence, is the detector working correctly in this scenario?
   Why or why not?
   I think the detector is working correctly in this scenario since it only flagged the poisoned camera.

