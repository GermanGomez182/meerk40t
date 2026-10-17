---
id: U04
title: Focused K40 companion workspace
status: todo
depends_on: [U03]
requirements: [R2]
invariants: [I1, I2, I6]
---

## Intent

Deliver the first useful vertical slice of focused k40 companion workspace for the accepted Mac/K40 roadmap.

## Scope

Implement the acceptance criteria using existing application capabilities and the shared conventions.

## Out of scope

New hardware protocols, automatic motion/start, remote storage, and unrelated UI rewrites.

## Acceptance criteria

- AC-U04-1: Given GUI registration, when the user opens K40Workspace from Window or console, a managed window with normal geometry persistence exposes translated groups for machine tools, job review, materials, and document checks.
- AC-U04-2: Given an active Lihuiyu device, when a tool shortcut is clicked, the established controller/navigation/operation/preferences window or laser pane opens; opening/refreshing the companion sends no hardware command.
- AC-U04-3: Given a non-Lihuiyu device or a device switch, when the window refreshes, the active label and supported-device state update and K40-specific tools are disabled.
- AC-U04-4: Given a missing registered tool, when a shortcut is invoked, a visible useful message appears rather than an unknown command or silent failure.

## Test plan

Follow engineering/CONVENTIONS.md. Reproduce missing behavior first, cover positive and negative states, then run targeted GUI/core suites and the core verification command. Read-only independent review guards invariants.

