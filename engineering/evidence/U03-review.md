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
