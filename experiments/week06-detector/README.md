# Week 06 Detector

Cross-camera embedding consistency detector protocol, commands, configuration, and notes.

## Methodological caveat: majority-poisoned cameras

The detector (`src/prime_mtmc/detector.py`) scores each camera by its robust
z-score against the **median** across cameras. This assumes poisoned cameras
are a minority. The Week 4 attack setting poisons c01 and c02 — two of three
cameras — so the "typical" camera the median represents is itself poisoned,
and the clean c03 can be flagged as the outlier instead. With only three
cameras, any 2-of-3 result should be interpreted with this in mind.

Suggested comparison sweep (single poisoned camera, where the detector's
minority assumption holds):

```bash
python scripts/run_baselines.py --all --poison-cameras c01 --apply
```

Outputs are named `S0N_poison_c01_eps0.5_seed7_*` and coexist with the
`c01-c02` set. Comparing detector precision/recall between the 1-of-3 and
2-of-3 regimes is a candidate result for the Week 6/7 writeups: it
characterizes where the consistency approach breaks down, which reviewers
will ask about.

(Caveat raised during batch tooling work, 2026-06-12; decision on whether to
run the sweep is the researcher's.)
