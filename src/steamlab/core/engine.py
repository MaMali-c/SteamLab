"""The sole IAPWS adapter. No Streamlit, table data, or UI state is imported here."""

import math
import warnings

from iapws import IAPWS97
from iapws.iapws97 import _PSat_T, _TSat_P

from .errors import CalculationError, InputError, SaturationAmbiguity
from .models import State
from .phase import is_critical, phase_for_pt, phase_for_quality
from .validation import (
    CRITICAL_QUALITY_GUARD_K,
    P_CRITICAL_MPA,
    P_TRIPLE_MPA,
    SATURATION_TOLERANCE_K,
    T_CRITICAL_K,
    T_MIN_K,
    validate_pressure,
    validate_pt,
    validate_quality,
    validate_temperature,
)


def _backend(**kwargs) -> IAPWS97:
    try:
        with warnings.catch_warnings():
            # Iterative failures must not become apparently valid UI results.
            warnings.simplefilter("error", RuntimeWarning)
            result = IAPWS97(**kwargs)
        values = [result.T, result.P, result.v, result.u, result.h, result.s]
        if not all(value is not None and math.isfinite(value) for value in values):
            raise ValueError("Non-finite backend state")
        if result.v <= 0:
            raise ValueError("Non-positive volume")
        if abs(result.h - result.u - result.P * 1000 * result.v) > 1e-5:
            raise ValueError("Energy identity failed")
        return result
    except (NotImplementedError, ValueError, ArithmeticError, RuntimeWarning) as exc:
        raise CalculationError(
            "The IF97 solver could not produce a consistent state for these inputs.",
            "حل‌گر برای این ورودی‌ها نتیجه معتبر تولید نکرد؛ محدوده و نزدیکی به نقطه بحرانی را بررسی کنید.",
        ) from exc


def saturation_temperature(pressure_mpa: object) -> float:
    pressure = validate_pressure(pressure_mpa)
    if not P_TRIPLE_MPA <= pressure <= P_CRITICAL_MPA:
        raise InputError(
            "Saturation pressure must be between the triple-point and critical pressures.",
            "فشار اشباع باید بین فشار نقطه سه‌گانه و فشار بحرانی باشد.",
        )
    # Region 4, Eq. 31. Calling an endpoint EOS can introduce region-3
    # pressure/density iteration residuals into an otherwise exact inverse.
    # These documented underscore APIs are isolated here and version-pinned.
    return float(_TSat_P(pressure))


def saturation_pressure(temperature_k: object) -> float:
    temperature = validate_temperature(temperature_k)
    if temperature > T_CRITICAL_K:
        raise InputError(
            "No saturation above the critical temperature.", "بالاتر از دمای بحرانی اشباع نداریم."
        )
    return float(_PSat_T(temperature))  # Region 4, Eq. 30.


def _state(result: IAPWS97, phase: str, pair: str, quality: float | None) -> State:
    notes = ()
    if abs(result.T - T_CRITICAL_K) < 1 and abs(result.P - P_CRITICAL_MPA) < 0.5:
        notes = (
            "Near the critical point: properties are sensitive to input precision "
            "(نزدیک نقطه بحرانی، خواص به دقت ورودی حساس‌اند).",
        )
    return State(
        temperature_k=float(result.T),
        pressure_mpa=float(result.P),
        v=float(result.v),
        u=float(result.u),
        h=float(result.h),
        s=float(result.s),
        phase=phase,
        region=int(result.region),
        quality=quality,
        input_pair=pair,
        warnings=notes,
    )


def solve_pt(temperature_k: object, pressure_mpa: object) -> State:
    temperature, pressure = validate_pt(temperature_k, pressure_mpa)
    critical = is_critical(temperature, pressure)
    if not critical and P_TRIPLE_MPA <= pressure < P_CRITICAL_MPA:
        tsat = saturation_temperature(pressure)
        if abs(temperature - tsat) <= SATURATION_TOLERANCE_K:
            raise SaturationAmbiguity(tsat, pressure)
    psat = saturation_pressure(temperature) if T_MIN_K <= temperature < T_CRITICAL_K else None
    result = _backend(T=temperature, P=pressure)
    # The library's x=0/1 on a single-phase state is not physical vapor quality.
    return _state(result, phase_for_pt(temperature, pressure, psat), "PT", None)


def _guard_quality_temperature(temperature: float) -> None:
    if temperature > T_CRITICAL_K - CRITICAL_QUALITY_GUARD_K:
        raise InputError(
            "Quality mode is disabled within 0.01 K of the critical temperature and above it.",
            "کیفیت بخار در فاصله کمتر از ۰٫۰۱ کلوین تا دمای بحرانی و بالاتر از آن پشتیبانی نمی‌شود.",
        )


def solve_px(pressure_mpa: object, quality: object) -> State:
    pressure, quality = validate_pressure(pressure_mpa), validate_quality(quality)
    temperature = saturation_temperature(pressure)
    _guard_quality_temperature(temperature)
    return _state(_backend(P=pressure, x=quality), phase_for_quality(quality), "PX", quality)


def solve_tx(temperature_k: object, quality: object) -> State:
    temperature, quality = validate_temperature(temperature_k), validate_quality(quality)
    _guard_quality_temperature(temperature)
    return _state(_backend(T=temperature, x=quality), phase_for_quality(quality), "TX", quality)
