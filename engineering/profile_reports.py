"""Measure report collection on deterministic vector documents without hardware."""

import argparse
import hashlib
import json
import platform
import statistics
import sys
import time
from types import SimpleNamespace

from meerk40t.core.geomstr import Geomstr
from meerk40t.core.node.elem_ellipse import EllipseNode
from meerk40t.core.node.elem_path import PathNode
from meerk40t.core.node.elem_rect import RectNode
from meerk40t.core.node.op_cut import CutOpNode
from meerk40t.core.units import UNITS_PER_MM
from meerk40t.gui.k40reports import (
    build_connection_report,
    build_design_audit,
    build_job_summary,
    build_preview_report,
)


def document(count: int) -> SimpleNamespace:
    operations = [
        CutOpNode(
            label=f"Synthetic operation {index}",
            output=index % 5 != 0,
            settings={"speed": 100, "power": 500, "passes_custom": False},
        )
        for index in range(40)
    ]
    nodes = []
    for index in range(count):
        pair = index // 2
        x = (400 if pair % 20 == 0 else pair % 100 * 2.5) * UNITS_PER_MM
        y = (pair // 100 % 70 * 2.5) * UNITS_PER_MM
        size = UNITS_PER_MM
        attributes = {"id": f"synthetic-{index}", "label": f"Synthetic vector {index}"}
        if pair % 3 == 0:
            node = RectNode(x=x, y=y, width=size, height=size, **attributes)
        elif pair % 3 == 1:
            geometry = Geomstr()
            geometry.line(complex(x, y), complex(x + size, y + size))
            geometry.line(complex(x + size, y + size), complex(x, y + size))
            node = PathNode(geometry=geometry, **attributes)
        else:
            node = EllipseNode(cx=x, cy=y, rx=size, ry=size, **attributes)
        nodes.append(node)
        if index % 4 != 0:
            operations[index % len(operations)].add_reference(node)
    return SimpleNamespace(
        device=SimpleNamespace(
            name="LihuiyuDevice",
            label="Synthetic CO2",
            bedwidth="300mm",
            bedheight="200mm",
            home_corner="auto",
            mock=True,
            networked=False,
            controller=SimpleNamespace(state="idle", connection_errors=0),
            driver=SimpleNamespace(paused=False),
            spooler=SimpleNamespace(queue=[]),
        ),
        elements=SimpleNamespace(
            ops=lambda: iter(operations), elems=lambda: iter(nodes)
        ),
    )


def measure(count: int, repeats: int) -> dict:
    context = document(count)
    reports = (
        ("job_summary", build_job_summary),
        ("connection", build_connection_report),
        ("preview", build_preview_report),
        ("audit", build_design_audit),
    )
    result = {
        "elements": count,
        "operations": 40,
        "references": sum(len(op.children) for op in context.elements.ops()),
        "reports": {},
    }
    for name, collect in reports:
        started = time.perf_counter()
        expected = collect(context, lambda value: value)
        first_ms = (time.perf_counter() - started) * 1000
        samples = []
        for _ in range(repeats):
            started = time.perf_counter()
            actual = collect(context, lambda value: value)
            samples.append((time.perf_counter() - started) * 1000)
            if actual != expected:
                raise RuntimeError(f"Report output changed during profiling: {name}")
        result["reports"][name] = {
            "first_ms": round(first_ms, 3),
            "median_ms": round(statistics.median(samples), 3),
            "min_ms": round(min(samples), 3),
            "max_ms": round(max(samples), 3),
            "characters": len(expected),
            "sha256": hashlib.sha256(expected.encode("utf-8")).hexdigest(),
        }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--elements", nargs="+", type=int, default=[500, 4000])
    parser.add_argument("--repeats", type=int, default=5)
    arguments = parser.parse_args()
    if arguments.repeats < 1 or any(
        count < 40 or count % 2 for count in arguments.elements
    ):
        parser.error("Use positive repeats and even element counts of at least 40.")
    result = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "repeats": arguments.repeats,
        "scope": "Report collection only; no GUI rendering, network or hardware.",
        "documents": [
            measure(count, arguments.repeats) for count in arguments.elements
        ],
    }
    sys.stdout.write(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
