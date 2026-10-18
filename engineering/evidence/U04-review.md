# U04 review evidence

## Test-fixture correction

Override: register Themes as a kernel service in the test fixture, matching
gui/plugin.py. The initial fixture assigned it directly on the root context,
which did not provide themes to the managed window's child context. Once the
new window was registered, this caused fixture errors before panel construction.
The shortcut, device-state, error, translation, and geometry assertions are
unchanged. An existing MWindow construction control now verifies the fixture's
service propagation independently of the new window.

## Round 1: 2026-10-18, reviewed `0c49d837b`

```text
VERDICT: PASS
ROUND: 1
VERIFY: PASS (independent runs: 633 core tests in 46.516s; 11 K40 workspace GUI tests)
TEST INTEGRITY: changed: testgui/test_gui_k40workspace.py since 3e6b149ac. Correction c20bea607 registers Themes through the production service mechanism and adds an existing-window control; justified in the commit and override log. Behavior assertions unchanged.
AC COVERAGE:
  AC-U04-1: ok
  AC-U04-2: ok
  AC-U04-3: ok
  AC-U04-4: ok
INVARIANTS:
  I1: guarded at meerk40t/gui/k40workspace.py:73 and :87; opening/refreshing reads state, and explicit shortcuts dispatch established UI commands
  I2: guarded at meerk40t/gui/k40workspace.py:114; existing MWindow geometry handling is reused without modifying document contents or main-window layout
  I6: guarded at meerk40t/gui/k40workspace.py:25 and :87; visible strings are translated, and driver/start behavior is unchanged
FINDINGS:
- [OPTIONAL] README.md:94: The documented menu name differs from the actual menu. Scenario: follow “Window menu” to find the companion → its registered location is Tools → Tools → K40 Workspace, because wxmmain.py:3951 creates the top-level Tools menu and k40workspace.py:123 selects its Tools submenu. Document the actual path.
WOULD NOT TRUST: nothing beyond the above. Independent GUI checks confirmed automatic device-switch updates, listener removal on close, and scrolling at 350×300. Kernel signals run through the GUI’s main-thread scheduler.
```

Handling: corrected the README and UI contract to document the actual managed
Tools menu path. No runtime change was required. No remaining U04 findings.

## Orchestration verification and acceptance-test mapping

Final orchestration verification passed 633 core tests and 32 GUI tests. The
independent reviewer separately passed 633 core tests and 11 K40 workspace GUI
tests, including automatic device-switch updates, listener removal on close,
and scrolling at 350×300. Translation checking used
`uv run --locked --with polib --with chardet python translate_check.py de`
and exited 0. The generated delta was ignored; no locale edits or automatic
translation were made, and English fallback remains.

Ruff passed for the new runtime module with `--target-version py37` and for the
GUI tests under the uv interpreter target. The default modern target proposes
Python 3.9 annotation syntax incompatible with the runtime compatibility contract;
the explicit legacy target is documented in CONVENTIONS.md.

- AC-U04-1: `test_ac_u04_1_window_menu_uses_managed_window_conventions`, `test_ac_u04_1_console_toggle_opens_with_saved_geometry`, `test_ac_u04_1_groups_and_shortcuts_are_translated`
- AC-U04-2: `test_ac_u04_2_shortcuts_dispatch_established_tools`, `test_ac_u04_2_opening_and_refreshing_dispatch_no_commands`
- AC-U04-3: `test_ac_u04_3_device_switch_updates_label_and_supported_tools`, `test_ac_u04_3_no_active_device_is_identified_without_hardware_work`
- AC-U04-4: `test_ac_u04_4_missing_window_tool_shows_useful_visible_error`, `test_ac_u04_4_missing_laser_pane_shows_error_without_dispatch`
- Fixture guards: `test_existing_gui_registration_fixture_still_exposes_navigation`, `test_existing_managed_window_fixture_resolves_themes_in_child_context`
