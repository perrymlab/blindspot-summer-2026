Date:7/18/2026
Last name: Page

Scenario:S03
Clean or poisoned:Poisoned
Epsilon (write n/a if this is a clean run):0.5

python scripts/analyze_embedding_export.py --input data/S03_poison_c01-c02_eps0.5_seed7_all-cams_tracked.csv.gz --track-column track_id --scenario S03 --poisoned-cameras c01,c02 --out-dir results/week07/S03_poisoned_eps0.5”

camera  mean_distance  variance  pair_count       z_score  flagged
   c01       0.599554  0.023937         370      0.694475    False
   c02       0.577616  0.016684         431     -0.674491    False
   c03       0.693528  0.020258         291      2.889145     True

Camera | clean mean | poisoned mean | drop
-------|------------|---------------|-----
  c01  |0.686541    |0.599554       |0.086987
  c02  |0.645078    |0.577616       |0.067462
  c03  |0.665963    |0.693528       |-0.027565

1. Which cameras were flagged?
   Camera 3 was the only camera that was flagged.

2. Were those the cameras that were actually poisoned (c01 and c02)?
   If not, which camera flagged instead, and why do you think that happened?
   Yes this was the only camera that was poisoned and this is the only camera that was flagged. 

3. Did the mean distance drop on c01 and c02 compared to the clean run?
   By how much?
   The mean distance dropped by 0.086987 and 0.067462 respectively. 

4. If you have run more than one epsilon level for this scenario was the drop bigger at higher epsilon, smaller, or about the same?
   This epsilon level has the largest drop as compared to the 0.1 epsilon level.

5. Did any camera get a z-score of exactly zero, and what does that mean?
   No none of the cameras had a z-score of exactly zero.

6. In one sentence, is the detector working correctly in this scenario?
   Why or why not? Yes, I think the detector is working correctly since the only poisoned camera was the only flagged camera. 


