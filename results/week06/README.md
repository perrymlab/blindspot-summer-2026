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
