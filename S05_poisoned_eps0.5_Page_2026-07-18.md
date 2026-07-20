Date:7/18/2026
Last name: Page 

Scenario:S05
Clean or poisoned:Poisoned
Epsilon (write n/a if this is a clean run):0.5

python scripts/analyze_embedding_export.py --input data/S05_poison_c01-c02_eps0.5_seed7_all-cams_tracked.csv.gz --track-column track_id --scenario S05 --poisoned-cameras c01,c02 --out-dir results/week07/S05_poisoned_eps0.5”

camera  mean_distance  variance  pair_count       z_score  flagged
   c01       0.669609  0.026105        1404      0.674491    False
   c02       0.564944  0.016922        1523     -1.520911    False
   c03       0.642834  0.030177        1449      0.674491    False

Camera | clean mean | poisoned mean | drop
-------|------------|---------------|-----
  c01  |0.742828    |0.669609       |0.073219
  c02  |0.616522    |0.564944       |0.051578
  c03  |0.605681    |0.642834       |-0.037153

1. Which cameras were flagged?
   None of the cameras flagged on this run.

2. Were those the cameras that were actually poisoned (c01 and c02)?
   If not, which camera flagged instead, and why do you think that happened?
   No, none of the cameras were flagged. 

3. Did the mean distance drop on c01 and c02 compared to the clean run?
   By how much?
   The mean distance dropped by 0.073219 and 0.051578 respectively. 

4. If you have run more than one epsilon level for this scenario was the drop bigger at higher epsilon, smaller, or about the same?
   This epsilon level had a bigger drop than the 0.1 epsilon level.

5. Did any camera get a z-score of exactly zero, and what does that mean?
   No, none of the cameras got a z-score of exactly zero.

6. In one sentence, is the detector working correctly in this scenario?
   Why or why not?
   No, I do not think the detector is working correctly since it was unable to accurately flag the poisoned camera.


