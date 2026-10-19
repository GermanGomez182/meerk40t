import unittest
from itertools import pairwise

import wx
from numpy.testing import assert_array_equal
from PIL import Image

from meerk40t.core.geomstr import Geomstr
from meerk40t.core.node.effect_hatch import HatchEffectNode
from meerk40t.core.node.elem_image import ImageNode
from meerk40t.core.node.elem_path import PathNode
from meerk40t.core.node.elem_rect import RectNode
from meerk40t.core.node.elem_text import TextNode
from meerk40t.core.node.groupnode import GroupNode
from meerk40t.core.units import UNITS_PER_MM
from meerk40t.svgelements import Color, Matrix
from testgui import test_gui_k40summary as summary_fixture
from testgui import test_gui_k40workspace as workspace_fixture


class TestK40DesignAudit(unittest.TestCase):
    make_window = summary_fixture.TestK40JobSummary.make_window
    cut = summary_fixture.TestK40JobSummary.cut
    logical_state = summary_fixture.TestK40JobSummary.logical_state
    button = workspace_fixture.TestK40Workspace.button
    click = workspace_fixture.TestK40Workspace.click

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

    def tearDown(self) -> None:
        summary_fixture.TestK40JobSummary.tearDown(self)

    def audit(self, window: wx.Window) -> str:
        controls = [
            child
            for child in workspace_fixture.descendants(window)
            if isinstance(child, wx.TextCtrl) and "audit" in child.GetValue().lower()
        ]
        self.assertEqual(
            len(controls), 1, "An independent design audit must be visible"
        )
        self.assertIsNot(controls[0], window.panel.job_summary)
        self.assertFalse(controls[0].IsEditable(), "Design audit must be read-only")
        return controls[0].GetValue().lower()

    def rect(
        self,
        label: str,
        x: float,
        y: float,
        width: float,
        height: float,
        dx: float = 0,
        dy: float = 0,
    ) -> RectNode:
        node = RectNode(
            label=label,
            id=label.replace(" ", "-"),
            x=x * UNITS_PER_MM,
            y=y * UNITS_PER_MM,
            width=width * UNITS_PER_MM,
            height=height * UNITS_PER_MM,
            matrix=Matrix.translate(dx * UNITS_PER_MM, dy * UNITS_PER_MM),
        )
        self.geometry.append(node)
        return node

    def path(
        self,
        label: str,
        points: tuple,
        dx: float = 0,
        dy: float = 0,
    ) -> PathNode:
        geometry = Geomstr()
        for start, end in pairwise(points):
            geometry.line(complex(*start) * UNITS_PER_MM, complex(*end) * UNITS_PER_MM)
        node = PathNode(
            geometry=geometry,
            label=label,
            id=label.replace(" ", "-"),
            matrix=Matrix.translate(dx * UNITS_PER_MM, dy * UNITS_PER_MM),
        )
        self.geometry.append(node)
        return node

    def assert_count(self, report: str, name: str, count: int) -> None:
        self.assertRegex(report, rf"\b{name}\s*(?:elements?)?\s*[:=]\s*{count}\b")

    def test_ac_u09_1_dimensions_use_transformed_scene_bounds_in_mm(self) -> None:
        node = self.rect("Transformed design", 5, 10, 15, 20)
        node.matrix = Matrix(2, 0, 0, 2, 5 * UNITS_PER_MM, 7 * UNITS_PER_MM)
        report = self.audit(self.make_window())
        dimensions = " ".join(
            line for line in report.splitlines() if "dimension" in line
        )
        self.assertRegex(
            dimensions, r"30(?:\.0+)?\s*(?:mm)?\s*[x×,]\s*40(?:\.0+)?\s*mm"
        )
        bounds = " ".join(line for line in report.splitlines() if "bounds" in line)
        self.assertIn("mm", bounds)
        for coordinate in (15, 27, 45, 67):
            self.assertRegex(bounds, rf"(?<![\d.]){coordinate}(?:\.0+)?(?![\d.])")
        self.assertEqual(self.commands, [])

    def test_ac_u09_1_refresh_rechecks_current_geometry_and_references(self) -> None:
        node = self.rect("Edited contour", 10, 10, 10, 10)
        window = self.make_window()
        self.assert_count(self.audit(window), "unassigned", 1)
        node.width = 25 * UNITS_PER_MM
        node.set_dirty_bounds()
        self.cut("New assignment").add_reference(node)
        before = self.logical_state()
        self.click(self.button(window, "Refresh"))
        report = self.audit(window)
        self.assert_count(report, "assigned", 1)
        self.assert_count(report, "unassigned", 0)
        dimensions = " ".join(
            line for line in report.splitlines() if "dimension" in line
        )
        self.assertRegex(
            dimensions, r"25(?:\.0+)?\s*(?:mm)?\s*[x×,]\s*10(?:\.0+)?\s*mm"
        )
        self.assertEqual(self.logical_state(), before)
        self.assertEqual(self.commands, [])

    def test_ac_u09_1_outside_elements_include_negative_and_overflow_not_edges(
        self,
    ) -> None:
        self.rect("Exact bed edge", 0, 0, 300, 200)
        for label, x, y, dx, dy in (
            ("Left outside", 1, 10, -2, 0),
            ("Top outside", 10, 1, 0, -2),
            ("Right outside", 280, 10, 11, 0),
            ("Bottom outside", 10, 180, 0, 11),
        ):
            self.rect(label, x, y, 10, 10, dx, dy)
        operation = self.cut("All assigned")
        for node in self.geometry:
            operation.add_reference(node)
        report = self.audit(self.make_window())
        self.assertRegex(report, r"(?:outside|out.of.bed)[^\n]*\b4\b")
        for label in ("left outside", "top outside", "right outside", "bottom outside"):
            self.assertIn(label, report)
        self.assertEqual(self.commands, [])

    def test_ac_u09_1_missing_bed_keeps_assignment_check_available(self) -> None:
        self.rect("Loose contour", 1, 2, 3, 4)
        self.context.device.bedwidth = None
        self.context.device.bedheight = None
        self.context.device.view = None
        report = self.audit(self.make_window())
        self.assertRegex(report, r"(?:bed|outside)[^\n]*(?:unavailable|unknown|cannot)")
        self.assert_count(report, "unassigned", 1)
        self.assertEqual(self.commands, [])

    def test_ac_u09_2_duplicate_segments_and_transform_ignore_style_not_bounds(
        self,
    ) -> None:
        points = ((0, 0), (10, 10), (0, 10))
        first = self.path("Pair alpha", points, 20, 30)
        second = self.path("Pair beta", points, 20, 30)
        first.stroke = Color("red")
        second.stroke = Color("blue")
        self.path("Different transform", points, 21, 30)
        self.path("Different segments same bounds", ((0, 0), (0, 10), (10, 10)), 20, 30)
        self.path("Reversed segments", tuple(reversed(points)), 20, 30)
        self.path("Same scene different matrix", ((20, 30), (30, 40), (20, 40)))
        operation = self.cut("Assigned paths")
        for node in self.geometry:
            operation.add_reference(node)
        before = self.logical_state()
        segments_before = [
            node.geometry.segments[: node.geometry.index].copy()
            for node in self.geometry
        ]
        window = self.make_window()
        report = self.audit(window)
        self.assertRegex(report, r"duplicate[^\n]*(?:\b1\s*group|groups?\s*[:=]\s*1\b)")
        for label in ("pair alpha", "pair beta"):
            self.assertIn(label, report)
        window.panel.refresh_data()
        self.audit(window)
        self.assertEqual(self.logical_state(), before)
        for node, segments in zip(self.geometry, segments_before):
            assert_array_equal(node.geometry.segments[: node.geometry.index], segments)
        self.assertEqual(self.commands, [])

    def test_ac_u09_2_similar_bounds_reversed_paths_and_other_matrices_are_not_duplicates(
        self,
    ) -> None:
        original = ((0, 0), (10, 10), (0, 10))
        for points, dx, dy in (
            (original, 21, 30),
            (((0, 0), (0, 10), (10, 10)), 20, 30),
            (tuple(reversed(original)), 20, 30),
            (((20, 30), (30, 40), (20, 40)), 0, 0),
        ):
            with self.subTest(points=points, dx=dx, dy=dy):
                self.geometry.clear()
                self.path("Original", original, 20, 30)
                self.path("Distinct vector", points, dx, dy)
                report = self.audit(self.make_window())
                self.assertRegex(
                    report, r"duplicate[^\n]*(?:\b0\b|none)|no (?:exact )?duplicates"
                )
                self.assertEqual(self.commands, [])

    def test_ac_u09_2_assignment_uses_all_operation_descendants_not_other_refs(
        self,
    ) -> None:
        direct = self.rect("Direct assigned", 10, 10, 1, 1)
        nested = self.rect("Effect assigned", 20, 10, 1, 1)
        loose = self.rect("Loose vector", 30, 10, 1, 1)
        unlabeled = self.rect("Temporary label", 40, 10, 1, 1)
        unlabeled.label = None
        unlabeled.id = "unlabeled-vector-42"
        self.cut("Disabled cut", output=False).add_reference(direct)
        effect = HatchEffectNode(label="Assigned through hatch")
        effect.add_reference(nested)
        self.cut("Effect cut").add_node(effect)
        group = GroupNode()
        group.add_reference(loose)
        report = self.audit(self.make_window())
        self.assert_count(report, "assigned", 2)
        self.assert_count(report, "unassigned", 2)
        self.assertIn("loose vector", report)
        self.assertIn("loose-vector", report)
        self.assertIn("unlabeled-vector-42", report)

    def test_ac_u09_2_open_refresh_preserves_document_geometry_undo_and_queue(
        self,
    ) -> None:
        first = self.rect("Preserved first", 10, 10, 10, 10)
        second = self.rect("Preserved duplicate", 10, 10, 10, 10)
        first.selected = True
        first.emphasized = True
        self.cut("Preserved references").add_reference(second)
        self.queue.append("Existing fixture job")
        before = self.logical_state()
        coordinates = [
            (node.x, node.y, node.width, node.height) for node in self.geometry
        ]
        window = self.make_window()
        self.audit(window)
        self.click(self.button(window, "Refresh"))
        self.audit(window)
        self.assertEqual(self.logical_state(), before)
        self.assertEqual(
            [(node.x, node.y, node.width, node.height) for node in self.geometry],
            coordinates,
        )
        self.assertEqual(self.commands, [])

    def test_ac_u09_3_empty_design_reports_limitation_and_zero_counts(self) -> None:
        report = self.audit(self.make_window())
        self.assertRegex(report, r"empty|no (?:design|elements|geometry)")
        self.assertRegex(report, r"unavailable|cannot|limitation")
        self.assert_count(report, "assigned", 0)
        self.assert_count(report, "unassigned", 0)
        self.assertEqual(self.commands, [])

    def test_ac_u09_3_unsupported_text_image_do_not_hide_supported_duplicates(
        self,
    ) -> None:
        for label in ("Supported alpha", "Supported beta"):
            self.rect(label, 299, 20, 2, 2)
        self.geometry.extend(
            (
                TextNode(
                    text="Fixture text", label="Text limitation", id="text-fixture"
                ),
                ImageNode(
                    image=Image.new("RGB", (2, 2)),
                    label="Image limitation",
                    id="image-fixture",
                ),
            )
        )
        before = self.logical_state()
        window = self.make_window()
        report = self.audit(window)
        self.assertRegex(report, r"(?:unsupported|limitation|not checked|unavailable)")
        self.assertIn("text", report)
        self.assertIn("image", report)
        self.assertIn("supported alpha", report)
        self.assertIn("supported beta", report)
        self.assertRegex(report, r"duplicate[^\n]*(?:\b1\s*group|groups?\s*[:=]\s*1\b)")
        self.assert_count(report, "unassigned", 4)
        window.panel.refresh_data()
        self.assertEqual(self.logical_state(), before)
        self.assertEqual(self.commands, [])

    def test_ac_u09_3_invalid_bounds_keep_audit_summary_and_framing_usable(
        self,
    ) -> None:
        for width in (None, "bad", float("nan")):
            with self.subTest(width=width):
                self.geometry.clear()
                valid = self.rect("Valid outside", 301, 10, 2, 2)
                malformed = self.rect("Malformed bounds", 1, 1, 2, 2)
                malformed.width = width
                before = self.logical_state()
                window = self.make_window()
                report = self.audit(window)
                self.assertIn("valid outside", report)
                self.assertIn("malformed bounds", report)
                self.assertRegex(report, r"unavailable|invalid|limitation|cannot")
                self.assert_count(report, "unassigned", 2)
                self.assertIn("Fixture CO2", window.panel.job_summary.GetValue())
                window.panel.refresh_data()
                self.assertTrue(self.button(window, "Framing controls").IsEnabled())
                self.assertEqual(self.logical_state(), before)
                self.assertEqual(valid.width, 2 * UNITS_PER_MM)
                self.assertIs(malformed.width, width)
                self.assertEqual(self.commands, [])
