---
id: U09
title: Read-only design/import audit
status: in-progress
depends_on: [U08]
requirements: [R7]
invariants: [I1, I2, I7]
---

## Intent

Deliver the first useful vertical slice of read-only design/import audit for the accepted Mac/K40 roadmap.

## Scope

Implement the acceptance criteria using existing application capabilities and the shared conventions.

## Out of scope

New hardware protocols, automatic motion/start, remote storage, and unrelated UI rewrites.

## Acceptance criteria

- AC-U09-1: Given scene-space geometry and bed size, when an audit is requested, it reports design dimensions and elements whose bounds lie outside the bed; transformed geometry is respected.
- AC-U09-2: Given assigned/unassigned elements and exact duplicate vector geometry, when audited, counts and useful identifiers are reported while references, selection, geometry and undo history remain unchanged.
- AC-U09-3: Given empty or unsupported geometry, when audited, it reports an explicit limitation and keeps supported checks usable; no automatic scale, classify or delete action runs.

## Test plan

Follow engineering/CONVENTIONS.md. Reproduce missing behavior first, cover positive and negative states, then run targeted GUI/core suites and the core verification command. Read-only independent review guards invariants.

