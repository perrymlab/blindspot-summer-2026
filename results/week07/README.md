# Week 07 Results — Scalability & Boundary Conditions

## Status: Not started

Prerequisite: week06 real-identity metrics must exist first (annotation +
join pipeline complete). Until then this gate cannot meaningfully be assessed.

## Planned experiments

- Vary number of cameras poisoned (1 of 3, 2 of 3, 3 of 3)
- Vary epsilon (0.1, 0.5, 1.0) — currently only 0.5 complete
- Test detector behavior at majority-poisoned boundary
- Single-camera sweep already planned as STATUS TODO #5

## Dependencies

- [ ] STATUS TODO #1 (trim windows) — fixes valid scenario set
- [ ] STATUS TODO #3 (annotation) — gives real identities for S07/S14/S15
- [ ] STATUS TODO #4 (join + analyze with track_id) — produces real metrics
- [ ] STATUS TODO #5 (single-cam sweep) — directly contributes to this gate
