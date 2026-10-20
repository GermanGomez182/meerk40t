# U10 report measurements

Measured on 2026-10-20 with Python 3.13.14 on macOS arm64. Report implementation:
`fb1ae759a`. Raw timings and output hashes are in
[U10-report-profile.json](U10-report-profile.json).

Reproduce from a source checkout:

```sh
uv run --locked python engineering/profile_reports.py --elements 500 4000 --repeats 5
```

The deterministic documents contain paired rectangles, paths and ellipses, 40
cut operations, and references for three quarters of the elements (375 and
3,000). Some operations are disabled and some elements lie outside the bed.
The device is a local synthetic context; collection makes no network or
hardware calls. Each report's first call is recorded, followed by five warm
samples. Reports run in workspace order and share geometry caches. GUI widget
rendering, SVG autosave and actual machine execution are outside this measure.

| Report | 500 elements, warm median | 4,000 elements, warm median |
| --- | ---: | ---: |
| Job summary | 0.387 ms | 2.724 ms |
| Connection | 0.002 ms | 0.002 ms |
| Preview and duration | 43.602 ms | 354.911 ms |
| Design/import audit | 19.178 ms | 154.954 ms |

The sum of warm medians is about 63 ms and 513 ms respectively. First-call sums
are about 472 ms and 1,136 ms; these include initially unpopulated geometry
caches. These are observations of this fixture and host, not timing guarantees.
Duration estimation dominates warm collection. Every repeated report exactly
matched its initial output; the utility records SHA-256 hashes for comparisons.

No report optimization was introduced. This slice records the larger-document
cost and preserves the reviewed report implementation. Profiling a user-reported
slow file or adding a targeted optimization remains a follow-up if this cost is
unacceptable in actual use.
