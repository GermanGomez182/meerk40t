# Technical contract

Follow AGENTS.md and the Python rules. Use existing wxPython/kernel conventions, explicit type annotations on new functions, translated visible text, and no swallowed errors. New runtime modules remain compatible with the package's Python 3.6 syntax.

## Verification

Core verify: `uv run --locked --group dev python -m unittest discover test -v`.
Targeted GUI suites run with a desktop display and wx.App. Access to test profiles and the Mac display can require sandbox escalation. Use in-memory kernels or temporary directories, never real machine configuration. Run Ruff on new Python files and inspect changed legacy-file hunks without mass formatting.

## Layout and fixtures

- U03: themes/color helpers and GuideWidget; tests in testgui/test_gui_readability.py; one owned wx.App per suite, no physical device.
- U04: gui/k40workspace.py, registered by wxmeerk40t.py; tests in testgui/test_gui_k40workspace.py. The registered window exposes `.panel` with `refresh_data()`. Reusable fixture creates a parent wx.Frame, minimal context and command recorder; helper signature `make_context(device=None)` belongs to this test module.
- U05: gui/k40reports.py; core tests in test/test_k40reports.py use bootstrap's dummy kernel and node operations. GUI integration extends U04's suite.
- U06: extends k40reports.py and k40workspace.py; tests cover passive controller attributes with explicit simple fake objects, never mocks that manufacture missing state.
- U07: gui/materialnotes.py and K40 workspace; local JSON tests use tempfile.TemporaryDirectory and explicit fictional material identifiers. No personal data or absolute local paths are tracked.
- U08: report/companion extensions; simulation uses the existing preparation path without spooling. Tests record dispatched commands and assert no movement.
- U09: report/companion extensions; exact geometry comparisons use current scene-space transforms. No destructive cleanup.
- U10: Autosaver in wxmmain.py; GUI tests in testgui/test_gui_autosave.py. Save failures are injected, dirty state and prior autosave preservation asserted.

Only the orchestrator stages and commits. Test author edits tests only; implementer never edits tests; reviewer is read-only; scribe edits records only. Shared report/window files are developed sequentially.

