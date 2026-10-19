# Iteration log

Date: 2026-10-17

## Accepted roadmap units

The accepted scope is defined in [engineering/PRODUCT.md](engineering/PRODUCT.md).
The existing application and uv workflow provide the walking skeleton and core
verify command; no new bootstrap unit or verify-gate is needed.

| Unit | Title | Depends on | Status |
| --- | --- | --- | --- |
| U03 | Readable workspace labels | U02 | done |
| U04 | Focused K40 companion workspace | U03 | done |
| U05 | Read-only job summary | U04 | done |
| U06 | Passive connection diagnosis | U05 | todo |
| U07 | Local material test notes | U06 | todo |
| U08 | Preview and framing context | U07 | todo |
| U09 | Read-only design/import audit | U08 | todo |
| U10 | Reliable autosave and measured reports | U09 | todo |

## Iteration log

### Paused for a lower-token workflow — 2026-10-18

Resume from [HANDOFF.md](HANDOFF.md) in a new session. U05 passed final review;
its unit record is pending. U06, U07, U08 and U10 have prepared red-test drafts;
U09 remains spec-only. Product implementation is paused. The workflow source in
agent-config was updated for fresh contexts and one active unit at a time.

### U01 macOS workspace readability

- Shipped: AC-U01-1 uses the existing bright workspace palette on macOS dark appearance, preserves saved choices, and leaves other platforms unchanged; AC-U01-2 restores the bright palette on macOS and for an explicit brighter reset while preserving other platforms' dark reset; AC-U01-3 dispatches reset and refresh when the brighter preference is enabled.
- Commits: red `7062274c2` → green `ce90466c6`.
- Review: round 1 PASS; 0 findings (0 fixed, 0 rejected, 0 deferred).
- Overrides: none.
- Deferred: none.

The change preserves existing color preferences. Users can choose Preferences > Colors > Reset Colors to brighter defaults for dark appearance or Reset Colors to Default for light appearance; this replaces custom colors. Native controls continue to follow macOS. No hardware behavior changed. A rendered-workspace desktop smoke check remains outstanding.

Backlog: visual feedback on Mac; K40-specific layout and workflow improvements after user input.

Spec-to-units was skipped because this is a single-slice change; verify-gate was skipped because the repository's existing unittest command was reused.

### U03 Readable workspace labels — 2026-10-18

- Shipped: AC-U03-1 through AC-U03-4 retain readable foreground selection, palette preservation, action-label contrast, RGBA round-tripping, and guide refresh/visibility behavior.
- Shipped: AC-U03-5 rasterizes ruler labels over mixed bed/canvas colors with backing confined to ruler bands and text footprints, including long and negative labels.
- Commits: red `6f3dbe98d` → green `4e0cd9fe5` → test `ebaea12c0` → test `45d503b38` → test `d9cb4c20a` → fix `df7419aac`.
- Review: round 1 CHANGES_REQUIRED → round 2 PASS; 1 finding (1 fixed, 0 rejected, 0 deferred).
- Overrides: corrected only the new raster fixture's wx text coordinates and sample regions; thresholds and invariants were unchanged.
- Deferred: icon, selection-handle, and toolbar-label polish remains a roadmap follow-up; no remaining U03-scope findings.
- Verification: final orchestration run passed 633 core tests and 21 GUI tests; independent review passed 633 core tests and 11 readability GUI tests. No new visible text was added, so translation checks were not applicable.

### U04 Focused K40 companion workspace — 2026-10-18

- Shipped: AC-U04-1 adds a managed K40 workspace available from Tools → Tools → K40 Workspace or the `window toggle K40Workspace` console command, with saved geometry and translated groups.
- Shipped: AC-U04-2 provides shortcuts to eight existing tools and panes without sending hardware commands during open or refresh; AC-U04-3 updates supported-device state on device changes; AC-U04-4 reports missing tools visibly.
- Commits: red `3e6b149ac` → test `c20bea607` → feat `0c49d837b`.
- Review: round 1 PASS; 1 finding (1 fixed, 0 rejected, 0 deferred).
- Overrides: corrected the test fixture to register Themes as a kernel service so child contexts receive it; behavior assertions were unchanged.
- Deferred: connection diagnosis, job summary, material notes, and other later roadmap capabilities remain future units; no remaining U04 findings.
- Verification: final orchestration run passed 633 core tests and 32 GUI tests; independent review passed 633 core tests and 11 K40 workspace GUI tests, including device-switch, listener-removal, and small-window scrolling checks. `uv run --locked --with polib --with chardet python translate_check.py de` exited 0; no locale edits were made and English fallback remains.

### U05 Read-only job summary — 2026-10-18

- Shipped: AC-U05-1 preserves operation order/state and reports operation details and effective passes; tests: `test_ac_u05_1_ordered_operation_rows_show_state_type_settings_and_units`, `test_ac_u05_1_passes_follow_effective_operation_setting`, `test_ac_u05_1_fractional_string_pass_count_is_unavailable`.
- Shipped: AC-U05-2 reports device, bed, and design bounds in millimeters with unavailable values for invalid data; tests: `test_ac_u05_2_device_bed_and_transformed_design_bounds_are_in_mm`, `test_ac_u05_2_missing_device_dimensions_and_empty_bounds_are_unavailable`, `test_ac_u05_2_invalid_geometry_width_keeps_refreshed_summary_usable`.
- Shipped: AC-U05-3 keeps empty, reference/effect, and utility-operation reports usable and read-only; tests: `test_ac_u05_3_empty_document_has_an_explicit_empty_operations_report`, `test_ac_u05_3_effect_references_and_utility_rows_do_not_fabricate_settings`, `test_ac_u05_3_opening_and_refresh_preserve_document_queue_and_selection`.
- Commits: red `01ac49c97` → green `28a662982` → test `71d63381c` → fix `cb238f64f`; branch documentation commits: docs `4d4e5c17c`, docs `fd88cb294`.
- Review: round 1 CHANGES_REQUIRED → round 2 PASS; 2 findings (2 fixed, 0 rejected, 0 deferred).
- Overrides: none.
- Deferred: none.
- Verification: 633 core tests and 46 combined GUI tests passed in the fresh verification run; runtime Ruff with Python 3.7 target and translation check passed, as recorded in U05 review evidence.

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
