Date:7/17/2026
Last name: Page

Scenario:S01
Clean or poisoned: Poisoned
Epsilon (write n/a if this is a clean run):1.0

python scripts/analyze_embedding_export.py --input "data/S01_poison_c01-c02_eps1.0_seed7_all-cams_tracked.csv.gz" --track-column track_id --scenario S01 --poisoned-cameras c01,c02 --out-dir "results/week07/S01_poisoned_eps1.0”

camera  mean_distance  variance  pair_count       z_score  flagged
   c01       0.468981  0.066472        2504      8.542237     True
   c02       0.393311  0.025912        2488      0.000000    False
   c03       0.687773  0.022710        1758      1.950223     True

Camera | clean mean | poisoned mean | drop
-------|------------|---------------|-----
  c01  |0.638082    |0.468981       |0.169101
  c02  |0.531347    |0.393311       |0.138036
  c03  |0.566363    |0.687773       |-0.12141

1. Which cameras were flagged? Camera 1 and Camera 3 were both flagged.

2. Were those the cameras that were actually poisoned (c01 and c02)?
   If not, which camera flagged instead, and why do you think that happened? Camera 1 was a poisoned camera, but camera 3 was not. I think it was flagged as a false positive since the reference camera (camera 2) had a z-score of 0 and camera 3's z-score was higher than that. 

3. Did the mean distance drop on c01 and c02 compared to the clean run?
   By how much? It dropped by 0.169101 and 0.138036 respectively. 

4. If you have run more than one epsilon level for this scenario was the drop bigger at higher epsilon, smaller, or about the same? The drop was the highest here which is the largest epsilon of the three poisoned runs.

5. Did any camera get a z-score of exactly zero, and what does that mean? Yes, camera 2 has a z-score of exactly zero meaning it was the reference point for this run. 

6. In one sentence, is the detector working correctly in this scenario?
   Why or why not? The detector is not working correctly in this scenario because it was unable to flag both of the poisoned cameras and falsely flagged a clean camera. 
