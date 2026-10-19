# U05 review evidence

## Round 1: 2026-10-18, reviewed working tree before 28a662982

```text
VERDICT: CHANGES_REQUIRED
ROUND: 1
VERIFY: PASS (independent runs: 633 core tests in 45.462s; 10 job-summary GUI tests)
TEST INTEGRITY: unchanged since 01ac49c97
AC COVERAGE:
  AC-U05-1: weak (effective-pass coverage omits malformed stored counts)
  AC-U05-2: weak (nonfinite values are covered, but exceptions while computing malformed geometry bounds are not)
  AC-U05-3: ok
INVARIANTS:
  I1: guarded at meerk40t/gui/k40reports.py:63; collection issues no hardware or console commands
  I3: unguarded path: meerk40t/gui/k40reports.py:96 converts malformed pass representations into misleading effective counts
  I7: guarded at meerk40t/gui/k40reports.py:42 and :87; traversal preserves operation order and logical document state
FINDINGS:
- [CRITICAL] meerk40t/gui/k40reports.py:43: Exceptions from invalid geometry escape before unavailable-value handling. Scenario: create a real RectNode, set its width to None or "bad", and include it in elements.elems() → build_job_summary raises TypeError instead of reporting unavailable bounds. Because refresh runs during window construction and before shortcut dispatch, this can also prevent the companion opening or its shortcuts working. Add a regression and narrowly handle expected invalid-geometry failures with a visible unavailable result.
- [CRITICAL] meerk40t/gui/k40reports.py:96: Float conversion changes effective-pass semantics. Scenario: CutOpNode(settings={"passes": "2.5", "passes_custom": True}) → operation.implicit_passes is 1, while the summary displays Passes: 2. Preserve the operation’s effective semantics or explicitly report the malformed value as unavailable; do not invent a different count.
WOULD NOT TRUST: nothing beyond the above
```

Both findings accepted. Regression tests precede fixes. Malformed pass strings
will be explicitly unavailable; valid numeric values retain operation conversion
semantics. Invalid numeric geometry will leave the report usable with unavailable
bounds.

## Regression evidence

The orchestrator reproduced the failures at `28a662982`: 14 summary tests,
one assertion failure for string passes and four subtest errors for invalid
rectangle widths during construction and refresh. The ten original tests and
the valid numeric fractional-pass control remained green. Tests were committed
as `71d63381c`, without changing existing assertions.

The fix catches numeric geometry failures at bounds access and reports
Unavailable. Direct `int(raw)` conversion preserves effective pass semantics;
invalid representations visibly remain Unavailable. The orchestrator's combined
GUI suite passed all 46 tests, and runtime Ruff passed with target Python 3.7.

## Round 2: 2026-10-18, reviewed cb238f64f

```text
VERDICT: PASS
ROUND: 2
VERIFY: PASS (independent: 14 job-summary GUI tests; 633 core tests in round 1. Orchestrator: post-fix 633 core tests passed in 46.978s)
TEST INTEGRITY: unchanged since regression RED 71d63381c. Four regression tests were added after 01ac49c97, justified by the accepted findings; original assertions remain unchanged.
AC COVERAGE:
  AC-U05-1: ok
  AC-U05-2: ok
  AC-U05-3: ok
INVARIANTS:
  I1: guarded at meerk40t/gui/k40reports.py:66; collection issues no hardware or console commands
  I3: guarded at meerk40t/gui/k40reports.py:43 and :99; invalid geometry and malformed pass representations visibly report Unavailable, while valid counts preserve effective conversion semantics
  I7: guarded at meerk40t/gui/k40reports.py:42 and :90; ordered traversal preserves logical document state, references, selection, undo history, and queue
FINDINGS:
none
WOULD NOT TRUST: nothing beyond the above
```
