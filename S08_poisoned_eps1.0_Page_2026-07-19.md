Date:7/19/2026
Last name: Page

Scenario:S08
Clean or poisoned:Poisoned
Epsilon (write n/a if this is a clean run):1.0

python scripts/analyze_embedding_export.py --input data/S08_poison_c01-c02_eps1.0_seed7_all-cams_tracked.csv.gz --track-column track_id --scenario S08 --poisoned-cameras c01,c02 --out-dir results/week07/S08_poisoned_eps1.0”

camera  mean_distance  variance  pair_count       z_score  flagged
   c01       0.410033  0.032359        1295      0.000000    False
   c02       0.455418  0.033172        1606      0.674491    False
   c03       0.728386  0.004990         759      4.056692     True

Camera | clean mean | poisoned mean | drop
-------|------------|---------------|-----
  c01  |0.664085    |0.410033       |0.254052
  c02  |0.630314    |0.455418       |0.174896
  c03  |0.608180    |0.728386       |-0.120206

1. Which cameras were flagged?
   Only camera 3 was flagged on this run.

2. Were those the cameras that were actually poisoned (c01 and c02)?
   If not, which camera flagged instead, and why do you think that happened?
   This was the only poisoned camera. 

3. Did the mean distance drop on c01 and c02 compared to the clean run?
   By how much?
   The mean distance dropped by 0.254052 and 0.174896 respectively.

4. If you have run more than one epsilon level for this scenario was the drop bigger at higher epsilon, smaller, or about the same?
   Of all three epsilon levels this one has the biggest drop.

5. Did any camera get a z-score of exactly zero, and what does that mean?
   Yes camera 1 got a z-score of exactly zero meaning it is the reference point for this run.

6. In one sentence, is the detector working correctly in this scenario?
   Why or why not?
   Yes, I think the detector is working correctly since the only camera that was flagged was the poisoned one.

