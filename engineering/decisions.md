# Decisions

## D1: Reuse the wxPython application and established tools

Why: the existing scene, driver, material and simulation capabilities are mature entry points.
Over: replacing the desktop stack or creating a second hardware-control layer.
Cost: new UI follows wxPython lifecycle and theme constraints.

## D2: Add a companion K40 workspace

Why: makes common tools discoverable while preserving existing saved main layouts.
Over: automatically rearranging panes on startup.
Cost: users open one additional managed window.

## D3: Separate read-only report data from widgets

Why: deterministic tests can use real nodes and dummy devices without physical USB access.
Over: collecting document and driver data inside button callbacks.
Cost: a small data/report module is maintained alongside the window.

## D4: Preserve the package's Python 3.6 source compatibility

Why: uv selects Python 3.13 but the existing package advertises older Python support.
Over: introducing modern-only syntax or standard-library dependencies into runtime modules.
Cost: use typing constructs compatible with existing source and avoid new runtime dependencies.

