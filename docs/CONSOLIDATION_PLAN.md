# Documentation Remediation Plan

**Rewritten:** 2026-06-19 (replaces the stale 2026-06-13 version, whose Priority 1
was already done and which referenced files that no longer exist).

**The problem:** the repo has ~30 docs with overlapping scope, an incomplete
`Sabrina → Dr. Perry` rename, dead cross-links, an unresolved merge conflict, and
no single source of truth — so the same question ("what's done? where do I start?")
has several conflicting answers.

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
- [ ] **Merge conflict** in `docs/data/SCENARIO_TRIMMING.md` L199–203
      (`Sabrina` vs `Dr. Perry`) — resolve as part of P1.
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
- [ ] **Decision needed — `docs/setup/GPU_CLOUD_FULL_TEST.md`:** NOT archived — it is a
  current, self-contained GPU-cloud runbook, but it overlaps `PERRY_QUICKSTART.md` +
  `BOTSORT_GPU_RUNBOOK.md` and links to a **non-existent `RESEARCHER_SETUP.md`**.
  Pick one: (a) promote it to *the* researcher runbook and fold the other two into it,
  or (b) keep it as a test plan and fix/remove the dead link. Currently untracked.

## P3 — Week tracking — deferred until re-export completes

`results/week03…07/README.md` already have content (not empty, as the old plan
claimed). Do **not** rewrite them now: the tsize-1536 re-export (TODO #1) is
regenerating all run data, so any table written now is immediately stale. After the
re-export + new `run_manifest.csv`:
- Copy the manifest into the relevant `results/weekXX/` and commit (it's gitignored
  under `runs/`, so the REPORT.md is currently orphaned).
- Add a row noting the `tsize 640 → 1536` re-export so the pre/post-fix CSV split is
  traceable.

## P4 — Researcher steps that block students (tracked in STATUS.md TODO #1)

The doc cleanup is cosmetic next to this. Students cannot analyze embeddings until
the **correct** (tsize-1536) exports exist and are published:

1. **Clean re-export @1536** — in progress (tmux `reexport` on the pod).
2. **Poisoned re-export @1536** (eps 0.5, to match) — pending; run after clean.
3. **Merge → `*_all-cams.csv`** — automatic in `run_baselines.py`.
4. **Publish** the new clean+poison `*_all-cams.csv` and bump the "use these files"
   note in `START_HERE.md` (the published CSVs predate the fix).
5. **Re-join annotations** → `*_tracked.csv` for annotated scenarios (the existing
   joins are now 640-stale); real metrics still gated on S07/S14/S15 annotation.

Caveat surfaced by the re-export: tsize-1536 CSVs are ~2× larger (S01/c01 clean went
62 MB-merged → 107 MB single-cam). Revisit the LFS/Release budget (STATUS TODO #8)
before publishing.

---

## Order of operations

1. **P4** (unblocks students — highest value; compute already running).
2. **P1 decision** → then execute P1 rename + the SCENARIO_TRIMMING conflict.
3. **P0/P2/P3** doc edits (a couple of hours of editing, no compute).
