# U03 review evidence

## Round 1: 2026-10-17, reviewed `4e0cd9fe5`

```text
VERDICT: CHANGES_REQUIRED
ROUND: 1
VERIFY: PASS (633 core tests; 7 targeted GUI tests)
TEST INTEGRITY: unchanged since 6f3dbe98d
AC COVERAGE:
  AC-U03-1: weak (tests compare against configured canvas color, excluding the actual bed beneath labels)
  AC-U03-2: ok
  AC-U03-3: ok
  AC-U03-4: ok
INVARIANTS:
  I2: guarded at meerk40t/gui/scenewidgets/guidewidget.py:172; effective colors are widget-local and saved settings remain unchanged
  I6: guarded at meerk40t/gui/themes.py:233; changes affect presentation only, with no new visible strings or driver changes
FINDINGS:
- [CRITICAL] meerk40t/gui/scenewidgets/guidewidget.py:173: Label contrast uses the configured canvas color even when the bed covers that area. Scenario: canvas #101010, saved guide #000000, white bed zoomed or panned beneath the rulers → fallback becomes white and labels disappear against the bed. Independently reproduced using a real wx.MemoryDC, BedWidget.process_draw(), and GuideWidget._draw_units(): effective label RGBA was (255,255,255,255), actual contrast was 1:1, and the label region contained only white pixels. Scene paints guides over the completed bed/document composite at meerk40t/gui/scene/scene.py:922. Require readable labels against their actual painted backing without changing stored colors, with a raster regression covering opposing canvas/bed colors.
WOULD NOT TRUST: The current mocked drawing tests establish foreground selection but cannot establish visible contrast over the composited workspace. Verify ruler labels over both canvas and bed, including zoom/pan transitions and rotated labels.
```

Handling: accepted. Added AC-U03-5 for a mixed bed/canvas raster regression and a consistent ruler backing. No override or test weakening.

## Test-fixture correction

Override: corrected only the new raster fixture's text placement and sample
regions. Empirical wx.DrawText rendering placed the injected rotated primary
text at x=0..4 for anchor (5,80), outside the test's x=5..25 search and across its
supposedly empty backing sample. The fixture now uses the actual generators'
orientation conventions and matching glyph regions. Contrast thresholds,
palette preservation, disabled behavior, and full interior checks are unchanged.
The test author confirmed bypassing only the new backing still produces 12
assertion failures and no errors. Product code is committed separately.

## Round 2: 2026-10-18, reviewed `df7419aac`

```text
VERDICT: PASS
ROUND: 2
VERIFY: PASS (independent runs: 633 core tests in 44.875s; 11 U03 GUI tests)
TEST INTEGRITY: changed: testgui/test_gui_readability.py gained raster and long-label regressions in ebaea12c0 and d9cb4c20a. Fixture-coordinate correction in 45d503b38 is justified by actual rendering and documented as an override; contrast thresholds and preservation assertions remain intact. Original tests unchanged; no test changes after d9cb4c20a.
AC COVERAGE:
  AC-U03-1: ok
  AC-U03-2: ok
  AC-U03-3: ok
  AC-U03-4: ok
  AC-U03-5: ok
INVARIANTS:
  I2: guarded at meerk40t/gui/scenewidgets/guidewidget.py:172 and :1089; effective colors and backing affect rendering only, with palette preservation and unchanged interior pixels asserted
  I6: guarded at meerk40t/gui/themes.py:233; presentation changes introduce no visible strings, driver changes, or hardware actions
FINDINGS:
none
WOULD NOT TRUST: nothing beyond the above
```

## Orchestration verification and acceptance-test mapping

Final orchestration verification passed 633 core tests and 21 GUI tests. The
independent reviewer separately passed 633 core tests and 11 readability GUI
tests. The registered uv verification command is documented in
`engineering/CONVENTIONS.md`. No new visible strings were introduced, so
translation checks were not applicable.

- AC-U03-1: `test_ac_u03_1_rendered_labels_have_contrast_on_each_background`, `test_ac_u03_1_readable_custom_source_is_used_without_rewriting`, `test_ac_u03_1_transparent_source_uses_effective_contrast`
- AC-U03-2: `test_ac_u03_2_action_labels_contrast_in_both_native_appearances`
- AC-U03-3: `test_ac_u03_3_low_rgba_channels_serialize_and_round_trip`
- AC-U03-4: `test_ac_u03_4_disabled_guides_draw_no_lines_or_labels`, `test_ac_u03_4_theme_refresh_updates_effective_color_without_document_edits`
- AC-U03-5: `test_ac_u03_5_rasterized_labels_are_readable_over_opposite_bed_color`, `test_ac_u03_5_ruler_backing_stays_in_edge_bands`, `test_ac_u03_5_disabled_guides_leave_bed_raster_unchanged`, `test_ac_u03_5_long_ruler_label_trailing_digit_remains_readable`
