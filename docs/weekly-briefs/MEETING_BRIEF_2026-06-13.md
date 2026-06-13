# Meeting brief — Brian / Dr. Perry, 2026-06-13

**Schedule position:** Week 6 → Week 7 boundary. The Week 6 task "review detector
implementation for statistical correctness before week 7 scaling tests" was
effectively completed by today's detector commit (`49375e0`); Week 7
(scalability) has not started.

Source docs: `docs/STATUS.md`, `docs/setup/REAL_DATA_IMPLEMENTATION_PLAN.md`,
`docs/weekly-briefs/RESEARCHER_ALL_WEEKS_TASKS.md`,
`docs/schedules/SRP_Research_Experience.pdf`, `docs/data/SCENARIO_WINDOWS_REVIEW.md`,
`experiments/week06-detector/README.md`.

## Where things stand (by gate)

**Gate 1 — Environment & data:** Done. Loose end: the official environment
method (conda per the schedule vs. the repo's `.venv`) was never formally
confirmed.

**Gate 2 — Clean baseline:** Partial, and weaker than STATUS claims. After
reconciling the window files, only **S14–S18** meet the 120–300 s trimming spec;
S01–S13 were trimmed to under-target windows (S09–S13 as short as 2–3 s). The
required tracking metrics — **IDF1 / HOTA / MOTA / IDS — are still not
implemented**. That is a Week 3 gate requirement and feeds the Week 4
comparison table, so it is a real gap.

**Gate 3 — Poisoning runs:** Partial. The eps 0.5 batch ran (c01,c02), but
**eps 0.1 and 1.0 are pending**. The schedule titles Week 4 the "Two-Camera
Attack," so the c01,c02 setting is the defined core attack — not a mistake.

**Gate 4 — Detector on real outputs:** Partial. The detector runs but on
`detection_index` (positional placeholder, not real identities). Today's commit
fixed the detector directionality bug (one-sided z-score, no more false-flagging
clean cameras) and wired in the ground-truth `track_id` join. Real metrics still
depend on **human annotation (S07, S14, S15), in progress**.

**Gate 5 — Scalability (Week 7):** Not started.

**Gate 6 — Writing:** Not started.

## Decisions to get from Dr. Perry today

1. **Approve the reconciled scenario windows.** Four open items in
   `docs/data/SCENARIO_WINDOWS_REVIEW.md`: the S01 start (0 vs 35), the S02–S09
   starts (Christine's vs the live file's), confirming Christine's third column
   is end-time not duration, and S12 = 300 s. Unblocks everything downstream.

2. **Tracking-metric scope.** IDF1/HOTA/MOTA/IDS are required by the gates but
   unimplemented — decide whether to build now or formally defer. Currently only
   detection precision/recall/F1 exist, on placeholder identities.

3. **Poison-count framing.** Confirm the split:
   - 2-camera (c01,c02) run = the **Week 4 attack** result (does poisoning
     degrade tracking).
   - Detector efficacy is demonstrated at **1 camera** (the minority case it is
     designed for).
   - **Week 7's "1-to-N" sweep** characterizes where it breaks.
   Key point: the Week 4 two-camera attack is 2-of-3 cameras — a majority —
   exactly the regime the consistency detector struggles with. Frame as a
   finding, not a bug.

4. **Annotation priority** — confirm S07, S14, S15 and who does them.

## Reprocessing required (in order)

1. **Re-trim S01–S13** with the approved windows (S14–S18 are fine, leave them).
2. **Re-run clean + poisoned baselines for S01–S13**, then extend the poison
   sweep to **eps 0.1 and 1.0** across the valid scenarios.
3. **After annotation:** run `build_track_ids.py` to produce `*_tracked.csv`
   joins, then regenerate reports keyed on real `track_id`, not
   `detection_index`.
4. **Regenerate the 2026-06-12 report** — its S01, S08–S13 numbers are
   meaningless (bad windows) and should not be cited until re-run.
5. **Week 7 sweep:** vary poisoned cameras 1→N on the corrected, annotated data.

## Worth mentioning briefly

The repo had a corrupt git index and a stale lock (now fixed) and a doc
consolidation plan (`docs/CONSOLIDATION_PLAN.md`) addressing stale/duplicated
docs. Minor, but worth a nod if Dr. Perry reviews PRs.

## Pending edits awaiting approval (already drafted, not yet applied)

- Make `--poison-cameras` default to `c01` in `scripts/run_baselines.py`
  (single-camera minority as the working default; 2-camera explicit for Week 7).
- Narrow the STATUS "valid scenarios" claim to S14–S18 only.
- Reconciled manifest proposed at `data/scenario_windows.reconciled.csv`.
- Fix the Sabrina vs. Dr. Perry approver-name inconsistency in
  `docs/data/SCENARIO_TRIMMING.md`.
