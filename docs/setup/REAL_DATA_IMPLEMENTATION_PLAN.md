# Real-Data Implementation Plan

Source of truth: `docs/schedules/PRIME_Schedule_new_revised.pdf`.

This plan lists the remaining implementation path from the current repository scaffold to a complete real-data research pipeline.

## Gate 1: Environment And Data

Owner: Sabrina.

Done when:

- Official environment method is chosen: conda or `.venv`.
- Python and PyTorch work on every student machine.
- BoT-SORT is cloned and patched.
- CityFlowV2 S01 is downloaded.
- Detector and FastReID weights are available.
- Local paths are documented in each machine's untracked `docs/setup/LOCAL_PATHS.md`.

Repository support:

- `scripts/setup_repo.py`
- `scripts/check_research_readiness.py`
- `docs/setup/DOWNLOADS.md`
- `docs/setup/LOCAL_PATHS.template.md`
- `docs/botsort-integration/BOTSORT_INTEGRATION.md`

Readiness check shape:

```bash
python scripts/check_research_readiness.py --cityflow-root <path-to-CityFlowV2> --detector-weights <path-to-detector-weights> --reid-weights <path-to-reid-weights>
```

## Gate 2: Clean Baseline

Owner: Sabrina confirms; students run and log.

Done when:

- BoT-SORT-ReID runs on CityFlowV2 S01 clean data.
- ReID embeddings are confirmed active.
- IDF1, HOTA, MOTA, and IDS are logged.
- A clean baseline run log is stored in `experiments/week03-baseline/`.
- A small approved summary is stored in `results/week03/`.

Repository support:

- `experiments/week03-baseline/RUNBOOK.md`
- `docs/templates/RUN_LOG_TEMPLATE.md`

## Gate 3: Poisoning Runs

Owner: Sabrina confirms hook/settings; students run and log.

Done when:

- Embedding hook is confirmed active.
- Cameras c01 and c02 are poisoned.
- Epsilon values 0.1, 0.5, and 1.0 are run.
- Clean-vs-poisoned comparison table includes IDF1, HOTA, MOTA, and IDS.

Repository support:

- `experiments/week04-poisoning/RUNBOOK.md`
- `docs/botsort-integration/BOTSORT_INTEGRATION.md`

## Gate 4: Detector On Real Outputs

Owner: Sabrina confirms global-ID source and statistics; students run and log.

Done when:

- Detection-level embedding exports are merged with tracker/global IDs or ground-truth IDs.
- `scripts/analyze_embedding_export.py` runs on clean and poisoned merged tables.
- Precision, recall, and F1 are reported.
- Cosine-distance distribution plots are produced or documented as pending.

Repository support:

- `scripts/analyze_embedding_export.py`
- `experiments/week06-detector/RUNBOOK.md`

## Gate 5: Scalability And Boundary Conditions

Owner: Sabrina confirms paper framing; students run and log.

Done when:

- Detector is tested on S01, S02, and S03.
- Poisoned-camera count varies from 1 to N-1.
- Random and targeted perturbation are compared if targeted selection is ready.
- Failure modes are documented with mechanistic hypotheses.
- Paper contribution statement is locked.

Repository support:

- `experiments/week07-scalability/RUNBOOK.md`
- `paper-draft/`

## Gate 6: Writing And Publication

Owner: Sabrina.

Done when:

- Literature review is organized around the four schedule pillars.
- Introduction, methods, results, abstract, and conclusion are integrated.
- Venue shortlist is documented.
- Post-program task ownership is assigned.

Repository support:

- `paper-draft/`
- `papers/`
- `results/`
