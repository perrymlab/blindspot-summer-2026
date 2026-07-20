Date:7/18/2026
Last name: Page

Scenario:S07
Clean or poisoned:Poisoned
Epsilon (write n/a if this is a clean run):0.5

python scripts/analyze_embedding_export.py --input data/S07_poison_c01-c02_eps0.5_seed7_all-cams_tracked.csv.gz --track-column track_id --scenario S07 --poisoned-cameras c01,c02 --out-dir results/week07/S07_poisoned_eps0.5”

camera  mean_distance  variance  pair_count       z_score  flagged
   c01       0.547742  0.024757        2262     11.786232     True
   c02       0.498238  0.017520        2316     -0.674491    False
   c03       0.604254  0.017912        1940      0.769985    False

Camera | clean mean | poisoned mean | drop
-------|------------|---------------|-----
  c01  |0.603676    |0.547742       |0.055934
  c02  |0.546259    |0.498238       |0.048021
  c03  |0.563952    |0.604254       |-0.040302

1. Which cameras were flagged?
   Camera 1 was the only camera that was flagged.

2. Were those the cameras that were actually poisoned (c01 and c02)?
   If not, which camera flagged instead, and why do you think that happened?
   Camera 1 was not poisoned and most likely flagged because it has a high z-score.

3. Did the mean distance drop on c01 and c02 compared to the clean run?
   By how much?
   The distance dropped by 0.055934 and 0.048021 respectively.

4. If you have run more than one epsilon level for this scenario was the drop bigger at higher epsilon, smaller, or about the same?
   This epsilon level has a bigger drop than the 0.1 epsilon level.

5. Did any camera get a z-score of exactly zero, and what does that mean?
   No, none of the cameras produced a z-score of exactly zero.

6. In one sentence, is the detector working correctly in this scenario?
   Why or why not?
   No I do not think the detector is working correctly since it did not flag the poisoned camera and flagged a camera that was clean.


