Date:7/18/2026
Last name: Page

Scenario:S02
Clean or poisoned:Poisoned
Epsilon (write n/a if this is a clean run): 0.1

python scripts/analyze_embedding_export.py --input "data/S02_poison_c01-c02_eps0.1_seed7_all-cams_tracked.csv.gz" --track-column track_id --scenario S02 --poisoned-cameras c01,c02 --out-dir "results/week07/S02_poisoned_eps0.1”

camera  mean_distance  variance  pair_count       z_score  flagged
   c01       0.656226  0.031732        1759      3.338534     True
   c02       0.571810  0.032677        1850      0.000000    False
   c03       0.554756  0.044643        1201      8.541420     True

Camera | clean mean | poisoned mean | drop
-------|------------|---------------|-----
  c01  |0.662492    |0.656226       |0.006266
  c02  |0.577249    |0.571810       |0.005439
  c03  |0.553678    |0.554756       |-0.001078

1. Which cameras were flagged?
   Camera 1 and Camera 3 were flagged.
   
2. Were those the cameras that were actually poisoned (c01 and c02)?
   If not, which camera flagged instead, and why do you think that happened? Camera 1 was not poisoned but flagged and I think that is because the z-score was much higher than the reference point from camera 2. Camera 3 was poisoned, but flagged in the clean run as well.

3. Did the mean distance drop on c01 and c02 compared to the clean run?
   By how much? The mean distance dropped 0.006266 and 0.005439 respectively. 


4. If you have run more than one epsilon level for this scenario was the drop bigger at higher epsilon, smaller, or about the same?
   I have not ran the other epsilon levels for this scenario.

5. Did any camera get a z-score of exactly zero, and what does that mean?
   Yes, camera 2 got a z-score of exactly zero meaning it is the reference point for the detector for this run. 

6. In one sentence, is the detector working correctly in this scenario?
   Why or why not?
   No the detector is not working correctly as it is producing a flag for a camera that was not poisoned. 
