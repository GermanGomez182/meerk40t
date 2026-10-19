---
id: U07
title: Local material test notes
status: in-progress
depends_on: [U06]
requirements: [R5]
invariants: [I2, I4, I5]
---

## Intent

Deliver the first useful vertical slice of local material test notes for the accepted Mac/K40 roadmap.

## Scope

Implement the acceptance criteria using existing application capabilities and the shared conventions.

## Out of scope

New hardware protocols, automatic motion/start, remote storage, and unrelated UI rewrites.

## Acceptance criteria

- AC-U07-1: Given a K40 workspace, when material/test shortcuts are clicked, existing material-manager and test-pattern tools open without applying a preset or starting a job.
- AC-U07-2: Given fictional material, thickness, controller settings and observed result entered for a device, when explicitly saved, the local record persists and reloads for the same device; switching device does not expose another machine's record.
- AC-U07-3: Given invalid input or a filesystem failure, when saving, a visible actionable error appears, existing records remain readable, and unsaved entry text remains available.

## Test plan

Follow engineering/CONVENTIONS.md. Reproduce missing behavior first, cover positive and negative states, then run targeted GUI/core suites and the core verification command. Read-only independent review guards invariants.

