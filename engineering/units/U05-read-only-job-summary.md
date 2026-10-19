---
id: U05
title: Read-only job summary
status: done
depends_on: [U04]
requirements: [R3]
invariants: [I1, I3, I7]
---

## Intent

Deliver the first useful vertical slice of read-only job summary for the accepted Mac/K40 roadmap.

## Scope

Implement the acceptance criteria using existing application capabilities and the shared conventions.

## Out of scope

New hardware protocols, automatic motion/start, remote storage, and unrelated UI rewrites.

## Acceptance criteria

- AC-U05-1: Given a document with ordered enabled/disabled operations, when the summary refreshes, rows preserve order and identify enabled state, operation name/type, speed with units, controller power setting, and effective passes.
- AC-U05-2: Given active device and geometry, when the summary refreshes, device label, bed dimensions, and scene-space design bounds are shown in millimeters; absent or invalid values appear as unavailable rather than zero or a crash.
- AC-U05-3: Given empty documents, references/effects, or utility operations lacking speed/power, when the report is built, it remains usable without fabricated values and does not mutate nodes, queue, or selection.

## Test plan

Follow engineering/CONVENTIONS.md. Reproduce missing behavior first, cover positive and negative states, then run targeted GUI/core suites and the core verification command. Read-only independent review guards invariants.

