# Week 07 Scalability Runbook

Source of truth: `docs/schedules/PRIME_Schedule_new_revised.pdf`.

Goal: test whether the detector generalizes across scenarios, perturbation types, and poisoned-camera counts.

## Required Conditions

- Week 6 detector pipeline works on S01.
- CityFlowV2 S02 and S03 paths are confirmed.
- Clean baseline and poisoned outputs can be generated for each scenario.

## Experiment Matrix

Scenarios:

- S01
- S02
- S03

Poisoned-camera counts:

- 1 camera
- 2 cameras
- 3 cameras
- N-1 cameras for each scenario

Perturbation types:

- Random shift
- Targeted shift toward a selected identity cluster, if target identity selection is ready

## Researcher Prerequisites

- Confirm which cameras are used in each scenario.
- Confirm target identity or cluster selection rule for targeted perturbation.
- Confirm whether the contribution is being framed as a method paper or a benchmark paper.
- Confirm failure-mode analysis format.

## Required Summary

```text
Scenario,Poisoned camera count,Poisoned cameras,Perturbation type,Epsilon,Precision,Recall,F1,IDF1,HOTA,MOTA,IDS,Failure notes
```
