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

## D5: Keep material observations in a separate managed window

Why: the companion's reports remain read-only while a small form can retain a
draft for the clearly displayed device during an active-device switch.
Over: mixing editable notes into the report text or redirecting a draft silently.
Cost: an additional local window, using existing geometry and tool registration.

## D6: Distinguish device incarnations in material notes

Why: normal device creation reuses deleted devices' service paths; a path alone
can expose the deleted machine's observations to a replacement.
Use a persisted per-device material_notes_id alongside the service path. A
surviving device restores its identifier from settings across restarts; a newly
created device receives a new identifier. Removed devices' note files remain
local for manual recovery. Never automatically associate old path-only notes
with a replacement.
Cost: the restart test fixture must restore the saved device identifier too.

## D7: Keep audit warnings exact and conservative

Per QUESTIONS.md Q6, duplicate warnings require identical vector segment
sequences and the same current transform. Bounds alone do not establish a
duplicate. No tolerance, reversed-path matching, or alternate path encoding
normalization is attempted. Styling does not change vector geometry, and the
audit never deletes anything.

Assignment means an element has a reference in the operation tree, including
disabled operations and nested effects. Other references do not establish job
assignment. Report labels with IDs or document indices so unlabeled or similarly
named elements remain identifiable. Unsupported checks report their limitations
without discarding supported bounds or assignment checks.

Why: makes the first slice predictable and read-only without inventing import
repair semantics. Cost: equivalent geometry encoded differently can remain
unflagged, and a reference to a disabled operation still counts as assigned.

