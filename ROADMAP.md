# Proposed improvements

The user accepted this sequence for the fork. The first accepted vertical slices
U03–U10 are complete; their status is in [ITERATIONS.md](ITERATIONS.md) and the
acceptance criteria are in [engineering/PRODUCT.md](engineering/PRODUCT.md) and
its linked unit files. Broader polish and workflow directions remain in the
optional backlog.
The starting point is a Mac user
with a K40/Lihuiyu CO₂ laser. Many underlying capabilities already exist in
MeerK40t; the focus is making them easier to find, understand, and trust.

| Status | Direction | Current scope |
| --- | --- | --- |
| Backlog | Mac readability polish | Ruler-label contrast and backing are implemented. Reviewing the rendered workspace, grid contrast, selection handles, icons, and toolbar labels in light and dark appearances remains optional. |
| Done | Focused K40 workspace and reports | The managed companion, job summary, passive diagnosis, local material notes, preview/framing, design/import audit, and reliable autosave/report profiling first slices are implemented. |
| Backlog | Real-file and raster performance | Profile representative user files and raster jobs when a measured performance concern arises; target only demonstrated delays. |
| Backlog | Physical hardware checks | Optional checks on the user's actual K40/controller workflow remain outside the completed software verification. |

## Completed groundwork

- Bright default drawing bed on macOS, with saved color choices preserved.
- Repeatable uv setup and a short launch command.
- First readability slice: ruler labels remain legible over the bed and canvas without changing saved palette values.
- First K40 workspace slice: a managed Tools window opens existing tools and reports active device support without sending hardware commands.
- U05–U10 first slices: read-only job summary, passive connection diagnosis, local material notes, preview/framing, design/import audit, and retryable atomic autosave with synthetic report measurements.

## How to choose the next slice

Only start another slice if the user selects a remaining direction. Confirm the
actual controller and supported feedback before changing machine controls. Any
selected behavior gets acceptance criteria, tests, independent review, and
matching documentation before it ships.
