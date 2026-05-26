# Scenario Trimming Guide

**Who this is for:** Dr. Perry, Christine, and Floyd  
**When to do this:** Week 3 - after Dr. Perry shares the intersection videos with you  
**What you are doing:** Creating a data folder on your laptop, copying the videos into it, watching through the footage, picking the best 2–5 minute window for each scenario, and filling in a shared spreadsheet so the trimming tool knows what to cut

---

## Background — why we trim
Each scenario contains three synchronized camera videos of the same intersection — `c001/vdo.mp4`, `c002/vdo.mp4`, and `c003/vdo.mp4`. The full videos are about 15 minutes long. For our experiments we only need a 2–5 minute window where the same vehicles are clearly visible across all three cameras at the same time.

The reason this matters: our detector works by comparing the appearance embeddings of the same vehicle as seen from different cameras. If a vehicle only appears in one camera during the experiment window it contributes no data to the comparison. A good trim window is one where multiple vehicles pass through all three camera views during the same period.

**Christine - scenarios S01 through S09**  
**Floyd - scenarios S10 through S18**

---

## Step 0 — Create your data folder and copy the videos

This is a one-time setup step. You only need to do this once.

**Create the data folder on your laptop:**

Open your terminal and run:

```bash
mkdir ~/blindspot_data
```

This creates a folder called `blindspot_data` in your home directory. You can also find it in Finder at the top level of your home folder.

**Copy the videos into that folder:**
Dr. Perry will share the intersection video folders with you. Once you have them on your machine, open Finder and drag all the video folders into `~/blindspot_data`. When you are done the folder should look like this:

```
blindspot_data/
  video 1/
  video 2/
  video 3/
  ...
  video 18/
```

Do not rename any of the video folders. The organize script expects the original folder names.

---

## Step 1 — Set up your environment

Open your terminal, navigate to the repo, and activate the virtual environment:

```bash
cd ~/blindspot-summer-2026
source .venv/bin/activate
```

Also install ffmpeg. This is the tool that does the actual video cutting:

```bash
brew install ffmpeg
```
---

## Step 2 — Organize the videos into scenario folders

The organize script moves your videos from the raw folder structure into the structure the trimming tool expects.

First do a dry run to confirm everything looks right:

```bash
python scripts/organize_blindspot_data.py
```

You should see output showing planned moves like this:

```
[dry run] MOVE ~/blindspot_data/video 1/Intersection-Camera-1_...mp4
     -> ~/blindspot_data/S01/c001/vdo.mp4
```

If that looks correct, apply it:

```bash
python scripts/organize_blindspot_data.py --apply
```

After this runs your `blindspot_data` folder will be reorganized into:

```
blindspot_data/
  S01/
    c001/vdo.mp4
    c002/vdo.mp4
    c003/vdo.mp4
  S02/
    c001/vdo.mp4
    ...
```

---

## Step 3 — Watch through your assigned scenarios
For each of your assigned scenarios, open all three camera videos side by side in QuickTime:

```
~/blindspot_data/S01/c001/vdo.mp4
~/blindspot_data/S01/c002/vdo.mp4
~/blindspot_data/S01/c003/vdo.mp4
```

You are looking for a moment where **the same vehicle is visible in all three camera feeds at the same time**. This is your anchor moment. Note the timestamp when you find it.

**What makes a good window:**

- At least one vehicle clearly visible across all three cameras at the same time
- Daytime footage with good visibility
- Busy enough that roughly 5 or more vehicles pass through all three cameras during the window
- 2 minutes is fine for a busy intersection — use 5 minutes for quieter or low-light footage

**What to avoid:**
- Windows where most vehicles only appear in one or two cameras
- Very dark or foggy footage
- Periods with very little traffic
---

## Step 4 — Fill in the manifest
Once you have chosen a window for a scenario, open this file in VS Code:

```
data/scenario_windows.csv
```

Add one row for your scenario using this format:

```
scenario,start,duration_s,anchor_notes
S01,00:01:30,180,"red pickup co-visible across all cams ~01:35; ~15 vehicles co-visible during window"
```

**Column guide:**
| Column | What to put |
|---|---|
| `scenario` | The scenario folder name — S01, S02, etc. |
| `start` | When your window starts from the beginning of the video. Use seconds (45) or time format (1:30) |
| `duration_s` | How long the window is in seconds. Between 120 and 300. |
| `anchor_notes` | Describe at least one vehicle visible in all three cameras and give a rough count of total co-visible vehicles |

**Example rows:**

```
S01,00:01:30,180,"white SUV co-visible across all cams ~01:35; ~15 vehicles co-visible"
S02,45,300,"low traffic; chose 5 min for sample size; blue sedan co-visible ~01:00"
S03,00:03:00,120,"busy midday; red truck co-visible ~03:10; ~20 vehicles co-visible"
```

Leave rows blank if you have not reviewed that scenario yet. The trimming tool will skip blank rows automatically.

---

## Step 5 — Run the trimming tool
After filling in one or more manifest rows, do a dry run first:

```bash
python scripts/trim_scenarios.py
```

If the output looks correct, apply the trim:

```bash
python scripts/trim_scenarios.py --apply
```

To trim just one scenario while you are working through them one at a time:

```bash
python scripts/trim_scenarios.py --scenario S01 --apply
```

---

## Step 6 — Generate preview images
After trimming, run the quicklook script to generate a side-by-side preview image for each scenario:

```bash
python scripts/scenario_quicklook.py
```

Preview images are saved to `runs/quicklook/S01.png` and so on. Open them in Finder to confirm that all three cameras show the intersection clearly at the midpoint of your chosen window.

---

## Step 7 — Commit your work
The trimmed video files are large and should not be committed to GitHub. What you commit is just the manifest and the preview images.

**Christine:**
```bash
git checkout main
git pull
git checkout -b trim-scenarios-christine
git add data/scenario_windows.csv
git add runs/quicklook/
git commit -m "add trim windows for S01 through S09"
git push -u origin trim-scenarios-christine
```

**Floyd:**
```bash
git checkout main
git pull
git checkout -b trim-scenarios-floyd
git add data/scenario_windows.csv
git add runs/quicklook/
git commit -m "add trim windows for S10 through S18"
git push -u origin trim-scenarios-floyd
```

Then open a pull request on GitHub. In the pull request description include one or two of the quicklook images so Dr. Perry can confirm the window choices look right without needing to download the videos.

---

