# Welcome to MeerK40t!
MeerK40t (pronounced MeerKat) is a built-from-the-ground-up MIT licensed open-source laser cutting software.

The primary goals of this software is simple:


* Provide users with high quality laser control software.
* Provide developers with a highly extensible platform to help further their own ideas, and provide novel work to the laser community at large.

## Getting started
To get up and running, simply download Meerk40t from [here](https://github.com/meerk40t/meerk40t/releases) for your specific platform. (Windows, Mac OSX, Linux, and by extension, Raspberry Pi).

## 🛠 Project Status: Maintenance Mode
**MeerK40t is currently in a low-maintenance phase.** The original maintainers have limited bandwidth for active development. What this means for users and contributors:
* **Response Times:** Issues and Pull Requests may not receive immediate feedback. Silence is not a lack of interest, but a lack of time.
* **Weekly Builds:** These are automated experimental snapshots. They **will** contain bugs and regressions. If you require a stable experience, please stick to the [latest stable Release](https://github.com/meerk40t/meerk40t/releases).
* **Contributions Welcome:** This project survives on community involvement. If you find a bug in a weekly build, the fastest way to get it fixed is to submit a Pull Request. 
* **Support:** Please use the [Discussions] tab or community forums for general help, as the Issue tracker is reserved for actionable bug reports and development tasks.

<details>
<summary>Release Versions (Just use the latest)</summary>


> * 0.9 - Active - New features and some underlying architectural changes. Try the latest released version: [0.9.9000](https://github.com/meerk40t/meerk40t/releases/tag/0.9.9000) (Jan 17, 2026) or try a prerelease even: [release list](https://github.com/meerk40t/meerk40t/releases)
> * 0.8 - Maintenance - may receive critical bugfixes but no more new features, latest version: [0.8.12](https://github.com/meerk40t/meerk40t/releases/tag/0.8.12000) (Oct 17, 2023)
> * 0.7 - Discontinued - K40 support only (including ruidacontrol emulator for 3rd party lasersoftware integration), latest version [0.7.10](https://github.com/meerk40t/meerk40t/releases/tag/0.7.10000) (June 13, 2023)
> * 0.6 - Discontinued - K40 support only, latest version: [0.6.24](https://github.com/meerk40t/meerk40t/releases/tag/0.6.24) (Oct 11, 2021)


</details>

### Command Line Interface

Meerk40t has an advanced internal console system allowing access to most parts of the code with various commands. It also provides a command line interface which should allow you to automate any processes. To learn more, download a version of Meerk40t for your platform, and execute it in a terminal with the ``--help`` argument to get a list of options.

## Compiling from source

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then run
these commands from your checkout:

```bash
uv sync --locked
uv run meerk40t
```

After the first install, `uv run meerk40t` is all you need. It runs this checkout
as an editable package, so local changes are picked up automatically. No virtual
environment activation is needed. The repository selects Python 3.13; uv can
download it if needed. Internet access is required for the initial install.

The default `desktop` group installs wxPython, Pillow, DXF support, HTTP and
WebSocket dependencies. Camera support is optional: use `uv run --extra cam
meerk40t`. Use `uv run meerk40t --simpleui` for the simplified interface.

The uv desktop workflow requires Python 3.8 or later. The package's legacy
Python requirement and setuptools metadata remain in place. On Linux, wxPython
may need native GTK development libraries and a source build when a compatible
wheel is unavailable; see the [wxPython installation guide](https://wxpython.org/pages/downloads/).
The locked desktop install is verified on Apple Silicon macOS with Python 3.13.

For development and verification:

```bash
uv sync --locked --group dev
uv run --group dev python -m unittest discover test -v
uv run python -m unittest testgui.test_gui_workspace_colors -v
```

GUI tests require access to a desktop display. `uv.lock` records dependency
versions, and `.python-version` selects the default interpreter. Packaging uses
the existing setuptools backend and console entry point, following
[uv's project packaging guidance](https://docs.astral.sh/uv/concepts/projects/config/).

### macOS workspace readability

On macOS, new workspaces use a light drawing bed and gray surrounding canvas,
including when macOS uses Dark Mode. Native controls still follow the system
appearance. Saved workspace colors are preserved.

Ruler labels choose a readable foreground when their configured color would
blend into the canvas, including translucent colors. Readable custom label
colors are kept, and this rendering adjustment does not rewrite saved colors.
Ruler bands keep a consistent backing when the bed is zoomed or panned beneath
them; the document inside the rulers is not changed.
Start, Pause, and Stop labels also use contrasting colors in both appearances.

To brighten an existing workspace, open **Preferences → Colors** and select
**Reset Colors to brighter defaults** in Dark Mode, or **Reset Colors to Default**
in Light Mode. Resetting replaces your custom workspace colors. Individual colors
can also be adjusted on that tab. Restarting retains the selected colors.

### Focused K40 workspace

Open **Tools → Tools → K40 Workspace**, or enter
`window toggle K40Workspace` in MeerK40t's console. This companion window saves
its size and position through the normal window settings.

It groups shortcuts to Controller, Navigation, Laser controls, Operations,
Material library, Material test, Properties, and Preferences. These open the
existing tools. The active device is shown, and K40-specific shortcuts are
disabled when another controller type is selected. A missing tool is reported
in the window. Opening or refreshing this workspace sends no machine commands.

The workspace includes a read-only job-summary snapshot: active device, bed
dimensions and scene-space design bounds in millimeters, then operations in
document order with enabled state, speed, controller power setting and effective
passes. The power value is a controller setting, not a measurement of tube output.
Missing or invalid values are shown as **Unavailable**. Click **Refresh** after
editing the artwork or settings to rebuild the snapshot.

The read-only **Design/import audit** reports scene-space bounds and dimensions
in millimeters, elements outside the configured bed, assignment counts and
unassigned identifiers, and groups of exact duplicate vectors. References under
disabled operations and nested effects count as assigned. Duplicates require
identical vector segment sequences and all six current transform values; styling
is ignored. Reversed paths, alternate encodings and equivalent geometry under
different transforms are not matched. Text and images are unsupported for duplicate
checks. Missing or invalid geometry and bed dimensions appear as limitations while
supported checks remain available; incomplete design bounds and dimensions are
unavailable. Click **Refresh** after editing. The audit never scales, classifies,
deletes, changes selections, or queues work.

Preview and framing shows scene origin (0, 0 mm), the configured home corner,
scene-space design bounds, and a **Software duration estimate** summed from enabled
operations. Missing or invalid estimates make the total **Unavailable**; the
estimate does not establish actual runtime or physical position. **Simulation**
prepares a separate plan through the existing planning pipeline and opens the
simulation only after preparation succeeds, without spooling it. Missing support
or preparation failures appear in the window. **Framing controls** opens the
existing laser-controls pane; it does not run an outline or move the machine.

The passive connection snapshot shows USB connection state from the existing
local handle, mock mode, or an **unverified** network connection. Network mode
takes precedence when both network and mock settings are enabled. It never opens
USB, probes a socket, or sends a machine command. Software controller state,
driver pause and queue size are separate observations; unavailable state stays
**Unknown**. Physical position and tube output remain unknown, and an empty
software queue does not confirm that a physical job has finished. Connection
errors and inaccessible status values appear with a next step while the other
reports and tools remain available. Use **Refresh** to collect a new snapshot.

Open **Material notes** from the companion's Materials group, or use
`window toggle MaterialNotes`. The separate window stays bound to the displayed
device even if you select another machine. Enter a Material and Observed result;
Thickness (mm) is optional and must be finite and nonnegative when supplied.
Settings tried is free text. **Save** records the observation and clears the form;
it never applies settings or runs a test. Material library and Material test open
the established tools without applying presets or starting a job.

Notes reload by the device's service path and a persistent `material_notes_id`
in its settings, independently of its label. Deleting a device and creating a
replacement at the same path gives the replacement a new identifier and separate
notes. Duplicating a device also gives the duplicate a separate identifier.
Removed devices' files and older path-only files remain available for
manual recovery; they are never automatically assigned to another device.
The identifier reaches disk through normal configuration saving. A first-session
crash before that save can leave a notes file requiring manual recovery.
Notes are local JSON files in the `material-notes` directory under MeerK40t's
application work directory. Saves replace the file atomically and preserve notes
saved by other open windows. Save or load errors appear in the window; a failed
save retains the draft and previous records so you can correct permissions and
retry. A corrupt file must be repaired or recovered from your backup before saving.

The wxMeerK40t is the GUI and is written in wxPython. We use AUI to allow to have a very highly configurable UI. We can easily add panes and tools and there are quite a few available already.

See [ROADMAP.md](ROADMAP.md) for proposed improvements to this fork's macOS and
K40/Lihuiyu workflow.

## Screenshots
![grafik](https://github.com/user-attachments/assets/e56135a2-7b1f-44be-9761-b92931e300f6)

## Drivers

Meerk40t provides a variety of drivers with an extensible framework to provide support for other new laser devices. The code was written with the myriad of possibilities for different software in mind. For example, it may be essential that GRBL be able to reset an alarm or notify the user of particular error codes. The configuration for GRBL is not the same for the configuration of other laser control drivers. With this in mind, MeerK40t can radically change how and when it works


### Supported devices
*   Lihuiyu M2/M3-Nano (aka K40 lasers)
*   Any GRBL device (Atomstack, Creality, Longer, Ortur etc...)
*   Ezcad2-compatible JCZ controllers galvo lasers
*   Moshiboard
*   NewlyDraw System 8.1 Lasers
*   Devices with Ruida-controller
*   Ruida-Emulation (Middleman between Lightburn and K40)
