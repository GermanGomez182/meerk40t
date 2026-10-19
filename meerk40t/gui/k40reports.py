# Python 3.6 cannot use postponed annotations or subscript built-in collections.
# ruff: noqa: FA100
from copy import copy
from math import isfinite
from re import fullmatch
from typing import Callable, Dict, List, Optional, Tuple

from meerk40t.core.node.node import Node
from meerk40t.core.units import UNITS_PER_MM, Length
from meerk40t.kernel.context import Context
from meerk40t.svgelements import Matrix


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


def _validate_audit_shape(node: Node, translate: Callable[[str], str]) -> None:
    _ = translate
    coordinates = {
        "elem rect": ("x", "y", "width", "height", "rx", "ry"),
        "elem ellipse": ("cx", "cy", "rx", "ry"),
        "elem line": ("x1", "y1", "x2", "y2"),
        "elem point": ("x", "y"),
    }
    # Shape bounding boxes can omit NaN coordinates and appear falsely complete.
    for attribute in coordinates.get(node.type, ()):
        if _finite_number(getattr(node, attribute, None)) is None:
            raise ValueError(
                _("Invalid shape coordinate: {attribute}").format(attribute=attribute)
            )


def _audit_bounds(
    node: Node, translate: Callable[[str], str]
) -> Tuple[float, float, float, float]:
    _ = translate
    _validate_audit_shape(node, _)
    candidate = node.bounds
    if candidate is None or len(candidate) != 4:
        raise ValueError(_("Missing bounds"))
    values = tuple(float(value) for value in candidate)
    if not all(isfinite(value) for value in values):
        raise ValueError(_("Nonfinite bounds"))
    left, top, right, bottom = values
    if left > right or top > bottom:
        raise ValueError(_("Invalid bounds order"))
    return left, top, right, bottom


def _audit_vector_key(
    node: Node, translate: Callable[[str], str]
) -> Tuple[object, ...]:
    _ = translate
    _validate_audit_shape(node, _)
    matrix = tuple(node.matrix[index] for index in range(6))
    if any(_finite_number(value) is None for value in matrix):
        raise ValueError(_("Nonfinite transform"))
    # Reset only the copy: a singular transform can hide distinct native segments.
    local = copy(node)
    local.matrix = Matrix()
    geometry = local.as_geometry()
    segments = geometry.segments[: geometry.index]
    return matrix, segments.shape, segments.dtype.str, segments.tobytes()


def build_design_audit(context: Context, translate: Callable[[str], str]) -> str:
    _ = translate
    unavailable = _("Unavailable")
    elements = getattr(context, "elements", None)
    nodes = list(elements.elems()) if elements is not None else []
    assigned_ids = set()
    if elements is not None:
        for operation in elements.ops():
            for descendant in operation.flat():
                if descendant.type == "reference":
                    assigned_ids.add(id(descendant.node))
    assigned: List[str] = []
    unassigned: List[str] = []
    outside: List[str] = []
    limitations: List[str] = []
    duplicates: Dict[Tuple[object, ...], List[str]] = {}
    bounds: List[Tuple[float, float, float, float]] = []
    device = getattr(context, "device", None)
    width = _bed_dimension(device, "bedwidth", "unit_width")
    height = _bed_dimension(device, "bedheight", "unit_height")
    vectors = {
        "elem path",
        "elem polyline",
        "elem rect",
        "elem ellipse",
        "elem line",
        "elem point",
    }
    for index, node in enumerate(nodes, 1):
        identifier = _("{label} [ID: {id}; element {index}]").format(
            label=node.label or _("Unlabeled"),
            id=getattr(node, "id", None) or unavailable,
            index=index,
        )
        (assigned if id(node) in assigned_ids else unassigned).append(identifier)
        try:
            candidate = _audit_bounds(node, _)
            bounds.append(candidate)
            if (
                width is not None
                and height is not None
                and (
                    candidate[0] < 0
                    or candidate[1] < 0
                    or candidate[2] > width * UNITS_PER_MM
                    or candidate[3] > height * UNITS_PER_MM
                )
            ):
                outside.append(identifier)
        except (ArithmeticError, AttributeError, TypeError, ValueError) as error:
            limitations.append(
                _("Bounds unavailable for {element}: {error}").format(
                    element=identifier, error=error
                )
            )
        if node.type not in vectors:
            limitations.append(
                _("Duplicate check unsupported for {element} ({type})").format(
                    element=identifier, type=_(node.type)
                )
            )
            continue
        try:
            key = _audit_vector_key(node, _)
            duplicates.setdefault(key, []).append(identifier)
        except (ArithmeticError, AttributeError, TypeError, ValueError) as error:
            limitations.append(
                _("Duplicate check unavailable for {element}: {error}").format(
                    element=identifier, error=error
                )
            )
    lines = [_("Design/import audit snapshot — refresh after editing")]
    if not nodes:
        lines.append(_("No design elements; geometry checks unavailable"))
    if bounds and len(bounds) == len(nodes):
        left = min(value[0] for value in bounds) / UNITS_PER_MM
        top = min(value[1] for value in bounds) / UNITS_PER_MM
        right = max(value[2] for value in bounds) / UNITS_PER_MM
        bottom = max(value[3] for value in bounds) / UNITS_PER_MM
        lines.extend(
            (
                _(
                    "Scene-space design bounds: {left:g}, {top:g}, {right:g}, {bottom:g} mm"
                ).format(left=left, top=top, right=right, bottom=bottom),
                _("Design dimensions: {width:g} × {height:g} mm").format(
                    width=right - left, height=bottom - top
                ),
            )
        )
    else:
        lines.extend(
            (_("Design bounds: Unavailable"), _("Design dimensions: Unavailable"))
        )
    if width is None or height is None:
        lines.append(_("Outside bed: Unavailable — missing or invalid bed dimensions"))
    else:
        lines.append(
            _("Outside bed: {count} (checked {checked} of {total} elements)").format(
                count=len(outside), checked=len(bounds), total=len(nodes)
            )
        )
        lines.extend(outside)
    lines.append(_("Assigned elements: {count}").format(count=len(assigned)))
    lines.append(_("Unassigned elements: {count}").format(count=len(unassigned)))
    lines.extend(unassigned)
    groups = [group for group in duplicates.values() if len(group) > 1]
    lines.append(_("Exact duplicate vector groups: {count}").format(count=len(groups)))
    lines.extend("; ".join(group) for group in groups)
    if limitations:
        lines.append(_("Limitations:"))
        lines.extend(limitations)
    return "\n".join(lines)
