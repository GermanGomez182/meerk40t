# U08 review evidence

## Round 1: 2026-10-19, reviewed 4e9a92f6c

```text
VERDICT: CHANGES_REQUIRED
ROUND: 1
VERIFY: PASS
TEST INTEGRITY: unchanged since c4b1dce9f
AC COVERAGE:
  AC-U08-1: ok
  AC-U08-2: ok
  AC-U08-3: weak (missing-framing test checks IsShown(), which remains true when the error is outside the viewport)
INVARIANTS:
  I1: guarded at meerk40t/gui/k40workspace.py:137 and meerk40t/gui/k40workspace.py:156
  I3: guarded at meerk40t/gui/k40reports.py:194 and meerk40t/gui/k40reports.py:240
  I7: guarded at meerk40t/gui/k40reports.py:201 and meerk40t/gui/k40workspace.py:156
FINDINGS:
- [IMPORTANT] meerk40t/gui/k40workspace.py:92: The new Framing controls shortcut uses open_tool(), which leaves failure messages outside the visible viewport. Scenario: unregister pane/laser, show the default 450×650 workspace, scroll to Framing controls, and click it -> “Framing controls is unavailable.” is set, but the scroll position remains (0,24); the error rectangle is (8,-448,419,16), entirely outside the client rectangle (0,0,435,622). The action appears to do nothing. Bring the error into view and add a viewport-visibility regression assertion.
WOULD NOT TRUST: nothing beyond the above
```

Accepted. A viewport-visibility regression precedes the fix. Independent round-one
verification passed 633 core tests (44.252s), 28 focused GUI tests (0.915s), Ruff
with Python 3.7 target, and whitespace checks. The orchestrator passed 633 core
tests (44.652s), 89 combined GUI tests (1.959s), Ruff, and translation checking
(exit 0, English fallback, no tracked locale changes).

## Regression evidence

The orchestrator reproduced the offscreen error against `4e9a92f6c`: 29 focused
GUI tests, one failure at the new viewport containment assertion. Regression
red `2d3b0e285` retains the original tests. Fix `d34b181c9` updates scroll extent
and brings nonempty shortcut errors into view. Orchestrator verification passed
633 core tests (44.342s), 90 combined GUI tests (1.947s), Ruff with Python 3.7
target, and whitespace checks.

## Round 2: 2026-10-19, reviewed d34b181c9

```text
VERDICT: PASS
ROUND: 2
VERIFY: PASS
TEST INTEGRITY: unchanged since 2d3b0e285 through reviewed commit d34b181c9; original red tests preserved, viewport regression justified by test(U08): reproduce offscreen framing error
AC COVERAGE:
  AC-U08-1: ok
  AC-U08-2: ok
  AC-U08-3: ok
INVARIANTS:
  I1: guarded at meerk40t/gui/k40workspace.py:137 and meerk40t/gui/k40workspace.py:159
  I3: guarded at meerk40t/gui/k40reports.py:194 and meerk40t/gui/k40reports.py:240
  I7: guarded at meerk40t/gui/k40reports.py:201 and meerk40t/gui/k40workspace.py:159
FINDINGS:
none
WOULD NOT TRUST: nothing beyond the above
```

Independent round-two verification passed 29 focused GUI tests (0.962s), Ruff,
and whitespace checks. Its viewport probe moved the error from y=-448 to y=12
inside the panel, with no dispatched commands.

After the final report, the orchestrator reran 633 core tests (44.424s) and 29
focused GUI tests (1.025s); both passed. The reviewer left tracked files
unchanged, and documentation recording was checked by diff before committing.
