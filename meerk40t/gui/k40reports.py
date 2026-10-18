# Python 3.6 cannot use postponed annotations or subscript built-in collections.
# ruff: noqa: FA100
from math import isfinite
from typing import Callable, Optional

from meerk40t.core.units import UNITS_PER_MM, Length
from meerk40t.kernel.context import Context


def _finite_number(value: object) -> Optional[float]:
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return number if isfinite(number) else None


def _number(value: object, unavailable: str) -> str:
    number = _finite_number(value)
    return unavailable if number is None else f"{number:g}"


def _bed_dimension(
    device: object, setting: str, view_attribute: str
) -> Optional[float]:
    value = getattr(device, setting, None)
    if value is not None:
        try:
            value = float(Length(value))
        except (TypeError, ValueError, OverflowError):
            return None
    else:
        value = getattr(getattr(device, "view", None), view_attribute, None)
    number = _finite_number(value)
    return number / UNITS_PER_MM if number is not None and number > 0 else None


def _design_bounds(elements: object, unavailable: str) -> str:
    bounds = None
    if elements is None:
        return unavailable
    for node in elements.elems():
        try:
            candidate = node.bounds
        except (TypeError, ValueError, OverflowError):
            return unavailable
        if candidate is None or len(candidate) != 4:
            return unavailable
        coordinates = tuple(_finite_number(value) for value in candidate)
        if any(value is None for value in coordinates):
            return unavailable
        if bounds is None:
            bounds = coordinates
        else:
            bounds = (
                min(bounds[0], coordinates[0]),
                min(bounds[1], coordinates[1]),
                max(bounds[2], coordinates[2]),
                max(bounds[3], coordinates[3]),
            )
    if bounds is None:
        return unavailable
    return ", ".join(f"{value / UNITS_PER_MM:g}" for value in bounds) + " mm"


def build_job_summary(context: Context, translate: Callable[[str], str]) -> str:
    _ = translate
    unavailable = _("Unavailable")
    device = getattr(context, "device", None)
    elements = getattr(context, "elements", None)
    width = _bed_dimension(device, "bedwidth", "unit_width")
    height = _bed_dimension(device, "bedheight", "unit_height")
    bed = unavailable
    if width is not None and height is not None:
        bed = f"{width:g} × {height:g} mm"
    lines = [
        _("Job summary snapshot — refresh after editing"),
        _("Device: {device}").format(
            device=getattr(device, "label", None) or unavailable
        ),
        _("Bed: {bed}").format(bed=bed),
        _("Design bounds: {bounds}").format(
            bounds=_design_bounds(elements, unavailable)
        ),
        _("Operations (controller power setting, not measured tube output):"),
    ]
    if elements is None:
        lines.append(unavailable)
        return "\n".join(lines)
    operations = list(elements.ops())
    if not operations:
        lines.append(_("No operations"))
    for operation in operations:
        speed = _number(getattr(operation, "speed", None), unavailable)
        if speed != unavailable:
            speed += " mm/s"
        passes = 1
        if getattr(operation, "passes_custom", False):
            try:
                passes = max(int(getattr(operation, "passes", None)), 1)
            except (TypeError, ValueError, OverflowError):
                passes = None
        lines.append(
            _(
                "{state} | {type} | {label} | Speed: {speed} | Controller power setting: {power} | Passes: {passes}"
            ).format(
                state=_("Enabled")
                if getattr(operation, "output", True)
                else _("Disabled"),
                type=_(operation.type),
                label=operation.label or unavailable,
                speed=speed,
                power=_number(getattr(operation, "power", None), unavailable),
                passes=_number(passes, unavailable),
            )
        )
    return "\n".join(lines)
