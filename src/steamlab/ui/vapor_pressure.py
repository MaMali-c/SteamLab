"""Interactive, bilingual vapor-pressure page."""

import streamlit as st

from steamlab.plots.vapor_pressure import (
    MAX_C,
    MIN_C,
    PRESSURE_FACTORS,
    curve_data,
    pressure_at_temperature,
    vapor_pressure_chart,
)


def vapor_pressure_page() -> None:
    st.subheader("Vapor Pressure Curve (نمودار فشار بخار)")
    st.write(
        "Saturation pressure of pure water versus temperature "
        "(فشار بخار اشباع آب خالص برحسب دما)."
    )
    st.caption(
        "Hover over the curve to read values; the orange point is your selected temperature "
        "(برای دیدن مقدارها روی منحنی حرکت کنید؛ نقطه نارنجی دمای انتخابی شماست)."
    )
    lower, upper = st.slider(
        "Temperature Range (بازه دما) · °C",
        min_value=MIN_C, max_value=MAX_C, value=(MIN_C, 200.0), step=0.01,
        format="%.3f", key="vapor_range",
    )
    if lower >= upper:
        st.info("Choose two different temperatures (دو دمای متفاوت برای بازه انتخاب کنید).")
        return
    left, right = st.columns(2)
    unit = left.selectbox(
        "Pressure Unit (واحد فشار)", list(PRESSURE_FACTORS), key="vapor_unit",
    )
    logarithmic = right.checkbox("Logarithmic Scale (مقیاس لگاریتمی)", key="vapor_log")
    st.session_state.vapor_temperature = min(
        upper, max(lower, st.session_state.get("vapor_temperature", 100.0))
    )
    temperature = st.number_input(
        "Selected Temperature (دمای انتخابی) · °C",
        min_value=lower, max_value=upper, step=1.0, format="%.3f", key="vapor_temperature",
    )
    pressure = pressure_at_temperature(temperature, unit)
    st.metric(f"Saturation Pressure (فشار اشباع) · {unit}", f"{pressure:.6g}")
    data = curve_data(lower, upper, unit)
    st.altair_chart(
        vapor_pressure_chart(data, temperature, pressure, unit, logarithmic),
        width="stretch",
    )
    st.caption(
        "IF97 saturation equation · absolute pressure · 0.01–373.946 °C "
        "(معادله اشباع IF97؛ فشار مطلق؛ از نقطه سه‌گانه تا نقطه بحرانی). "
        "Above the critical temperature there is no liquid–vapor saturation boundary "
        "(بالاتر از دمای بحرانی، مرز اشباع مایع و بخار وجود ندارد)."
    )
    with st.expander("Curve Data (داده‌های نمودار)"):
        st.dataframe(
            data.rename(columns={
                "temperature_c": "Temperature (دما) · °C",
                "pressure": f"Saturation Pressure (فشار اشباع) · {unit}",
            }), hide_index=True, width="stretch",
        )
