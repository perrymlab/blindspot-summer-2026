# Week 1 Researcher Brief

Purpose: resolve the minimum decisions Sabrina Perry needs to make before students start environment setup and the first paper presentations.

## Week 1 Outcome

By the end of Week 1, the group should have:

- A plain-language explanation of the project stack: BoT-SORT-ReID, CityFlowV2, and embedding-space attack surface.
- A confirmed Week 1 setup target for each student machine.
- A confirmed CityFlowV2 S01 download/access plan.
- Two student paper presentations completed using the 6-point format.
- Two annotated bibliography entries completed, one per assigned seed paper.

## Questions For Sabrina

### 1. How should the project be explained in Week 1?

Decision needed:

- What is the short, student-facing explanation of the project before students know the full threat model?

Suggested default:

- "We are studying how multi-camera tracking systems use ReID embeddings to keep identities consistent across cameras, and why that embedding layer is a meaningful security surface."

Why this matters:

- Week 1 is about orientation and vocabulary, not locking the final paper direction.

### 2. What should students understand about ReID this week?

Decision needed:

- What explanation should Sabrina use for a ReID embedding?
- What should students be able to say by Friday?

Suggested default:

- A ReID embedding is a compact feature vector that represents the appearance of an object so detections can be compared across frames or cameras.
- Students should be able to explain why ByteTrack alone is not enough for this project: it does not provide the appearance-embedding layer needed for identity-layer questions.

Why this matters:

- This is directly tied to the Week 1 learning objective: understand what a ReID embedding is and why it matters for multi-camera tracking.

### 3. What terminology should be used in Week 1?

Decision needed:

- The schedule title says "poisoned frames," but the Week 1 stack introduces an embedding-space attack surface. What wording should students use now?

Suggested default:

- For Week 1, use "embedding-space attack surface" and "ReID embeddings."
- Do not require students to distinguish every attack variant yet; that belongs more naturally in Week 2.

### 4. Which BoT-SORT baseline is official for this project?

Decision needed:

- Should students use the local patched clone in `vendor/BoT-SORT`?
- Which object detector weights and FastReID weights should be used?
- CPU-only setup allowed, or GPU required?

Current repo state:

- BoT-SORT is cloned at `vendor/BoT-SORT`.
- PRIME patch branch: `prime-reid-poison-export`.
- Patch commit: `e9dafea0ad85f8bbfb6ad6e7626aa3e31a511285`.

Suggested default:

- Treat `vendor/BoT-SORT` branch `prime-reid-poison-export` as the official research fork for now.
- Sabrina should confirm whether Week 1 setup requires only cloning/import checks, or also downloading model weights.

### 5. What is the Week 1 dataset target?

Decision needed:

- Should students attempt CityFlowV2 S01 immediately?
- Who verifies access and storage layout?
- What is the fallback if setup slips?

Suggested default:

- Week 1 target: confirm CityFlowV2 S01 access and document expected path layout.
- Week 1 fallback: run only synthetic smoke tests and BoT-SORT import/setup checks.
- Do not introduce alternate datasets in Week 1 unless CityFlowV2 access is blocked.

### 6. What is the minimum Week 1 technical check?

Decision needed:

- What must be working before Week 1 is considered successful?

Suggested default:

- Students can run:

```bash
python scripts/smoke_test.py
```

- Students can explain where the BoT-SORT ReID hook is:

```text
vendor/BoT-SORT/fast_reid/fast_reid_interfece.py
FastReIDInterface.inference()
```

- Students can describe why ByteTrack alone is not enough for this project: it lacks the ReID appearance layer that creates the cross-camera identity attack surface.
- If model weights are not yet available, this can remain a code-location and environment check rather than a full tracker run.

### 7. What should Christina and Floyd each own this week?

Decision needed:

- Should ownership be split by literature topic, technical setup, or both?

Suggested default:

- Christina: Seed 1, poisoning survey vocabulary, and the question "what is data poisoning and why does it matter for vision?"
- Floyd: Seed 2, ByteTrack pipeline basics, and the question "how does ByteTrack work and what are MOTA and IDF1?"
- Both: run the agreed Week 1 setup check and write one paragraph explaining ReID embeddings.

## Week 1 Decisions Summary

This section restates the suggested defaults from the questions above so Sabrina can approve or edit them quickly. It does not add new Week 1 requirements.

1. Week 1 explanation, from Question 1: focus on multi-camera tracking, ReID embeddings, and why the identity layer matters.
2. Week 1 terminology, from Question 3: say "ReID embeddings" and "embedding-space attack surface"; defer detailed threat-model variants to Week 2.
3. Official fork for setup, from Question 4: `vendor/BoT-SORT`, branch `prime-reid-poison-export`.
4. Dataset target, from Question 5: confirm CityFlowV2 S01 access and expected path layout.
5. Week 1 success criteria, from Questions 2, 6, and 7: students understand ReID at a plain-language level, complete setup checks, and present the two seed papers.

## Friday Discussion Prompts From The Week 1 Scope

- What does ByteTrack track without ReID, and what does BoT-SORT add?
- What is data poisoning, what types exist, and why does it matter for vision?
- How does ByteTrack work, and what do MOTA and IDF1 measure?
- ByteTrack has no appearance embeddings. What does that mean for an identity-layer attack?
- What did each student find confusing in their assigned seed paper?

## Open Items After Week 1

- Confirm object detector and FastReID weights if not resolved during setup.
- Confirm CityFlowV2 S01 path and storage requirements.
- Prepare Week 2 threat-model discussion using BadNets and the MOT attack paper.
- Decide whether Sabrina wants a formal run log template before Week 3.
