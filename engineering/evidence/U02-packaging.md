# U02 packaging verification — 2026-10-17

Verified packaging commit: `c8d3e5e8c`.
Platform: Apple Silicon macOS; uv 0.11.28; CPython 3.13.14.

## Scope and review

Only packaging configuration, the lockfile, interpreter selection, and documents
changed. Application code and tests are unchanged. The configuration diff and
generated metadata were reviewed locally. The TDD skill excludes configuration
and documentation changes, so no artificial failing tests or role-agent review
were introduced. The existing core verification command was reused.

## Existing checkout

- `uv run --locked meerk40t --version`: exit 0; `MeerK40t 0.9.9040 pkg`.
- `uv run --locked python -I`: verified `meerk40t.__file__` resolves inside this
  checkout, distribution metadata identifies an editable install, and the
  `meerk40t` console entry point exists. Imported wxPython, Pillow, ezdxf,
  requests, and websocket-client successfully.
- `uv run --locked --group dev python -m unittest discover test -v`: 633 tests
  passed in 45.514 seconds, with test-profile access outside the sandbox.
- `uv run --locked python -m unittest testgui.test_gui_workspace_colors -v`:
  10 tests passed with macOS display access.
- `uv build --wheel`: built the wheel successfully using the existing
  setuptools metadata. The pre-existing distribution version `0.9.9000` and
  application's displayed version `0.9.9040` remain unchanged.
- `git diff --check`: passed.

## Fresh clone

Cloned the committed repository locally into a new temporary directory. No
existing virtual environment or untracked source files were copied.

1. `uv sync --locked`: created a new `.venv` with CPython 3.13.14 and installed
   16 desktop packages, including this clone as an editable package.
2. `uv run --locked meerk40t --version`: exit 0; `MeerK40t 0.9.9040 pkg`.
3. The same isolated source/metadata/import assertions passed against the new
   clone, verifying the entry point uses its source rather than another install.
4. `uv run --locked python -m unittest testgui.test_gui_workspace_colors -v`:
   10 tests passed in 3.894 seconds with display access.
5. `git status --short`: clean; HEAD remained `c8d3e5e8c`.

## Limits

Other operating systems and older Python versions were not exercised. Linux
wxPython installation may need native build dependencies; the README links its
installation guide. These checks cover installation, CLI entry-point execution,
dependency imports, and GUI color behavior; they do not include an interactive
application session or physical laser operation.
