# Researcher Tasks Across All Weeks

Source of truth: `docs/schedules/PRIME_Schedule_new_revised.pdf`.

This checklist turns the schedule's researcher responsibilities into concrete actions Sabrina can track. It does not replace the schedule; it is the working checklist for repository coordination, setup, and weekly handoffs.

## Current Project Gate

The repository currently supports Week 1 orientation, setup checks, synthetic experiments, and BoT-SORT hook documentation. The group is not yet through the real-data experiment gate.

Before claiming full experimental completion, the researcher still needs to confirm:

- CityFlowV2 Scenario S01 path and storage layout.
- Official Python environment method: conda, as written in the schedule, or the repository's current `.venv` helper.
- PyTorch install target for each machine.
- Detector and FastReID weight paths.
- Clean BoT-SORT-ReID baseline run on CityFlowV2 S01.
- Metric extraction path for IDF1, HOTA, MOTA, and IDS.
- Rules for where large outputs and model weights live outside git.

## Week 1: Orientation And Research Landscape

Researcher tasks:

- Orient students to the PRIME mission, the 10-week arc, and the revised stack: BoT-SORT-ReID, CityFlowV2, and embedding-space attack.
- Explain why ByteTrack alone is insufficient: no ReID means no identity layer and no useful identity-layer attack surface.
- Demonstrate what a ReID embedding looks like by running OSNet on two crop images and printing cosine similarity.
- Download CityFlowV2 Scenario S01 directly from `aicitychallenge.org`.
- Confirm both students can clone BoT-SORT, create the agreed Python environment, and confirm Python/PyTorch install.

Researcher outputs to create or confirm:

- CityFlowV2 S01 local path note.
- OSNet/ReID demo command or notebook.
- Week 1 setup decision: conda versus `.venv`.
- Friday discussion prompts and paper presentation order.

Repository locations:

- Setup guidance: `docs/setup/`
- Week 1 brief: `docs/weekly-briefs/WEEK1_RESEARCHER_BRIEF.md`
- Student notes: `papers/christina/`, `papers/floyd/`

## Week 2: Threat Modeling And ReID Attack Surface

Researcher tasks:

- Walk students through the BoT-SORT-ReID codebase.
- Show exactly where OSNet extracts embeddings in the FastReID module.
- Demonstrate why pixel noise is not the intended attack layer.
- Demonstrate why embedding shift works by manually adding a small vector to an embedding and showing the cosine distance jump.
- Confirm CityFlowV2 access.
- If CityFlowV2 access is delayed, prepare the MOT17 multi-sequence fallback plan.

Researcher outputs to create or confirm:

- Code walkthrough notes identifying the embedding hook.
- Pixel-noise versus embedding-shift demo.
- CityFlowV2 access status or fallback decision.
- Threat-model review rubric for student diagrams.

Repository locations:

- BoT-SORT hook notes: `docs/botsort-integration/BOTSORT_INTEGRATION.md`
- Patch file: `patches/0001-Add-PRIME-ReID-poison-and-export-hooks.patch`
- Threat-model diagrams: `docs/` or `paper-draft/figures/` if created later.

## Week 3: Dataset Setup And Clean Baseline

Researcher tasks:

- Confirm the CityFlowV2 dataset directory structure is correct.
- Confirm the evaluation script runs without error.
- Confirm BoT-SORT-ReID runs on Scenario S01 clean data.
- Deepen the detection literature review, especially how existing papers detect compromised camera feeds.
- Begin drafting the problem formalization: define clean embedding distribution versus poisoned embedding distribution.

Researcher outputs to create or confirm:

- Clean baseline run log.
- Clean baseline metrics: IDF1, HOTA, MOTA, IDS.
- Embedding inspection acceptance criteria: shape, range, cosine sanity checks.
- Problem formalization notes.

Repository locations:

- Baseline protocol: `experiments/week03-baseline/`
- Baseline summaries: `results/week03/`
- Literature notes: `papers/shared-bibliography/`
- Draft formalization: `paper-draft/`

## Week 4: Embedding-Space Poisoning

Researcher tasks:

- Guide the poisoning hook implementation.
- Show students which feature extraction function call to intercept.
- Introduce targeted versus untargeted perturbation.
- Explain random shift versus shift toward the centroid of a different identity cluster.
- Begin drafting the formal threat model for the paper.

Researcher outputs to create or confirm:

- Poison hook review notes.
- Accepted poisoning settings: cameras c01/c02 and epsilon values 0.1, 0.5, 1.0.
- Clean versus poisoned comparison table requirements.
- Reproducibility fields: camera IDs, perturbation method, epsilon, seed, and command.

Repository locations:

- Poisoning protocol: `experiments/week04-poisoning/`
- Poisoning summaries: `results/week04/`
- BoT-SORT hook doc: `docs/botsort-integration/BOTSORT_INTEGRATION.md`

