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

### U02 uv desktop setup — 2026-10-17

- Added an editable setuptools project for `uv run meerk40t`, a dependency lock,
  a tracked Python 3.13 selection, default desktop dependencies, and an optional
  development group. Legacy package metadata and the Python 3.6 requirement are
  retained; uv desktop/development groups require Python 3.8 or later.
- Updated source setup instructions and recorded proposed Mac/K40 improvements
  in [ROADMAP.md](ROADMAP.md).
- Verified the installed entry point imports this checkout in isolated Python
  mode; desktop imports, wheel build, 633 core tests, and 10 GUI tests passed.
- Packaging/configuration change: no artificial red-test commit. TDD role steps
  and spec-to-units do not apply; the existing unittest verification is reused.
- Fresh local clone of `c8d3e5e8c`: `uv sync --locked` installed 16 desktop
  packages; `uv run meerk40t --version`, isolated editable-source/import checks,
  and all 10 workspace tests passed. The clone remained clean afterward.
- Verification details: [U02 packaging evidence](engineering/evidence/U02-packaging.md).
