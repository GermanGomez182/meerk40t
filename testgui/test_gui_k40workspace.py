import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import wx

from meerk40t.gui.mwindow import MWindow
from meerk40t.gui.themes import Themes
from meerk40t.gui.wxmeerk40t import wxMeerK40t
from meerk40t.kernel import Kernel, Service
from meerk40t.kernel.context import Context


def make_context(device: object = None) -> Context:
    kernel = Kernel("K40WorkspaceTests", "0", "fixture", ignore_settings=True)
    kernel.args = SimpleNamespace()
    context = kernel.root
    context.themes = Themes(kernel)
    wxMeerK40t.sub_register(kernel)
    # Use the application's registration path without constructing a second wx.App.
    wxMeerK40t.module_open(SimpleNamespace(context=context))
    if device is not None:
        service = Service(kernel, "fixture-device")
        service.name = device
        service.label = "Fixture CO2" if device == "LihuiyuDevice" else "Fixture GRBL"
        service.register("window/Controller", object)
        kernel.add_service("device", service, activate=True)
    else:
        context.device = None
    kernel.register("pane/laser", SimpleNamespace(name="laser"))
    context.test_commands = []
    return context


def descendants(window: wx.Window) -> list:
    result = []
    for child in window.GetChildren():
        result.append(child)
        result.extend(descendants(child))
    return result


