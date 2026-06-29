# Week 06 Results — Detector Performance

## Status: Partial — real `track_id` available, metrics not yet extracted ⚠️

The original 2026-06-12 detector run used `detection_index` (fake cross-camera
pairings). Since then, ground-truth annotations were produced for **all 18**
scenarios and joined onto the 1536 re-export for the **14 usable** scenarios
(S01–S08, S11, S13–S17) as real global `track_id` (mean per-camera coverage
~0.45), published as Release `exports-2026-06-20`. Real precision/recall can now
be computed (`analyze_embedding_export.py --track-column track_id`); the
IDF1/HOTA/MOTA/IDS extraction (STATUS TODO #6) is still outstanding before the
gate fully closes.

## Run log

| Date | Scenarios | Track column | Poison cams | P | R | F1 | Valid? |
|------|-----------|-------------|-------------|---|---|----|--------|
| 2026-06-12 | S01–S18 | `detection_index` | c01, c02 | — | — | — | NO — placeholder identities |
| 2026-06-20 | 14 usable | `track_id` | c01, c02 | — | — | — | real GT joined; metrics not yet tabulated |
| 2026-06-27 | S11,S13–S17 (Floyd) | `track_id` | c01, c02 | see below | see below | see below | CAVEAT — majority-poisoned (see below) |

### Floyd's poisoned-run detector metrics (2026-06-27, real `track_id`)

Poison target = **c01, c02** (2 of 3 cameras = majority). Per-run `.md` logs are
in this folder.

| Scenario | z-thr | TP | FP | FN | TN | P | R | F1 | Cameras flagged |
|----------|-------|----|----|----|----|------|------|-------|-----------------|
| S11 | 1.0 | 0 | 1 | 2 | 0 | 0.00 | 0.00 | 0.00 | c03 (clean cam) |
| S13 | 1.0 | 1 | 1 | 1 | 0 | 0.50 | 0.50 | 0.50 | c01, c03 |
| S14 | 1.0 | 1 | 1 | 1 | 0 | 0.50 | 0.50 | 0.50 | c01, c03 |
| S15 | 0.5 | 0 | 1 | 2 | 0 | 0.00 | 0.00 | 0.00 | c03 (clean cam) |
| S16 | 2.0 | 0 | 0 | 2 | 1 | 0.00 | 0.00 | 0.00 | none |
| S17 | 2.0 | 1 | 0 | 1 | 1 | 1.00 | 0.50 | 0.67 | c01 |

**These are NOT the detector's representative performance.** Every run poisons
the majority of cameras, which is the documented failure mode below — the
detector frequently flags the lone *clean* camera (c03) as the outlier (S11,
S15). The valid comparison requires the single-camera poison sweep (TODO #4/#5).

**Two systematic problems visible in the data:**

- **Majority-poison inversion** — with c01+c02 poisoned (2/3), the z-score
  detector's "most cameras are clean" assumption breaks; the clean camera looks
  anomalous. Expected, not a regression.
- **n=3 degeneracy** — with only 3 cameras the z-scores collapse to fixed values
  (`±0.674491`, `0.0` recur throughout) and the variance channel explodes into
  meaningless magnitudes (c01 z = 53 on clean S15; 22 on S14; **314** on S17).
  A 3-sample outlier test is not statistically meaningful; flag to the team.

## Important caveat — majority-poisoned scenarios

When more than half of cameras are poisoned, the z-score detector's majority
assumption breaks (it flags the clean camera as the outlier). See
`experiments/week06-detector/README.md` for the full caveat. Single-camera
poison sweep (STATUS TODO #5) is the planned mitigation test.

## Provenance

- Progress report: `reports/2026-06-12/REPORT.md`
- Detector code: `src/prime_mtmc/detector.py`
- Analysis script: `scripts/analyze_embedding_export.py`

## Open items before gate closes

- [x] Annotate scenarios (done for all 18; STATUS TODO #2 / ANNOTATION_GUIDE.md)
- [x] Run join `scripts/build_track_ids.py` (done for the 14 usable scenarios, IoU 0.2)
- [ ] Tabulate detector results with `--track-column track_id` (real numbers — pending)
- [ ] IDF1/HOTA/MOTA/IDS extraction (STATUS TODO #6)
- [ ] Single-camera poison sweep (STATUS TODO #4)
- [ ] Document majority-poisoned caveat in paper draft
