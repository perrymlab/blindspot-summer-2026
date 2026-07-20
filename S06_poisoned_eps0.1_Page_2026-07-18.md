Date:7/18/2026
Last name: Page

Scenario:S06
Clean or poisoned:Poisoned
Epsilon (write n/a if this is a clean run):0.1

python scripts/analyze_embedding_export.py --input data/S06_poison_c01-c02_eps0.1_seed7_all-cams_tracked.csv.gz --track-column track_id --scenario S06 --poisoned-cameras c01,c02 --out-dir results/week07/S06_poisoned_eps0.1”

camera  mean_distance  variance  pair_count       z_score  flagged
   c01       0.717019  0.011713        1441      3.768240     True
   c02       0.680621  0.015259        1430      0.000000    False
   c03       0.674106  0.023052         585      1.482257     True

Camera | clean mean | poisoned mean | drop
-------|------------|---------------|-----
  c01  |0.723297    |0.717019       |0.006278
  c02  |0.686841    |0.680621       |0.00622
  c03  |0.673634    |0.674106       |-0.000472

1. Which cameras were flagged?
   Camera 1 and camera 3 both flagged in this run.

2. Were those the cameras that were actually poisoned (c01 and c02)?
   If not, which camera flagged instead, and why do you think that happened?
   Camera 3 was poisoned, but camera 1 was not and it most likely flagged because of its z-score.

3. Did the mean distance drop on c01 and c02 compared to the clean run?
   By how much?
   The mean distance dropped by 0.006278 and 0.00622 respectively.

4. If you have run more than one epsilon level for this scenario was the drop bigger at higher epsilon, smaller, or about the same?
   This is the first epsilon level I have ran so far.

5. Did any camera get a z-score of exactly zero, and what does that mean?
   Yes, camera 2 produced a z-score of exactly zero meaning it is the reference point for this run.

6. In one sentence, is the detector working correctly in this scenario?
   Why or why not?
   No I do not think the detector is working correctly since it flagged a camera that was not poisoned. 
