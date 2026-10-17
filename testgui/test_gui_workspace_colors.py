import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

import wx

from meerk40t.kernel import Kernel


class WorkspaceColorsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.owns_app = wx.App.Get() is None
        cls.app = wx.App.Get() or wx.App(False)
        from meerk40t.gui import guicolors
        from meerk40t.gui.preferences import Preferences

        cls.guicolors = guicolors
        cls.preferences = Preferences

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.owns_app:
            cls.app.Destroy()

    def setUp(self) -> None:
        self.kernel = Kernel(
            "WorkspaceColorsTest", "0", "WorkspaceColorsTest", ignore_settings=True
        )
        self.kernel.root.themes = SimpleNamespace(dark=True)

    def assert_palette(self, colors, expected: dict) -> None:
        self.assertEqual(
            {key: colors.get_color(key) for key in expected}, expected
        )

    def test_ac_u01_1_macos_dark_appearance_starts_with_bright_workspace(self) -> None:
        with patch.object(self.guicolors, "system", return_value="Darwin", create=True):
            colors = self.guicolors.GuiColors(self.kernel)
        self.assert_palette(colors, self.guicolors.default_color)

    def test_ac_u01_1_other_platforms_keep_dark_workspace_defaults(self) -> None:
        for platform in ("Linux", "Windows"):
            with self.subTest(platform=platform):
                with patch.object(
                    self.guicolors, "system", return_value=platform, create=True
                ):
                    colors = self.guicolors.GuiColors(self.kernel)
                expected = dict(self.guicolors.default_color)
                expected.update(self.guicolors.default_colors_dark)
                self.assert_palette(colors, expected)

    def test_ac_u01_1_saved_macos_workspace_colors_are_preserved(self) -> None:
        saved = {"bed": "#123456", "background": "#234567", "grid": "#345678"}
        for key, value in saved.items():
            self.kernel.write_persistent("colors", key, value)
        with patch.object(self.guicolors, "system", return_value="Darwin", create=True):
            colors = self.guicolors.GuiColors(self.kernel)
        self.assert_palette(colors, saved)

    def test_ac_u01_1_light_appearance_keeps_bright_defaults_everywhere(self) -> None:
        self.kernel.root.themes.dark = False
        for platform in ("Darwin", "Linux", "Windows"):
            with self.subTest(platform=platform):
                with patch.object(
                    self.guicolors, "system", return_value=platform, create=True
                ):
                    colors = self.guicolors.GuiColors(self.kernel)
                self.assert_palette(colors, self.guicolors.default_color)

    def test_ac_u01_2_macos_default_reset_restores_bright_workspace(self) -> None:
        with patch.object(self.guicolors, "system", return_value="Darwin", create=True):
            colors = self.guicolors.GuiColors(self.kernel)
            colors.background = "#123456"
            colors.set_default_colors()
        self.assert_palette(colors, self.guicolors.default_color)

    def test_ac_u01_2_brighter_reset_restores_bright_palette_everywhere(self) -> None:
        for platform in ("Darwin", "Linux", "Windows"):
            with self.subTest(platform=platform):
                with patch.object(
                    self.guicolors, "system", return_value=platform, create=True
                ):
                    colors = self.guicolors.GuiColors(self.kernel)
                    colors.background = "#123456"
                    colors.set_default_colors(brighter=True)
                self.assert_palette(colors, self.guicolors.default_color)

    def test_ac_u01_2_other_platforms_keep_dark_default_reset(self) -> None:
        for platform in ("Linux", "Windows"):
            with self.subTest(platform=platform):
                with patch.object(
                    self.guicolors, "system", return_value=platform, create=True
                ):
                    colors = self.guicolors.GuiColors(self.kernel)
                    colors.set_default_colors()
                expected = dict(self.guicolors.default_color)
                expected.update(self.guicolors.default_colors_dark)
                self.assert_palette(colors, expected)

    def preferences_fixture(self) -> SimpleNamespace:
        return SimpleNamespace(
            context=Mock(root=SimpleNamespace(label_display_color="#123456")),
            panel_color=Mock(),
            color_reset=Mock(),
        )

    def test_ac_u01_3_reading_brighter_button_has_no_side_effects(self) -> None:
        preferences = self.preferences_fixture()
        value = self.preferences.color_reset_brighter.__get__(preferences)
        self.assertIs(value, False)
        preferences.context.assert_not_called()
        preferences.context.signal.assert_not_called()
        preferences.panel_color.reload.assert_not_called()
        preferences.color_reset.assert_not_called()
        self.assertEqual(preferences.context.root.label_display_color, "#123456")

    def test_ac_u01_3_brighter_button_dispatches_reset_and_refresh(self) -> None:
        preferences = self.preferences_fixture()
        self.preferences.color_reset_brighter.__set__(preferences, True)
        preferences.context.assert_called_once_with("scene color unsetbright\n")
        self.assertEqual(preferences.context.root.label_display_color, "#ff0000ff")
        preferences.context.signal.assert_called_once_with("theme", True)
        preferences.panel_color.reload.assert_called_once_with()
        preferences.color_reset.assert_not_called()

    def test_ac_u01_3_false_brighter_button_does_nothing(self) -> None:
        preferences = self.preferences_fixture()
        self.preferences.color_reset_brighter.__set__(preferences, False)
        preferences.context.assert_not_called()
        preferences.context.signal.assert_not_called()
        preferences.panel_color.reload.assert_not_called()
        preferences.color_reset.assert_not_called()
        self.assertEqual(preferences.context.root.label_display_color, "#123456")
