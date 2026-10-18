import re
import unittest
from types import SimpleNamespace

import wx

from meerk40t.core.node.effect_hatch import HatchEffectNode
from meerk40t.core.node.elem_rect import RectNode
from meerk40t.core.node.op_cut import CutOpNode
from meerk40t.core.node.util_wait import WaitOperation
from meerk40t.core.units import UNITS_PER_MM, Length
from meerk40t.svgelements import Matrix
from testgui.test_gui_k40workspace import descendants, make_context


class TestK40JobSummary(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.owns_app = wx.App.Get() is None
        cls.app = wx.App.Get() or wx.App(False)

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.owns_app:
            cls.app.Destroy()

    def setUp(self) -> None:
        self.context = make_context("LihuiyuDevice")
        self.parent = wx.Frame(None)
        self.context.gui = self.parent
        self.windows = []
        self.operations = []
        self.geometry = []
        self.undo_history = ["Fixture undo marker"]
        self.context.elements = SimpleNamespace(
            ops=lambda **kwargs: iter(self.operations),
            elems=lambda **kwargs: iter(self.geometry),
            undo=SimpleNamespace(history=self.undo_history),
        )
        device = self.context.device
        device.bedwidth = "300mm"
        device.bedheight = "200mm"
        device.view = SimpleNamespace(
            unit_width=float(Length("300mm")), unit_height=float(Length("200mm"))
        )
        self.queue = []
        device.spooler = SimpleNamespace(queue=self.queue)
        self.commands = []
        self.context.kernel.console = self.commands.append

    def tearDown(self) -> None:
        for window in self.windows:
            window.Destroy()
        self.context.opened.clear()
        self.parent.Destroy()
        self.app.ProcessPendingEvents()

    def make_window(self) -> wx.Window:
        registered = self.context.lookup("window/K40Workspace")
        self.assertIsNotNone(registered)
        window = registered(self.context, "window/K40Workspace", self.parent)
        self.windows.append(window)
        return window

    def report(self, window: wx.Window) -> str:
        reports = [
            child
            for child in descendants(window)
            if isinstance(child, (wx.TextCtrl, wx.ListCtrl))
        ]
        self.assertTrue(reports, "K40 Workspace must display a read-only job summary")
        texts = []
        for control in reports:
            if isinstance(control, wx.TextCtrl):
                self.assertFalse(control.IsEditable(), "Job reports must be read-only")
                texts.append(control.GetValue())
            else:
                self.assertFalse(control.GetWindowStyleFlag() & wx.LC_EDIT_LABELS)
                texts.append(
                    "\n".join(
                        " | ".join(
                            control.GetItemText(row, column)
                            for column in range(control.GetColumnCount())
                        )
                        for row in range(control.GetItemCount())
                    )
                )
        return "\n".join(texts)

    def row(self, report: str, label: str) -> str:
        rows = [line for line in report.splitlines() if label.lower() in line.lower()]
        self.assertEqual(len(rows), 1, "Expected one operation row for " + label)
        return rows[0].lower()

    def rectangle(self) -> RectNode:
        rect = RectNode(
            x=10 * UNITS_PER_MM,
            y=20 * UNITS_PER_MM,
            width=30 * UNITS_PER_MM,
            height=40 * UNITS_PER_MM,
            matrix=Matrix.translate(5 * UNITS_PER_MM, 7 * UNITS_PER_MM),
        )
        self.geometry.append(rect)
        return rect

    def cut(self, label: str, output: bool = True) -> CutOpNode:
        operation = CutOpNode(
            label=label,
            settings={"speed": 12.5, "power": 731, "passes": 3, "passes_custom": True},
            output=output,
        )
        self.operations.append(operation)
        return operation

    def logical_state(self) -> tuple:
        nodes = list(self.operations) + list(self.geometry)
        for operation in self.operations:
            nodes.extend(operation.flat())
        return (
            tuple(self.operations),
            tuple(self.geometry),
            tuple(
                (
                    id(node),
                    node.type,
                    node.label,
                    node.parent,
                    tuple(node.children),
                    tuple(node._references),
                    node.emphasized,
                    node.selected,
                    dict(getattr(node, "settings", {})),
                    str(getattr(node, "matrix", None)),
                )
                for node in nodes
            ),
            tuple(self.undo_history),
            tuple(self.queue),
        )

    def test_ac_u05_1_ordered_operation_rows_show_state_type_settings_and_units(
        self,
    ) -> None:
        self.cut("Outer contour")
        self.cut("Disabled score", output=False)
        window = self.make_window()
        window.panel.refresh_data()
        report = self.report(window)
        self.assertLess(report.index("Outer contour"), report.index("Disabled score"))
        for label, state in (
            ("Outer contour", "enabled"),
            ("Disabled score", "disabled"),
        ):
            row = self.row(report, label)
            self.assertIn(state, row)
            self.assertIn("cut", row)
            self.assertRegex(row, r"12\.5\s*mm/s")
            self.assertRegex(row, r"\b731\b")
            self.assertRegex(row, r"passes?\s*[:=]?\s*3|\b3\s*(?:x|passes?)")
        self.assertRegex(report.lower(), r"controller.*power|power.*controller")
        self.assertIn("setting", report.lower())

    def test_ac_u05_1_passes_follow_effective_operation_setting(self) -> None:
        operation = self.cut("Single pass despite stored count")
        operation.passes = 9
        operation.passes_custom = False
        report = self.report(self.make_window())
        self.assertRegex(
            self.row(report, operation.label),
            r"passes?\s*[:=]?\s*1\b|\b1\s*(?:x|passes?)",
        )

    def test_ac_u05_2_device_bed_and_transformed_design_bounds_are_in_mm(self) -> None:
        rect = self.rectangle()
        self.cut("Assigned contour").add_reference(rect)
        report = self.report(self.make_window()).lower()
        self.assertIn("fixture co2", report)
        self.assertRegex(report, r"300(?:\.0+)?\s*(?:mm)?\s*[x×,]\s*200(?:\.0+)?\s*mm")
        bounds = [line for line in report.splitlines() if "bounds" in line]
        self.assertTrue(bounds, "Scene-space design bounds must be visible")
        bounds_text = " ".join(bounds)
        self.assertIn("mm", bounds_text)
        for coordinate in (15, 27, 45, 67):
            self.assertRegex(bounds_text, rf"(?<![\d.]){coordinate}(?:\.0+)?(?![\d.])")

    def test_ac_u05_2_missing_device_dimensions_and_empty_bounds_are_unavailable(
        self,
    ) -> None:
        self.context.device.bedwidth = None
        self.context.device.bedheight = None
        self.context.device.view = None
        report = self.report(self.make_window()).lower()
        for field in ("bed", "bounds"):
            lines = [line for line in report.splitlines() if field in line]
            self.assertTrue(lines, field + " must be reported")
            self.assertIn("unavailable", " ".join(lines))

    def test_ac_u05_2_nonfinite_dimensions_and_operation_settings_are_unavailable(
        self,
    ) -> None:
        self.context.device.bedwidth = float("nan")
        self.context.device.bedheight = float("inf")
        self.context.device.view.unit_width = float("nan")
        self.context.device.view.unit_height = float("inf")
        operation = self.cut("Invalid settings")
        operation.speed = float("nan")
        operation.power = float("inf")
        report = self.report(self.make_window()).lower()
        row = self.row(report, operation.label)
        self.assertGreaterEqual(row.count("unavailable"), 2)
        bed_rows = [line for line in report.splitlines() if "bed" in line]
        self.assertIn("unavailable", " ".join(bed_rows))
        self.assertIsNone(re.search(r"\b(?:nan|inf|infinity)\b", report))

    def test_ac_u05_2_nonfinite_geometry_bounds_are_unavailable(self) -> None:
        rect = self.rectangle()
        rect.x = float("nan")
        report = self.report(self.make_window()).lower()
        bounds = [line for line in report.splitlines() if "bounds" in line]
        self.assertTrue(bounds)
        self.assertIn("unavailable", " ".join(bounds))
        self.assertIsNone(re.search(r"\b(?:nan|inf|infinity)\b", report))

    def test_ac_u05_2_refresh_button_rebuilds_active_device_and_operation_values(
        self,
    ) -> None:
        operation = self.cut("Updated contour")
        window = self.make_window()
        self.report(window)
        self.context.device.label = "Updated fixture CO2"
        operation.speed = 18.75
        buttons = [
            child
            for child in descendants(window)
            if isinstance(child, wx.Button) and child.GetLabel() == "Refresh"
        ]
        self.assertEqual(len(buttons), 1)
        event = wx.CommandEvent(wx.EVT_BUTTON.typeId, buttons[0].GetId())
        event.SetEventObject(buttons[0])
        buttons[0].GetEventHandler().ProcessEvent(event)
        report = self.report(window)
        self.assertIn("Updated fixture CO2", report)
        self.assertRegex(self.row(report, operation.label), r"18\.75\s*mm/s")
        self.assertEqual(self.commands, [])

    def test_ac_u05_3_empty_document_has_an_explicit_empty_operations_report(
        self,
    ) -> None:
        report = self.report(self.make_window()).lower()
        self.assertRegex(report, r"no operations|operations\s*[:=]?\s*(?:none|0)|empty")
        self.assertIn("unavailable", report)
        self.assertEqual(self.commands, [])

    def test_ac_u05_3_effect_references_and_utility_rows_do_not_fabricate_settings(
        self,
    ) -> None:
        rect = self.rectangle()
        effect = HatchEffectNode(label="Fixture hatch")
        effect.add_reference(rect)
        cut = self.cut("Effect cut")
        cut.add_node(effect)
        wait = WaitOperation(label="Cooling pause", wait=2)
        self.operations.append(wait)
        report = self.report(self.make_window())
        self.assertLess(report.index("Effect cut"), report.index("Cooling pause"))
        wait_row = self.row(report, "Cooling pause")
        self.assertIn("wait", wait_row)
        self.assertGreaterEqual(wait_row.count("unavailable"), 2)
        self.assertRegex(wait_row, r"passes?\s*[:=]?\s*1\b|\b1\s*(?:x|passes?)")
        self.assertNotIn("mm/s", wait_row)
        self.assertEqual(self.commands, [])

    def test_ac_u05_3_opening_and_refresh_preserve_document_queue_and_selection(
        self,
    ) -> None:
        rect = self.rectangle()
        rect.emphasized = True
        rect.selected = True
        self.cut("Preserved contour").add_reference(rect)
        before = self.logical_state()
        window = self.make_window()
        self.report(window)
        window.panel.refresh_data()
        window.panel.refresh_data()
        self.assertEqual(self.logical_state(), before)
        self.assertEqual(self.commands, [])
