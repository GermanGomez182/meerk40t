---
id: U06
title: Passive connection diagnosis
status: done
depends_on: [U05]
requirements: [R4]
invariants: [I1, I3, I5]
---

## Intent

Deliver the first useful vertical slice of passive connection diagnosis for the accepted Mac/K40 roadmap.

## Scope

Implement the acceptance criteria using existing application capabilities and the shared conventions.

## Out of scope

New hardware protocols, automatic motion/start, remote storage, and unrelated UI rewrites.

## Acceptance criteria

- AC-U06-1: Given disconnected/connected/mock/network Lihuiyu services, when status refreshes, transport and passive connection state are accurately labeled without opening or probing hardware.
- AC-U06-2: Given paused or queued software state, when diagnosis refreshes, it reports pause and queue size without claiming physical position or completion; unknown states remain explicitly unknown.
- AC-U06-3: Given a connection error or inaccessible status property, when diagnosis refreshes, the user sees the error plus a relevant next step and the report remains available.

## Test plan

Follow engineering/CONVENTIONS.md. Reproduce missing behavior first, cover positive and negative states, then run targeted GUI/core suites and the core verification command. Read-only independent review guards invariants.

