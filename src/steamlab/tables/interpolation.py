"""Linear interpolation with explicit weights and no extrapolation."""

from dataclasses import dataclass

from steamlab.core.errors import InputError
from steamlab.core.units import finite_number


@dataclass(frozen=True)
class LinearStep:
    property_name: str
    coordinate: str
    z: float
    z1: float
    z2: float
    y1: float
    y2: float
    weight: float
    result: float


def linear_step(
    name: str, coordinate: str, z: float, z1: float, z2: float, y1: float, y2: float
) -> LinearStep:
    z, z1, z2, y1, y2 = [
        finite_number(v, "interpolation value (مقدار درون‌یابی)") for v in (z, z1, z2, y1, y2)
    ]
    if z1 >= z2:
        raise InputError(
            "Interpolation bounds must increase.", "کران‌های درون‌یابی باید صعودی باشند."
        )
    if not z1 <= z <= z2:
        raise InputError("Extrapolation is disabled.", "برون‌یابی مجاز نیست.")
    weight = (z - z1) / (z2 - z1)
    return LinearStep(name, coordinate, z, z1, z2, y1, y2, weight, y1 + weight * (y2 - y1))
