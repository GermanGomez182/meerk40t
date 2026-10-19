# U06 review evidence

## Round 1: 2026-10-18, reviewed 41e83a724

```text
VERDICT: CHANGES_REQUIRED
ROUND: 1
VERIFY: PASS
TEST INTEGRITY: unchanged since 444a04de6
AC COVERAGE:
  AC-U06-1: weak (combined networked/mock settings are untested and mislabeled)
  AC-U06-2: weak (pause assertions accept “Not paused”)
  AC-U06-3: ok
INVARIANTS:
  I1: guarded at meerk40t/gui/k40reports.py:132; connection checks read local handle state without hardware probing
  I3: unguarded path: meerk40t/gui/k40reports.py:133 selects the mock label before checking the active network transport
  I5: guarded at meerk40t/gui/k40reports.py:147, :165, :173, :186
FINDINGS:
- [CRITICAL] meerk40t/gui/k40reports.py:133: Transport selection contradicts LihuiyuDevice.output and driver.out_pipe. Scenario: mock=True and networked=True -> the report displays “Mock transport — no hardware connection observed”, although device.py:1288 selects TCP. Reproduced using the actual output property and report function without hardware.
- [IMPORTANT] testgui/test_gui_k40connection.py:192: The pause assertion checks only that software and pause appear on a line; the controller-pause test at line 175 has the same weakness. Scenario: driver.paused=True with controller.state="idle", or controller.state="pause" -> incorrect output “Software pause: Not paused” satisfies these assertions, allowing a broken pause report to pass.
WOULD NOT TRUST: nothing beyond the above; independently passed core verification (633 tests), focused GUI suites (38 tests), and Ruff with target py37.
```

Both findings accepted. Add a combined-mode regression and strengthen pause
assertions without removing existing checks, then match the active TCP routing
precedence. No test override is needed.

## Regression evidence

At `41e83a724`, the orchestrator reproduced one failing transport regression
out of 14 connection tests; all other tests, including the stronger pause
assertions, passed. Regression tests were committed as `564077da2` before
the fix `c9d42a83a`. Existing assertions were retained. Post-fix orchestration
passed 633 core tests (43.954s), 60 relevant GUI tests (0.946s), and runtime
Ruff with target py37. Translation check exited 0 with English fallback;
no tracked locale edits or automatic translations were made.

## Round 2: 2026-10-18, reviewed c9d42a83a

```text
VERDICT: PASS
ROUND: 2
VERIFY: PASS
TEST INTEGRITY: unchanged since 564077da2; earlier additions and strengthened assertions justified by that commit’s message
AC COVERAGE:
  AC-U06-1: ok
  AC-U06-2: ok
  AC-U06-3: ok
INVARIANTS:
  I1: guarded at meerk40t/gui/k40reports.py:132; only passive local state is read
  I3: guarded at meerk40t/gui/k40reports.py:133, :157, :172, :189; network precedence matches device output, and software observations remain distinct from physical unknowns
  I5: guarded at meerk40t/gui/k40reports.py:147, :165, :173, :186
FINDINGS:
none
WOULD NOT TRUST: nothing beyond the above; both round-one findings resolved. Independently passed core verification (633 tests, 45.057s), focused GUI suites (39 tests), and Ruff with target py37.
```