class TestK40Workspace(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = wx.App(False)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.app.Destroy()

    def setUp(self) -> None:
        self.context = make_context("LihuiyuDevice")
        self.parent = wx.Frame(None)
        self.context.gui = self.parent
        self.windows = []

    def tearDown(self) -> None:
        for window in self.windows:
            if window:
                window.Destroy()
        self.context.opened.clear()
        self.parent.Destroy()
        self.app.ProcessPendingEvents()

    def workspace_class(self) -> type:
        window_class = self.context.lookup("window/K40Workspace")
        self.assertIsNotNone(
            window_class, "GUI registration must expose window/K40Workspace"
        )
        return window_class

    def make_window(self) -> MWindow:
        window = self.workspace_class()(
            self.context, "window/K40Workspace", self.parent
        )
        self.windows.append(window)
        return window

    def button(self, window: wx.Window, label: str) -> wx.Button:
        matches = [
            child
            for child in descendants(window)
            if isinstance(child, wx.Button) and child.GetLabel() == label
        ]
        self.assertEqual(len(matches), 1, "Expected one shortcut: " + label)
        return matches[0]

    def click(self, button: wx.Button) -> None:
        event = wx.CommandEvent(wx.EVT_BUTTON.typeId, button.GetId())
        event.SetEventObject(button)
        button.GetEventHandler().ProcessEvent(event)

    def labels(self, window: wx.Window) -> list:
        return [child.GetLabel() for child in descendants(window)]

    def record_commands(self) -> list:
        commands = self.context.test_commands
        self.context.kernel.console = commands.append
        return commands

    def test_existing_gui_registration_fixture_still_exposes_navigation(self) -> None:
        self.assertIsNotNone(self.context.lookup("window/Navigation"))

    def test_ac_u04_1_window_menu_uses_managed_window_conventions(self) -> None:
        window_class = self.workspace_class()
        self.assertTrue(issubclass(window_class, MWindow))
        submenu = window_class.submenu()
        self.assertIsInstance(submenu, tuple)
        self.assertEqual(len(submenu), 2)
        self.assertTrue(all(isinstance(part, str) and part for part in submenu))

    def test_ac_u04_1_console_toggle_opens_with_saved_geometry(self) -> None:
        self.workspace_class()
        saved = self.context.get_context("window/K40Workspace")
        saved.width = 610
        saved.height = 460
        self.context("window toggle K40Workspace\n")
        window = self.context.opened.get("window/K40Workspace")
        self.assertIsNotNone(window)
        self.windows.append(window)
        self.assertTrue(window.IsShown())
        self.assertEqual(tuple(window.GetSize()), (610, 460))
        self.assertIs(window.window_context, saved)
        self.assertTrue(window.window_save)

    def test_ac_u04_1_groups_and_shortcuts_are_translated(self) -> None:
        window_class = self.workspace_class()
        module = sys.modules[window_class.__module__]
        with patch.object(module, "_", side_effect=lambda text: "TR:" + text):
            window = self.make_window()
        labels = self.labels(window)
        for label in (
            "Machine tools",
            "Job review",
            "Materials",
            "Document checks",
            "Controller",
            "Navigation",
            "Operations",
            "Preferences",
            "Laser controls",
            "Material library",
            "Material test",
            "Properties",
        ):
            with self.subTest(label=label):
                self.assertIn("TR:" + label, labels)

    def test_ac_u04_2_shortcuts_dispatch_established_tools(self) -> None:
        window = self.make_window()
        commands = self.record_commands()
        for label, command in (
            ("Controller", "window toggle Controller\n"),
            ("Navigation", "window toggle Navigation\n"),
            ("Operations", "window toggle OperationInfo\n"),
            ("Preferences", "window toggle Preferences\n"),
            ("Laser controls", "pane show laser\n"),
            ("Material library", "window toggle MatManager\n"),
            ("Material test", "window toggle Templatetool\n"),
            ("Properties", "window toggle Properties\n"),
        ):
            with self.subTest(label=label):
                commands.clear()
                button = self.button(window, label)
                self.assertTrue(button.IsEnabled())
                self.click(button)
                self.assertEqual(commands, [command])

    def test_ac_u04_2_opening_and_refreshing_dispatch_no_commands(self) -> None:
        commands = self.record_commands()
        window = self.make_window()
        window.panel.refresh_data()
        window.panel.refresh_data()
        self.assertEqual(commands, [])
        labels = self.labels(window)
        self.assertFalse(
            any(
                isinstance(child, wx.Button)
                and child.GetLabel().lower() in ("start", "home", "fire", "connect")
                for child in descendants(window)
            ),
            labels,
        )

    def test_ac_u04_3_device_switch_updates_label_and_supported_tools(self) -> None:
        window = self.make_window()
        self.assertIn("Fixture CO2", " ".join(self.labels(window)))
        kernel = self.context.kernel
        device = Service(kernel, "fixture-grbl")
        device.name = "GRBLDevice"
        device.label = "Fixture GRBL"
        kernel.add_service("device", device)
        commands = self.record_commands()
        kernel.activate_service_path("device", device.path)
        window.panel.refresh_data()
        labels = " ".join(self.labels(window))
        self.assertIn("Fixture GRBL", labels)
        self.assertNotIn("Fixture CO2", labels)
        self.assertIn("unsupported", labels.lower())
        for label in ("Controller", "Navigation", "Laser controls"):
            self.assertFalse(self.button(window, label).IsEnabled())
        for label in (
            "Operations",
            "Preferences",
            "Material library",
            "Material test",
            "Properties",
        ):
            self.assertTrue(self.button(window, label).IsEnabled())
        kernel.activate_service_path("device", "fixture-device")
        window.panel.refresh_data()
        self.assertIn("Fixture CO2", " ".join(self.labels(window)))
        self.assertTrue(self.button(window, "Controller").IsEnabled())
        self.assertEqual(commands, [])

    def test_ac_u04_3_no_active_device_is_identified_without_hardware_work(
        self,
    ) -> None:
        self.context = make_context()
        self.context.gui = self.parent
        commands = self.record_commands()
        window = self.make_window()
        window.panel.refresh_data()
        self.assertIn("no active device", " ".join(self.labels(window)).lower())
        for label in ("Controller", "Navigation", "Laser controls"):
            self.assertFalse(self.button(window, label).IsEnabled())
        self.assertEqual(commands, [])

    def test_ac_u04_4_missing_window_tool_shows_useful_visible_error(self) -> None:
        window = self.make_window()
        self.context.kernel.unregister("window/Navigation")
        commands = self.record_commands()
        self.click(self.button(window, "Navigation"))
        self.assertEqual(commands, [])
        errors = [
            child.GetLabel().lower()
            for child in descendants(window)
            if isinstance(child, wx.StaticText) and child.IsShown()
        ]
        self.assertTrue(
            any(
                "navigation" in text
                and any(
                    word in text for word in ("unavailable", "not found", "missing")
                )
                for text in errors
            ),
            errors,
        )

    def test_ac_u04_4_missing_laser_pane_shows_error_without_dispatch(self) -> None:
        window = self.make_window()
        self.context.kernel.unregister("pane/laser")
        commands = self.record_commands()
        self.click(self.button(window, "Laser controls"))
        self.assertEqual(commands, [])
        errors = [
            child.GetLabel().lower()
            for child in descendants(window)
            if isinstance(child, wx.StaticText) and child.IsShown()
        ]
        self.assertTrue(
            any(
                "laser" in text
                and any(
                    word in text for word in ("unavailable", "not found", "missing")
                )
                for text in errors
            ),
            errors,
        )
