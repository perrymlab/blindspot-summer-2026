# Blindspot progress report — 2026-06-12

Repo commit: `e2229c0`. Produced by `scripts/make_progress_report.py` from `runs/botsort/` (see `run_manifest.csv` for full provenance).

## S01

### Clean run — camera consistency scores

| camera | mean_distance | pair_count | z_score | flagged |
| --- | --- | --- | --- | --- |
| c01 | 0.827 | 797.0 | 3.279 | True |
| c02 | 0.762 | 662.0 | 0.674 | False |
| c03 | 0.773 | 791.0 | 0.0 | False |


### Poisoned run (`poison_c01-c02_eps0.5_seed7`) — scores and detection

| camera | mean_distance | pair_count | z_score | flagged |
| --- | --- | --- | --- | --- |
| c01 | 0.758 | 797.0 | 0.674 | False |
| c02 | 0.685 | 662.0 | 1.863 | True |
| c03 | 0.785 | 791.0 | 1.053 | False |


| tp | fp | fn | precision | recall | f1 |
| --- | --- | --- | --- | --- | --- |
| 1.0 | 0.0 | 1.0 | 1.0 | 0.5 | 0.667 |


![S01_c01_t003s](stills/S01_c01_t003s.jpg)
![S01_c01_t010s](stills/S01_c01_t010s.jpg)
![S01_c01_t016s](stills/S01_c01_t016s.jpg)

Full clip: `videos/S01_c01_clean_boxes.mp4` (attached to the GitHub Release for this report)

![S01_c02_t003s](stills/S01_c02_t003s.jpg)
![S01_c02_t009s](stills/S01_c02_t009s.jpg)
![S01_c02_t016s](stills/S01_c02_t016s.jpg)

Full clip: `videos/S01_c02_clean_boxes.mp4` (attached to the GitHub Release for this report)

![S01_c03_t003s](stills/S01_c03_t003s.jpg)
![S01_c03_t009s](stills/S01_c03_t009s.jpg)
![S01_c03_t016s](stills/S01_c03_t016s.jpg)

Full clip: `videos/S01_c03_clean_boxes.mp4` (attached to the GitHub Release for this report)

## S02

### Clean run — camera consistency scores

| camera | mean_distance | pair_count | z_score | flagged |
| --- | --- | --- | --- | --- |
| c01 | 0.407 | 39.0 | 40.832 | True |
| c02 | 0.574 | 98.0 | 0.674 | False |
| c03 | 0.571 | 95.0 | 0.674 | False |


### Poisoned run (`poison_c01-c02_eps0.5_seed7`) — scores and detection

| camera | mean_distance | pair_count | z_score | flagged |
| --- | --- | --- | --- | --- |
| c01 | 0.387 | 39.0 | 9.225 | True |
| c02 | 0.584 | 98.0 | 0.674 | False |
| c03 | 0.613 | 95.0 | 0.674 | False |


| tp | fp | fn | precision | recall | f1 |
| --- | --- | --- | --- | --- | --- |
| 1.0 | 0.0 | 1.0 | 1.0 | 0.5 | 0.667 |


![S02_c01_t003s](stills/S02_c01_t003s.jpg)
![S02_c01_t009s](stills/S02_c01_t009s.jpg)
![S02_c01_t016s](stills/S02_c01_t016s.jpg)

Full clip: `videos/S02_c01_clean_boxes.mp4` (attached to the GitHub Release for this report)

![S02_c02_t003s](stills/S02_c02_t003s.jpg)
![S02_c02_t009s](stills/S02_c02_t009s.jpg)
![S02_c02_t016s](stills/S02_c02_t016s.jpg)

Full clip: `videos/S02_c02_clean_boxes.mp4` (attached to the GitHub Release for this report)

![S02_c03_t003s](stills/S02_c03_t003s.jpg)
![S02_c03_t010s](stills/S02_c03_t010s.jpg)
![S02_c03_t016s](stills/S02_c03_t016s.jpg)

Full clip: `videos/S02_c03_clean_boxes.mp4` (attached to the GitHub Release for this report)

## S03

### Clean run — camera consistency scores

