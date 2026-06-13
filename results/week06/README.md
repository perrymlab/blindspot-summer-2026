# Week 06 Results — Detector Performance

## Status: Partial — metrics are placeholders ⚠️

Detector ran on all scenarios 2026-06-12, but on `detection_index` (fake
cross-camera pairings), **not real ground-truth identities**. The structural
pattern (poisoned-pair coherence) is visible, but precision/recall numbers
are not publishable until TODO #4 (annotation) is complete.

## Run log

| Date | Scenarios | Track column | Poison cams | P | R | F1 | Valid? |
|------|-----------|-------------|-------------|---|---|----|--------|
| 2026-06-12 | S01–S18 | `detection_index` | c01, c02 | — | — | — | NO — placeholder identities |
| TBD | S07, S14, S15 | `track_id` | c01, c02 | — | — | — | After annotation (TODO #3) |

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

- [ ] Annotate S07, S14, S15 (STATUS TODO #3 / ANNOTATION_GUIDE.md)
- [ ] Run join: `scripts/build_track_ids.py` for each scenario + export
- [ ] Re-run detector with `--track-column track_id` — these are the real numbers
- [ ] Single-camera poison sweep (STATUS TODO #5)
- [ ] Document majority-poisoned caveat in paper draft
