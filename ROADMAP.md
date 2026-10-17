# Proposed improvements

These are proposals for this fork, in suggested order. They are not implemented
features or a commitment to build every item. The starting point is a Mac user
with a K40/Lihuiyu CO₂ laser. Many underlying capabilities already exist in
MeerK40t; the focus is making them easier to find, understand, and trust.

| Priority | Improvement | Intended result |
| --- | --- | --- |
| 1 | Finish Mac readability | Review the rendered workspace, then improve ruler text, grid contrast, selection handles, icons, and toolbar labels in light and dark appearances. |
| 2 | A focused K40 workspace | Offer a saved layout with connection status, jog and home controls, framing, cut/engrave settings, and job controls in a consistent place. Keep advanced tools accessible. |
| 3 | A clearer job summary | Before starting, show operation order, speed and power settings with units, passes, dimensions, and placement on the bed. Make the selected device obvious. |
| 4 | Better connection diagnostics | Explain USB connection failures and recovery steps, and distinguish connected, idle, queued, paused, and disconnected states. Never report hardware feedback the controller does not provide. |
| 5 | Materials and test results | Make existing material presets and test patterns easier to use; record material thickness, settings, and observed results locally for the actual machine. Avoid universal power recommendations. |
| 6 | Easier preview and framing | Make existing simulation, travel paths, estimated time, origin, and bounds easier to compare before sending a job. Distinguish estimated state from measured machine state. |
| 7 | A smoother import workflow | Improve SVG/DXF scale checks, placement, duplicate-path visibility, and cut/engrave assignment, with useful messages when an import loses information. |
| 8 | Recovery and performance | Review autosave/recovery and undo behavior, then profile large SVGs and raster jobs to target demonstrated delays. Show progress and allow cancellation where supported. |

## Completed groundwork

- Bright default drawing bed on macOS, with saved color choices preserved.
- Repeatable uv setup and a short launch command.

## How to choose the next slice

Start with a desktop review of the current Mac interface and a typical file from
the user's workflow. Confirm the actual controller and supported feedback before
changing machine controls. Each selected behavior gets acceptance criteria,
tests, independent review, and matching documentation before it ships.
