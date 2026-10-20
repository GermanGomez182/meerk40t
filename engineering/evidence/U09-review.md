# U09 review evidence

## Round 1: 2026-10-20, reviewed 445fd5e2d

```text
VERDICT: CHANGES_REQUIRED
ROUND: 1
VERIFY: PASS
TEST INTEGRITY: unchanged since 0a847768a through reviewed green 445fd5e2d
AC COVERAGE:
  AC-U09-1: ok
  AC-U09-2: ok
  AC-U09-3: weak (malformed-coordinate coverage tests rectangles only; path/polyline NaN segments escape validation)
INVARIANTS:
  I1: guarded at meerk40t/gui/k40workspace.py:129; report collection dispatches no hardware commands
  I2: guarded at meerk40t/gui/k40reports.py:300; transform reset applies to a detached copy
  I7: guarded at meerk40t/gui/k40reports.py:313; assignment traversal and duplicate collection preserve document state
FINDINGS:
- [CRITICAL] meerk40t/gui/k40reports.py:267: Validation omits path/polyline segment coordinates, allowing incomplete geometry to appear fully checked. Scenario: construct a PathNode or PolylineNode with identity transform and two Geomstr lines, (0,0)→(10,10) mm and (NaN,5)→(400,5) mm, on a 300×200 mm bed → audit reports bounds 0,0,10,10 mm, dimensions 10×10 mm, “Outside bed: 0 (checked 1 of 1 elements),” and no limitation. Geomstr bounds discard the invalid segment. Validate required segment coordinates before accepting bounds or duplicate keys, while respecting intentional metadata/separator placeholders.
WOULD NOT TRUST: nothing beyond the above. Independently ran core verification: 633 tests passed in 58.967s; focused audit/workspace/summary GUI suites: 36 passed in 3.002s; runtime Ruff targeting Python 3.7 and diff whitespace checks passed.
```

Accepted. The orchestrator reproduced two failing subcases (PathNode and
PolylineNode) in 37 focused GUI tests; all 35 other tests passed. Regression red
`dac946711` retains original assertions and adds nonfinite segment coverage,
including supported checks, duplicate exclusion, and source-array preservation.

Fix `fb1ae759a` validates only populated segment coordinate fields, allowing
intentional separator and unused-field placeholders. Orchestrator verification
passed 633 core tests (49.265s), 102 combined GUI tests (3.014s), Ruff with
Python 3.7 target, whitespace checks, and translation checking (exit 0, English
fallback, no tracked locale edits).

## Round 2: 2026-10-20, reviewed fb1ae759a

```text
VERDICT: PASS
ROUND: 2
VERIFY: PASS
TEST INTEGRITY: unchanged since regression red dac946711; testgui/test_gui_k40audit.py gained an additive regression after original red 0a847768a, justified by commit dac946711. Original assertions remain unchanged.
AC COVERAGE:
  AC-U09-1: ok
  AC-U09-2: ok
  AC-U09-3: ok
INVARIANTS:
  I1: guarded at meerk40t/gui/k40workspace.py:129; report collection dispatches no hardware commands
  I2: guarded at meerk40t/gui/k40reports.py:310; transform reset applies to a detached copy
  I7: guarded at meerk40t/gui/k40reports.py:323; read-only traversal preserves references, selection, geometry and undo history
FINDINGS:
none
WOULD NOT TRUST: nothing beyond the above. Reviewed fix fb1ae759a resolves round 1 by validating populated path/polyline coordinate fields while permitting separator and unused-field NaNs. Independently passed 37 focused GUI tests, 18 in-memory geometry checks, runtime Ruff and whitespace checks. Confirmed the orchestrator’s final core log records 633 passing tests in 49.265s; independent core verification also passed during round 1.
```

Independent round-two focused GUI verification took 1.107s; the reviewer left
tracked files unchanged.

After the final report the orchestrator reran 633 core tests (47.352s) and 37
focused GUI tests (1.029s); both passed. Documentation recording was checked by
diff and whitespace validation before committing.
