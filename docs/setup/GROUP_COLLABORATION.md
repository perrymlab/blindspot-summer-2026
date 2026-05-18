# Group Collaboration Plan

This document explains how the researcher and students should collaborate in this repository.

Source of truth: `docs/schedules/PRIME_Schedule_new_revised.pdf`. This collaboration plan supports that 10-week schedule.

## Roles

Researcher:

- Owns research direction, weekly priorities, dataset access, and final technical decisions.
- Reviews pull requests before they merge to `main`.
- Decides which results are strong enough for reports or papers.
- Owns GitHub repository administration, branch protection, collaborator permissions, and release/archive decisions.

Students:

- Work on separate branches.
- Keep paper notes, experiment logs, and small summaries in the right folders.
- Open pull requests for review instead of pushing directly to `main`.
- Do not commit large raw data or local environment files.

## GitHub Permissions

Recommended repository owner:

- Sabrina owns the GitHub organization/repository settings.
- Sabrina or a designated maintainer has admin rights.
- Students have write access only if branch protection is enabled.

Recommended branch protection for `main`:

- Require pull requests before merge.
- Require at least one review from Sabrina or the designated maintainer.
- Block force-pushes to `main`.
- Block direct pushes to `main`.
- Allow students to push to their own branches.

If branch protection is not enabled, students should be given lower permissions or asked to work from forks. The safest workflow is protected `main` plus student branches in the shared repo.

## Branch Rules

Use `main` as the stable shared branch.

Branch naming:

- `student/christina-<topic>`
- `student/floyd-<topic>`
- `research/<topic>`
- `docs/<topic>`

Each pull request should include:

- What changed.
- Why it changed.
- How it was tested.
- Any open questions.

## Weekly Rhythm

Monday:

- Researcher confirms the weekly goal from the schedule.
- Students create or update their branches.
- Researcher confirms which folders are in scope for the week.

Midweek:

- Students push early work.
- Researcher reviews direction before too much work accumulates.

Friday:

- Students submit notes, run logs, or result summaries.
- Students give the scheduled Friday presentation.
- Group decides what becomes part of the tracked project record.

## Independent Weekly Workflow

Researcher weekly workflow:

- Review the schedule goal for the week.
- Open or update one weekly coordination issue in GitHub.
- Confirm student assignments and expected deliverables.
- Confirm dataset, model weight, and compute access for any experiment week.
- Review pull requests and decide what merges to `main`.
- Write or update the weekly researcher note in `docs/weekly-briefs/` when direction changes.

Student weekly workflow:

- Pull the latest `main` at the start of the week.
- Create one branch for that week's assignment.
- Add paper notes, experiment logs, code, or summaries only in the assigned folders.
- Push progress before the midweek check-in.
- Open a pull request by the agreed deadline.
- Present the scheduled Friday work using the schedule format.

Group weekly workflow:

- Keep one shared list of open blockers.
- Use pull requests for reviewable work.
- Use issues or a shared notes file for questions that are not ready for code.
- Decide every Friday what should become permanent project record and what should stay local.

## Schedule Milestones

Week 1:

- ReID explanation, setup begins, CityFlowV2 S01 downloaded, first paper presentations.

Week 2:

- Threat model diagrams, BadNets/MOT attack discussion, BoT-SORT-ReID test clip.

Week 3:

- Clean CityFlowV2 S01 baseline with IDF1, HOTA, MOTA, and IDS logged.

Week 4:

- Two-camera embedding poisoning at epsilon values 0.1, 0.5, and 1.0, with clean-vs-poisoned comparison table.

Week 5:

- Midpoint presentations, researcher rubric assessment, contribution statement.

Week 6:

- Cross-camera embedding consistency detector with precision, recall, F1, and distribution plots.

Week 7:

- Scalability and boundary-condition tests across scenarios and poisoned-camera counts.

Weeks 8-10:

- Literature review, introduction, methods, results, full draft, final presentation, and publication plan.

## Folder Ownership

- `docs/`: shared project instructions, schedule notes, setup guidance.
- `papers/`: student literature work and bibliography.
- `experiments/`: protocols, commands, configs, and notes.
- `results/`: small summaries, tables, and final figures.
- `src/prime_mtmc/`: reusable project code.
- `scripts/`: command-line tools.
- `runs/`: local generated outputs; do not commit unless explicitly approved.
- `vendor/`: local external repositories; do not commit.

Recommended ownership:

- Sabrina owns `docs/`, final decisions in `experiments/`, and accepted summaries in `results/`.
- Christine owns `papers/christina/` and her assigned experiment notes.
- Floyd owns `papers/floyd/` and his assigned experiment notes.
- Both students may contribute to `papers/shared-bibliography/`.
- Shared code under `src/` and `scripts/` requires researcher review before merge.

## Collaboration Rules

- Pull before starting new work.
- Work on a branch, not directly on `main`.
- Keep commits focused.
- Put exact commands in experiment notes.
- Keep raw data, model weights, and large generated outputs outside git.
- Ask for review when a branch changes shared code, setup instructions, or reported results.

## Real-Data Experiment Handoff

Before a student runs real BoT-SORT experiments, the researcher should provide:

- Dataset path.
- Scenario and camera list.
- Detector weights path.
- FastReID weights path.
- CPU/GPU expectation.
- Output folder.
- Poisoning settings, if any.

The student should return:

- Exact command.
- Run log.
- Output path.
- Any errors or warnings.
- Small summary file in `results/weekXX/` if approved.

## Current Project Gate

The group is currently before the real-data experiment gate. The synthetic package and BoT-SORT patch documentation exist, but the group still needs dataset access, model weights, and a confirmed CityFlowV2 baseline run before claiming full experimental completion.
