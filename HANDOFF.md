# Resume the Mac / K40 roadmap

Paused at the user's request on 2026-10-18 to reduce token use and update the
workflow. Resume in a new session so the updated skill loads. No product agents
should continue running. Start by reading this file, AGENTS.md, ITERATIONS.md,
engineering/CONVENTIONS.md and the next unit; avoid loading the old conversation.

## Working agreements

- User's machine: Chinese CO2 K40 / Lihuiyu, usually M2 Nano; Mac host.
- One commit per TDD step, configured git author only, no AI trailers.
- Role-separated TDD; tests unchanged after red except justified test commits.
- Fresh agent contexts (`fork_turns="none"`), narrow briefs, one unit at a time;
  cheapest scribe for unit records and strongest independent reviewer.
- Do not start tests for additional units. Future tests below were already
  prepared and are drafts, not accepted green implementations.
- No hardware connection, movement, laser firing or spooling on report refresh.
- User authorized the fork and publishing finished units to it. No upstream PR,
  merge, rebase, squash, amend or force-push.

## Git and launch

- Branch: `fix/macos-workspace-readability`.
- Product HEAD before this handoff: `cb238f64f` (U05 review fixes).
- Last published fork branch: `86cda5117` (U04); U05 is local only.
- `origin` is upstream; `fork` is the user's GitHub fork.
- Run: `uv sync --locked`, then `uv run meerk40t`.
- Companion: **Tools → Tools → K40 Workspace**, or console
  `window toggle K40Workspace`.
- Existing HTTPS pushes needed the gh credential helper:
  `git -c credential.helper= -c 'credential.helper=!gh auth git-credential' push fork fix/macos-workspace-readability`.
  Publish only a fully green, reviewed checkpoint; do not push a red TDD HEAD.

## Completed and current work

- U02 uv desktop setup: complete, fresh-clone installation verified.
- U03 readable ruler/action labels: complete, two-round review passed.
- U04 managed K40 companion / shortcuts: complete and published.
- U05 read-only job summary: implementation and final review passed; **record
  step remains**. README already describes snapshot semantics. Complete the U05
  iteration entry, set its unit/status-table entry done, inspect the evidence,
  and commit the documentation before starting U06.
- U05 commits: red `01ac49c97`, green `28a662982`, regression red `71d63381c`,
  fix `cb238f64f`. Clarified later-unit contracts are in `4d4e5c17c`.
- U05 round 1 found invalid RectNode bounds crashing refresh and malformed
  passes string `"2.5"` incorrectly reported as two. Both fixed with regression
  tests; round 2 PASS, no open findings. Reports are saved verbatim in
  `engineering/evidence/U05-review.md`. No test override in U05.

## Pending roadmap, in order

1. **Finish U05 record and publish** the completed checkpoint if appropriate.
2. **U06 passive connection diagnosis**: draft
   `testgui/test_gui_k40connection.py` has 11 methods. Orchestrator verified all
   11 fail assertions for missing diagnosis, not fixture/import failures.
   Commit red plus in-progress status, then implement in k40reports.py and
   k40workspace.py. USB `is_connected()` reads a local handle only; TCP socket
   presence remains unverified; mock never reads USB. Show software pause/queue,
   errors and next steps; physical state/tube output remain unknown. See Q9.
3. **U07 local material notes**: draft `testgui/test_gui_materialnotes.py`,
   seven methods, test author reports nine expected missing-registration
   assertion failures. Orchestrator still needs to inspect and reproduce red.
   Separate managed `MaterialNotes` window, linked from companion; local JSON
   scoped by stable device path, bound to device at opening. Required material
   and result; thickness blank or finite nonnegative. Inline visible errors,
   retain draft and old records on failure. See Q10 and D5.
4. **U08 preview/framing context**: draft `testgui/test_gui_k40preview.py`,
   ten methods. Author was interrupted by usage limit; **no final validated
   report**, so inspect and run it before accepting red. Scene origin/bounds,
   home corner and explicitly estimated enabled-operation duration; any missing
   estimate makes total unavailable. Explicit Simulation prepares a free plan
   with `clear copy preprocess validate blob finish` then opens Simulation,
   never spools. Framing access only opens existing laser controls.
5. **U09 read-only design/import audit**: spec only, no tests or implementation.
   Dimensions, out-of-bed placement, unassigned elements, exact duplicate vector
   geometry plus transform. No automatic modification or deletion.
6. **U10 autosave and measured reports**: draft `testgui/test_gui_autosave.py`,
   eight methods. Earlier red: five failing methods / seven subcases, three
   controls pass; re-run when this unit starts. Existing Autosaver loses dirty
   state and may corrupt the normal recovery path on failed saves. Stage a
   complete replacement before publication; retain retryable dirty state,
   actionable errors and six prior versions. Profile the new reports on a
   deterministic large synthetic document; optimize only a measured problem.

## Verification already observed

- Latest product run: **633 core tests passed in 46.978s** after U05 fixes.
- Combined GUI suite: **46 tests passed** (14 summary, 11 companion, existing
  workspace-color and readability suites).
- Independent final review: 14 summary tests passed; round 1 independently ran
  all 633 core tests. Runtime Ruff passed with `--target-version py37`.
- Translation check exited 0. Missing translations retain English fallback;
  no automatic translation or tracked locale edits were made.
- Reuse `uv run --locked --group dev python -m unittest discover test -v` as core
  verify. Target GUI modules explicitly; blanket GUI discovery includes expected
  red drafts. GUI/display, uv cache and test profile writes can need escalation.
- Runtime supports legacy Python 3.6 syntax; uv selects 3.13. Ruff's oldest
  supported target is py37; do not modernize runtime annotations to satisfy the
  default lint target. No physical laser testing has occurred.

## Files to preserve

- Four prepared, untracked test files: k40connection, materialnotes, k40preview,
  autosave under testgui; commit each only at that unit's verified red step.
- `.DS_Store` is preexisting user data; leave it untracked and untouched.
- U05 evidence had uncommitted verification additions when this handoff began.
  This handoff also saves the final round-2 report so it survives a restart.
- No runtime changes are pending outside committed U05 code.

## Workflow source update

`~/dev/agent-config/skills/tdd-unit/SKILL.md` now specifies fresh isolated agent
contexts, one active unit, bounded briefs/tool budgets, compact reports and local
test logs, while preserving required verification and independent review.
README and ITERATIONS there document the change. Model tiers are unchanged.
Generated agents were rebuilt; installed skill/agents are symlinks into that repo.
Restart before resuming. Existing uncommitted source/role/generated changes in
agent-config predated this task and were preserved; do not discard or commit them
blindly. The source update is intentionally left uncommitted for review together
with those existing changes.

Verification of the updated agent-config passed: lint, formatting, strict types,
41 tests plus 14 subtests, generated-in-sync and shell syntax. Log:
`/private/tmp/agent-config-token-budget-verify.log` (temporary local evidence).
Documentation-only changes did not require product TDD roles or new product
tests. The MeerK40t product test results above remain the last observed results.
