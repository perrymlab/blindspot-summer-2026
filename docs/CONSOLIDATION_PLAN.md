# Documentation Remediation Plan

**Rewritten:** 2026-06-19 (replaces the stale 2026-06-13 version, whose Priority 1
was already done and which referenced files that no longer exist).
**Updated 2026-06-21:** P0/P1/P2/P4 done; P3 partly done (week READMEs refreshed,
`run_manifest.csv` copy still pod-side). The remaining `Sabrina` rename leftovers
(`README.md`, `week03-baseline/RUNBOOK.md`) and `START_HERE.md`/week-README state
drift from the 2026-06-20 milestone were all fixed in the same pass.

**The problem (mostly resolved):** the repo had ~30 docs with overlapping scope, an
incomplete `Sabrina → Dr. Perry` rename, dead cross-links, an unresolved merge
conflict, and no single source of truth — so the same question ("what's done? where
do I start?") had several conflicting answers.

**The fix is one rule, applied everywhere:**

> **Live state lives in exactly one file (`STATUS.md`). Every audience has exactly
> one entry point. Everything else is reference and links to those — it never
> restates progress.**

---

## Target information architecture

| Audience | Single entry point | Holds |
| --- | --- | --- |
| **Student** | `docs/START_HERE.md` | setup → which CSVs to use → first analysis |
| **Researcher (Dr. Perry)** | `docs/setup/PERRY_QUICKSTART.md` | env, daily git, running the pipeline |
| **AI agent / new machine** | `docs/AGENT_HANDOFF.md` | pick up the repo cold |
| **Everyone, for status** | `docs/STATUS.md` | the *only* place for progress + TODOs |
| **Index / map** | `docs/README.md` | links only, no state |

Reference docs (setup, data, botsort-integration, templates) are linked from the
entry points and must not duplicate state or each other.

---

## P0 — Contradictions (fix immediately)

- [x] `docs/README.md` linked dead `SABRINA_QUICKSTART.md` / `SABRINA_PR_REVIEW.md`
      → repointed to `PERRY_QUICKSTART.md` (2026-06-19).
- [x] **Merge conflict** in `docs/data/SCENARIO_TRIMMING.md` L199–203
      (`Sabrina` vs `Dr. Perry`) — resolved to the Dr. Perry line as part of P1
      (no conflict markers remain anywhere; verified 2026-06-21).
- [x] This file no longer references the deleted `LOCAL_STUDENT_HANDOFF.md`.

## P1 — Naming: `Sabrina → Dr. Perry` — ✅ done (2026-06-19)

Confirmed same person — full name **Dr. Sabrina Perry** (Sabrina = first name,
Perry = surname; org `perrymlab`). Global-replaced `Sabrina → Dr. Perry` across all
docs, retitled `PERRY_QUICKSTART.md` ("Sabrina Quickstart" → "Dr. Perry Quickstart"),
fixed the two spots where the old text was already "Dr. Sabrina Perry" / "Sabrina
Perry" (avoided "Dr. Dr. Perry Perry"), and resolved the SCENARIO_TRIMMING.md merge
conflict to the Dr. Perry line. This file intentionally still says "Sabrina" because
it documents the rename.

## P2 — Collapse overlapping entry points — partly done (2026-06-19)

- Keep the four entry points in the table above; demote everything else to reference.
- `docs/experiments/STUDENT_EMBEDDING_ANALYSIS.md`: **keep** — it is the detailed
  analysis walkthrough that `START_HERE.md` links to (the old plan wrongly called it
  a duplicate). Strip any lines that restate run status.
- [x] Archived to `docs/setup/archive/` (with an "ARCHIVED" header, dropped from the
  README index): `IMPLEMENTATION.md` (outdated snapshot) and `workflow_full_test.md`
  (a GitHub-workflow test, not research).
- [x] **Decided — `docs/setup/GPU_CLOUD_FULL_TEST.md`:** kept as a self-contained
  test/runbook (option b); the two dead links (`RESEARCHER_SETUP.md`,
  `SABRINA_QUICKSTART.md`) were repointed to `PERRY_QUICKSTART.md` (2026-06-21). The
  larger fold-in into `PERRY_QUICKSTART.md` + `BOTSORT_GPU_RUNBOOK.md` (option a) is
  deferred — revisit only if the three runbooks start to drift.

## P3 — Week tracking — partly done (2026-06-21)

The tsize-1536 re-export is complete, so the week READMEs were refreshed:
- [x] `results/week03–07/README.md` updated (2026-06-21): removed the resolved
  "S01/S08–S13 broken trim windows" claims, recorded the `tsize 640 → 1536`
  re-export split in the run-log tables, marked the annotation/join as done for the
  14 usable scenarios, and remapped stale STATUS TODO cross-references to the current
  numbering.
- [ ] **Still pending — `run_manifest.csv`:** lives on the pod (gitignored under
  `runs/`), so the `results/weekXX/` copy + commit can only happen from the pod
  (STATUS TODO #7). The REPORT.md provenance stays orphaned until then.

## P4 — Researcher steps that block students — ✅ done (2026-06-20)

All five blocking steps are complete; students can now run real `track_id`
analysis (published as GitHub Release `exports-2026-06-20`):

1. [x] **Clean re-export @1536** — done (6-worker parallel, `reexport_parallel.sh`).
2. [x] **Poisoned re-export @1536** (eps 0.5) — done (`poison_parallel.sh`; S10 skipped).
3. [x] **Merge → `*_all-cams.csv`** — automatic in `run_baselines.py`.
4. [x] **Publish** clean+poison `*_all-cams.csv` (gzipped) + bumped `START_HERE.md`.
5. [x] **Re-join annotations** → `*_tracked.csv` for the 14 usable scenarios (IoU 0.2,
   mean coverage ~0.45); the old "gated on S07/S14/S15 annotation" framing is obsolete
   (annotations exist for all 18, joins published for 14).

LFS/Release budget (STATUS TODO #8) was settled in the process: distribution is via
**gzipped Release assets, not LFS** (28 `*_all-cams.csv.gz` + 28 `*_tracked.csv.gz`,
56 assets / ~5.7 GB).

---

## Order of operations — ✅ executed (P3 manifest copy is the only remainder)

1. **P4** (unblocked students) — ✅ done 2026-06-20 (Release `exports-2026-06-20`).
2. **P1 rename + SCENARIO_TRIMMING conflict** — ✅ done (final leftovers cleared 2026-06-21).
3. **P0/P2/P3 doc edits** — ✅ done 2026-06-21, except the pod-side `run_manifest.csv`
   copy into `results/weekXX/` (P3; needs the pod).

**Only open item:** commit `run_manifest.csv` from the pod (STATUS TODO #7). When
that lands, this plan can be archived.
