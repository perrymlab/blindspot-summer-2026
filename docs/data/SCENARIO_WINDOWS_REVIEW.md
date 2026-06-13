# Scenario windows & trimming — what's wrong and what's needed

**Date:** 2026-06-13
**Scope:** `data/scenario_windows.csv` and the trim workflow (`docs/data/SCENARIO_TRIMMING.md`, `scripts/trim_scenarios.py`).

The spec (from `SCENARIO_TRIMMING.md`): `duration_s` is the **window length in
seconds**, target **120–300 s** (a 2–5 minute window). `trim_scenarios.py`
feeds `duration_s` straight to `ffmpeg -t`, so a wrong value here silently
produces a wrong-length clip and every downstream run inherits it.

## The core problem: three window files that disagree, none complete + correct

| File | Coverage | State |
|------|----------|-------|
| `data/scenario_windows.csv` (the **live** one the tooling reads) | All 18 rows | Durations for **S01–S13 are below the 120 s target** (S09–S13 are 2–3 s). Only **S14–S18** meet spec. |
| `data/edited scenario windows.csv` | S01, S10–S18 filled; **S02–S09 blank** | Durations are correct (120–300 s) but incomplete. |
| `papers/christine/scenario_windows_christine - scenario_windows.csv` | S01–S09 filled; **S10–S18 blank** | Third column holds **end timestamps, not durations** (e.g. S02 `125,245` → 245 is the end; real length = 245−125 = 120 s). Correct windows, wrong units, incomplete. |

So the "broken windows" issue is real, but the earlier diagnosis was only half
right: the *live* file isn't start/end pairs mislabeled as durations — those
are genuine (too-short) durations. It's **Christine's copy** that has end
times in the duration column. The two files have different problems.

## What's actually wrong, concretely

1. **Live file durations are too short for S01–S13.** S09–S13 at 2–3 s are
   essentially unusable; S01–S08 (5–88 s) are all under the 120 s minimum.
   Any trim/run produced from these rows for S01–S13 is invalid.

2. **STATUS overstates what's valid.** STATUS lists valid results as
   "S02–S07, S14–S18." But by the 120–300 s spec, S02 (20 s), S03 (20 s),
   S04 (74 s), S05 (51 s), S06 (77 s), S07 (88 s) are **all under target**.
   The only live rows that meet spec are **S14–S18**. STATUS should be
   corrected to "valid windows: S14–S18 only" until the rest are re-trimmed.

3. **Three conflicting files, no single source of truth.** The tooling reads
   only `data/scenario_windows.csv`; the other two are out-of-band drafts that
   were never merged back. They should be reconciled into the live file and
   then deleted.

4. **Start times also disagree** between the live file and Christine's copy
   for S01–S09 (e.g. S02 start 150 vs 125; S03 215 vs 195). This isn't a unit
   problem — they're different window choices and need a human decision.

5. **Doc inconsistency:** `SCENARIO_TRIMMING.md` names the approver as
   "Sabrina" (line ~128) and "Dr. Perry" (line ~199). Pick one name. (No git
   merge-conflict markers are present — earlier note about a conflict at
   lines 199–203 was inaccurate.)

## What's needed

A single, complete, spec-compliant `data/scenario_windows.csv`. I've built a
proposed reconciliation at **`data/scenario_windows.reconciled.csv`**:

- **S01, S10–S18** taken from `edited scenario windows.csv` (correct durations).
  S14–S18 already match the live file.
- **S02–S09** taken from Christine's copy, converting end → duration
  (`duration = col3 − start`), which yields a clean 120–130 s for each.

Once approved, that file becomes `data/scenario_windows.csv`, the two alternate
files are deleted, and **all of S01–S13 must be re-trimmed and re-run** (S14–S18
are unaffected).

### Needs a human decision before it's final (per the PR workflow, the approver signs off)

- **S01 start:** live=35, Christine/edited=0. Anchor is ~00:54; a 0→120 s
  window covers it. Proposed: `0,120`. Confirm.
- **S02–S09 starts:** proposal uses Christine's starts (they pair with her
  durations and anchor notes). Confirm these over the live file's starts.
- **Confirm the end-vs-duration reading** of Christine's file (the arithmetic
  is consistent across all nine rows, but worth a sanity check).
- **S12 = 300 s** (the 5-minute max) — confirm intentional.

## Suggested order of operations

1. Review `data/scenario_windows.reconciled.csv`; adjust the four items above.
2. Replace `data/scenario_windows.csv` with the approved reconciliation; delete
   `data/edited scenario windows.csv` (leave Christine's copy in `papers/` as
   her reference).
3. `python scripts/trim_scenarios.py` (dry run) → eyeball the plan → `--apply`.
4. `python scripts/scenario_quicklook.py` and confirm anchors are present.
5. Re-run baselines for S01–S13; correct STATUS to reflect real coverage.
6. Fix the Sabrina/Dr. Perry name in `SCENARIO_TRIMMING.md`.
