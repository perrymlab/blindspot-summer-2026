# Week 07 Results — Scalability & Boundary Conditions

## Status: Not started

Prerequisite: week06 real-identity metrics. The annotation + join pipeline is now
complete (real `track_id` for the 14 usable scenarios), so the remaining blocker
is tabulating those metrics (STATUS TODO #6) before this gate can be assessed.

## Planned experiments

- Vary number of cameras poisoned (1 of 3, 2 of 3, 3 of 3)
- Vary epsilon (0.1, 0.5, 1.0) — currently only 0.5 complete
- Test detector behavior at majority-poisoned boundary
- Single-camera sweep already planned as STATUS TODO #5

## Dependencies

- [x] Valid scenario set — trim windows verified + 1536 re-export done (2026-06-20)
- [x] Annotation — done for all 18; real `track_id` joined for 14 usable (STATUS TODO #2)
- [ ] Tabulate real `track_id` metrics + IDF1/HOTA/MOTA/IDS (STATUS TODO #6)
- [ ] Single-camera poison sweep (STATUS TODO #4) — directly contributes to this gate
- [ ] Full epsilon sweep 0.1/1.0 (STATUS TODO #3)