| camera | mean_distance | pair_count | z_score | flagged |
| --- | --- | --- | --- | --- |
| c01 | 0.688 | 16.0 | 0.828 | False |
| c02 | 0.779 | 16.0 | 1.98 | True |
| c03 | 0.657 | 12.0 | 0.674 | False |


### Poisoned run (`poison_c01-c02_eps0.5_seed7`) — scores and detection

| camera | mean_distance | pair_count | z_score | flagged |
| --- | --- | --- | --- | --- |
| c01 | 0.606 | 16.0 | 14.293 | True |
| c02 | 0.685 | 16.0 | 0.769 | False |
| c03 | 0.682 | 12.0 | 0.674 | False |


| tp | fp | fn | precision | recall | f1 |
| --- | --- | --- | --- | --- | --- |
| 1.0 | 0.0 | 1.0 | 1.0 | 0.5 | 0.667 |


![S03_c01_t003s](stills/S03_c01_t003s.jpg)
![S03_c01_t010s](stills/S03_c01_t010s.jpg)
![S03_c01_t016s](stills/S03_c01_t016s.jpg)

Full clip: `videos/S03_c01_clean_boxes.mp4` (attached to the GitHub Release for this report)

![S03_c02_t003s](stills/S03_c02_t003s.jpg)
![S03_c02_t010s](stills/S03_c02_t010s.jpg)
![S03_c02_t016s](stills/S03_c02_t016s.jpg)

Full clip: `videos/S03_c02_clean_boxes.mp4` (attached to the GitHub Release for this report)

![S03_c03_t003s](stills/S03_c03_t003s.jpg)
![S03_c03_t009s](stills/S03_c03_t009s.jpg)
![S03_c03_t016s](stills/S03_c03_t016s.jpg)

Full clip: `videos/S03_c03_clean_boxes.mp4` (attached to the GitHub Release for this report)

## S04

### Clean run — camera consistency scores

| camera | mean_distance | pair_count | z_score | flagged |
| --- | --- | --- | --- | --- |
| c01 | 0.825 | 267.0 | 1.238 | False |
| c02 | 0.815 | 262.0 | 0.0 | False |
| c03 | 0.779 | 233.0 | 2.388 | True |


### Poisoned run (`poison_c01-c02_eps0.5_seed7`) — scores and detection

| camera | mean_distance | pair_count | z_score | flagged |
| --- | --- | --- | --- | --- |
| c01 | 0.741 | 267.0 | 0.977 | False |
| c02 | 0.73 | 262.0 | 0.674 | False |
| c03 | 0.807 | 233.0 | 4.177 | True |


| tp | fp | fn | precision | recall | f1 |
| --- | --- | --- | --- | --- | --- |
| 0.0 | 1.0 | 2.0 | 0.0 | 0.0 | 0.0 |


![S04_c01_t012s](stills/S04_c01_t012s.jpg)
![S04_c01_t036s](stills/S04_c01_t036s.jpg)
![S04_c01_t061s](stills/S04_c01_t061s.jpg)

Full clip: `videos/S04_c01_clean_boxes.mp4` (attached to the GitHub Release for this report)

![S04_c02_t012s](stills/S04_c02_t012s.jpg)
![S04_c02_t037s](stills/S04_c02_t037s.jpg)
![S04_c02_t061s](stills/S04_c02_t061s.jpg)

Full clip: `videos/S04_c02_clean_boxes.mp4` (attached to the GitHub Release for this report)

![S04_c03_t012s](stills/S04_c03_t012s.jpg)
![S04_c03_t037s](stills/S04_c03_t037s.jpg)
![S04_c03_t061s](stills/S04_c03_t061s.jpg)

Full clip: `videos/S04_c03_clean_boxes.mp4` (attached to the GitHub Release for this report)

## S05

### Clean run — camera consistency scores

| camera | mean_distance | pair_count | z_score | flagged |
| --- | --- | --- | --- | --- |
| c01 | 0.829 | 433.0 | 2.059 | True |
| c02 | 0.776 | 433.0 | 0.674 | False |
| c03 | 0.758 | 218.0 | 0.674 | False |


### Poisoned run (`poison_c01-c02_eps0.5_seed7`) — scores and detection

