# Python 3.6 cannot use postponed annotations or subscript built-in collections.
# ruff: noqa: FA100
from math import isfinite
from re import fullmatch
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


def build_connection_report(context: Context, translate: Callable[[str], str]) -> str:
    _ = translate
    unknown = _("Unknown")
    device = getattr(context, "device", None)
    if device is None:
        return _("Connection: unavailable — no active device")
    if getattr(device, "name", None) != "LihuiyuDevice":
        return _("Connection: unavailable — unsupported device")
    lines = [_("Passive connection snapshot — no hardware probing")]
    next_step = _(
        "Check the USB cable and controller; review the Controller window, then refresh."
    )
    try:
        if getattr(device, "networked", False):
            transport = _("Network / TCP connection: unverified (no socket probing)")
        elif getattr(device, "mock", False):
            transport = _("Mock transport — no hardware connection observed")
        else:
            controller = getattr(device, "controller", None)
            connection = getattr(controller, "connection", None)
            connected = connection is not None and connection.is_connected()
            transport = (
                _("USB connection: connected (local software handle only)")
                if connected
                else _("USB connection: disconnected")
            )
        lines.append(transport)
    except (AttributeError, OSError, RuntimeError, TypeError, ValueError) as error:
        # Status providers can fail independently; expose each failure in the report.
        lines.append(_("Connection status error: {error}").format(error=error))
        lines.append(next_step)
    try:
        controller = getattr(device, "controller", None)
        state = getattr(controller, "state", None)
        driver = getattr(device, "driver", None)
        paused = getattr(driver, "paused", None)
        lines.append(
            _("Software controller state: {state}").format(
                state=_(state) if state else unknown
            )
        )
        pause = _("Paused") if paused is True or state == "pause" else unknown
        if paused is False and state != "pause":
            pause = _("Not paused")
        lines.append(_("Software pause: {pause}").format(pause=pause))
    except (AttributeError, OSError, RuntimeError, TypeError, ValueError) as error:
        lines.append(_("Software controller status error: {error}").format(error=error))
        lines.append(next_step)
    try:
        spooler = getattr(device, "spooler", None)
        queue = getattr(spooler, "queue", None)
        size = str(len(queue)) if queue is not None else unknown
        lines.append(_("Software queue size: {size}").format(size=size))
    except (AttributeError, OSError, RuntimeError, TypeError, ValueError) as error:
        lines.append(_("Software queue status error: {error}").format(error=error))
        lines.append(next_step)
    try:
        controller = getattr(device, "controller", None)
        errors = getattr(controller, "connection_errors", None)
        lines.append(
            _("Connection errors: {count}").format(
                count=str(errors) if errors is not None else unknown
            )
        )
        if errors:
            lines.append(next_step)
    except (AttributeError, OSError, RuntimeError, TypeError, ValueError) as error:
        lines.append(_("Connection errors unavailable: {error}").format(error=error))
        lines.append(next_step)
    lines.extend((_("Physical position: unknown"), _("Tube output: unknown")))
    return "\n".join(lines)


def _software_duration(elements: object, translate: Callable[[str], str]) -> str:
    _ = translate
    unavailable = _("Unavailable")
    if elements is None:
        return unavailable
    total = 0
    found = False
    for operation in elements.ops():
        if not getattr(operation, "output", True):
            continue
        found = True
        estimate = getattr(operation, "time_estimate", None)
        if not callable(estimate):
            return unavailable
        try:
            duration = estimate()
        except (
            ArithmeticError,
            AttributeError,
            OSError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as error:
            return _("Unavailable — estimation error: {error}").format(error=error)
        if (
            not isinstance(duration, str)
            or fullmatch(r"[0-9]+:[0-5][0-9]:[0-5][0-9]", duration) is None
        ):
            return unavailable
        hours, minutes, seconds = (int(part) for part in duration.split(":"))
        total += hours * 3600 + minutes * 60 + seconds
    if not found:
        return unavailable
    hours, remainder = divmod(total, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}:{minutes:02d}:{seconds:02d}"


def build_preview_report(context: Context, translate: Callable[[str], str]) -> str:
    _ = translate
    unavailable = _("Unavailable")
    device = getattr(context, "device", None)
    elements = getattr(context, "elements", None)
    return "\n".join(
        (
            _("Scene origin: 0, 0 mm"),
            _("Configured home corner: {corner}").format(
                corner=_(getattr(device, "home_corner", None) or unavailable)
            ),
            _("Physical position: unknown"),
            _("Scene-space design bounds: {bounds}").format(
                bounds=_design_bounds(elements, unavailable)
            ),
            _("Software duration estimate: {duration}").format(
                duration=_software_duration(elements, _)
            ),
        )
    )
