"""Saturation curve sampled directly from the validated IF97 adapter."""

import altair as alt
import pandas as pd

from steamlab.core.engine import saturation_pressure
from steamlab.core.validation import T_CRITICAL_K, T_MIN_K

MIN_C = round(T_MIN_K - 273.15, 3)
MAX_C = round(T_CRITICAL_K - 273.15, 3)
PRESSURE_FACTORS = {"kPa": 1000.0, "MPa": 1.0, "bar": 10.0}


def pressure_at_temperature(temperature_c: float, unit: str) -> float:
    if not MIN_C <= temperature_c <= MAX_C:
        raise ValueError("Temperature must lie within the saturation boundary.")
    # Preserve exact endpoints across Celsius-to-Kelvin floating-point conversion.
    temperature_k = (
        T_MIN_K if temperature_c == MIN_C
        else T_CRITICAL_K if temperature_c == MAX_C
        else temperature_c + 273.15
    )
    return saturation_pressure(temperature_k) * PRESSURE_FACTORS[unit]


def curve_data(lower_c: float, upper_c: float, unit: str) -> pd.DataFrame:
    if not MIN_C <= lower_c < upper_c <= MAX_C:
        raise ValueError("Temperature range must lie within the saturation boundary.")
    temperatures = [lower_c + (upper_c - lower_c) * i / 400 for i in range(401)]
    temperatures[-1] = upper_c
    return pd.DataFrame(
        {
            "temperature_c": temperatures,
            "pressure": [pressure_at_temperature(t, unit) for t in temperatures],
        }
    )


def vapor_pressure_chart(data, temperature_c, pressure, unit, logarithmic):
    tooltip = [
        alt.Tooltip("temperature_c:Q", title="Temperature (دما) · °C", format=".3f"),
        alt.Tooltip("pressure:Q", title=f"Pressure (فشار) · {unit}", format=".6g"),
    ]
    base = alt.Chart(data).encode(
        x=alt.X("temperature_c:Q", title="Temperature (دما) · °C", scale=alt.Scale(zero=False)),
        y=alt.Y(
            "pressure:Q",
            title=f"Saturation pressure (فشار اشباع) · {unit}",
            scale=alt.Scale(type="log" if logarithmic else "linear", zero=False),
        ),
        tooltip=tooltip,
    )
    hover = alt.selection_point(nearest=True, on="pointerover", fields=["temperature_c"],
                                empty=False, clear="pointerout")
    line = base.mark_line(color="#1685ff", strokeWidth=3, clip=True)
    points = base.mark_circle(size=65).encode(
        opacity=alt.condition(hover, alt.value(1), alt.value(0)),
        color=alt.value("#1685ff"),
    ).add_params(hover)
    selected = pd.DataFrame({"temperature_c": [temperature_c], "pressure": [pressure]})
    marker = alt.Chart(selected).mark_point(
        color="#f59e0b", filled=True, size=150, stroke="white", strokeWidth=1.5
    ).encode(x="temperature_c:Q", y="pressure:Q", tooltip=tooltip)
    return (line + points + marker).properties(height=420)
