# ruff: noqa: FA100 -- Python 3.6 cannot import future annotations.
import hashlib
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple
from uuid import uuid4

import wx
from wx.lib.scrolledpanel import ScrolledPanel

from meerk40t.gui.mwindow import MWindow
from meerk40t.kernel.context import Context

_ = wx.GetTranslation


class MaterialNotes(MWindow):
    def __init__(self, context: Context, path: str, parent: wx.Window) -> None:
        super().__init__(520, 680, context, path, parent)
        device = getattr(context, "device", None)
        self.device_path = getattr(device, "path", "")
        self.device_id = ""
        if self.device_path:
            device.setting(str, "material_notes_id", "")
            if not device.material_notes_id:
                device.material_notes_id = str(uuid4())
                device.write_persistent("material_notes_id", device.material_notes_id)
            self.device_id = device.material_notes_id
        identity = hashlib.sha256(
            json.dumps([self.device_path, self.device_id]).encode("utf-8")
        ).hexdigest()
        self.store_path = (
            Path(context.kernel.os_information["WORKDIR"])
            / "material-notes"
            / (identity + ".json")
        )
        panel = self.panel = ScrolledPanel(self, style=wx.TAB_TRAVERSAL)
        context.themes.set_window_colors(panel)
        layout = wx.BoxSizer(wx.VERTICAL)
        device_label = getattr(device, "label", _("No active device"))
        layout.Add(
            wx.StaticText(
                panel, label=_("Device: {device}").format(device=device_label)
            ),
            0,
            wx.EXPAND | wx.ALL,
            8,
        )
        layout.Add(
            wx.StaticText(
                panel,
                label=_("Observations only. Saving does not apply machine settings."),
            ),
            0,
            wx.EXPAND | wx.ALL,
            8,
        )
        self.inputs = {}  # type: Dict[str, wx.TextCtrl]
        self.fields = (
            ("material_name", _("Material")),
            ("thickness_mm", _("Thickness (mm)")),
            ("settings_tried", _("Settings tried")),
            ("observed_result", _("Observed result")),
        )
        for name, label in self.fields:
            layout.Add(wx.StaticText(panel, label=label), 0, wx.LEFT | wx.RIGHT, 8)
            style = (
                wx.TE_MULTILINE if name in ("settings_tried", "observed_result") else 0
            )
            control = wx.TextCtrl(panel, name=name, style=style)
            self.inputs[name] = control
            layout.Add(control, 0, wx.EXPAND | wx.ALL, 8)
        self.status = wx.StaticText(panel)
        layout.Add(self.status, 0, wx.EXPAND | wx.ALL, 8)
        save = wx.Button(panel, label=_("Save"))
        save.Enable(bool(self.device_path))
        save.Bind(wx.EVT_BUTTON, self.on_save)
        layout.Add(save, 0, wx.ALIGN_RIGHT | wx.ALL, 8)
        self.history = wx.TextCtrl(
            panel, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(-1, 180)
        )
        layout.Add(self.history, 1, wx.EXPAND | wx.ALL, 8)
        panel.SetSizer(layout)
        panel.SetupScrolling(scroll_x=False)
        self.sizer.Add(panel, 1, wx.EXPAND)
        self.SetTitle(_("Material Notes"))
        self.restore_aspect(honor_initial_values=True)
        if self.device_path:
            try:
                self.show_records(self.read_records())
            except (OSError, ValueError, UnicodeError) as error:
                self.show_error(error)
        else:
            self.status.SetLabel(_("Select a device, then reopen Material Notes."))

    def validate_record(self, record: Dict[str, str]) -> None:
        if not record["material_name"].strip():
            raise ValueError(_("Material is required. Enter a material name."))
        if not record["observed_result"].strip():
            raise ValueError(_("Observed result is required. Enter a result."))
        thickness = record["thickness_mm"].strip()
        if thickness:
            try:
                value = float(thickness)
            except ValueError as error:
                raise ValueError(
                    _("Enter a finite nonnegative thickness in mm.")
                ) from error
            if not math.isfinite(value) or value < 0:
                raise ValueError(_("Enter a finite nonnegative thickness in mm."))

    def read_records(self) -> List[Dict[str, str]]:
        try:
            with self.store_path.open("r", encoding="utf-8") as stream:
                data = json.load(stream)
        except FileNotFoundError:
            return []
        if (
            not isinstance(data, dict)
            or set(data) != {"device_path", "material_notes_id", "records"}
            or data["device_path"] != self.device_path
            or data["material_notes_id"] != self.device_id
            or not isinstance(data["records"], list)
        ):
            raise ValueError(
                _("Invalid material notes file. Recover a backup before saving.")
            )
        for record in data["records"]:
            if (
                not isinstance(record, dict)
                or set(record) != set(self.inputs)
                or not all(isinstance(value, str) for value in record.values())
            ):
                raise ValueError(
                    _("Invalid material notes record. Repair the file before saving.")
                )
            self.validate_record(record)
        return data["records"]

    def write_records(self, records: List[Dict[str, str]]) -> None:
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=str(self.store_path.parent),
                delete=False,
            ) as stream:
                temporary_path = Path(stream.name)
                json.dump(
                    {
                        "device_path": self.device_path,
                        "material_notes_id": self.device_id,
                        "records": records,
                    },
                    stream,
                    ensure_ascii=False,
                    allow_nan=False,
                )
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(str(temporary_path), str(self.store_path))
        finally:
            if temporary_path is not None and temporary_path.exists():
                temporary_path.unlink()

    def show_records(self, records: List[Dict[str, str]]) -> None:
        self.history.ChangeValue(
            "\n\n".join(
                "\n".join(f"{label}: {record[name]}" for name, label in self.fields)
                for record in records
            )
        )

    def show_error(self, error: Exception) -> None:
        self.status.SetLabel(
            _(
                "Cannot save or load material notes:\n{error}\nCheck the file and directory permissions,\nor recover a backup, then retry."
            ).format(error=error)
        )
        self.panel.Layout()
        self.panel.FitInside()
        self.Layout()

    def on_save(self, event: wx.CommandEvent) -> None:
        if not self.device_path:
            self.status.SetLabel(_("Select a device, then reopen Material Notes."))
            return
        record = {name: control.GetValue() for name, control in self.inputs.items()}
        try:
            self.validate_record(record)
            # Another open window may have saved since this window was opened.
            records = self.read_records()
            records.append(record)
            self.write_records(records)
        except (OSError, ValueError, UnicodeError) as error:
            self.show_error(error)
            return
        self.show_records(records)
        for control in self.inputs.values():
            control.ChangeValue("")
        self.status.SetLabel(_("Observation saved locally."))
        self.Layout()

    @staticmethod
    def submenu() -> Tuple[str, str]:
        return _("Tools"), _("Material Notes")

    @staticmethod
    def helptext() -> str:
        return _("Record local material test observations for this device")
