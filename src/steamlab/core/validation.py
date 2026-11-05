"""Software limits are documented separately from the IF97 formulation."""

from .errors import InputError
from .units import finite_number

T_MIN_K = 273.16  # Conservative fluid-only lower bound; avoids the sub-triple strip.
T_MAX_K = 2273.15
T_REGION5_K = 1073.15
T_CRITICAL_K = 647.096
P_CRITICAL_MPA = 22.064
P_MIN_MPA = 0.000611212677444  # iapws 1.5.5 public TP solver lower bound.
P_TRIPLE_MPA = 0.0006116570000106653
SATURATION_TOLERANCE_K = 0.01
CRITICAL_QUALITY_GUARD_K = 0.01


def validate_temperature(value: object) -> float:
    temperature = finite_number(value, "temperature (دما)")
    if not T_MIN_K <= temperature <= T_MAX_K:
        raise InputError(
            "Temperature must be between 273.16 and 2273.15 K (0.01–2000 °C).",
            "دما باید بین ۰٫۰۱ و ۲۰۰۰ درجه سلسیوس باشد؛ مدل یخ در این نسخه وجود ندارد.",
        )
    return temperature


def validate_pressure(value: object) -> float:
    pressure = finite_number(value, "absolute pressure (فشار مطلق)")
    if not P_MIN_MPA <= pressure <= 100.0:
        raise InputError(
            f"Absolute pressure must be between {P_MIN_MPA:.12g} and 100 MPa.",
            "فشار مطلق باید در محدوده نرم‌افزار باشد؛ فشار گیج را مستقیم وارد نکنید.",
        )
    return pressure


def validate_pt(temperature: object, pressure: object) -> tuple[float, float]:
    temperature, pressure = validate_temperature(temperature), validate_pressure(pressure)
    if temperature > T_REGION5_K and pressure > 50.0:
        raise InputError(
            "Above 1073.15 K (800 °C), pressure must not exceed 50 MPa.",
            "بالاتر از ۸۰۰ درجه سلسیوس، فشار نباید بیشتر از ۵۰ مگاپاسکال باشد.",
        )
    return temperature, pressure


def validate_quality(value: object) -> float:
    quality = finite_number(value, "vapor quality (کیفیت بخار)")
    if not 0 <= quality <= 1:
        raise InputError("Quality must satisfy 0 ≤ x ≤ 1.", "کیفیت بخار باید بین صفر و یک باشد.")
    return quality
