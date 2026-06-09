# Week 03 Baseline Runbook

Source of truth: `docs/schedules/PRIME_Schedule_new_revised.pdf`.

Goal: run BoT-SORT-ReID on clean local `blindspot_data` Scenario S01 and log IDF1, HOTA, MOTA, and IDS.

> **Who does what:** the **researcher** runs BoT-SORT on a GPU box (see
> `docs/botsort-integration/BOTSORT_GPU_RUNBOOK.md`) and exports embedding
> CSVs. **Students** analyze those CSVs (see
> `docs/experiments/STUDENT_EMBEDDING_ANALYSIS.md`) -- students do not run
> BoT-SORT.

## Researcher Prerequisites

- Local `blindspot_data` S01 path confirmed in local notes.
- BoT-SORT checkout exists and is on `prime-reid-poison-export`.
- PyTorch works on the target machine.
- Object detector weights path confirmed.
- FastReID/OSNet weights path confirmed.
- Output folder chosen outside git.

## Student Task

Students consume the embedding CSVs the researcher exports; they do not run
BoT-SORT. Full steps are in `docs/experiments/STUDENT_EMBEDDING_ANALYSIS.md`.

1. Pull latest `main`.
2. Create a branch for Week 3 baseline notes.
3. Copy `docs/templates/RUN_LOG_TEMPLATE.md` into this folder with a dated filename.
4. Get the S01 clean embedding CSV(s) from the researcher.
5. Analyze them with `scripts/analyze_embedding_export.py` (see the student guide).
6. Record input CSV, command, output paths, and the metric output.
7. Add a small summary to `results/week03/` only after Sabrina approves it.

## Required Result

The run is complete only when the log includes:

- Scenario and cameras.
- Exact command.
- Weight paths.
- Output paths.
- IDF1, HOTA, MOTA, IDS.
- Confirmation that ReID embeddings are active.

## Example Embedding Export Shape

```bash
cd vendor/BoT-SORT
python tools/demo.py video --path <path-to-S01-c001-video> --with-reid --prime-camera-id c01 --prime-export-embeddings ../../runs/botsort/clean_c01.csv
```

Repeat for each S01 camera, then merge/export as required by the metric workflow Sabrina approves.
