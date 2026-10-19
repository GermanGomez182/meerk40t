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
| U06 | Passive connection diagnosis | U05 | done |
| U07 | Local material test notes | U06 | done |
| U08 | Preview and framing context | U07 | done |
| U09 | Read-only design/import audit | U08 | in-progress |
| U10 | Reliable autosave and measured reports | U09 | todo |

## Iteration log

### Workflow pause — 2026-10-18

Historical note: work paused to update the workflow source in agent-config and
resume with fresh contexts. Current progress and next steps are recorded in
[HANDOFF.md](HANDOFF.md).

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

### U06 Passive connection diagnosis — 2026-10-18

- Shipped: AC-U06-1 passively reports transport and connection state; tests: `test_ac_u06_1_unopened_usb_is_disconnected_without_probe`, `test_ac_u06_1_closed_usb_handle_is_disconnected_without_probe`, `test_ac_u06_1_open_usb_handle_reports_local_connected_state`, `test_ac_u06_1_mock_mode_does_not_read_hardware_connection_getter`, `test_ac_u06_1_network_socket_presence_is_unverified`, `test_ac_u06_1_network_transport_takes_precedence_over_mock_mode`.
- Shipped: AC-U06-2 reports software pause and queue while leaving physical progress unknown; tests: `test_ac_u06_2_software_pause_and_queue_do_not_claim_physical_progress`, `test_ac_u06_2_missing_controller_state_remains_unknown`, `test_ac_u06_2_driver_pause_is_reported_when_controller_is_idle`, `test_ac_u06_2_missing_software_queue_remains_unknown`.
- Shipped: AC-U06-3 keeps diagnosis available with actionable connection/status errors and generic tools; tests: `test_ac_u06_3_connection_errors_show_count_and_relevant_next_step`, `test_ac_u06_3_inaccessible_status_shows_error_and_keeps_report_available`, `test_ac_u06_3_switch_to_unsupported_device_drops_previous_diagnosis`, `test_ac_u06_3_no_active_device_keeps_generic_tools_available`.
- Commits: red `444a04de6` → green `41e83a724` → regression red `564077da2` → fix `c9d42a83a`.
- Review: round 1 CHANGES_REQUIRED → round 2 PASS; 2 findings (2 fixed, 0 rejected, 0 deferred).
- Overrides: none.
- Deferred: none.
- Verification: final orchestration passed 633 core tests (43.954s), 60 GUI tests (0.946s), and Ruff with Python 3.7 target; translation check exited 0 with English fallback and no locale changes. Independent review passed 633 core tests (45.057s), 39 focused GUI tests, and Ruff with Python 3.7 target. Evidence: [U06 review](engineering/evidence/U06-review.md).

### U07 Local material test notes — 2026-10-19

- Shipped: AC-U07-1 opens existing material/test shortcuts and a managed notes window; tests: `test_ac_u07_1_material_notes_shortcut_opens_registered_managed_window`.
- Shipped: AC-U07-2 persists notes in explicit local WORKDIR/material-notes JSON, bound to the opening device path and persisted identifier read directly from settings; tests: `test_ac_u07_2_explicit_save_reloads_observation_without_applying_settings`, `test_ac_u07_2_reused_service_path_does_not_expose_deleted_machine_notes`, `test_ac_u07_2_duplicate_reusing_deleted_path_keeps_machine_notes_isolated`, `test_ac_u07_2_machine_identity_isolates_notes_even_with_same_label`, `test_ac_u07_2_device_switch_keeps_draft_bound_to_opening_machine`.
- Shipped: AC-U07-3 validates required fields and blank or finite nonnegative thickness, retains drafts and existing records on errors, retries atomic replacement, and protects corrupt/unreadable stores; tests: `test_ac_u07_3_invalid_required_or_thickness_input_keeps_existing_records`, `test_ac_u07_3_blank_zero_and_fractional_thickness_are_valid`, `test_ac_u07_3_write_failure_preserves_draft_existing_notes_and_retry`, `test_ac_u07_3_replace_failure_preserves_records_draft_and_retry`, `test_ac_u07_3_corrupt_store_is_reported_and_not_overwritten`, `test_ac_u07_3_unreadable_store_is_reported_and_not_overwritten`.
- Commits: red `b237c6e4f` → green `cc7de39d2` → regression `fe578a3b3` → fix `7c0d6e158` → regression `1b1a3f88d` → fix `dd0e57a31`.
- Review: round 1 CHANGES_REQUIRED → round 2 PASS; 2 findings (2 fixed, 0 rejected, 0 deferred). Evidence: [U07 review](engineering/evidence/U07-review.md).
- Overrides: restart fixture round-trips temporary real settings instead of recreating the ignore-settings fixture; original assertions preserved, justified by the persisted identity contract.
- Deferred: first-session crash before identifier configuration save can orphan local notes requiring manual recovery; this limitation is documented. No remaining review findings.
- Verification: final orchestration passed 633 core tests (48.102s), 72 combined GUI tests (1.290s), Ruff (Python 3.7 target), and translation check with English fallback/no locale edits. Independent review passed 23 focused GUI tests (0.847s), Ruff, and lifecycle probes.
- Publish checkpoint: `dd0e57a31` plus this record, ready for the authorized fork publication.

