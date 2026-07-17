Date:7/17/2026
Last name: Page

Scenario: S01
Clean or poisoned: Poisoned
Epsilon (write n/a if this is a clean run): 0.1

python scripts/analyze_embedding_export.py --input "data/S01_poison_c01-c02_eps0.1_seed7_all-cams_tracked.csv.gz" --track-column track_id --scenario S01 --poisoned-cameras c01,c02 --out-dir "results/week07/S01_poisoned_eps0.1"

camera  mean_distance  variance  pair_count    z_score     flagged
   c01       0.633026  0.029821        2504    1.073036    False
   c02       0.526926  0.028817        2488   -0.674491    False
   c03       0.567878  0.046308        1758   11.080677    True



Camera | clean mean | poisoned mean | drop
-------|------------|---------------|-----
  c01  |0.638082    |0.633026       |0.005056
  c02  |0.531347    |0.526926       |0.004421
  c03  |0.566363    |0.567878       |-0.001515


1. Which cameras were flagged?
   Only camera 3 was flagged.

2. Were those the cameras that were actually poisoned (c01 and c02)?
   If not, which camera flagged instead, and why do you think that happened?
   No, this was the only camera that was not poisoned. I think that camera 3 was flagged because there was something in the embeddings that triggered the detector. Both the clean and the poisoned camera 3 had very high z-scores compared to the other two cameras. 

3. Did the mean distance drop on c01 and c02 compared to the clean run?
   By how much? Yes, by 0.005056 and 0.004421 respectively. 

4. If you have run more than one epsilon level for this scenario was the drop bigger at higher epsilon, smaller, or about the same?
    This is the first epsilon I have ran so I have nothing to compare it to yet. 

5. Did any camera get a z-score of exactly zero, and what does that mean?
   No none of them have a z-score of exactly zero for this run.

6. In one sentence, is the detector working correctly in this scenario?
   Why or why not?
   No since the detector failed to flag the two poisoned cameras. 
