# Resume the Mac / K40 roadmap

Current checkpoint: U07 completed and reviewed on 2026-10-19. The next unit is
U08. The current branch is `fix/macos-workspace-readability`; the U07 product
head is `dd0e57a31`, followed by the documentation record. Before beginning U08,
confirm the fork contains the complete checkpoint and publish it if needed.

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
- U07 product head: `dd0e57a31`, followed by its documentation record.
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

## Pending roadmap, in order

1. **U08 preview/framing context**: draft `testgui/test_gui_k40preview.py`, ten
   methods. Author was interrupted by usage limit; no final validated report,
   so inspect and run it when U08 starts. Scene origin/bounds, home corner and
   explicitly estimated enabled-operation duration; any missing estimate makes
   total unavailable. Explicit Simulation prepares a free plan with
   `clear copy preprocess validate blob finish` then opens Simulation, never
   spools. Framing access only opens existing laser controls.
2. **U09 read-only design/import audit**: spec only, no tests or implementation.
   Dimensions, out-of-bed placement, unassigned elements, exact duplicate
   vector geometry plus transform. No automatic modification or deletion.
3. **U10 autosave and measured reports**: draft `testgui/test_gui_autosave.py`,
   eight methods. Earlier red: five failing methods / seven subcases, three
   controls pass; re-run when this unit starts. Existing Autosaver loses dirty
   state and may corrupt the normal recovery path on failed saves. Stage a
   complete replacement before publication; retain retryable dirty state,
   actionable errors and six prior versions. Profile the new reports on a
   deterministic large synthetic document; optimize only a measured problem.

## Verification already observed

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

- Prepared untracked test drafts: `testgui/test_gui_k40preview.py` and
  `testgui/test_gui_autosave.py`; commit each only at its verified red step.
- `.DS_Store` is user data; leave it untracked and untouched.
- Do not discard untracked files or unrelated user changes.

## Shared conventions

See [engineering/CONVENTIONS.md](engineering/CONVENTIONS.md) and the root
`AGENTS.md` for testing, fixture, and ownership rules.

The earlier workflow update in `~/dev/agent-config` remains outside this product
change. Uncommitted source, role, and generated changes there predated or
accompanied that update; preserve them and do not commit or discard them blindly.
