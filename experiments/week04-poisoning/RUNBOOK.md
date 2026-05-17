# Week 04 Poisoning Runbook

Source of truth: `docs/schedules/PRIME_Schedule_new_revised.pdf`.

Goal: shift embeddings from cameras c01 and c02 in CityFlowV2 S01 and compare clean against poisoned conditions.

## Required Conditions

- Clean Week 3 baseline exists.
- BoT-SORT PRIME ReID hook is active.
- Run log template is used for every condition.
- Epsilon values: `0.1`, `0.5`, `1.0`.
- Poisoned cameras: `c01,c02`.

## Researcher Prerequisites

- Confirm perturbation is applied before or after feature normalization.
- Confirm random seed.
- Confirm whether Week 4 uses random perturbation only or includes targeted perturbation as a demo.
- Confirm output folder outside git.

## Student Task

For each epsilon:

1. Run poisoned BoT-SORT-ReID on S01.
2. Export embeddings.
3. Record exact command and output path.
4. Record IDF1, HOTA, MOTA, IDS.
5. Update the clean-vs-poisoned comparison table.

## Example Command Shape

```bash
cd vendor/BoT-SORT
python tools/demo.py video --path <path-to-S01-c001-video> --with-reid --prime-camera-id c01 --prime-poison-cameras c01,c02 --prime-poison-epsilon 0.5 --prime-poison-seed 7 --prime-export-embeddings ../../runs/botsort/poisoned_eps_0_5_c01.csv
```

## Required Summary Table

```text
Condition,Poisoned cameras,Epsilon,IDF1,HOTA,MOTA,IDS,Notes
clean,none,0.0,,,,,
poisoned,c01;c02,0.1,,,,,
poisoned,c01;c02,0.5,,,,,
poisoned,c01;c02,1.0,,,,,
```
