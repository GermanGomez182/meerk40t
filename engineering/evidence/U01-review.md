# U01 review evidence

## Round 1: 2026-10-17, reviewed `ce90466c6`

VERDICT: PASS
ROUND: 1
VERIFY: PASS (independently ran 10 GUI tests with macOS display access; git diff --check passed; full core suite remains with orchestrator)
TEST INTEGRITY: unchanged since 7062274c2
AC COVERAGE:
  AC-U01-1: ok
  AC-U01-2: ok
  AC-U01-3: ok
INVARIANTS:
  Saved custom colors: preserved through existing settings loading at meerk40t/gui/guicolors.py:102.
  Native theme separation: guarded by limiting changes to workspace colors at meerk40t/gui/guicolors.py:95; native theme handling remains unchanged.
  Hardware behavior: no driver, motion, power, or device configuration changes.
FINDINGS:
none
WOULD NOT TRUST: Actual visual readability still needs a desktop smoke check: tests validate palette values and reset dispatch, but do not render the workspace or click the Preferences controls. README instructions match the implementation.

## Orchestration verification

The full core suite passed: `.venv/bin/python -m unittest discover test -v` (633 tests, 44.500 seconds). The first sandboxed run had one GRBL persistence failure; the isolated run and full suite passed with escalated profile access. The new test file passed flake8 with `--max-line-length=88`.

## Acceptance criteria and test methods

- AC-U01-1: `test_ac_u01_1_macos_dark_appearance_starts_with_bright_workspace`, `test_ac_u01_1_other_platforms_keep_dark_workspace_defaults`, `test_ac_u01_1_saved_macos_workspace_colors_are_preserved`, `test_ac_u01_1_light_appearance_keeps_bright_defaults_everywhere`.
- AC-U01-2: `test_ac_u01_2_macos_default_reset_restores_bright_workspace`, `test_ac_u01_2_brighter_reset_restores_bright_palette_everywhere`, `test_ac_u01_2_other_platforms_keep_dark_default_reset`.
- AC-U01-3: `test_ac_u01_3_reading_brighter_button_has_no_side_effects`, `test_ac_u01_3_brighter_button_dispatches_reset_and_refresh`, `test_ac_u01_3_false_brighter_button_does_nothing`.

Red `7062274c2`: 2 expected assertion failures and 8 passes. Green `ce90466c6`: 10 GUI tests passed.
