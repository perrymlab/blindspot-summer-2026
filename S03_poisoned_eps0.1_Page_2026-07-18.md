Date:7/18/2026
Last name: Page

Scenario:S03
Clean or poisoned:Poisoned
Epsilon (write n/a if this is a clean run):0.1

python scripts/analyze_embedding_export.py --input "data/S03_poison_c01-c02_eps0.1_seed7_all-cams_tracked.csv.gz" --track-column track_id --scenario S03 --poisoned-cameras c01,c02 --out-dir "results/week07/S03_poisoned_eps0.1”

camera  mean_distance  variance  pair_count       z_score  flagged
   c01       0.681332  0.018714         370      0.674491    False
   c02       0.640594  0.018375         431     -0.674491    False
   c03       0.665945  0.024962         291     12.431916     True

Camera | clean mean | poisoned mean | drop
-------|------------|---------------|-----
  c01  |0.686541    |0.681332       |0.005209
  c02  |0.645078    |0.640594       |0.004484
  c03  |0.665963    |0.665945       |0.000018

1. Which cameras were flagged?
   Camera 3 was the only camera that flagged. 

2. Were those the cameras that were actually poisoned (c01 and c02)?
   If not, which camera flagged instead, and why do you think that happened?
   Yes, that was the only poisoned camera and it was the only camera flagged. 

3. Did the mean distance drop on c01 and c02 compared to the clean run?
   By how much? The mean distance dropped by 0.005209 and 0.004484 respectively. 

4. If you have run more than one epsilon level for this scenario was the drop bigger at higher epsilon, smaller, or about the same?
   This is the first epsilon level for this scenario.

5. Did any camera get a z-score of exactly zero, and what does that mean?
  No, none of the cameras produced a z-score of exactly zero. 

6. In one sentence, is the detector working correctly in this scenario?
   Why or why not?
Yes, I think the detector is working correctly since the only camera that was flagged was the poisoned camera.