## Week 5: Midpoint Assessment

Researcher tasks:

- Complete the formal Week 5 rubric assessment for each student.
- Include scores and written narrative in every rubric domain.
- Write an updated research direction memo based on weeks 1-4.
- Schedule a one-on-one feedback session with each student after presentations.
- Lead the group toward one agreed paper contribution statement.

Researcher outputs to create or confirm:

- Christina midpoint rubric and narrative.
- Floyd midpoint rubric and narrative.
- Updated research direction memo.
- One-sentence paper contribution statement.
- Feedback meeting notes.

Repository locations:

- Rubric notes: `docs/weekly-briefs/` or a private researcher location if sensitive.
- Research direction memo: `paper-draft/` or `docs/weekly-briefs/`

## Week 6: Cross-Camera Embedding Consistency Detector

Researcher tasks:

- Survey detection literature more deeply.
- Identify 2-3 prior approaches to compare against.
- Draft the related work section outline for the paper.
- Review detector implementation for statistical correctness before week 7 scaling tests.

Researcher outputs to create or confirm:

- Related work outline.
- Detector correctness review.
- Comparison-method shortlist.
- Precision, recall, and F1 table acceptance criteria.
- Plot requirements for clean versus poisoned cosine distance distributions.

Repository locations:

- Detector protocol: `experiments/week06-detector/`
- Detector summaries: `results/week06/`
- Detector code: `src/prime_mtmc/`
- Paper notes: `paper-draft/`

## Week 7: Sustainability And Scalability Review

Researcher tasks:

- Review scalability findings.
- Determine whether the contribution is best framed as a method paper or benchmark paper.
- Lock the paper's core argument.
- Draft the abstract for group review.
- Confirm publication target list and check calls for papers/deadlines.

Researcher outputs to create or confirm:

- Scalability review notes.
- Failure-mode framing.
- Final contribution statement.
- Draft abstract.
- Publication target shortlist.

Repository locations:

- Scalability protocol: `experiments/week07-scalability/`
- Scalability summaries: `results/week07/`
- Draft abstract: `paper-draft/`

## Week 8: Literature Review And Introduction

Researcher tasks:

- Draft the paper introduction.
- Frame the problem, gap, contribution, and paper organization.
- Peer review both students' literature review drafts with written section-level feedback.
- Ensure the Week 7 contribution statement appears consistently in the introduction.

Researcher outputs to create or confirm:

- Introduction draft.
- Written feedback on Christina's literature review section.
- Written feedback on Floyd's literature review section.
- Remaining citation-gap assignments.

Repository locations:

- Literature notes: `papers/`
- Draft sections: `paper-draft/`

## Week 9: Methods, Results, And Contribution Framing

Researcher tasks:

- Synthesize all sections into one coherent full draft.
- Check argument consistency throughout the paper.
- Write or revise the abstract and conclusion.
- Ensure threat model and contribution framing are consistent from introduction through discussion.
- Lead the full-paper read-aloud review.

Researcher outputs to create or confirm:

- Complete rough draft with all sections present.
- Revised abstract.
- Revised conclusion.
- Week 10 revision plan with section ownership.

Repository locations:

- Full draft: `paper-draft/`
- Result summaries: `results/`

## Week 10: Revision, Venue Targeting, And Final Presentation

Researcher tasks:

- Identify 2-3 target venues, such as CVPR adversarial ML workshop, IEEE S&P workshop or main track, ECCV, USENIX Security, or ACM CCS depending on paper framing.
- Assign post-program revision tasks with owners and deadlines.
- Confirm each student's continued authorship role.
- Acknowledge each student's specific contribution to the paper and science.
- Ensure the final NDSU presentation tells the complete story.

Researcher outputs to create or confirm:

- Revised paper draft with all feedback incorporated.
- Final presentation deck.
- Venue shortlist with deadlines, format, and page limits.
- Post-program task assignment list.
- Authorship and contribution notes.

Repository locations:

- Final draft: `paper-draft/`
- Presentation materials: `docs/` or `paper-draft/`
- Venue notes: `paper-draft/`

## Standing Researcher Responsibilities

Every week:

- Confirm the weekly schedule goal.
- Open or update one GitHub issue for the week's work.
- Confirm which branches and folders are in scope.
- Review student pull requests before merge.
- Decide what becomes tracked project record.
- Keep raw data, model weights, and large outputs out of git.
- Maintain one current list of blockers.

Every experiment week:

- Confirm dataset path.
- Confirm camera/scenario list.
- Confirm exact command lines.
- Confirm output paths.
- Require a run log.
- Require a small summary suitable for `results/weekXX/`.

Every writing week:

- Confirm section ownership.
- Review argument consistency.
- Track citation gaps.
- Preserve the agreed contribution statement.
