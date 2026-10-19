import builtins
import io
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import wx

from meerk40t.gui.mwindow import MWindow
from meerk40t.kernel import Service
from testgui.test_gui_k40workspace import descendants, make_context


class TestMaterialNotes(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.owns_app = wx.App.Get() is None
        cls.app = wx.App.Get() or wx.App(False)

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.owns_app:
            cls.app.Destroy()

    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.context = make_context("LihuiyuDevice")
        self.context.kernel.os_information["WORKDIR"] = self.directory.name
        self.context.elements = SimpleNamespace(
            ops=lambda: iter(()), elems=lambda: iter(())
        )
        self.parent = wx.Frame(None)
        self.context.gui = self.parent
        self.windows = []
        self.commands = []
        self.context.kernel.console = self.commands.append
        self.first_device = self.context.device
        self.first_device.speed = 9.5
        self.first_device.power = 321

    def tearDown(self) -> None:
        for window in self.windows:
            window.Destroy()
        self.context.opened.clear()
        self.parent.Destroy()
        self.app.ProcessPendingEvents()

    def open_notes(self) -> wx.Window:
        registered = self.context.lookup("window/MaterialNotes")
        self.assertIsNotNone(registered, "GUI registration must expose MaterialNotes")
        self.assertTrue(issubclass(registered, MWindow))
        window = registered(self.context, "window/MaterialNotes", self.parent)
        self.windows.append(window)
        return window

    def control(self, window: wx.Window, name: str) -> wx.TextCtrl:
        matches = [
            child
            for child in descendants(window)
            if isinstance(child, wx.TextCtrl) and child.GetName() == name
        ]
        self.assertEqual(len(matches), 1, "Expected input " + name)
        return matches[0]

    def fill(self, window: wx.Window, **values: str) -> None:
        defaults = {
            "material_name": "Fixture mineral-fiber analogue",
            "thickness_mm": "2.75",
            "settings_tried": "speed 9.5 mm/s, controller setting 321, one pass",
            "observed_result": "Fixture edge remained attached",
        }
        defaults.update(values)
        for name, value in defaults.items():
            self.control(window, name).SetValue(value)

    def save(self, window: wx.Window) -> None:
        buttons = [
            child
            for child in descendants(window)
            if isinstance(child, wx.Button) and child.GetLabel() == "Save"
        ]
        self.assertEqual(len(buttons), 1)
        event = wx.CommandEvent(wx.EVT_BUTTON.typeId, buttons[0].GetId())
        event.SetEventObject(buttons[0])
        buttons[0].GetEventHandler().ProcessEvent(event)

    def text(self, window: wx.Window, include_inputs: bool = True) -> str:
        texts = []
        input_names = {
            "material_name",
            "thickness_mm",
            "settings_tried",
            "observed_result",
        }
        for child in descendants(window):
            if isinstance(child, wx.StaticText):
                texts.append(child.GetLabel())
            elif isinstance(child, wx.TextCtrl):
                if include_inputs or child.GetName() not in input_names:
                    texts.append(child.GetValue())
            elif isinstance(child, wx.ListCtrl):
                texts.extend(
                    " | ".join(
                        child.GetItemText(row, column)
                        for column in range(child.GetColumnCount())
                    )
                    for row in range(child.GetItemCount())
                )
        return "\n".join(texts)

    def stored_files(self) -> dict:
        directory = Path(self.directory.name)
        return {
            str(path.relative_to(directory)): path.read_bytes()
            for path in directory.rglob("*.json")
        }

    def draft(self, window: wx.Window) -> dict:
        return {
            name: self.control(window, name).GetValue()
            for name in (
                "material_name",
                "thickness_mm",
                "settings_tried",
                "observed_result",
            )
        }

    def second_device(self, label: str = "Fixture CO2") -> Service:
        device = Service(self.context.kernel, "fixture-second-machine")
        device.name = "LihuiyuDevice"
        device.label = label
        self.context.kernel.add_service("device", device)
        self.context.kernel.activate_service_path("device", device.path)
        return device

    def test_ac_u07_1_material_notes_shortcut_opens_registered_managed_window(
        self,
    ) -> None:
        self.open_notes()
        workspace_class = self.context.lookup("window/K40Workspace")
        workspace = workspace_class(self.context, "window/K40Workspace", self.parent)
        self.windows.append(workspace)
        buttons = [
            child
            for child in descendants(workspace)
            if isinstance(child, wx.Button)
            and child.GetLabel().lower() == "material notes"
        ]
        self.assertEqual(len(buttons), 1)
        event = wx.CommandEvent(wx.EVT_BUTTON.typeId, buttons[0].GetId())
        event.SetEventObject(buttons[0])
        buttons[0].GetEventHandler().ProcessEvent(event)
        self.assertEqual(self.commands, ["window toggle MaterialNotes\n"])

    def test_ac_u07_2_explicit_save_reloads_observation_without_applying_settings(
        self,
    ) -> None:
        window = self.open_notes()
        self.fill(window)
        self.assertEqual(self.stored_files(), {}, "Draft input must not save itself")
        self.save(window)
        self.assertTrue(self.stored_files(), "Explicit save must create local JSON")
        settings_path = Path(self.directory.name, "fixture-settings.cfg")
        self.first_device.flush()
        self.context.kernel.write_configuration(settings_path)
        self.context = make_context("LihuiyuDevice")
        self.context.kernel.read_configuration(settings_path)
        self.context.kernel.os_information["WORKDIR"] = self.directory.name
        self.context.gui = self.parent
        self.context.kernel.console = self.commands.append
        report = self.text(self.open_notes())
        self.assertIn("Fixture mineral-fiber analogue", report)
        self.assertIn("2.75", report)
        self.assertIn("speed 9.5 mm/s, controller setting 321, one pass", report)
        self.assertIn("Fixture edge remained attached", report)
        self.assertEqual(self.commands, [])
        self.assertEqual(self.first_device.speed, 9.5)
        self.assertEqual(self.first_device.power, 321)

    def test_ac_u07_2_reused_service_path_does_not_expose_deleted_machine_notes(
        self,
    ) -> None:
        first = self.open_notes()
        self.fill(first, material_name="Fixture deleted-machine observation")
        self.save(first)
        previous = self.stored_files()
        self.second_device()
        services = list(self.context.kernel.services("device"))
        self.context.kernel.destroy_service_index(
            "device", services.index(self.first_device)
        )
        replacement = Service(self.context.kernel, self.first_device.path)
        replacement.name = "LihuiyuDevice"
        replacement.label = self.first_device.label
        self.context.kernel.add_service("device", replacement)
        self.context.kernel.activate_service_path("device", replacement.path)
        reopened = self.open_notes()
        self.assertNotIn("Fixture deleted-machine observation", self.text(reopened))
        self.assertEqual(self.stored_files(), previous)
        self.fill(reopened, material_name="Fixture replacement-machine observation")
        self.save(reopened)
        report = self.text(self.open_notes())
        self.assertIn("Fixture replacement-machine observation", report)
        self.assertNotIn("Fixture deleted-machine observation", report)
        for name, contents in previous.items():
            self.assertEqual(self.stored_files()[name], contents)
        self.assertEqual(self.commands, [])

    def test_ac_u07_2_machine_identity_isolates_notes_even_with_same_label(
        self,
    ) -> None:
        first = self.open_notes()
        self.fill(first, material_name="Fixture first-machine stock")
        self.save(first)
        self.second_device()
        second = self.open_notes()
        self.assertNotIn("Fixture first-machine stock", self.text(second))
        self.fill(second, material_name="Fixture second-machine stock")
        self.save(second)
        self.context.kernel.activate_service_path("device", self.first_device.path)
        reopened = self.text(self.open_notes())
        self.assertIn("Fixture first-machine stock", reopened)
        self.assertNotIn("Fixture second-machine stock", reopened)
        self.assertEqual(self.commands, [])

    def test_ac_u07_2_device_switch_keeps_draft_bound_to_opening_machine(self) -> None:
        window = self.open_notes()
        self.fill(window, material_name="Fixture bound observation")
        self.second_device("Fixture different machine")
        self.context.kernel.process_queue()
        self.assertEqual(
            self.control(window, "material_name").GetValue(),
            "Fixture bound observation",
        )
        self.assertIn("Fixture CO2", self.text(window, include_inputs=False))
        self.save(window)
        self.assertNotIn("Fixture bound observation", self.text(self.open_notes()))
        self.context.kernel.activate_service_path("device", self.first_device.path)
        self.assertIn("Fixture bound observation", self.text(self.open_notes()))
        self.assertEqual(self.commands, [])

    def test_ac_u07_3_invalid_required_or_thickness_input_keeps_existing_records(
        self,
    ) -> None:
        window = self.open_notes()
        self.fill(window, material_name="Fixture prior valid note")
        self.save(window)
        previous = self.stored_files()
        invalid_cases = (
            ("material_name", "", "material"),
            ("material_name", "   ", "material"),
            ("observed_result", "", "result"),
            ("observed_result", "   ", "result"),
            ("thickness_mm", "-0.01", "thickness"),
            ("thickness_mm", "nan", "thickness"),
            ("thickness_mm", "inf", "thickness"),
            ("thickness_mm", "1e999", "thickness"),
            ("thickness_mm", "fixture invalid number", "thickness"),
        )
        for field, value, error_field in invalid_cases:
            with self.subTest(field=field, value=value):
                self.fill(window, **{field: value})
                draft = self.draft(window)
                self.save(window)
                self.assertEqual(self.stored_files(), previous)
                self.assertEqual(self.draft(window), draft)
                error = self.text(window, include_inputs=False).lower()
                self.assertIn(error_field, error)
                self.assertRegex(
                    error, r"required|enter|finite|nonnegative|non-negative|valid"
                )
        self.assertIn("Fixture prior valid note", self.text(self.open_notes()))

    def test_ac_u07_3_blank_zero_and_fractional_thickness_are_valid(self) -> None:
        for thickness in ("", "0", "2.75"):
            with self.subTest(thickness=thickness):
                window = self.open_notes()
                marker = "Fixture accepted thickness " + (thickness or "blank")
                self.fill(window, thickness_mm=thickness, observed_result=marker)
                self.save(window)
                self.assertIn(marker, self.text(self.open_notes()))
        self.assertEqual(self.commands, [])

    def test_ac_u07_3_write_failure_preserves_draft_existing_notes_and_retry(
        self,
    ) -> None:
        window = self.open_notes()
        self.fill(window, material_name="Fixture prior recoverable note")
        self.save(window)
        previous = self.stored_files()
        self.fill(window, material_name="Fixture retryable draft")
        draft = self.draft(window)
        original_open, original_io_open, original_os_open = (
            builtins.open,
            io.open,
            os.open,
        )

        def open_file(
            file: object, mode: str = "r", *args: object, **kwargs: object
        ) -> object:
            if any(flag in mode for flag in "wax+"):
                raise PermissionError(
                    "fixture material notes directory is not writable"
                )
            return original_open(file, mode, *args, **kwargs)

        def io_open_file(
            file: object, mode: str = "r", *args: object, **kwargs: object
        ) -> object:
            if any(flag in mode for flag in "wax+"):
                raise PermissionError(
                    "fixture material notes directory is not writable"
                )
            return original_io_open(file, mode, *args, **kwargs)

        def os_open_file(
            path: object, flags: int, *args: object, **kwargs: object
        ) -> int:
            if flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT):
                raise PermissionError(
                    "fixture material notes directory is not writable"
                )
            return original_os_open(path, flags, *args, **kwargs)

        with (
            patch("builtins.open", side_effect=open_file),
            patch("io.open", side_effect=io_open_file),
            patch("os.open", side_effect=os_open_file),
        ):
            self.save(window)
        self.assertEqual(self.stored_files(), previous)
        self.assertEqual(self.draft(window), draft)
        error = self.text(window, include_inputs=False).lower()
        self.assertIn("not writable", error)
        self.assertRegex(error, r"retry|check|permission|directory")
        reopened = self.text(self.open_notes())
        self.assertIn("Fixture prior recoverable note", reopened)
        self.assertNotIn("Fixture retryable draft", reopened)
        self.save(window)
        self.assertIn("Fixture retryable draft", self.text(self.open_notes()))
        self.assertEqual(self.commands, [])

    def test_ac_u07_3_replace_failure_preserves_records_draft_and_retry(self) -> None:
        window = self.open_notes()
        self.fill(window, material_name="Fixture prior atomic note")
        self.save(window)
        previous = self.stored_files()
        self.fill(window, material_name="Fixture atomic retry draft")
        draft = self.draft(window)
        with patch(
            "os.replace", side_effect=OSError("fixture atomic replacement failed")
        ):
            self.save(window)
        self.assertEqual(self.stored_files(), previous)
        self.assertEqual(self.draft(window), draft)
        error = self.text(window, include_inputs=False).lower()
        self.assertIn("atomic replacement failed", error)
        self.assertRegex(error, r"check|retry|permission|file")
        report = self.text(self.open_notes())
        self.assertIn("Fixture prior atomic note", report)
        self.assertNotIn("Fixture atomic retry draft", report)
        self.save(window)
        report = self.text(self.open_notes())
        self.assertIn("Fixture prior atomic note", report)
        self.assertIn("Fixture atomic retry draft", report)
        self.assertEqual(self.commands, [])

    def test_ac_u07_3_corrupt_store_is_reported_and_not_overwritten(self) -> None:
        window = self.open_notes()
        self.fill(window)
        self.save(window)
        for relative_path in self.stored_files():
            Path(self.directory.name, relative_path).write_text(
                '{"fixture interrupted record":', encoding="utf-8"
            )
        previous = self.stored_files()
        reopened = self.open_notes()
        error = self.text(reopened, include_inputs=False).lower()
        self.assertRegex(error, r"error|failed|cannot|unable|invalid|corrupt")
        self.assertRegex(error, r"check|recover|repair|backup|permission|file")
        self.fill(reopened, material_name="Fixture recovery draft")
        draft = self.draft(reopened)
        self.save(reopened)
        self.assertEqual(self.stored_files(), previous)
        self.assertEqual(self.draft(reopened), draft)
        self.assertEqual(self.commands, [])

    def test_ac_u07_3_unreadable_store_is_reported_and_not_overwritten(self) -> None:
        window = self.open_notes()
        self.fill(window)
        self.save(window)
        previous = self.stored_files()
        paths = {Path(self.directory.name, name) for name in previous}
        original_open = io.open

        def open_file(
            file: object, mode: str = "r", *args: object, **kwargs: object
        ) -> object:
            if (
                isinstance(file, (str, os.PathLike))
                and Path(file) in paths
                and "r" in mode
            ):
                raise PermissionError("fixture notes file is not readable")
            return original_open(file, mode, *args, **kwargs)

        with (
            patch("builtins.open", side_effect=open_file),
            patch("io.open", side_effect=open_file),
        ):
            reopened = self.open_notes()
            error = self.text(reopened, include_inputs=False).lower()
            self.assertIn("not readable", error)
            self.assertRegex(error, r"check|retry|permission|file")
            self.fill(reopened, material_name="Fixture unreadable-store draft")
            draft = self.draft(reopened)
            self.save(reopened)
            self.assertEqual(self.draft(reopened), draft)
        self.assertEqual(self.stored_files(), previous)
        self.assertIn("Fixture mineral-fiber analogue", self.text(self.open_notes()))
        self.assertEqual(self.commands, [])
