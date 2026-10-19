import re
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import wx

from meerk40t.core.cutcode.cutcode import CutCode
from meerk40t.core.cutplan import CutPlan, CutPlanningFailedError
from meerk40t.core.node.op_cut import CutOpNode
from meerk40t.core.node.op_raster import RasterOpNode
from meerk40t.core.node.util_wait import WaitOperation
from meerk40t.gui.themes import Themes
from meerk40t.gui.wxmeerk40t import wxMeerK40t
from test import bootstrap
from testgui import test_gui_k40summary as summary_fixture
from testgui.test_gui_k40workspace import descendants


class TestK40Preview(unittest.TestCase):
    make_window = summary_fixture.TestK40JobSummary.make_window
    report = summary_fixture.TestK40JobSummary.report
    rectangle = summary_fixture.TestK40JobSummary.rectangle
    cut = summary_fixture.TestK40JobSummary.cut
    logical_state = summary_fixture.TestK40JobSummary.logical_state

    @classmethod
    def setUpClass(cls) -> None:
        cls.owns_app = wx.App.Get() is None
        cls.app = wx.App.Get() or wx.App(False)

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.owns_app:
            cls.app.Destroy()

    def setUp(self) -> None:
        summary_fixture.TestK40JobSummary.setUp(self)
        self.context.device.home_corner = "top-right"
        self.plan_requests = []

        def free_plan() -> str:
            self.plan_requests.append("free plan")
            return "preview-fixture"

        self.context.planner = SimpleNamespace(
            get_free_plan=free_plan,
            is_finished=lambda name: any(" finish" in cmd for cmd in self.commands),
        )

    def tearDown(self) -> None:
        summary_fixture.TestK40JobSummary.tearDown(self)

    def button(self, window: wx.Window, label: str) -> wx.Button:
        buttons = [
            child
            for child in descendants(window)
            if isinstance(child, wx.Button) and child.GetLabel() == label
        ]
        self.assertEqual(len(buttons), 1, "Missing preview shortcut: " + label)
        return buttons[0]

    def click(self, button: wx.Button) -> None:
        event = wx.CommandEvent(wx.EVT_BUTTON.typeId, button.GetId())
        event.SetEventObject(button)
        button.GetEventHandler().ProcessEvent(event)

    def duration_line(self, window: wx.Window) -> str:
        report = self.report(window).lower()
        estimates = [line for line in report.splitlines() if "estimate" in line]
        self.assertTrue(estimates, "Preview must show a software duration estimate")
        line = " ".join(estimates)
        self.assertIn("software", line)
        return line

    def inline_errors(self, window: wx.Window) -> str:
        return " ".join(
            child.GetLabel().lower()
            for child in descendants(window)
            if isinstance(child, wx.StaticText) and child.IsShown()
        )

    def test_ac_u08_1_preview_explains_scene_origin_home_corner_and_design_bounds(
        self,
    ) -> None:
        self.cut("Preview contour").add_reference(self.rectangle())
        window = self.make_window()
        report = self.report(window).lower()
        origins = [line for line in report.splitlines() if "origin" in line]
        self.assertTrue(origins, "Scene origin must be explicit")
        self.assertRegex(" ".join(origins), r"scene.*0(?:\.0+)?\s*,\s*0(?:\.0+)?\s*mm")
        self.assertRegex(report, r"(?:configured|home).*top.right")
        positions = [
            line
            for line in report.splitlines()
            if "physical" in line and "position" in line
        ]
        self.assertTrue(
            positions, "Configured home must not imply known physical position"
        )
        self.assertRegex(" ".join(positions), r"unavailable|unknown")
        bounds = " ".join(line for line in report.splitlines() if "bounds" in line)
        self.assertIn("mm", bounds)
        for coordinate in (15, 27, 45, 67):
            self.assertRegex(bounds, rf"(?<![\d.]){coordinate}(?:\.0+)?(?![\d.])")

    def test_ac_u08_1_duration_sums_enabled_real_operation_estimates_only(self) -> None:
        rect = self.rectangle()
        for label, enabled in (
            ("First cut", True),
            ("Second cut", True),
            ("Disabled cut", False),
        ):
            operation = self.cut(label, output=enabled)
            operation.add_reference(rect)
            self.assertEqual(operation.time_estimate(), "0:00:33")
        window = self.make_window()
        self.assertRegex(self.duration_line(window), r"0:01:06|\b66\s*(?:s|seconds)\b")
        self.assertEqual(self.commands, [])
        self.assertEqual(self.plan_requests, [])

    def test_ac_u08_1_refresh_recomputes_estimate_without_document_or_queue_edits(
        self,
    ) -> None:
        operation = self.cut("Changing estimate")
        operation.add_reference(self.rectangle())
        window = self.make_window()
        self.duration_line(window)
        operation.speed = 25
        before = self.logical_state()
        window.panel.refresh_data()
        self.assertRegex(self.duration_line(window), r"0:00:16|\b16\s*(?:s|seconds)\b")
        self.assertEqual(self.logical_state(), before)
        self.assertEqual(self.commands, [])
        self.assertEqual(self.plan_requests, [])

    def test_ac_u08_2_simulation_uses_free_plan_preparation_and_never_spools(
        self,
    ) -> None:
        self.cut("Simulated contour").add_reference(self.rectangle())
        before = self.logical_state()
        window = self.make_window()
        self.assertEqual(self.plan_requests, [])
        self.assertEqual(self.commands, [])
        self.click(self.button(window, "Simulation"))
        self.assertEqual(self.plan_requests, ["free plan"])
        commands = [
            line for command in self.commands for line in command.splitlines() if line
        ]
        self.assertEqual(len(commands), 2)
        self.assertEqual(
            commands[0],
            "planpreview-fixture clear copy preprocess validate blob finish",
        )
        self.assertRegex(
            commands[1], r"^window open Simulation preview-fixture(?: 0(?: 0)?)?$"
        )
        self.assertIsNone(
            re.search(
                r"\b(?:spool|start|home|trace|move|fire|connect|outline)\b",
                " ".join(commands),
            )
        )
        self.assertEqual(self.logical_state(), before)

    def test_ac_u08_2_missing_planner_shows_inline_error_without_commands(self) -> None:
        self.context.planner = None
        window = self.make_window()
        self.click(self.button(window, "Simulation"))
        error = self.inline_errors(window)
        self.assertRegex(error, r"planner|simulation")
        self.assertRegex(error, r"unavailable|missing|not found")
        self.assertEqual(self.commands, [])
        self.assertEqual(self.plan_requests, [])

    def test_ac_u08_2_missing_simulation_window_does_not_prepare_a_plan(self) -> None:
        self.context.kernel.unregister("window/Simulation")
        window = self.make_window()
        self.click(self.button(window, "Simulation"))
        error = self.inline_errors(window)
        self.assertIn("simulation", error)
        self.assertRegex(error, r"unavailable|missing|not found")
        self.assertEqual(self.commands, [])
        self.assertEqual(self.plan_requests, [])

    def test_ac_u08_3_empty_document_reports_unavailable_bounds_and_estimate(
        self,
    ) -> None:
        window = self.make_window()
        self.assertIn("unavailable", self.duration_line(window))
        bounds = " ".join(
            line
            for line in self.report(window).lower().splitlines()
            if "bounds" in line
        )
        self.assertIn("unavailable", bounds)
        self.assertEqual(self.commands, [])
        self.assertEqual(self.plan_requests, [])

    def test_ac_u08_3_missing_or_malformed_operation_estimate_is_unavailable(
        self,
    ) -> None:
        self.cut("Unknown duration").add_reference(self.rectangle())
        for estimate in (None, "bad", "0:99:00", "-1:00:00", "nan"):
            with (
                self.subTest(estimate=estimate),
                patch.object(CutOpNode, "time_estimate", return_value=estimate),
            ):
                window = self.make_window()
                self.assertIn("unavailable", self.duration_line(window))
        self.assertEqual(self.commands, [])
        self.assertEqual(self.plan_requests, [])

    def test_ac_u08_3_one_unknown_enabled_estimate_prevents_a_partial_total(
        self,
    ) -> None:
        self.cut("Known duration").add_reference(self.rectangle())
        self.operations.append(WaitOperation(wait=2))
        before = self.logical_state()
        window = self.make_window()
        self.assertIn("unavailable", self.duration_line(window))
        self.assertEqual(self.logical_state(), before)
        self.assertEqual(self.commands, [])

    def test_ac_u08_1_disabled_unknown_estimate_does_not_poison_total(self) -> None:
        self.cut("Known duration").add_reference(self.rectangle())
        self.operations.append(WaitOperation(wait=2, output=False))
        window = self.make_window()
        self.assertRegex(self.duration_line(window), r"0:00:33|\b33\s*(?:s|seconds)\b")
        self.assertEqual(self.commands, [])

    def test_ac_u08_3_estimator_arithmetic_error_is_visible_and_preserves_document(
        self,
    ) -> None:
        operation = self.cut("Zero speed contour")
        operation.speed = 0
        operation.add_reference(self.rectangle())
        before = self.logical_state()
        window = self.make_window()
        self.assertIn("unavailable", self.duration_line(window))
        self.assertEqual(self.logical_state(), before)
        self.assertEqual(self.commands, [])

    def test_ac_u08_1_real_raster_estimate_preserves_references_and_selection(
        self,
    ) -> None:
        rectangle = self.rectangle()
        rectangle.selected = True
        rectangle.emphasized = True
        operation = RasterOpNode(settings={"speed": 150, "dpi": 100})
        operation.add_reference(rectangle)
        self.operations.append(operation)
        expected = operation.time_estimate()
        before = self.logical_state()
        window = self.make_window()
        window.panel.refresh_data()
        self.assertIn(expected, self.duration_line(window))
        self.assertEqual(self.logical_state(), before)
        self.assertEqual(self.commands, [])

    def test_ac_u08_1_missing_configured_home_remains_unavailable(self) -> None:
        self.context.device.home_corner = None
        window = self.make_window()
        lines = [
            line for line in self.report(window).lower().splitlines() if "home" in line
        ]
        self.assertTrue(lines, "Configured home must have an explicit unknown state")
        self.assertRegex(" ".join(lines), r"unavailable|unknown")
        self.assertEqual(self.commands, [])

    def use_real_planner(self) -> object:
        kernel = bootstrap.bootstrap(profile="K40Preview_U08")
        self.addCleanup(kernel)
        kernel.add_service("themes", Themes(kernel))
        wxMeerK40t.sub_register(kernel)
        wxMeerK40t.module_open(SimpleNamespace(context=kernel.root))
        self.context = kernel.root
        self.context.gui = self.parent
        kernel.console("rect 10mm 20mm 30mm 40mm\n")
        kernel.elements.clear_operations()
        operation = kernel.elements.op_branch.add(type="op cut", speed=12.5)
        operation.add_reference(next(kernel.elements.elems()))
        self.operations = list(kernel.elements.ops())
        self.geometry = list(kernel.elements.elems())
        self.assertEqual(len(self.operations), 1)
        self.assertEqual(len(self.geometry), 1)
        self.geometry[0].selected = True
        self.geometry[0].emphasized = True
        self.queue = kernel.device.spooler.queue
        self.undo_history = kernel.elements.undo._undo_stack
        self.commands = []
        self.simulation_plans = []
        console = kernel.console

        def dispatch(command: str) -> object:
            self.commands.append(command)
            if command.startswith("window open Simulation "):
                name = command.split()[3]
                self.assertTrue(kernel.planner.is_finished(name))
                plan = kernel.planner.get_or_make_plan(name)
                self.assertTrue(
                    any(isinstance(item, CutCode) and len(item) for item in plan.plan)
                )
                self.simulation_plans.append(name)
                return None
            return console(command)

        kernel.console = dispatch
        return kernel

    def test_ac_u08_2_real_pipeline_finishes_cutcode_before_simulation_opens(
        self,
    ) -> None:
        kernel = self.use_real_planner()
        before = self.logical_state()
        undo_index = kernel.elements.undo._undo_index
        window = self.make_window()
        self.assertEqual(self.commands, [])
        self.click(self.button(window, "Simulation"))
        self.assertEqual(len(self.simulation_plans), 1)
        self.assertEqual(self.logical_state(), before)
        self.assertEqual(kernel.elements.undo._undo_index, undo_index)
        self.assertIsNone(
            re.search(
                r"\b(?:spool|start|home|trace|move|fire|connect|outline)\b",
                " ".join(self.commands),
            )
        )

    def test_ac_u08_2_validation_failure_does_not_open_simulation(self) -> None:
        self.use_real_planner()
        before = self.logical_state()
        window = self.make_window()
        with patch.object(
            CutPlan,
            "execute",
            side_effect=CutPlanningFailedError("Fixture validation rejected"),
        ):
            self.click(self.button(window, "Simulation"))
        self.assertEqual(self.simulation_plans, [])
        self.assertRegex(self.inline_errors(window), r"fail|error|unavailable|rejected")
        self.assertFalse(
            any("window open Simulation" in command for command in self.commands)
        )
        self.assertEqual(self.logical_state(), before)

    def test_ac_u08_3_framing_shortcut_only_opens_existing_laser_controls(self) -> None:
        before = self.logical_state()
        window = self.make_window()
        self.assertEqual(self.commands, [])
        self.click(self.button(window, "Framing controls"))
        self.assertEqual(self.commands, ["pane show laser\n"])
        self.assertEqual(self.plan_requests, [])
        self.assertEqual(self.logical_state(), before)

    def test_ac_u08_3_missing_framing_pane_shows_inline_error_without_commands(
        self,
    ) -> None:
        self.context.kernel.unregister("pane/laser")
        window = self.make_window()
        self.click(self.button(window, "Framing controls"))
        error = self.inline_errors(window)
        self.assertRegex(error, r"laser|framing")
        self.assertRegex(error, r"unavailable|missing|not found")
        self.assertEqual(self.commands, [])
        self.assertEqual(self.plan_requests, [])

    def test_ac_u08_3_missing_framing_pane_error_is_readable_after_scrolling(
        self,
    ) -> None:
        self.context.kernel.unregister("pane/laser")
        before = self.logical_state()
        window = self.make_window()
        window.SetSize((450, 650))
        window.Show()
        window.Layout()
        self.app.ProcessPendingEvents()
        panel = window.panel
        framing = self.button(window, "Framing controls")
        panel.ScrollChildIntoView(framing)
        self.app.ProcessPendingEvents()
        self.assertGreater(panel.GetViewStart()[1], 0)
        self.click(framing)
        panel.Layout()
        self.app.ProcessPendingEvents()
        errors = [
            child
            for child in descendants(panel)
            if isinstance(child, wx.StaticText)
            and re.search(r"unavailable|missing|not found", child.GetLabel().lower())
        ]
        self.assertTrue(errors, "Missing framing controls must produce an error")
        viewport = panel.GetClientRect()
        self.assertTrue(
            any(
                viewport.Contains(
                    wx.Rect(
                        panel.ScreenToClient(error.GetScreenPosition()),
                        error.GetSize(),
                    )
                )
                for error in errors
            ),
            "The error must be readable inside the scrolled panel viewport",
        )
        self.assertEqual(self.commands, [])
        self.assertEqual(self.plan_requests, [])
        self.assertEqual(self.logical_state(), before)
