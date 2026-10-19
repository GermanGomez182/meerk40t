# Mac and K40 workflow improvements

## Product contract

The existing desktop application remains the product. An opt-in K40 Workspace companion window groups the established tools and read-only reports. It opens through Tools → Tools → K40 Workspace or `window toggle K40Workspace`. The companion uses normal window geometry persistence. Existing main-window layouts remain intact.

## Requirements

- R1: Improve workspace ruler and action-label readability across appearances, retaining stored colors. Correct RGBA serialization so dark low-channel colors are valid.
- R2: Provide a focused K40 companion with clear access to existing laser controls, navigation, controller, operations, and preferences. Unsupported devices are clearly identified and K40-specific actions disabled.
- R3: Show active-device label, bed dimensions, operation order and enabled state, speed units, controller power setting, passes, and design bounds in a read-only refreshable job summary.
- R4: Display passive K40 connection/queue state and actionable diagnosis without opening USB or inferring physical position or tube output.
- R5: Offer existing material-manager and test-pattern tools plus local machine-scoped material test notes with visible save failures.
- R6: Explain origin, design bounds, and software-estimated duration beside access to existing preview and framing controls. No motion is triggered merely by opening a preview view.
- R7: Audit imported/current design dimensions, out-of-bed placement, unassigned elements, and exact duplicate vector geometry without automatically changing the document.
- R8: Preserve the dirty workspace and report autosave failures, retaining recoverable prior files. Profile the new reports on a synthetic larger document and record results before adding optimizations.

Material notes open in a separate managed Material Notes window from the
companion's Materials group. The window is bound to the device displayed when
opened, so switching the active device does not redirect an unsaved draft. Its
form has Material, Thickness (mm), Settings tried, and Observed result fields.
Records use a persisted device identifier alongside its service path, so deleting
and recreating a device at the same path does not inherit the deleted device's
observations. Material and result are required; thickness may be blank or a finite nonnegative
number. Saving records an observation locally and never applies machine settings.

## Invariants

- I1: Opening or refreshing reports never starts, homes, connects, fires, moves, or queues hardware work.
- I2: Existing settings, layouts, and document contents remain intact unless a named user action explicitly edits them.
- I3: Hardware observations, software queue state, and estimated position/time are labeled distinctly. Unknown values remain unknown.
- I4: User data stays local; no new network service, telemetry, or provider persistence is introduced.
- I5: Errors introduced or touched by the slice surface through a visible message or kernel channel. Failed persistence retains retryable state.
- I6: New GUI text is translatable; existing driver protocols and deliberate-start protections remain in place.
- I7: Each report is read-only and preserves operation order, references, selection, and undo history.

## Delivery scope

Each roadmap item receives a first useful vertical slice. Follow-up polish stays in the backlog; a first slice is not a claim that every possible UI or performance improvement is complete. Physical laser testing requires the actual device and is not replaced by mocked connection tests. U03 starts with ruler/action-label contrast; broader icon/handle redesign remains a follow-up unless empirical inspection identifies a concrete defect.