| camera | mean_distance | pair_count | z_score | flagged |
| --- | --- | --- | --- | --- |
| c01 | 0.71 | 433.0 | 0.0 | False |
| c02 | 0.662 | 433.0 | 0.674 | False |
| c03 | 0.781 | 218.0 | 1.015 | False |


| tp | fp | fn | precision | recall | f1 |
| --- | --- | --- | --- | --- | --- |
| 0.0 | 0.0 | 2.0 | 0.0 | 0.0 | 0.0 |


![S05_c01_t008s](stills/S05_c01_t008s.jpg)
![S05_c01_t025s](stills/S05_c01_t025s.jpg)
![S05_c01_t042s](stills/S05_c01_t042s.jpg)

Full clip: `videos/S05_c01_clean_boxes.mp4` (attached to the GitHub Release for this report)

![S05_c02_t008s](stills/S05_c02_t008s.jpg)
![S05_c02_t025s](stills/S05_c02_t025s.jpg)
![S05_c02_t042s](stills/S05_c02_t042s.jpg)

Full clip: `videos/S05_c02_clean_boxes.mp4` (attached to the GitHub Release for this report)

![S05_c03_t008s](stills/S05_c03_t008s.jpg)
![S05_c03_t025s](stills/S05_c03_t025s.jpg)
![S05_c03_t042s](stills/S05_c03_t042s.jpg)

Full clip: `videos/S05_c03_clean_boxes.mp4` (attached to the GitHub Release for this report)

## S06

### Clean run — camera consistency scores

| camera | mean_distance | pair_count | z_score | flagged |
| --- | --- | --- | --- | --- |
| c01 | 0.861 | 55.0 | 0.0 | False |
| c02 | 0.84 | 55.0 | 0.674 | False |
| c03 | 0.926 | 10.0 | 2.02 | True |


### Poisoned run (`poison_c01-c02_eps0.5_seed7`) — scores and detection

| camera | mean_distance | pair_count | z_score | flagged |
| --- | --- | --- | --- | --- |
| c01 | 0.706 | 55.0 | 0.674 | False |
| c02 | 0.687 | 55.0 | 0.841 | False |
| c03 | 0.925 | 10.0 | 7.71 | True |


| tp | fp | fn | precision | recall | f1 |
| --- | --- | --- | --- | --- | --- |
| 0.0 | 1.0 | 2.0 | 0.0 | 0.0 | 0.0 |


![S06_c01_t012s](stills/S06_c01_t012s.jpg)
![S06_c01_t038s](stills/S06_c01_t038s.jpg)
![S06_c01_t064s](stills/S06_c01_t064s.jpg)

Full clip: `videos/S06_c01_clean_boxes.mp4` (attached to the GitHub Release for this report)

![S06_c02_t012s](stills/S06_c02_t012s.jpg)
![S06_c02_t038s](stills/S06_c02_t038s.jpg)
![S06_c02_t064s](stills/S06_c02_t064s.jpg)

Full clip: `videos/S06_c02_clean_boxes.mp4` (attached to the GitHub Release for this report)

![S06_c03_t012s](stills/S06_c03_t012s.jpg)
![S06_c03_t038s](stills/S06_c03_t038s.jpg)
![S06_c03_t064s](stills/S06_c03_t064s.jpg)

Full clip: `videos/S06_c03_clean_boxes.mp4` (attached to the GitHub Release for this report)

## S07

### Clean run — camera consistency scores

| camera | mean_distance | pair_count | z_score | flagged |
| --- | --- | --- | --- | --- |
| c01 | 0.842 | 1628.0 | 0.674 | False |
| c02 | 0.842 | 1628.0 | 0.0 | False |
| c03 | 0.819 | 350.0 | 110.789 | True |


### Poisoned run (`poison_c01-c02_eps0.5_seed7`) — scores and detection

| camera | mean_distance | pair_count | z_score | flagged |
| --- | --- | --- | --- | --- |
| c01 | 0.689 | 1628.0 | 0.674 | False |
| c02 | 0.689 | 1628.0 | 0.674 | False |
| c03 | 0.838 | 350.0 | 381.739 | True |


