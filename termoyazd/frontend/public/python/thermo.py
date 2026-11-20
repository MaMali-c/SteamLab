"""IF97 boundary validation and SI engineering-unit serialization.

Temperature is kelvin and pressure MPa inside iapws; public API uses °C/kPa.
Quality is deliberately null for every single-phase T,P state.
"""
from functools import lru_cache
from math import isfinite

from iapws import IAPWS97
from iapws.iapws97 import _PSat_T

TC = 647.096
PC = 22.064
PMIN = 0.000611212677444
SATURATION_TOL_MPA = 1e-8


class StateError(ValueError):
    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(message)


def calculate_tp(temperature_c: float, pressure_kpa: float) -> dict:
    if not all(isfinite(n) for n in (temperature_c, pressure_kpa)):
        raise StateError("invalid_number", "Temperature and pressure must be finite numbers.")
    t, p = temperature_c + 273.15, pressure_kpa / 1000.0
    if not 273.15 <= t <= 2273.15 or not PMIN <= p <= 100:
        raise StateError("out_of_range", "IF97 requires 0–2000 °C and 0.611212677444–100000 kPa; above 800 °C pressure must not exceed 50000 kPa.")
    if t > 1073.15 and p > 50:
        raise StateError("out_of_range", "Above 800 °C IF97 permits pressure only up to 50000 kPa.")
    # At the critical point x and cp are undefined/singular. Do not report a
    # numerically unstable result as a normal single-phase state.
    if abs(t - TC) <= 1e-7 and abs(p - PC) <= SATURATION_TOL_MPA:
        raise StateError("critical_point", "The exact critical point is not supported in this milestone; quality is undefined and heat capacity is singular.")
    if t < TC and abs(p - _PSat_T(t)) <= SATURATION_TOL_MPA:
        raise StateError("ambiguous_saturation", "T and P lie on the saturation curve (within 0.00001 kPa). Quality or another independent property is required to determine h, u, s and v.")
    try:
        state = IAPWS97(T=t, P=p)
    except (NotImplementedError, ValueError, OverflowError, RuntimeError) as exc:
        raise StateError("unsupported_state", "The IF97 solver could not resolve this state. Check the input and validity limits.") from exc
    if t >= TC and p >= PC:
        phase = "Supercritical fluid"
    elif t >= TC:
        phase = "Gas"
    elif p > _PSat_T(t):
        phase = "Compressed liquid"
    else:
        phase = "Superheated vapor"
    properties = {"T": temperature_c, "P": pressure_kpa, "h": state.h,
                  "u": state.u, "s": state.s, "v": state.v,
                  "rho": state.rho, "cp": state.cp}
    if not all(value is not None and isfinite(value) for value in properties.values()):
        raise StateError("numerical_failure", "The solver returned a non-finite property; no result was accepted.")
    return {"fluid": "Water", "input_pair": "TP", "properties": properties,
            "units": {"T": "°C", "P": "kPa", "h": "kJ/kg", "u": "kJ/kg",
                      "s": "kJ/(kg·K)", "v": "m³/kg", "rho": "kg/m³", "cp": "kJ/(kg·K)"},
            "phase": phase, "region": int(state.region), "quality": None,
            "quality_note": "Quality is defined only on the liquid–vapor coexistence curve; T + P alone cannot select a mixture state.",
            "method": "IAPWS-IF97", "warnings": []}


@lru_cache(maxsize=1)
def saturation_diagram() -> dict:
    # Saturation boundary for context only. These are real IF97 states,
    # not an inverse-input solver exposed by the calculator.
    points = []
    for index in range(81):
        t = 273.16 + (TC - 0.02 - 273.16) * index / 80
        liquid, vapor = IAPWS97(T=t, x=0), IAPWS97(T=t, x=1)
        points.append({"T": t - 273.15, "sf": liquid.s, "sg": vapor.s})
    return {"method": "IAPWS-IF97", "points": points,
            "note": "Sampled saturation boundary; lines between samples are for visualization only."}
