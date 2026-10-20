# Resume the Mac / K40 roadmap

Current checkpoint: U10 completed and reviewed on 2026-10-20. The current
branch is `fix/macos-workspace-readability`; product head is `def59e2e3`, followed
by this documentation record. U03–U10 first slices are accepted and complete;
U01/U02 groundwork is done. Final post-review verification passed 633 core tests
and 114 GUI tests. A fresh local checkout installed and passed the CLI,
editable-source, 12 autosave tests and profiling utility smoke checks. Confirm
the fork contains this complete checkpoint when resuming.

## Working agreements

- User's machine: Chinese CO2 K40 / Lihuiyu, usually M2 Nano; Mac host.
- One commit per TDD step, configured git author only, no AI trailers.
- Role-separated TDD; tests unchanged after red except justified test commits.
- Fresh agent contexts, narrow briefs, one unit at a time; strongest independent
  reviewer and cheapest scribe for records.
- No automatic units remain. Broader Mac icon/toolbar polish, real-file/raster
  performance work, and physical hardware checks are optional backlog.
- No hardware connection, movement, laser firing or spooling on report refresh.
- User authorized publishing finished units to the fork. No upstream PR, merge,
  rebase, squash, amend or force-push.

## Git and launch

- Branch: `fix/macos-workspace-readability`.
- Final product head: `def59e2e3`, followed by this documentation record.
- `origin` is upstream; `fork` is the user's GitHub fork.
- Run: `uv sync --locked`, then `uv run meerk40t`.
- Companion: **Tools → Tools → K40 Workspace**, or console
  `window toggle K40Workspace`.
- Existing HTTPS pushes needed the gh credential helper:
  `git -c credential.helper= -c 'credential.helper=!gh auth git-credential' push fork fix/macos-workspace-readability`.
- Publish only a fully green, reviewed checkpoint; do not push a red TDD HEAD.

## Completed and current work

- U02 uv desktop setup: complete, fresh-clone installation verified.
- U03 readable ruler/action labels: complete, two-round review passed.
- U04 managed K40 companion / shortcuts: complete and published.
- U05 read-only job summary: complete and published at `a578484ca`.
- U06 passive connection diagnosis: complete and reviewed; evidence:
  `engineering/evidence/U06-review.md`.
- U07 local material test notes: complete; round 2 PASS, both identity-reuse
  findings fixed. Evidence: [U07 review](engineering/evidence/U07-review.md).
  The first-session crash before identifier configuration is saved can orphan
  local notes that need manual recovery; README documents this limit.
- U08 preview and framing context: complete; round 2 PASS, the offscreen framing
  error finding was fixed. Evidence: [U08 review](engineering/evidence/U08-review.md).
  Simulation opens only after free-plan preparation; framing access opens
  existing laser controls only.
- U09 read-only design/import audit: complete; round 2 PASS, malformed vector
  coordinate handling fixed with regression coverage. Evidence:
  [U09 review](engineering/evidence/U09-review.md).

## U10 completion

U10 red `17c2c1705` → green `def59e2e3`; round 1 review PASS with no findings.
Autosave failures remain visible and retryable, replacement publication is
atomic, and history retains six prior versions. Synthetic report measurements
and hashes are recorded in [U10 profile evidence](engineering/evidence/U10-report-profile.md).
Final post-review reruns and fresh-clone installation/smoke checks passed.
No accepted units remain; additional work requires a selected follow-up scope.

## Verification already observed

- U10 final verification passed 633 core tests (46.355s) and 114 combined GUI
  tests (2.673s). Independent review passed 633 core tests, 24 focused GUI tests,
  failure/retry probes and repeated profiling hashes. Fresh checkout of
  `def59e2e3`: `uv sync --locked --group dev`, CLI version, isolated editable
  import assertion, 12 autosave tests and profiling smoke all passed; checkout
  stayed clean. Evidence: [U10 review](engineering/evidence/U10-review.md).
- U09 orchestration passed 633 core tests (49.265s), 102 combined GUI tests
  (3.014s), Ruff with Python 3.7 target, whitespace checks, and translation
  checking (exit 0; English fallback, no locale edits). Independent review
  passed 633 core tests (58.967s) and 36 focused GUI tests (3.002s) in round
  one; round two passed 37 focused GUI tests (1.107s), 18 geometry probes,
  Ruff and whitespace checks. Final post-review reruns passed 633 core tests
  (47.352s) and 37 focused GUI tests (1.029s). Evidence:
  [U09 review](engineering/evidence/U09-review.md).
- U08 orchestration passed 633 core tests (44.342s), 90 combined GUI tests
  (1.947s), Ruff with Python 3.7 target, whitespace checks, and translation
  checking with English fallback/no locale edits. Final post-review reruns
  passed 633 core tests (44.424s) and 29 focused GUI tests (1.025s). Independent
  review passed 633 core tests in round one and 29 focused GUI tests plus the
  viewport probe in round two. Evidence: [U08 review](engineering/evidence/U08-review.md).
- U07 final orchestration passed 633 core tests (48.102s), 72 combined GUI
  tests (1.290s), runtime Ruff with Python 3.7 target, and translation check
  with English fallback/no locale edits. Independent review passed 23 focused
  GUI tests (0.847s), Ruff, and lifecycle probes. Results are detailed in
  `engineering/evidence/U07-review.md` and `ITERATIONS.md`.
- U06 final orchestration passed 633 core tests, 60 GUI tests, Ruff and
  translation check. Independent review passed 633 core tests, 39 focused GUI
  tests, and Ruff. Evidence: [U06 review](engineering/evidence/U06-review.md).
- Reuse `uv run --locked --group dev python -m unittest discover test -v` as
  core verify. Target GUI modules explicitly; blanket GUI discovery includes
  expected draft tests. GUI/display, uv cache and test profile writes can need
  escalation. No physical laser testing has occurred.
- Runtime retains Python 3.6 source syntax; uv selects Python 3.13 and Ruff's
  oldest supported target is py37. Do not modernize runtime syntax for lint.

## Files to preserve

- Autosave tests in `testgui/test_gui_autosave.py` are tracked in the red commit;
  the red and green commits are present on the branch.
- `.DS_Store` is user data; leave it untracked and untouched.
- Do not discard untracked files or unrelated user changes.

## Shared conventions

See [engineering/CONVENTIONS.md](engineering/CONVENTIONS.md) and the root
`AGENTS.md` for testing, fixture, and ownership rules.

The earlier workflow update in `~/dev/agent-config` remains outside this product
change. Uncommitted source, role, and generated changes there predated or
accompanied that update; preserve them and do not commit or discard them blindly.