| tp | fp | fn | precision | recall | f1 |
| --- | --- | --- | --- | --- | --- |
| 0.0 | 1.0 | 2.0 | 0.0 | 0.0 | 0.0 |


![S07_c01_t014s](stills/S07_c01_t014s.jpg)
![S07_c01_t044s](stills/S07_c01_t044s.jpg)
![S07_c01_t073s](stills/S07_c01_t073s.jpg)

Full clip: `videos/S07_c01_clean_boxes.mp4` (attached to the GitHub Release for this report)

![S07_c02_t014s](stills/S07_c02_t014s.jpg)
![S07_c02_t044s](stills/S07_c02_t044s.jpg)
![S07_c02_t073s](stills/S07_c02_t073s.jpg)

Full clip: `videos/S07_c02_clean_boxes.mp4` (attached to the GitHub Release for this report)

![S07_c03_t014s](stills/S07_c03_t014s.jpg)
![S07_c03_t044s](stills/S07_c03_t044s.jpg)
![S07_c03_t073s](stills/S07_c03_t073s.jpg)

Full clip: `videos/S07_c03_clean_boxes.mp4` (attached to the GitHub Release for this report)

## S08

### Clean run — camera consistency scores

| camera | mean_distance | pair_count | z_score | flagged |
| --- | --- | --- | --- | --- |
| c01 | 0.984 | 15.0 | 0.0 | False |
| c03 | 0.984 | 15.0 | 0.0 | False |


### Poisoned run (`poison_c01-c02_eps0.5_seed7`) — scores and detection

| camera | mean_distance | pair_count | z_score | flagged |
| --- | --- | --- | --- | --- |
| c01 | 0.97 | 15.0 | 0.0 | False |
| c03 | 0.97 | 15.0 | 0.0 | False |


| tp | fp | fn | precision | recall | f1 |
| --- | --- | --- | --- | --- | --- |
| 0.0 | 0.0 | 2.0 | 0.0 | 0.0 | 0.0 |


![S08_c01_t000s](stills/S08_c01_t000s.jpg)
![S08_c01_t002s](stills/S08_c01_t002s.jpg)
![S08_c01_t004s](stills/S08_c01_t004s.jpg)

Full clip: `videos/S08_c01_clean_boxes.mp4` (attached to the GitHub Release for this report)

![S08_c03_t000s](stills/S08_c03_t000s.jpg)
![S08_c03_t002s](stills/S08_c03_t002s.jpg)
![S08_c03_t004s](stills/S08_c03_t004s.jpg)

Full clip: `videos/S08_c03_clean_boxes.mp4` (attached to the GitHub Release for this report)

## S09

### Clean run — camera consistency scores

_no data_


### Poisoned run (`poison_c01-c02_eps0.5_seed7`) — scores and detection

_no data_


| tp | fp | fn | precision | recall | f1 |
| --- | --- | --- | --- | --- | --- |
| 0.0 | 0.0 | 2.0 | 0.0 | 0.0 | 0.0 |


![S09_c01_t000s](stills/S09_c01_t000s.jpg)
![S09_c01_t001s](stills/S09_c01_t001s.jpg)
![S09_c01_t002s](stills/S09_c01_t002s.jpg)

Full clip: `videos/S09_c01_clean_boxes.mp4` (attached to the GitHub Release for this report)

## S10

### Clean run — camera consistency scores

_no data_


### Poisoned run (`poison_c01-c02_eps0.5_seed7`) — scores and detection

_no data_


## S11

### Clean run — camera consistency scores

| camera | mean_distance | pair_count | z_score | flagged |
| --- | --- | --- | --- | --- |
| c01 | 0.857 | 17.0 | 0.674 | False |
| c02 | 0.806 | 14.0 | 2.488 | True |
| c03 | 0.846 | 17.0 | 0.674 | False |


### Poisoned run (`poison_c01-c02_eps0.5_seed7`) — scores and detection

| camera | mean_distance | pair_count | z_score | flagged |
| --- | --- | --- | --- | --- |
| c01 | 0.79 | 17.0 | 0.674 | False |
| c02 | 0.728 | 14.0 | 0.674 | False |
| c03 | 0.861 | 17.0 | 2.086 | True |


