Date:7/18/2026
Last name: Page

Scenario:S06
Clean or poisoned:Poisoned
Epsilon (write n/a if this is a clean run):0.5

python scripts/analyze_embedding_export.py --input data/S06_poison_c01-c02_eps0.5_seed7_all-cams_tracked.csv.gz --track-column track_id --scenario S06 --poisoned-cameras c01,c02 --out-dir results/week07/S06_poisoned_eps0.5”

camera  mean_distance  variance  pair_count       z_score  flagged
   c01       0.612031  0.015199        1441      0.000000    False
   c02       0.578053  0.009282        1430     -0.674491    False
   c03       0.702490  0.018574         585      1.795673     True

Camera | clean mean | poisoned mean | drop
-------|------------|---------------|-----
  c01  |0.723297    |0.612031       |0.111266
  c02  |0.686841    |0.578053       |0.108788
  c03  |0.673634    |0.702490       |-0.028856

1. Which cameras were flagged?
   Camera 3 was the only camera to flag on this run.

2. Were those the cameras that were actually poisoned (c01 and c02)?
   If not, which camera flagged instead, and why do you think that happened?
   This was the only camera that was poisoned. 

3. Did the mean distance drop on c01 and c02 compared to the clean run?
   By how much?
   The mean distance dropped by 0.111266 and 0.108788 respectively.

4. If you have run more than one epsilon level for this scenario was the drop bigger at higher epsilon, smaller, or about the same?
   This epsilon level has bigger drops than the 0.1 epsilon level.

5. Did any camera get a z-score of exactly zero, and what does that mean?
   Yes, camera 1 produced a z-score of exactly zero meaning it was the reference point for this run.

6. In one sentence, is the detector working correctly in this scenario?
   Why or why not?
   Yes, I think the detector is working correctly since it only flagged the camera that was poisoned. 

