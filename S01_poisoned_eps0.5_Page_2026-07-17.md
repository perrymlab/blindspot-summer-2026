Date: 7/17/2026
Last name:Page

Scenario:S01
Clean or poisoned:Poisoned
Epsilon (write n/a if this is a clean run):0.5

python scripts/analyze_embedding_export.py --input "data/S01_poison_c01-c02_eps0.5_seed7_all-cams_tracked.csv.gz" --track-column track_id --scenario S01 --poisoned-cameras c01,c02 --out-dir "results/week07/S01_poisoned_eps0.5”

camera  mean_distance  variance  pair_count       z_score  flagged
   c01       0.565672  0.035538        2504      0.000000    False
   c02       0.470289  0.015035        2488     -1.484333    False
   c03       0.609014  0.036918        1758      0.674491    False

Camera | clean mean | poisoned mean | drop
-------|------------|---------------|-----
  c01  |0.638082    |0.565672       |0.07241
  c02  |0.531347    |0.470289       |0.061058
  c03  |0.566363    |0.609014       |-0.042651

1. Which cameras were flagged? None of the cameras were flagged for this run. 

2. Were those the cameras that were actually poisoned (c01 and c02)?
   If not, which camera flagged instead, and why do you think that happened? None of the cameras were flagged. 
   
3. Did the mean distance drop on c01 and c02 compared to the clean run?
   By how much? Yes by 0.07241 and 0.061058 respectively.

4. If you have run more than one epsilon level for this scenario was the drop bigger at higher epsilon, smaller, or about the same?
   The drop at this epsilon was bigger than the drop at the 0.1 epsilon.

5. Did any camera get a z-score of exactly zero, and what does that mean?
   Yes camera 1 had a z-score of exactly zero meaning it was the reference point for this run.

6. In one sentence, is the detector working correctly in this scenario?
   Why or why not? I think the detector is not working correctly for this scenario because it is not able to flag the cameras that have been poisoned.