### U08 Preview and framing context — 2026-10-19

- Shipped: AC-U08-1 reports scene origin (0, 0 mm), configured home corner, transformed design bounds, and software duration summed only from enabled operation estimates; unknown or invalid enabled estimates make the total unavailable. Tests: `test_ac_u08_1_preview_explains_scene_origin_home_corner_and_design_bounds`, `test_ac_u08_1_duration_sums_enabled_real_operation_estimates_only`, `test_ac_u08_1_refresh_recomputes_estimate_without_document_or_queue_edits`, `test_ac_u08_1_disabled_unknown_estimate_does_not_poison_total`, `test_ac_u08_1_real_raster_estimate_preserves_references_and_selection`, `test_ac_u08_1_missing_configured_home_remains_unavailable`, `test_ac_u08_3_missing_or_malformed_operation_estimate_is_unavailable`, `test_ac_u08_3_one_unknown_enabled_estimate_prevents_a_partial_total`, `test_ac_u08_3_estimator_arithmetic_error_is_visible_and_preserves_document`.
- Shipped: AC-U08-2 prepares an explicit simulation through the existing free-plan pipeline and opens only after completion; missing planner/window support and validation failure remain visible without spooling or hardware commands. Tests: `test_ac_u08_2_simulation_uses_free_plan_preparation_and_never_spools`, `test_ac_u08_2_missing_planner_shows_inline_error_without_commands`, `test_ac_u08_2_missing_simulation_window_does_not_prepare_a_plan`, `test_ac_u08_2_real_pipeline_finishes_cutcode_before_simulation_opens`, `test_ac_u08_2_validation_failure_does_not_open_simulation`.
- Shipped: AC-U08-3 reports empty/unknown states and opens existing framing controls only; missing framing errors scroll into view. Tests: `test_ac_u08_3_empty_document_reports_unavailable_bounds_and_estimate`, `test_ac_u08_3_framing_shortcut_only_opens_existing_laser_controls`, `test_ac_u08_3_missing_framing_pane_shows_inline_error_without_commands`, `test_ac_u08_3_missing_framing_pane_error_is_readable_after_scrolling`.
- Commits: red `c4b1dce9f` → green `4e9a92f6c` → test `2d3b0e285` → fix `d34b181c9`.
- Review: round 1 CHANGES_REQUIRED → round 2 PASS; 1 finding (1 fixed, 0 rejected, 0 deferred). Evidence: [U08 review](engineering/evidence/U08-review.md).
- Overrides: none.
- Deferred: none. Next U09 is a read-only design/import audit, spec-only.
- Verification: orchestration passed 633 core tests (44.342s), 90 combined GUI tests (1.947s), Ruff for Python 3.7, diff checks, and translation check (exit 0; English fallback, no locale edits). Independent review passed 633 core tests (44.252s) in round one, then 29 focused GUI tests (0.962s), Ruff, whitespace checks, and viewport probe (error moved to y=12 with no commands) in round two. Final post-review reruns passed 633 core tests (44.424s) and 29 focused GUI tests (1.025s).

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
