Date:7/19/2026
Last name: Page

Scenario:S08
Clean or poisoned:Poisoned
Epsilon (write n/a if this is a clean run):0.5

python scripts/analyze_embedding_export.py --input data/S08_poison_c01-c02_eps0.5_seed7_all-cams_tracked.csv.gz --track-column track_id --scenario S08 --poisoned-cameras c01,c02 --out-dir results/week07/S08_poisoned_eps0.5”

camera  mean_distance  variance  pair_count       z_score  flagged
   c01       0.563413  0.011453        1295      2.422905     True
   c02       0.559958  0.006897        1606     -0.674491    False
   c03       0.652068  0.007889         759     17.309832     True

Camera | clean mean | poisoned mean | drop
-------|------------|---------------|-----
  c01  |0.664085    |0.563413       |0.100672
  c02  |0.630314    |0.559958       |0.070356
  c03  |0.608180    |0.652068       |-0.043888

1. Which cameras were flagged?
   Camera 1 and camera 3 were flagged in this run.

2. Were those the cameras that were actually poisoned (c01 and c02)?
   If not, which camera flagged instead, and why do you think that happened?
   Camera 1 was not poisoned but was flagged most likely because of its z-score.

3. Did the mean distance drop on c01 and c02 compared to the clean run?
   By how much?
   The mean distance dropped by 0.100672 and 0.070356 respectively.

4. If you have run more than one epsilon level for this scenario was the drop bigger at higher epsilon, smaller, or about the same?
   This epsilon level has a bigger drop than the 0.1 epsilon level.

5. Did any camera get a z-score of exactly zero, and what does that mean?
   No, none of the cameras produced a z-score of exactly zero.

6. In one sentence, is the detector working correctly in this scenario?
   Why or why not?
   No, I do not think the detector is working correctly since it flagged a clean camera.
