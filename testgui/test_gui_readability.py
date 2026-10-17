import math
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

import wx

from meerk40t.kernel import Kernel
from meerk40t.svgelements import Matrix


def luminance(channels: tuple) -> float:
    linear = []
    for channel in channels:
        value = channel / 255
        linear.append(
            value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
        )
    return sum(
        value * weight for value, weight in zip(linear, (0.2126, 0.7152, 0.0722))
    )


def contrast(foreground: wx.Colour, background: wx.Colour) -> float:
    foreground = wx.Colour(foreground)
    alpha = foreground.Alpha() / 255
    effective = tuple(
        alpha * foreground[index] + (1 - alpha) * background[index]
        for index in range(3)
    )
    values = (luminance(effective), luminance(tuple(background[:3])))
    return (max(values) + 0.05) / (min(values) + 0.05)


class Scene(SimpleNamespace):
    """The widget requires a scene-named object but no physical device."""


class GuiReadabilityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.owns_app = wx.App.Get() is None
        cls.app = wx.App.Get() or wx.App(False)
        from meerk40t.gui import guicolors
        from meerk40t.gui.laserrender import DRAW_MODE_GUIDES
        from meerk40t.gui.scenewidgets.guidewidget import GuideWidget
        from meerk40t.gui.themes import Themes

        cls.guicolors = guicolors
        cls.guide_type = GuideWidget
        cls.theme_type = Themes
        cls.guides_disabled_flag = DRAW_MODE_GUIDES

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.owns_app:
            cls.app.Destroy()

    def make_guide(self, background: str, source: str) -> object:
        kernel = Kernel(
            "GuiReadabilityTest", "0", "GuiReadabilityTest", ignore_settings=True
        )
        kernel.root.themes = SimpleNamespace(dark=False)
        colors = self.guicolors.GuiColors(kernel)
        colors.background = background
        colors.guide = source
        colors.guide2 = source
        context = SimpleNamespace(
            draw_mode=0,
            units_name="mm",
            elements=SimpleNamespace(modified=False),
            space=SimpleNamespace(
                right_positive=True, bottom_positive=True, origin_zero=lambda: (0, 0)
            ),
        )
        scene = Scene(
            context=context,
            colors=colors,
            widget_root=SimpleNamespace(scene_widget=SimpleNamespace(matrix=Matrix())),
            pane=SimpleNamespace(
                grid=SimpleNamespace(
                    tick_distance=10,
                    draw_grid_primary=True,
                    draw_grid_secondary=True,
                )
            ),
        )
        return self.guide_type(scene)

    def render_labels(self, guide: object) -> Mock:
        gc = Mock(Size=(300, 200))
        gc.GetTextExtent.return_value = (8, 12)
        with (
            patch.object(
                guide,
                "_calculate_primary_grid_data",
                return_value=([(10, 0)], [(10, 20)], [("10", 10, 5, 0)]),
            ),
            patch.object(
                guide,
                "_calculate_secondary_guides",
                return_value=([(290, 0)], [(290, 20)], [("20", 290, 5, 0)]),
            ),
            patch.object(guide, "_draw_magnet_lines"),
        ):
            guide.process_draw(gc)
        return gc

    def test_ac_u03_1_rendered_labels_have_contrast_on_each_background(self) -> None:
        for background in ("#ffffff", "#101010", "#777777"):
            with self.subTest(background=background):
                guide = self.make_guide(background, background)
                saved = dict(guide.scene.colors.__dict__)
                gc = self.render_labels(guide)
                self.assertEqual(gc.SetFont.call_count, 3)
                for call in gc.SetFont.call_args_list:
                    self.assertGreaterEqual(
                        contrast(call.args[1], wx.Colour(background)), 4.5
                    )
                self.assertEqual(guide.scene.colors.__dict__, saved)
                self.assertFalse(guide.scene.context.elements.modified)

    def test_ac_u03_1_readable_custom_source_is_used_without_rewriting(self) -> None:
        guide = self.make_guide("#ffffff", "#203060")
        saved = dict(guide.scene.colors.__dict__)
        gc = self.render_labels(guide)
        self.assertEqual(gc.SetFont.call_count, 3)
        for call in gc.SetFont.call_args_list:
            self.assertEqual(wx.Colour(call.args[1]), wx.Colour("#203060"))
        self.assertEqual(guide.scene.colors.__dict__, saved)

    def test_ac_u03_1_transparent_source_uses_effective_contrast(self) -> None:
        guide = self.make_guide("#ffffff", "#00000020")
        saved = dict(guide.scene.colors.__dict__)
        gc = self.render_labels(guide)
        for call in gc.SetFont.call_args_list:
            self.assertGreaterEqual(contrast(call.args[1], wx.WHITE), 4.5)
        self.assertEqual(guide.scene.colors.__dict__, saved)

    def test_ac_u03_2_action_labels_contrast_in_both_native_appearances(self) -> None:
        for appearance in ("light", "dark"):
            with self.subTest(appearance=appearance):
                foreground = wx.WHITE if appearance == "dark" else wx.BLACK
                background = wx.Colour(30, 30, 30) if appearance == "dark" else wx.WHITE

                def native_color(
                    index: int,
                    foreground: wx.Colour = foreground,
                    background: wx.Colour = background,
                ) -> wx.Colour:
                    if index in (
                        wx.SYS_COLOUR_WINDOWTEXT,
                        wx.SYS_COLOUR_BTNTEXT,
                        wx.SYS_COLOUR_LISTBOXTEXT,
                        wx.SYS_COLOUR_CAPTIONTEXT,
                        wx.SYS_COLOUR_INACTIVECAPTIONTEXT,
                    ):
                        return foreground
                    return background

                kernel = Kernel(
                    "GuiReadabilityTest",
                    "0",
                    "GuiReadabilityTest",
                    ignore_settings=True,
                )
                with patch.object(
                    wx.SystemSettings, "GetColour", side_effect=native_color
                ):
                    theme = self.theme_type(kernel)
                    theme.forced_theme = appearance
                    theme.load_system_default()
                self.assertEqual(theme.dark, appearance == "dark")
                for action in ("start", "pause", "stop"):
                    with self.subTest(action=action):
                        self.assertGreaterEqual(
                            contrast(
                                theme.get(action + "_fg"), theme.get(action + "_bg")
                            ),
                            4.5,
                        )

    def test_ac_u03_3_low_rgba_channels_serialize_and_round_trip(self) -> None:
        for channels, expected in (
            ((0, 1, 15, 255), "#00010fff"),
            ((1, 2, 3, 4), "#01020304"),
            ((255, 16, 0, 15), "#ff10000f"),
        ):
            with self.subTest(channels=channels):
                encoded = self.guicolors.to_hex(wx.Colour(*channels))
                self.assertEqual(encoded.lower(), expected)
                self.assertRegex(encoded, r"^#[0-9a-fA-F]{8}$")
                guide = self.make_guide("#ffffff", encoded)
                self.assertEqual(tuple(guide.scene.colors.get("guide")), channels)

    def test_ac_u03_4_disabled_guides_draw_no_lines_or_labels(self) -> None:
        guide = self.make_guide("#ffffff", "#203060")
        guide.scene.context.draw_mode = self.guides_disabled_flag
        saved = dict(guide.scene.colors.__dict__)
        gc = self.render_labels(guide)
        gc.SetFont.assert_not_called()
        gc.DrawText.assert_not_called()
        gc.StrokeLineSegments.assert_not_called()
        self.assertEqual(guide.scene.colors.__dict__, saved)
        self.assertFalse(guide.scene.context.elements.modified)

    def test_ac_u03_4_theme_refresh_updates_effective_color_without_document_edits(
        self,
    ) -> None:
        guide = self.make_guide("#ffffff", "#203060")
        first_gc = self.render_labels(guide)
        guide._text_extent_cache["stale"] = (1, 1)
        guide.scene.colors.background = "#203060"
        saved = dict(guide.scene.colors.__dict__)
        guide.signal("theme")
        self.assertEqual(guide._text_extent_cache, {})
        second_gc = self.render_labels(guide)
        self.assertEqual(second_gc.SetFont.call_count, 3)
        for call in second_gc.SetFont.call_args_list:
            self.assertGreaterEqual(contrast(call.args[1], wx.Colour("#203060")), 4.5)
        self.assertNotEqual(
            first_gc.SetFont.call_args_list[0].args[1],
            second_gc.SetFont.call_args_list[0].args[1],
        )
        self.assertEqual(guide.scene.colors.__dict__, saved)
        self.assertFalse(guide.scene.context.elements.modified)

    def rasterize_bed_and_guides(self, guide: object, bed_color: str) -> tuple:
        from meerk40t.gui.scenewidgets.bedwidget import BedWidget

        guide.scene.colors.bed = bed_color
        guide.scene.context.device = SimpleNamespace(
            label="Fixture laser",
            view=SimpleNamespace(unit_width=1000, unit_height=1000),
        )
        guide.scene.has_background = False
        saved = dict(guide.scene.colors.__dict__)
        bitmap = wx.Bitmap(300, 200)
        dc = wx.MemoryDC(bitmap)
        dc.SetBackground(wx.Brush(guide.scene.colors.color_background))
        dc.Clear()
        gc = wx.GraphicsContext.Create(dc)
        gc.Size = (300, 200)
        try:
            gc.PushState()
            gc.Translate(-125, -75)
            gc.Scale(0.5, 0.5)
            BedWidget(guide.scene).process_draw(gc)
            gc.PopState()
            guide.scene.widget_root.scene_widget.matrix = Matrix(
                0.5, 0, 0, 0.5, -125, -75
            )
            gc.Flush()
            before = bitmap.ConvertToImage()
            with (
                patch.object(
                    guide,
                    "_calculate_primary_grid_data",
                    return_value=(
                        [],
                        [],
                        [("10", 5, 80, 0), ("30", 80, 5, -math.pi / 2)],
                    ),
                ),
                patch.object(
                    guide,
                    "_calculate_secondary_guides",
                    return_value=(
                        [],
                        [],
                        [("20", 295, 90, 0), ("40", 100, 195, -math.pi / 2)],
                    ),
                ),
                patch.object(guide, "_draw_magnet_lines"),
            ):
                guide.process_draw(gc)
            gc.Flush()
            after = bitmap.ConvertToImage()
        finally:
            del gc
            dc.SelectObject(wx.NullBitmap)
        self.assertEqual(guide.scene.colors.__dict__, saved)
        self.assertFalse(guide.scene.context.elements.modified)
        return before, after

    def test_ac_u03_5_rasterized_labels_are_readable_over_opposite_bed_color(
        self,
    ) -> None:
        for canvas, bed, source in (
            ("#101010", "#ffffff", "#000000"),
            ("#ffffff", "#101010", "#ffffff"),
        ):
            guide = self.make_guide(canvas, source)
            before, after = self.rasterize_bed_and_guides(guide, bed)
            for label, bounds in (
                ("units", (5, 5, 35, 25)),
                ("primary", (5, 80, 30, 100)),
                ("secondary", (275, 75, 299, 100)),
                ("primary vertical", (65, 5, 85, 25)),
                ("secondary vertical", (85, 175, 105, 199)),
            ):
                with self.subTest(canvas=canvas, label=label):
                    left, top, right, bottom = bounds
                    pixels = [
                        wx.Colour(
                            after.GetRed(x, y),
                            after.GetGreen(x, y),
                            after.GetBlue(x, y),
                        )
                        for x in range(left, right)
                        for y in range(top, bottom)
                    ]
                    self.assertGreaterEqual(
                        max(contrast(pixel, wx.Colour(bed)) for pixel in pixels),
                        4.5,
                        "Ruler label region remains indistinguishable from the bed",
                    )
                    darkest = min(pixels, key=lambda color: luminance(tuple(color[:3])))
                    lightest = max(
                        pixels, key=lambda color: luminance(tuple(color[:3]))
                    )
                    self.assertGreaterEqual(
                        contrast(darkest, lightest),
                        4.5,
                        "Rasterized glyphs need contrast against their actual backing",
                    )
            self.assertEqual(before.GetWidth(), after.GetWidth())

    def test_ac_u03_5_ruler_backing_stays_in_edge_bands(self) -> None:
        for canvas, bed in (("#101010", "#ffffff"), ("#ffffff", "#101010")):
            with self.subTest(canvas=canvas):
                guide = self.make_guide(canvas, "#000000")
                before, after = self.rasterize_bed_and_guides(guide, bed)
                for x, y in ((50, 2), (2, 120), (298, 120), (70, 198)):
                    self.assertEqual(
                        (after.GetRed(x, y), after.GetGreen(x, y), after.GetBlue(x, y)),
                        tuple(wx.Colour(canvas)[:3]),
                    )
                for y in range(40, 160):
                    for x in range(40, 260):
                        self.assertEqual(
                            (
                                after.GetRed(x, y),
                                after.GetGreen(x, y),
                                after.GetBlue(x, y),
                            ),
                            (
                                before.GetRed(x, y),
                                before.GetGreen(x, y),
                                before.GetBlue(x, y),
                            ),
                        )

    def test_ac_u03_5_disabled_guides_leave_bed_raster_unchanged(self) -> None:
        guide = self.make_guide("#101010", "#000000")
        guide.scene.context.draw_mode = self.guides_disabled_flag
        before, after = self.rasterize_bed_and_guides(guide, "#ffffff")
        self.assertEqual(bytes(before.GetData()), bytes(after.GetData()))
