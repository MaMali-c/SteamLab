"""Comparison is independent of backend validation; a PDF is not ground truth."""

import math
from dataclasses import dataclass

from steamlab.core.errors import SteamLabError
from steamlab.core.models import State

from .interpolation import LinearStep, linear_step
from .repository import TableRow

PROPERTIES = ("v", "u", "h", "s")


class TableUnavailable(SteamLabError):
    def __init__(self):
        super().__init__(
            "No checked source rows bracket this state in the V1 dataset; no extrapolation was used.",
            "در مجموعه محدود نسخه اول، ردیف‌های تأییدشده کافی برای این حالت موجود نیست؛ برون‌یابی انجام نشد.",
        )


@dataclass(frozen=True)
class TableEstimate:
    properties: dict[str, float]
    source_rows: tuple[TableRow, ...]
    steps: tuple[LinearStep, ...]
    method: str


def _close(a: float, b: float) -> bool:
    return math.isclose(a, b, rel_tol=0, abs_tol=1e-8)


def _at_coordinate(rows: list[TableRow], axis: str, target: float) -> TableEstimate:
    rows = sorted(rows, key=lambda row: getattr(row, axis))
    for row in rows:
        if _close(getattr(row, axis), target):
            return TableEstimate(row.properties, (row,), (), "Direct lookup (خواندن مستقیم)")
    for low, high in zip(rows, rows[1:]):
        z1, z2 = getattr(low, axis), getattr(high, axis)
        if z1 < target < z2:
            steps = tuple(
                linear_step(name, axis, target, z1, z2, low.properties[name], high.properties[name])
                for name in PROPERTIES
            )
            return TableEstimate(
                {step.property_name: step.result for step in steps},
                (low, high),
                steps,
                "Linear interpolation (درون‌یابی خطی)",
            )
    raise TableUnavailable()


def estimate_for_state(state: State, rows: tuple[TableRow, ...]) -> TableEstimate:
    if state.quality is not None:
        axis = "temperature_c" if state.input_pair == "TX" else "pressure_kpa"
        target = state.temperature_c if axis == "temperature_c" else state.pressure_mpa * 1000
        endpoints = (0, 1) if 0 < state.quality < 1 else (state.quality,)
        estimates = [
            _at_coordinate(
                [r for r in rows if r.kind == "saturation" and r.quality == x], axis, target
            )
            for x in endpoints
        ]
        if len(estimates) == 1:
            return estimates[0]
        low, high = estimates
        mixture_steps = tuple(
            linear_step(
                name, "quality", state.quality, 0, 1, low.properties[name], high.properties[name]
            )
            for name in PROPERTIES
        )
        return TableEstimate(
            {step.property_name: step.result for step in mixture_steps},
            low.source_rows + high.source_rows,
            low.steps + high.steps + mixture_steps,
            "Saturation lookup/interpolation + mass mixture (جدول اشباع و میانگین جرمی)",
        )
    if state.phase != "superheated_vapor":
        raise TableUnavailable()
    candidates = [r for r in rows if r.kind == "superheated"]
    same_pressure = [r for r in candidates if _close(r.pressure_kpa, state.pressure_mpa * 1000)]
    try:
        return _at_coordinate(same_pressure, "temperature_c", state.temperature_c)
    except TableUnavailable:
        same_temperature = [r for r in candidates if _close(r.temperature_c, state.temperature_c)]
        return _at_coordinate(same_temperature, "pressure_kpa", state.pressure_mpa * 1000)


def differences(state: State, estimate: TableEstimate) -> list[dict]:
    records = []
    for name in PROPERTIES:
        reference, computed = estimate.properties[name], getattr(state, name)
        absolute = abs(computed - reference)
        # Guard in the property's documented engineering units.
        relative = None if abs(reference) <= 1e-12 else 100 * absolute / abs(reference)
        records.append(
            {
                "property": name,
                "if97": computed,
                "table": reference,
                "absolute": absolute,
                "relative_percent": relative,
            }
        )
    return records
