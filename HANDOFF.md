# Resume the Mac / K40 roadmap

Current checkpoint: U09 completed and reviewed on 2026-10-20. The current
branch is `fix/macos-workspace-readability`; U09 product head is `fb1ae759a`,
followed by this documentation record. Final post-review reruns passed 633 core
tests (47.352s) and 37 focused GUI tests (1.029s). Confirm the fork contains the
complete checkpoint before starting U10.

## Working agreements

- User's machine: Chinese CO2 K40 / Lihuiyu, usually M2 Nano; Mac host.
- One commit per TDD step, configured git author only, no AI trailers.
- Role-separated TDD; tests unchanged after red except justified test commits.
- Fresh agent contexts, narrow briefs, one unit at a time; strongest independent
  reviewer and cheapest scribe for records.
- Do not start tests for additional units. Future tests below are drafts, not
  accepted implementations.
- No hardware connection, movement, laser firing or spooling on report refresh.
- User authorized publishing finished units to the fork. No upstream PR, merge,
  rebase, squash, amend or force-push.

## Git and launch

- Branch: `fix/macos-workspace-readability`.
- U09 product head: `fb1ae759a`, followed by this documentation record.
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

## Pending roadmap, in order

1. **U10 autosave and measured reports**: draft `testgui/test_gui_autosave.py`,
   eight methods. Earlier red: five failing methods / seven subcases, three
   controls pass; re-run when this unit starts. Existing Autosaver loses dirty
   state and may corrupt the normal recovery path on failed saves. Stage a
   complete replacement before publication; retain retryable dirty state,
   actionable errors and six prior versions. Profile the new reports on a
   deterministic large synthetic document; optimize only a measured problem.

## Verification already observed

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

- Prepared untracked test draft: `testgui/test_gui_autosave.py`; commit only at
  its verified red step.
- `.DS_Store` is user data; leave it untracked and untouched.
- Do not discard untracked files or unrelated user changes.

## Shared conventions

See [engineering/CONVENTIONS.md](engineering/CONVENTIONS.md) and the root
`AGENTS.md` for testing, fixture, and ownership rules.

The earlier workflow update in `~/dev/agent-config` remains outside this product
change. Uncommitted source, role, and generated changes there predated or
accompanied that update; preserve them and do not commit or discard them blindly.