| tp | fp | fn | precision | recall | f1 |
| --- | --- | --- | --- | --- | --- |
| 0.0 | 1.0 | 2.0 | 0.0 | 0.0 | 0.0 |


![S11_c01_t000s](stills/S11_c01_t000s.jpg)
![S11_c01_t001s](stills/S11_c01_t001s.jpg)
![S11_c01_t002s](stills/S11_c01_t002s.jpg)

Full clip: `videos/S11_c01_clean_boxes.mp4` (attached to the GitHub Release for this report)

![S11_c02_t000s](stills/S11_c02_t000s.jpg)
![S11_c02_t001s](stills/S11_c02_t001s.jpg)
![S11_c02_t002s](stills/S11_c02_t002s.jpg)

Full clip: `videos/S11_c02_clean_boxes.mp4` (attached to the GitHub Release for this report)

![S11_c03_t000s](stills/S11_c03_t000s.jpg)
![S11_c03_t001s](stills/S11_c03_t001s.jpg)
![S11_c03_t002s](stills/S11_c03_t002s.jpg)

Full clip: `videos/S11_c03_clean_boxes.mp4` (attached to the GitHub Release for this report)

## S12

### Clean run — camera consistency scores

| camera | mean_distance | pair_count | z_score | flagged |
| --- | --- | --- | --- | --- |
| c01 | 0.345 | 1.0 | 0.0 | False |
| c02 | 0.345 | 1.0 | 0.0 | False |


### Poisoned run (`poison_c01-c02_eps0.5_seed7`) — scores and detection

| camera | mean_distance | pair_count | z_score | flagged |
| --- | --- | --- | --- | --- |
| c01 | 0.277 | 1.0 | 0.0 | False |
| c02 | 0.277 | 1.0 | 0.0 | False |


| tp | fp | fn | precision | recall | f1 |
| --- | --- | --- | --- | --- | --- |
| 0.0 | 0.0 | 2.0 | 0.0 | 0.0 | 0.0 |


![S12_c01_t000s](stills/S12_c01_t000s.jpg)
![S12_c01_t001s](stills/S12_c01_t001s.jpg)
![S12_c01_t002s](stills/S12_c01_t002s.jpg)

Full clip: `videos/S12_c01_clean_boxes.mp4` (attached to the GitHub Release for this report)

![S12_c02_t000s](stills/S12_c02_t000s.jpg)
![S12_c02_t001s](stills/S12_c02_t001s.jpg)
![S12_c02_t002s](stills/S12_c02_t002s.jpg)

Full clip: `videos/S12_c02_clean_boxes.mp4` (attached to the GitHub Release for this report)

## S13

### Clean run — camera consistency scores

_no data_


### Poisoned run (`poison_c01-c02_eps0.5_seed7`) — scores and detection

_no data_


| tp | fp | fn | precision | recall | f1 |
| --- | --- | --- | --- | --- | --- |
| 0.0 | 0.0 | 2.0 | 0.0 | 0.0 | 0.0 |


![S13_c02_t000s](stills/S13_c02_t000s.jpg)
![S13_c02_t001s](stills/S13_c02_t001s.jpg)
![S13_c02_t001s](stills/S13_c02_t001s.jpg)

Full clip: `videos/S13_c02_clean_boxes.mp4` (attached to the GitHub Release for this report)

## S14

### Clean run — camera consistency scores

| camera | mean_distance | pair_count | z_score | flagged |
| --- | --- | --- | --- | --- |
| c01 | 0.796 | 1183.0 | 0.674 | False |
| c02 | 0.783 | 1183.0 | 2.993 | True |
| c03 | 0.793 | 738.0 | 0.674 | False |


### Poisoned run (`poison_c01-c02_eps0.5_seed7`) — scores and detection

| camera | mean_distance | pair_count | z_score | flagged |
| --- | --- | --- | --- | --- |
| c01 | 0.682 | 1347.0 | 0.674 | False |
| c02 | 0.672 | 1347.0 | 0.674 | False |
| c03 | 0.814 | 738.0 | 9.088 | True |


