# Proposed improvements

The user accepted this sequence for the fork. Implementation proceeds as small
vertical slices; the status table is in [ITERATIONS.md](ITERATIONS.md) and the
acceptance criteria are in [engineering/PRODUCT.md](engineering/PRODUCT.md) and
its linked unit files. Items below describe the direction, not completed features.
The starting point is a Mac user
with a K40/Lihuiyu CO₂ laser. Many underlying capabilities already exist in
MeerK40t; the focus is making them easier to find, understand, and trust.

| Priority | Improvement | Intended result |
| --- | --- | --- |
| 1 | Continue Mac readability polish | Ruler-label contrast and backing are implemented. Review the rendered workspace, then improve grid contrast, selection handles, icons, and toolbar labels in light and dark appearances. |
| 2 | A focused K40 workspace (first slice) | A managed companion window now groups shortcuts to existing machine, operation, preference, property, and material tools. Connection diagnosis, job summary, material notes, and additional workflow improvements remain future slices. |
| 3 | A clearer job summary | Before starting, show operation order, speed and power settings with units, passes, dimensions, and placement on the bed. Make the selected device obvious. |
| 4 | Better connection diagnostics | Explain USB connection failures and recovery steps, and distinguish connected, idle, queued, paused, and disconnected states. Never report hardware feedback the controller does not provide. |
| 5 | Materials and test results | Make existing material presets and test patterns easier to use; record material thickness, settings, and observed results locally for the actual machine. Avoid universal power recommendations. |
| 6 | Easier preview and framing | Make existing simulation, travel paths, estimated time, origin, and bounds easier to compare before sending a job. Distinguish estimated state from measured machine state. |
| 7 | A smoother import workflow | Improve SVG/DXF scale checks, placement, duplicate-path visibility, and cut/engrave assignment, with useful messages when an import loses information. |
| 8 | Recovery and performance | Review autosave/recovery and undo behavior, then profile large SVGs and raster jobs to target demonstrated delays. Show progress and allow cancellation where supported. |

## Completed groundwork

- Bright default drawing bed on macOS, with saved color choices preserved.
- Repeatable uv setup and a short launch command.
- First readability slice: ruler labels remain legible over the bed and canvas without changing saved palette values.
- First K40 workspace slice: a managed Tools window opens existing tools and reports active device support without sending hardware commands.

## How to choose the next slice

Start with a desktop review of the current Mac interface and a typical file from
the user's workflow. Confirm the actual controller and supported feedback before
changing machine controls. Each selected behavior gets acceptance criteria,
tests, independent review, and matching documentation before it ships.
