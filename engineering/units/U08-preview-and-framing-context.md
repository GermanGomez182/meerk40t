---
id: U08
title: Preview and framing context
status: done
depends_on: [U07]
requirements: [R6]
invariants: [I1, I3, I7]
---

## Intent

Deliver the first useful vertical slice of preview and framing context for the accepted Mac/K40 roadmap.

## Scope

Implement the acceptance criteria using existing application capabilities and the shared conventions.

The passive report identifies scene origin (0, 0 mm), configured device home
corner when available, and scene-space design bounds. Operation durations reuse
the existing `time_estimate()` result for enabled operations and are explicitly
software estimates; missing or invalid estimates remain unavailable. Framing
access opens the existing laser-controls pane without executing an outline.
An explicit Simulation button prepares a free plan with the existing
`clear copy preprocess validate blob finish` pipeline, then opens Simulation;
it does not spool the plan. Missing planner or window support is reported inline.

## Out of scope

New hardware protocols, automatic motion/start, remote storage, and unrelated UI rewrites.

## Acceptance criteria

- AC-U08-1: Given design/device context, when preview information refreshes, it shows scene-space origin/bounds and explicitly labels available operation time as an estimate, never actual runtime.
- AC-U08-2: Given a preview shortcut, when clicked, the existing simulation preparation opens for the document without spooling or sending framing/motion commands.
- AC-U08-3: Given missing geometry or unknown estimates, when reviewing, the user sees an explicit empty/unavailable state and can access existing framing controls without automatic movement.

## Test plan

Follow engineering/CONVENTIONS.md. Reproduce missing behavior first, cover positive and negative states, then run targeted GUI/core suites and the core verification command. Read-only independent review guards invariants.

