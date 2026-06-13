# Meeting brief — Brian / Dr. Perry, 2026-06-13

**Schedule position: Week 3 — Dataset Curation and Clean Baseline (Gate 2).**

The repository contains scaffolding for later weeks (poisoning, the cross-camera
detector, scalability), but those are built ahead of schedule and are **not**
this week's deliverables. STATUS.md and the all-weeks doc describe built
*capability*, not schedule position — worth realigning them to Week 3.

Source docs: `docs/STATUS.md`, `docs/setup/REAL_DATA_IMPLEMENTATION_PLAN.md`,
`docs/weekly-briefs/RESEARCHER_ALL_WEEKS_TASKS.md`,
`docs/schedules/SRP_Research_Experience.pdf`, `docs/data/SCENARIO_WINDOWS_REVIEW.md`,
`docs/data/GROUND_TRUTH.md`.

## The headline decision for this meeting: dataset & ground truth

The schedule was written around **CityFlowV2 S01**, which ships with
ground-truth annotations — with it, the Week 3 metrics (IDF1/HOTA/MOTA/IDS) are
nearly free to compute. Gate 1 records that **local intersection footage
replaced CityFlowV2**, and that footage has **no ground truth**. That single
decision is what turns "run the eval script" into "annotate first, then run the
eval script," and it's the root of the metrics gap below.

**Decide:** keep custom footage and commit to the annotation effort, or use an
annotated benchmark (CityFlowV2) as the baseline source. Everything else in
Week 3 depends on this.

## Week 3 deliverable status (Gate 2 — Clean Baseline)

- **Trim windows are broken.** After reconciling the three window files, only
  **S14–S18** meet the 120–300 s spec; S01–S13 are under target (S09–S13 as
  short as 2–3 s). Re-trim needed. See `docs/data/SCENARIO_WINDOWS_REVIEW.md`
  and the proposed `data/scenario_windows.reconciled.csv`.
- **Clean BoT-SORT baseline** runs on trimmed footage, but needs to be
  re-confirmed on corrected windows.
- **IDF1 / HOTA / MOTA / IDS — not yet implemented.** This is the current Week 3
  metric deliverable, not an overdue item. It is blocked on ground truth (see
  headline decision): these are identity/tracking metrics scored against
  ground-truth track IDs, which the custom footage lacks. No tracking-eval
  library (TrackEval / py-motmetrics) is wired in yet either.
- **Environment method** (conda per schedule vs. the repo's `.venv`) still
  unconfirmed.

## Decisions to get from Dr. Perry today

1. **Dataset / ground-truth path** (headline above) — custom footage + annotate,
   or annotated benchmark. Drives everything else.
2. **Approve the reconciled scenario windows** if staying on custom footage.
   Four open items in `SCENARIO_WINDOWS_REVIEW.md`: S01 start (0 vs 35), S02–S09
   starts, confirming Christine's third column is end-time not duration, and
   S12 = 300 s.
3. **Metric implementation scope & owner** — full TrackEval/HOTA vs. a lighter
   py-motmetrics subset (IDF1/MOTA/IDS) first; who builds it.
4. **Annotation plan** if staying on custom footage — which scenarios, who, when.

## Reprocessing required (once decisions are made)

1. Re-trim S01–S13 with the approved windows (S14–S18 are fine).
2. Re-confirm the clean BoT-SORT baseline on the corrected footage.
3. Stand up ground truth (annotation, or adopt benchmark GT).
4. Implement and run IDF1/HOTA/MOTA/IDS against that ground truth.

## Housekeeping (brief)

- Git index was corrupt + a stale lock; fixed on Brian's machine.
- Doc consolidation plan (`docs/CONSOLIDATION_PLAN.md`) addresses stale and
  duplicated docs; STATUS overstates progress relative to a Week 3 position.

## Drafted, not yet applied (for later weeks — parked)

- `--poison-cameras` default → `c01` in `scripts/run_baselines.py` (Week 4+).
- Reconciled manifest at `data/scenario_windows.reconciled.csv` (Week 3, pending
  approval).
- Fix Sabrina vs. Dr. Perry approver-name inconsistency in
  `docs/data/SCENARIO_TRIMMING.md`.
