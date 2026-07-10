# PHANTOM: Run Log Template Part Two

**What this is:** Every time you run the analysis script, fill out one of these logs and save it as a `.md` file in `results/week07/`. This is how we track what everyone ran, what the numbers showed, and what we think it means.

---

## Naming your file(s)

Use this format and save it as a `.md` file:

```
S01_clean_Perry_2026-07-14.md
S01_poisoned_eps0.5_Perry_2026-07-14.md
```

Your filename needs five things in this order:
1. Scenario: `S01`, `S02`, etc.
2. Clean or poisoned: `clean` or `poisoned`
3. Epsilon if poisoned: `eps0.1`, `eps0.5`, or `eps1.0`
4. Your last name: `Perry`
5. Date: `2026-07-14`

---

## What to run for each scenario

Run these four in order. Do not skip any. Save all four as `.md` files, then commit them before moving on to the next scenario.

```
1. Clean run          S01_clean_Lastname_date.md
2. Poisoned eps 0.1   S01_poisoned_eps0.1_Lastname_date.md
3. Poisoned eps 0.5   S01_poisoned_eps0.5_Lastname_date.md
4. Poisoned eps 1.0   S01_poisoned_eps1.0_Lastname_date.md
```

---

## Standard settings — everyone uses these

```
Track column:   track_id
z-threshold:    1.25
```

Do not change these. If you need to try something different, start a new log file and note in the filename that it is a test run.

---

## Step 1: Metadata

```
Date:
Last name:
```

---

## Step 2: Scenario details

```
Scenario:
Clean or poisoned:
Epsilon (write n/a if this is a clean run):
```

---

## Step 3: Command

Copy and paste the exact command you ran from your terminal. Do not retype it.

```bash

```

---

## Step 4: Results

Copy the numbers from your terminal output into this table.

```
Camera | mean_distance | variance | pair_count | z_score | flagged
-------|---------------|----------|------------|---------|--------
  c01  |               |          |            |         |
  c02  |               |          |            |         |
  c03  |               |          |            |         |
```

**For poisoned runs only** fill in how much the mean distance dropped compared to your clean run for the same scenario. Run the clean version first if you have not already.

```
Camera | clean mean | poisoned mean | drop
-------|------------|---------------|-----
  c01  |            |               |
  c02  |            |               |
  c03  |            |               |
```

---

## Step 5: Only if something looks suspicious, visualize the bounding boxes

**Only do this step if a result looks unexpected**, for example, a very high z-score on a clean run, a camera flagging when it should not, or a drop that seems too large or too small. Skip this step if everything looks normal.

Run this command, replacing the scenario, camera, and paths with your actual values:

```bash
python scripts/visualize_boxes.py \
  --csv "data/S01_clean_all-cams_tracked.csv.gz" \
  --video /path/to/S01/c01/vdo.mp4 \
  --camera c01 \
  --out results/week07/S01_clean_c01_boxes.mp4
```

Open the output video in VLC or QuickTime. You are looking for whether the tracker is correctly following vehicles across cameras, or whether it is dropping and reassigning IDs unexpectedly.

If you ran this step, write one sentence about what you saw:

```
Bounding box observation:
```

If you did not run this step, write: `Not needed if results looked normal.`

---

## Step 6: Interpretation

Answer every question. Write at least one full sentence for each. Do not leave any blank.

```
1. Which cameras were flagged?

2. Were those the cameras that were actually poisoned (c01 and c02)?
   If not, which camera flagged instead, and why do you think that happened?

3. Did the mean distance drop on c01 and c02 compared to the clean run?
   By how much?

4. If you have run more than one epsilon level for this scenario was the drop bigger at higher epsilon, smaller, or about the same?

5. Did any camera get a z-score of exactly zero, and what does that mean?

6. In one sentence, is the detector working correctly in this scenario?
   Why or why not?

```

---
