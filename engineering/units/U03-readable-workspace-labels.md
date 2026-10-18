---
id: U03
title: Readable workspace labels
status: done
depends_on: []
requirements: [R1]
invariants: [I2, I6]
---

## Intent

Deliver the first useful vertical slice of readable workspace labels for the accepted Mac/K40 roadmap.

## Scope

Implement the acceptance criteria using existing application capabilities and the shared conventions.

## Out of scope

New hardware protocols, automatic motion/start, remote storage, and unrelated UI rewrites.

## Acceptance criteria

- AC-U03-1: Given light, dark, and mid-gray backgrounds, when a ruler label is rendered, its effective foreground is selected for at least 4.5:1 contrast where black or white can achieve it; the configured source color is retained if sufficient, and saved settings are not rewritten.
- AC-U03-2: Given Start/Pause/Stop button backgrounds, when theme properties are loaded under either appearance, the ordinary label colors remain readable against the actual button backgrounds; driver behavior is unchanged.
- AC-U03-3: Given RGBA values containing single-digit hex channels, when serialized, the result contains exactly eight hex digits and round-trips all channels.
- AC-U03-4: Given guides are disabled or a theme changes, when the guide renders/refreshes, existing visibility behavior remains and colors refresh without document mutation.
- AC-U03-5: Given a light bed panned beneath rulers on a dark outer canvas (or the inverse), when the actual scene layers and ruler labels are rasterized, a consistent backing surface makes the primary, secondary, and unit labels readable at their actual pixels, including trailing digits of long or negative labels. The backing is limited to the ruler bands and actual text footprints, disabled guides add no backing, and configured palette values remain intact.

## Test plan

Follow engineering/CONVENTIONS.md. Reproduce missing behavior first, cover positive and negative states, then run targeted GUI/core suites and the core verification command. Read-only independent review guards invariants.

