Date:7/18/2026
Last name: Page

Scenario:S02
Clean or poisoned: Poisoned
Epsilon (write n/a if this is a clean run):0.5

python scripts/analyze_embedding_export.py --input data/S02_poison_c01-c02_eps0.5_seed7_all-cams_tracked.csv.gz --track-column track_id --scenario S02 --poisoned-cameras c01,c02 --out-dir results/week07/S02_poisoned_eps0.5”

camera  mean_distance  variance  pair_count       z_score  flagged
   c01       0.575647  0.031002        1759      0.000000    False
   c02       0.505342  0.016037        1850     -2.063333    False
   c03       0.595183  0.035894        1201      0.674491    False

Camera | clean mean | poisoned mean | drop
-------|------------|---------------|-----
  c01  |0.662492    |0.575647       |0.086845
  c02  |0.577249    |0.505342       |0.071907
  c03  |0.553678    |0.595183       |-0.041505

1. Which cameras were flagged?
   None of the cameras were flagged in this run. 

2. Were those the cameras that were actually poisoned (c01 and c02)?
   If not, which camera flagged instead, and why do you think that happened?
   No, the camera that was poisoned did not get flagged.

3. Did the mean distance drop on c01 and c02 compared to the clean run?
   By how much? The mean distance dropped by 0.086845 and 0.071907 respectively.
 
4. If you have run more than one epsilon level for this scenario was the drop bigger at higher epsilon, smaller, or about the same?
   The drop for this epsilon level is the bigger as compared to the drop at 0.1 epsilon.
 
5. Did any camera get a z-score of exactly zero, and what does that mean?
   Yes, camera 1 got a z-score of exactly zero meaning it is the reference point for this run. 

6. In one sentence, is the detector working correctly in this scenario?
   Why or why not?  No, I do not think the detector is working since it did not flag the poisoned camera at all. 


