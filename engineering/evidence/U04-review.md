# U04 review evidence

## Test-fixture correction

Override: register Themes as a kernel service in the test fixture, matching
gui/plugin.py. The initial fixture assigned it directly on the root context,
which did not provide themes to the managed window's child context. Once the
new window was registered, this caused fixture errors before panel construction.
The shortcut, device-state, error, translation, and geometry assertions are
unchanged. An existing MWindow construction control now verifies the fixture's
service propagation independently of the new window.
