# U10 review evidence

## Round 1: 2026-10-20, reviewed def59e2e3

```text
VERDICT: PASS
ROUND: 1
VERIFY: PASS
TEST INTEGRITY: unchanged since 17c2c1705
AC COVERAGE:
  AC-U10-1: ok
  AC-U10-2: ok
  AC-U10-3: ok
  AC-U10-4: ok
INVARIANTS:
  I2: guarded at meerk40t/gui/wxmmain.py:243 (temporary save), meerk40t/gui/wxmmain.py:247 (atomic publication), meerk40t/gui/wxmmain.py:268 (prior recovery preserved during history copy)
  I4: guarded at meerk40t/gui/wxmmain.py:184 (local work directory); no network persistence introduced
  I5: guarded at meerk40t/gui/wxmmain.py:248 (visible failure and retained dirty state), meerk40t/gui/wxmmain.py:256 (clear only after completion)
FINDINGS:
none
WOULD NOT TRUST: nothing beyond the above
```

The reviewer independently passed 633 core tests (45.949s), 24 focused autosave
and material-notes GUI tests (0.811s), real permission-denial, writer ValueError,
and post-publication cleanup-failure probes with successful retries. Reproducing
both profiling sizes with two repetitions matched all eight recorded report
hashes. Ruff checks and whitespace validation passed; the reviewer left tracked
files unchanged and original red tests were preserved.

The orchestrator passed 633 core tests (46.466s), 114 combined GUI tests
(2.891s), translation checking (exit 0, English fallback, no locale changes),
Ruff for the diagnostic utility/tests, and an isolated Autosaver class lint check
with Python 3.7 target. Unrelated legacy-file diagnostics were not reformatted.
Measurements are recorded in [U10-report-profile.md](U10-report-profile.md).

## Final verification and fresh checkout

After the final report the orchestrator passed 633 core tests (46.355s) and
114 combined GUI tests (2.673s). Review left tracked files unchanged.

A fresh local clone of reviewed product commit `def59e2e3` passed:

- `uv sync --locked --group dev`.
- `uv run --locked meerk40t --version` (installed entry point).
- Isolated Python `-I` assertion that the imported package belongs to the clone.
- `uv run --locked --group dev python -m unittest testgui.test_gui_autosave -v`
  (12 tests, 0.258s, including the real SVG save/reload integration).
- `uv run --locked python engineering/profile_reports.py --elements 40 --repeats 1`.

The fresh checkout stayed clean. These checks exercised software only; no
physical hardware was connected or commanded. Documentation recording was
checked by diff and whitespace validation before the completion commit.