| tp | fp | fn | precision | recall | f1 |
| --- | --- | --- | --- | --- | --- |
| 0.0 | 1.0 | 2.0 | 0.0 | 0.0 | 0.0 |


![S14_c01_t020s](stills/S14_c01_t020s.jpg)
![S14_c01_t060s](stills/S14_c01_t060s.jpg)
![S14_c01_t100s](stills/S14_c01_t100s.jpg)

Full clip: `videos/S14_c01_clean_boxes.mp4` (attached to the GitHub Release for this report)

![S14_c02_t020s](stills/S14_c02_t020s.jpg)
![S14_c02_t060s](stills/S14_c02_t060s.jpg)
![S14_c02_t100s](stills/S14_c02_t100s.jpg)

Full clip: `videos/S14_c02_clean_boxes.mp4` (attached to the GitHub Release for this report)

![S14_c03_t020s](stills/S14_c03_t020s.jpg)
![S14_c03_t060s](stills/S14_c03_t060s.jpg)
![S14_c03_t100s](stills/S14_c03_t100s.jpg)

Full clip: `videos/S14_c03_clean_boxes.mp4` (attached to the GitHub Release for this report)

## S15

### Clean run — camera consistency scores

| camera | mean_distance | pair_count | z_score | flagged |
| --- | --- | --- | --- | --- |
| c01 | 0.809 | 2248.0 | 9.447 | True |
| c02 | 0.775 | 2248.0 | 0.674 | False |
| c03 | 0.777 | 1548.0 | 0.674 | False |


### Poisoned run (`poison_c01-c02_eps0.5_seed7`) — scores and detection

| camera | mean_distance | pair_count | z_score | flagged |
| --- | --- | --- | --- | --- |
| c01 | 0.707 | 2248.0 | 0.959 | False |
| c02 | 0.677 | 2248.0 | 0.674 | False |
| c03 | 0.801 | 1548.0 | 2.06 | True |


| tp | fp | fn | precision | recall | f1 |
| --- | --- | --- | --- | --- | --- |
| 0.0 | 1.0 | 2.0 | 0.0 | 0.0 | 0.0 |


![S15_c01_t019s](stills/S15_c01_t019s.jpg)
![S15_c01_t059s](stills/S15_c01_t059s.jpg)
![S15_c01_t099s](stills/S15_c01_t099s.jpg)

Full clip: `videos/S15_c01_clean_boxes.mp4` (attached to the GitHub Release for this report)

![S15_c02_t019s](stills/S15_c02_t019s.jpg)
![S15_c02_t059s](stills/S15_c02_t059s.jpg)
![S15_c02_t099s](stills/S15_c02_t099s.jpg)

Full clip: `videos/S15_c02_clean_boxes.mp4` (attached to the GitHub Release for this report)

![S15_c03_t020s](stills/S15_c03_t020s.jpg)
![S15_c03_t060s](stills/S15_c03_t060s.jpg)
![S15_c03_t100s](stills/S15_c03_t100s.jpg)

Full clip: `videos/S15_c03_clean_boxes.mp4` (attached to the GitHub Release for this report)

## S16

### Clean run — camera consistency scores

| camera | mean_distance | pair_count | z_score | flagged |
| --- | --- | --- | --- | --- |
| c01 | 0.83 | 397.0 | 10.939 | True |
| c02 | 0.771 | 397.0 | 0.674 | False |
| c03 | 0.749 | 366.0 | 0.674 | False |


### Poisoned run (`poison_c01-c02_eps0.5_seed7`) — scores and detection

| camera | mean_distance | pair_count | z_score | flagged |
| --- | --- | --- | --- | --- |
| c01 | 0.741 | 397.0 | 0.0 | False |
| c02 | 0.688 | 397.0 | 1.153 | False |
| c03 | 0.771 | 366.0 | 1.169 | False |


| tp | fp | fn | precision | recall | f1 |
| --- | --- | --- | --- | --- | --- |
| 0.0 | 0.0 | 2.0 | 0.0 | 0.0 | 0.0 |


![S16_c01_t020s](stills/S16_c01_t020s.jpg)
![S16_c01_t060s](stills/S16_c01_t060s.jpg)
![S16_c01_t100s](stills/S16_c01_t100s.jpg)

