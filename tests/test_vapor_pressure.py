from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from steamlab.plots.vapor_pressure import MAX_C, MIN_C, curve_data


@pytest.mark.parametrize("unit, expected", [("kPa", 100), ("MPa", 0.1), ("bar", 1)])
def test_curve_matches_published_saturation_reference(unit, expected):
    # IAPWS table 36: 0.1 MPa at 372.755919 K (published rounded temperature).
    data = curve_data(372.755919 - 273.15, 200, unit)
    assert data.pressure.iloc[0] == pytest.approx(expected, rel=1e-7)


def test_full_curve_is_positive_monotonic_and_reaches_critical_point():
    data = curve_data(MIN_C, MAX_C, "MPa")
    assert data.pressure.gt(0).all()
    assert data.pressure.diff().dropna().gt(0).all()
    assert data.pressure.iloc[-1] == pytest.approx(22.064, abs=1e-7)
    assert data.temperature_c.iloc[-1] == MAX_C


@pytest.mark.parametrize("bounds", [(100, 100), (200, 100), (0, 200), (1, 374)])
def test_curve_rejects_invalid_ranges(bounds):
    with pytest.raises(ValueError):
        curve_data(*bounds, "kPa")


def test_chart_page_controls_ranges_and_calculator_preservation():
    root = Path(__file__).resolve().parents[1]
    at = AppTest.from_file(str(root / "app.py"), default_timeout=20).run()
    at.number_input(key="temperature").set_value(310).run()
    at.radio(key="page").set_value("vapor_pressure").run()
    assert not at.exception
    assert float(at.metric[0].value) == pytest.approx(101.418, rel=1e-5)
    at.selectbox(key="vapor_unit").set_value("bar").run()
    assert float(at.metric[0].value) == pytest.approx(1.01418, rel=1e-5)
    at.checkbox(key="vapor_log").check().run()
    at.slider(key="vapor_range").set_value((MIN_C, MAX_C)).run()
    at.number_input(key="vapor_temperature").set_value(MAX_C).run()
    assert not at.exception
    assert float(at.metric[0].value) == pytest.approx(220.64, rel=1e-6)
    at.number_input(key="vapor_temperature").set_value(MIN_C).run()
    assert not at.exception
    assert float(at.metric[0].value) == pytest.approx(0.00611657, rel=1e-6)
    at.number_input(key="vapor_temperature").set_value(MAX_C).run()
    at.slider(key="vapor_range").set_value((20.0, 80.0)).run()
    assert not at.exception
    assert at.number_input(key="vapor_temperature").value == 80
    at.radio(key="appearance").set_value("Light (روشن)").run()
    assert not at.exception
    at.slider(key="vapor_range").set_value((50.0, 50.0)).run()
    assert not at.exception
    assert at.info
    at.radio(key="page").set_value("calculator").run()
    assert at.number_input(key="temperature").value == 310
