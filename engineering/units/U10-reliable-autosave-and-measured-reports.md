---
id: U10
title: Reliable autosave and measured reports
status: todo
depends_on: [U09]
requirements: [R8]
invariants: [I2, I4, I5]
---

## Intent

Deliver the first useful vertical slice of reliable autosave and measured reports for the accepted Mac/K40 roadmap.

## Scope

Implement the acceptance criteria using existing application capabilities and the shared conventions.

## Out of scope

New hardware protocols, automatic motion/start, remote storage, and unrelated UI rewrites.

## Acceptance criteria

- AC-U10-1: Given a dirty workspace whose autosave fails, when the autosave job runs, a visible error reports the failure and dirty state remains true so a later run can retry.
- AC-U10-2: Given a prior autosave and a failing replacement save, when autosaving, the prior contents remain intact at the normal autosave path until a replacement is ready, so startup recovery can still find them; successful saves clear dirty state only after completion.
- AC-U10-3: Given autosave disabled or a clean workspace, when the job runs, no save occurs; normal history retention remains bounded.
- AC-U10-4: Given a deterministic larger synthetic document, when new reports are profiled, timing and document size are recorded; optimizations are introduced only for a demonstrated issue and preserve report results.

## Test plan

Follow engineering/CONVENTIONS.md. Reproduce missing behavior first, cover positive and negative states, then run targeted GUI/core suites and the core verification command. Read-only independent review guards invariants.

