from functools import partial
from typing import List, Tuple

import wx
from wx.lib.scrolledpanel import ScrolledPanel

from meerk40t.gui.k40reports import (
    build_connection_report,
    build_job_summary,
    build_preview_report,
)
from meerk40t.gui.mwindow import MWindow
from meerk40t.kernel import signal_listener
from meerk40t.kernel.context import Context

_ = wx.GetTranslation


class K40WorkspacePanel(ScrolledPanel):
    def __init__(self, parent: wx.Window, context: Context) -> None:
        super().__init__(parent, style=wx.TAB_TRAVERSAL)
        self.context = context
        context.themes.set_window_colors(self)
        self.machine_buttons: List[wx.Button] = []  # noqa: FA100 - Python 3.6 compatibility.
        layout = wx.BoxSizer(wx.VERTICAL)
        self.device_status = wx.StaticText(self)
        self.error = wx.StaticText(self)
        layout.Add(self.device_status, 0, wx.EXPAND | wx.ALL, 8)
        layout.Add(self.error, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)
        groups = (
            (
                _("Machine tools"),
                (
                    (_("Controller"), "window/Controller", True),
                    (_("Navigation"), "window/Navigation", True),
                    (_("Laser controls"), "pane/laser", True),
                ),
            ),
            (
                _("Job review"),
                (
                    (_("Operations"), "window/OperationInfo", False),
                    (_("Preferences"), "window/Preferences", False),
                ),
            ),
            (
                _("Materials"),
                (
                    (_("Material library"), "window/MatManager", False),
                    (_("Material test"), "window/Templatetool", False),
                    (_("Material notes"), "window/MaterialNotes", False),
                ),
            ),
            (_("Document checks"), ((_("Properties"), "window/Properties", False),)),
        )
        for title, tools in groups:
            group = wx.StaticBoxSizer(wx.VERTICAL, self, title)
            for label, path, machine_specific in tools:
                button = wx.Button(group.GetStaticBox(), label=label)
                button.Bind(
                    wx.EVT_BUTTON,
                    partial(self.open_tool, label, path, machine_specific),
                )
                group.Add(button, 0, wx.EXPAND | wx.ALL, 3)
                if machine_specific:
                    self.machine_buttons.append(button)
            layout.Add(group, 0, wx.EXPAND | wx.ALL, 8)
        self.job_summary = wx.TextCtrl(
            self, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(-1, 180)
        )
        self.job_summary.SetMinSize((-1, 180))
        layout.Add(self.job_summary, 0, wx.EXPAND | wx.ALL, 8)
        self.connection_report = wx.TextCtrl(
            self, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(-1, 180)
        )
        self.connection_report.SetMinSize((-1, 180))
        layout.Add(self.connection_report, 0, wx.EXPAND | wx.ALL, 8)
        preview = wx.StaticBoxSizer(wx.VERTICAL, self, _("Preview and framing"))
        self.preview_report = wx.TextCtrl(
            preview.GetStaticBox(),
            style=wx.TE_MULTILINE | wx.TE_READONLY,
            size=(-1, 130),
        )
        self.preview_report.SetMinSize((-1, 130))
        preview.Add(self.preview_report, 0, wx.EXPAND | wx.ALL, 3)
        simulation = wx.Button(preview.GetStaticBox(), label=_("Simulation"))
        simulation.Bind(wx.EVT_BUTTON, self.on_simulation)
        preview.Add(simulation, 0, wx.EXPAND | wx.ALL, 3)
        framing = wx.Button(preview.GetStaticBox(), label=_("Framing controls"))
        framing.Bind(
            wx.EVT_BUTTON,
            partial(self.open_tool, _("Framing controls"), "pane/laser", True),
        )
        self.machine_buttons.append(framing)
        preview.Add(framing, 0, wx.EXPAND | wx.ALL, 3)
        layout.Add(preview, 0, wx.EXPAND | wx.ALL, 8)
        refresh = wx.Button(self, label=_("Refresh"))
        refresh.Bind(wx.EVT_BUTTON, self.on_refresh)
        layout.Add(refresh, 0, wx.ALIGN_RIGHT | wx.ALL, 8)
        self.SetSizer(layout)
        self.SetupScrolling(scroll_x=False)
        self.refresh_data()

    def supported_device(self) -> bool:
        device = getattr(self.context, "device", None)
        return getattr(device, "name", None) == "LihuiyuDevice"

    def refresh_data(self) -> None:
        device = getattr(self.context, "device", None)
        supported = self.supported_device()
        if device is None:
            status = _("No active device")
        elif supported:
            status = _("{device} — K40 / Lihuiyu").format(device=device.label)
        else:
            status = _("{device} — unsupported device").format(device=device.label)
        self.device_status.SetLabel(status)
        for button in self.machine_buttons:
            button.Enable(supported)
        self.job_summary.ChangeValue(build_job_summary(self.context, _))
        self.connection_report.ChangeValue(build_connection_report(self.context, _))
        self.preview_report.ChangeValue(build_preview_report(self.context, _))
        self.Layout()

    def open_tool(
        self, label: str, path: str, machine_specific: bool, event: wx.CommandEvent
    ) -> None:
        self.refresh_data()
        if machine_specific and not self.supported_device():
            self.error.SetLabel(_("This tool requires an active K40 / Lihuiyu device."))
        elif self.context.lookup(path) is None:
            self.error.SetLabel(_("{tool} is unavailable.").format(tool=label))
        else:
            self.error.SetLabel("")
            kind, name = path.split("/", 1)
            if kind == "pane":
                self.context(f"pane show {name}\n")
            else:
                self.context(f"window toggle {name}\n")
        self.Layout()

    def on_refresh(self, event: wx.CommandEvent) -> None:
        self.refresh_data()

    def on_simulation(self, event: wx.CommandEvent) -> None:
        planner = getattr(self.context, "planner", None)
        if not callable(getattr(planner, "get_free_plan", None)) or not callable(
            getattr(planner, "is_finished", None)
        ):
            self.error.SetLabel(_("Simulation planner is unavailable."))
        elif self.context.lookup("window/Simulation") is None:
            self.error.SetLabel(_("Simulation is unavailable."))
        else:
            try:
                plan = planner.get_free_plan()
                self.context(f"plan{plan} clear copy preprocess validate blob finish\n")
                # Validation reports some failures without raising a command error.
                if not planner.is_finished(plan):
                    self.error.SetLabel(_("Simulation preparation failed."))
                else:
                    self.context(f"window open Simulation {plan} 0 0\n")
                    self.error.SetLabel("")
            except (
                ArithmeticError,
                AttributeError,
                OSError,
                RuntimeError,
                TypeError,
                ValueError,
            ) as error:
                self.error.SetLabel(
                    _("Simulation preparation failed: {error}").format(error=error)
                )
        self.Layout()
        self.FitInside()
        if self.error.GetLabel():
            self.ScrollChildIntoView(self.error)

    @signal_listener("activate;device")
    def on_device_change(self, origin: str, *args: object) -> None:
        self.refresh_data()


class K40Workspace(MWindow):
    def __init__(self, context: Context, path: str, parent: wx.Window) -> None:
        super().__init__(450, 650, context, path, parent)
        self.panel = K40WorkspacePanel(self, context)
        self.sizer.Add(self.panel, 1, wx.EXPAND)
        self.add_module_delegate(self.panel)
        self.SetTitle(_("K40 Workspace"))
        self.restore_aspect(honor_initial_values=True)

    @staticmethod
    def submenu() -> Tuple[str, str]:  # noqa: FA100 - Python 3.6 compatibility.
        return _("Tools"), _("K40 Workspace")

    @staticmethod
    def helptext() -> str:
        return _("Open existing tools for a K40 / Lihuiyu laser")
