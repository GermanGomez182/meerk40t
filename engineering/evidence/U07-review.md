# U07 review evidence

## Round 1: 2026-10-18, reviewed cc7de39d2

```text
VERDICT: CHANGES_REQUIRED
ROUND: 1
VERIFY: PASS (633 core tests; 20 focused GUI tests; runtime Ruff)
TEST INTEGRITY: unchanged since b237c6e4f
AC COVERAGE:
  AC-U07-1: ok
  AC-U07-2: weak (distinct paths covered; deleted-device path reuse is not)
  AC-U07-3: ok
INVARIANTS:
  I2: guarded at meerk40t/gui/materialnotes.py:174
  I4: guarded at meerk40t/gui/materialnotes.py:25
  I5: guarded at meerk40t/gui/materialnotes.py:132 and meerk40t/gui/materialnotes.py:185
FINDINGS:
- [CRITICAL] meerk40t/gui/materialnotes.py:23: The storage identity uses a reusable service path, allowing a newly created machine to inherit another machine’s observations. Scenario: save notes for machine A, activate machine B, delete A, then add a replacement of A’s device type. Normal device creation reuses A’s freed path (meerk40t/device/basedevice.py:168), and opening Material Notes for the replacement displays A’s records. Independently reproduced through the normal device delete/add commands.
WOULD NOT TRUST: nothing beyond the above
```

Accepted. A regression will distinguish a surviving device across restart from
a deleted device's replacement at the same path. The correction uses a persisted
device identifier alongside the service path. The restart fixture must restore
that setting, as a real surviving device does, rather than create a new device.

## Regression evidence

The orchestrator reproduced the deleted-device path leak against `cc7de39d2`:
11 notes tests, one failing and ten passing. Regression red `fe578a3b3` retains
all original assertions and corrects the restart fixture to round-trip actual
device settings through a temporary configuration file. This fixture correction
is an explicit test override justified by the persisted identity contract.
Fix `7c0d6e158` passed 633 core tests (45.640s), 71 GUI tests (1.262s), and Ruff.

## Round 2 interim observation — 2026-10-19

The reviewer confirmed a second route to identity reuse before finishing round
two. Its exact observation:

```text
CONFIRMED through normal commands: keep base path fixture-device occupied; source A at fixture-device1 saves a note and UUID; `device duplicate "Fixture source" "Fixture clone"` creates fixture-device2 with copied UUID; activate clone; `device delete "Fixture source"`; duplicate clone to replacement -> allocator reuses fixture-device1 and copied UUID, replacement displays A's notes. Probe exit0 printed all three true; copy occurs basedevice.py:267-274. Private in-memory ID plus explicit persistent read/write under material_notes_id can avoid this without basedevice edits, but Context.setting ignores underscore keys, so use explicit read_persistent/write_persistent. Holding final for correction in this round.
```

Accepted. Regression `1b1a3f88d` exercises the production duplicate/delete
commands; the orchestrator observed 12 notes tests, one failing and eleven
passing against `7c0d6e158`. The correction keeps the identifier exclusively in
persistent settings and the opened notes window, outside attributes copied by
device duplication. The final round-two report follows after this correction.

Final correction `dd0e57a31` passed 633 core tests (48.102s), 72 combined GUI
tests (1.290s), runtime Ruff with Python 3.7 target, and whitespace checks.
Translation checking exited 0 with English fallback and no tracked locale edits.

## Round 2: 2026-10-19, reviewed dd0e57a31

```text
VERDICT: PASS
ROUND: 2
VERIFY: PASS (dd0e57a31; independently ran 23 focused GUI tests, Ruff, and lifecycle probes; inspected orchestrator’s successful 633-test core log)
TEST INTEGRITY: unchanged since 1b1a3f88d; earlier restart-fixture correction justified by fe578a3b3, with original assertions preserved
AC COVERAGE:
  AC-U07-1: ok
  AC-U07-2: ok
  AC-U07-3: ok
INVARIANTS:
  I2: guarded at meerk40t/gui/materialnotes.py:189
  I4: guarded at meerk40t/gui/materialnotes.py:35
  I5: guarded at meerk40t/gui/materialnotes.py:143 and meerk40t/gui/materialnotes.py:200
FINDINGS:
none
WOULD NOT TRUST: Crash recovery before the identifier’s first configuration save: saved notes can require manual recovery after a crash. This limitation is documented; clean restart, duplicated-device isolation, and old-window saves were verified.
```

After receiving the final report, the orchestrator reran the core suite (633
tests, 44.528s) and focused notes/workspace suites (23 tests, 0.792s); both passed.
The reviewer left tracked files unchanged. Documentation recording was checked
by diff and whitespace validation before committing.