Full clip: `videos/S16_c01_clean_boxes.mp4` (attached to the GitHub Release for this report)

![S16_c02_t020s](stills/S16_c02_t020s.jpg)
![S16_c02_t060s](stills/S16_c02_t060s.jpg)
![S16_c02_t100s](stills/S16_c02_t100s.jpg)

Full clip: `videos/S16_c02_clean_boxes.mp4` (attached to the GitHub Release for this report)

![S16_c03_t020s](stills/S16_c03_t020s.jpg)
![S16_c03_t060s](stills/S16_c03_t060s.jpg)
![S16_c03_t100s](stills/S16_c03_t100s.jpg)

Full clip: `videos/S16_c03_clean_boxes.mp4` (attached to the GitHub Release for this report)

## S17

### Clean run — camera consistency scores

| camera | mean_distance | pair_count | z_score | flagged |
| --- | --- | --- | --- | --- |
| c01 | 0.775 | 198.0 | 4.246 | True |
| c02 | 0.738 | 196.0 | 0.674 | False |
| c03 | 0.743 | 158.0 | 0.0 | False |


### Poisoned run (`poison_c01-c02_eps0.5_seed7`) — scores and detection

| camera | mean_distance | pair_count | z_score | flagged |
| --- | --- | --- | --- | --- |
| c01 | 0.688 | 198.0 | 140.789 | True |
| c02 | 0.655 | 196.0 | 0.674 | False |
| c03 | 0.765 | 158.0 | 1.529 | True |


| tp | fp | fn | precision | recall | f1 |
| --- | --- | --- | --- | --- | --- |
| 1.0 | 1.0 | 1.0 | 0.5 | 0.5 | 0.5 |


![S17_c01_t020s](stills/S17_c01_t020s.jpg)
![S17_c01_t060s](stills/S17_c01_t060s.jpg)
![S17_c01_t100s](stills/S17_c01_t100s.jpg)

Full clip: `videos/S17_c01_clean_boxes.mp4` (attached to the GitHub Release for this report)

![S17_c02_t020s](stills/S17_c02_t020s.jpg)
![S17_c02_t060s](stills/S17_c02_t060s.jpg)
![S17_c02_t100s](stills/S17_c02_t100s.jpg)

Full clip: `videos/S17_c02_clean_boxes.mp4` (attached to the GitHub Release for this report)

![S17_c03_t020s](stills/S17_c03_t020s.jpg)
![S17_c03_t060s](stills/S17_c03_t060s.jpg)
![S17_c03_t100s](stills/S17_c03_t100s.jpg)

Full clip: `videos/S17_c03_clean_boxes.mp4` (attached to the GitHub Release for this report)

## S18

### Clean run — camera consistency scores

| camera | mean_distance | pair_count | z_score | flagged |
| --- | --- | --- | --- | --- |
| c01 | 0.851 | 6.0 | 0.0 | False |
| c02 | 0.851 | 6.0 | 0.0 | False |


### Poisoned run (`poison_c01-c02_eps0.5_seed7`) — scores and detection

| camera | mean_distance | pair_count | z_score | flagged |
| --- | --- | --- | --- | --- |
| c01 | 0.68 | 6.0 | 0.0 | False |
| c02 | 0.68 | 6.0 | 0.0 | False |


| tp | fp | fn | precision | recall | f1 |
| --- | --- | --- | --- | --- | --- |
| 0.0 | 0.0 | 2.0 | 0.0 | 0.0 | 0.0 |


![S18_c01_t040s](stills/S18_c01_t040s.jpg)
![S18_c01_t120s](stills/S18_c01_t120s.jpg)
![S18_c01_t200s](stills/S18_c01_t200s.jpg)

Full clip: `videos/S18_c01_clean_boxes.mp4` (attached to the GitHub Release for this report)

![S18_c02_t040s](stills/S18_c02_t040s.jpg)
![S18_c02_t120s](stills/S18_c02_t120s.jpg)
![S18_c02_t200s](stills/S18_c02_t200s.jpg)

Full clip: `videos/S18_c02_clean_boxes.mp4` (attached to the GitHub Release for this report)
