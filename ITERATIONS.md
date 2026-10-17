# Iteration log

Date: 2026-10-17

### U01 macOS workspace readability

- Shipped: AC-U01-1 uses the existing bright workspace palette on macOS dark appearance, preserves saved choices, and leaves other platforms unchanged; AC-U01-2 restores the bright palette on macOS and for an explicit brighter reset while preserving other platforms' dark reset; AC-U01-3 dispatches reset and refresh when the brighter preference is enabled.
- Commits: red `7062274c2` → green `ce90466c6`.
- Review: round 1 PASS; 0 findings (0 fixed, 0 rejected, 0 deferred).
- Overrides: none.
- Deferred: none.

The change preserves existing color preferences. Users can choose Preferences > Colors > Reset Colors to brighter defaults for dark appearance or Reset Colors to Default for light appearance; this replaces custom colors. Native controls continue to follow macOS. No hardware behavior changed. A rendered-workspace desktop smoke check remains outstanding.

Backlog: visual feedback on Mac; K40-specific layout and workflow improvements after user input.

Spec-to-units was skipped because this is a single-slice change; verify-gate was skipped because the repository's existing unittest command was reused.
