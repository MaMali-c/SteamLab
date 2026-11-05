"""Convert at the boundary; never round values before calculation."""

import math

from .errors import InputError


def finite_number(value: object, name: str) -> float:
    if isinstance(value, bool):
        raise InputError(f"{name} must be a number.", "ورودی باید عدد باشد.")
    try:
        number = float(value)
    except (ValueError, TypeError, OverflowError) as exc:
        raise InputError(f"Enter a numeric {name}.", "مقدار عددی را وارد کنید.") from exc
    if not math.isfinite(number):
        raise InputError(f"{name} must be finite.", "ورودی باید عدد متناهی باشد.")
    return number


def temperature_to_k(value: object, unit: str) -> float:
    value = finite_number(value, "temperature (دما)")
    if unit == "°C":
        return value + 273.15
    if unit == "K":
        return value
    raise InputError("Unsupported temperature unit.", "واحد دما پشتیبانی نمی‌شود.")


def pressure_to_mpa(value: object, unit: str) -> float:
    factors = {"Pa": 1e-6, "kPa": 1e-3, "MPa": 1.0, "bar": 0.1}
    if unit not in factors:
        raise InputError("Unsupported pressure unit.", "واحد فشار پشتیبانی نمی‌شود.")
    return finite_number(value, "pressure (فشار)") * factors[unit]


def volume_to_m3kg(value: object, unit: str) -> float:
    factors = {"cm³/g": 1e-3, "m³/kg": 1.0}
    if unit not in factors:
        raise InputError("Unsupported volume unit.", "واحد حجم ویژه پشتیبانی نمی‌شود.")
    return finite_number(value, "specific volume (حجم ویژه)") * factors[unit]
