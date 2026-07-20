Date:7/19/2026
Last name: Page

Scenario:S08
Clean or poisoned:Poisoned
Epsilon (write n/a if this is a clean run):0.1

python scripts/analyze_embedding_export.py --input data/S08_poison_c01-c02_eps0.1_seed7_all-cams_tracked.csv.gz --track-column track_id --scenario S08 --poisoned-cameras c01,c02 --out-dir results/week07/S08_poisoned_eps0.1”

camera  mean_distance  variance  pair_count       z_score  flagged
   c01       0.659689  0.008864        1295      1.303895     True
   c02       0.627310  0.008601        1606      0.000000    False
   c03       0.610561  0.009597         759      1.879612     True

Camera | clean mean | poisoned mean | drop
-------|------------|---------------|-----
  c01  |0.664085    |0.659689       |0.004396
  c02  |0.630314    |0.627310       |0.003004
  c03  |0.608180    |0.610561       |-0.002381

1. Which cameras were flagged?
   Camera 1 and camera 3 were flagged.

2. Were those the cameras that were actually poisoned (c01 and c02)?
   If not, which camera flagged instead, and why do you think that happened?
   Camera 1 was not poisoned but was most likely flagged because of its z-score.

3. Did the mean distance drop on c01 and c02 compared to the clean run?
   By how much?
   The mean distance dropped by 0.004396 and 0.003004 respectively.

4. If you have run more than one epsilon level for this scenario was the drop bigger at higher epsilon, smaller, or about the same?
   This is the first epsilon level I have ran for this scenario.

5. Did any camera get a z-score of exactly zero, and what does that mean?
   Yes, camera 2 got a z-score of exactly zero meaning it was the reference point for this run.

6. In one sentence, is the detector working correctly in this scenario?
   Why or why not?
   No, I do not think the detector is working correctly since it flagged a clean camera.

