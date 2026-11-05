"""Physical phase labels must not be inferred from the region number alone."""

from .validation import P_CRITICAL_MPA, T_CRITICAL_K

PHASE_LABELS = {
    "compressed_liquid": "Compressed liquid (مایع فشرده)",
    "superheated_vapor": "Superheated vapor (بخار فوق‌گرم)",
    "gas": "Gas above critical temperature (گاز بالاتر از دمای بحرانی)",
    "supercritical": "Supercritical fluid (سیال فوق‌بحرانی)",
    "critical": "Critical point (نقطه بحرانی)",
    "saturated_liquid": "Saturated liquid (مایع اشباع)",
    "saturated_vapor": "Saturated vapor (بخار اشباع)",
    "two_phase": "Liquid–vapor mixture (مخلوط مایع و بخار)",
}


def is_critical(temperature: float, pressure: float) -> bool:
    return abs(temperature - T_CRITICAL_K) <= 1e-8 and abs(pressure - P_CRITICAL_MPA) <= 1e-8


def phase_for_pt(temperature: float, pressure: float, saturation_pressure: float | None) -> str:
    if is_critical(temperature, pressure):
        return "critical"
    if temperature >= T_CRITICAL_K:
        return "supercritical" if pressure >= P_CRITICAL_MPA else "gas"
    if saturation_pressure is None:
        raise ValueError("Subcritical phase classification requires saturation pressure.")
    return "compressed_liquid" if pressure > saturation_pressure else "superheated_vapor"


def phase_for_quality(quality: float) -> str:
    if quality == 0:
        return "saturated_liquid"
    if quality == 1:
        return "saturated_vapor"
    return "two_phase"
