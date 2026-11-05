from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


def app():
    return AppTest.from_file(str(ROOT / "app.py"), default_timeout=15).run()


def test_empty_then_real_result_and_stale_state():
    at = app()
    assert not at.exception
    assert all(m.value == "—" for m in at.metric)
    at.button(key="calculate").click().run()
    assert not at.exception
    assert at.session_state.result.h == pytest.approx(3064.5962196258724)
    assert at.session_state.result.quality is None
    assert at.dataframe
    at.number_input(key="temperature").set_value(310).run()
    assert at.session_state.stale is True
    assert not at.success
    assert any("Previous result" in w.value for w in at.warning)


def test_invalid_input_removes_old_results():
    at = app()
    at.button(key="calculate").click().run()
    at.number_input(key="pressure").set_value(-5).run()
    at.button(key="calculate").click().run()
    assert not at.exception
    assert at.error
    assert at.session_state.result is None
    assert all(m.value == "—" for m in at.metric)


def test_saturation_asks_for_quality_and_has_no_default():
    at = app()
    at.number_input(key="temperature").set_value(99.6059186113)
    at.number_input(key="pressure").set_value(100).run()
    at.button(key="calculate").click().run()
    assert at.session_state.result is None
    assert "Near saturation" in at.error[0].value
    at.radio(key="mode").set_value("PX").run()
    assert at.number_input(key="quality").value is None
    at.button(key="calculate").click().run()
    assert at.error
    at.number_input(key="quality").set_value(0.5).run()
    at.button(key="calculate").click().run()
    assert not at.exception
    assert at.session_state.result.quality == 0.5


def test_unit_change_preserves_physical_value():
    at = app()
    at.selectbox(key="pressure_unit").set_value("bar").run()
    assert at.number_input(key="pressure").value == pytest.approx(5)
    at.selectbox(key="temp_unit").set_value("K").run()
    assert at.number_input(key="temperature").value == pytest.approx(573.15)
    at.button(key="calculate").click().run()
    assert not at.exception
    assert at.session_state.result.pressure_mpa == pytest.approx(0.5)


def test_reset_restores_empty_state():
    at = app()
    at.button(key="calculate").click().run()
    at.button(key="reset").click().run()
    assert not at.exception
    assert at.session_state.result is None
    assert at.number_input(key="temperature").value == 300


def test_examples_pages_validation_and_theme():
    at = app()
    next(b for b in at.button if "Saturated Mixture" in b.label).click().run()
    at.button(key="calculate").click().run()
    assert not at.exception
    assert at.session_state.result.input_pair == "TX"
    assert at.dataframe
    for page in ["tables", "theory", "validation"]:
        at.radio(key="page").set_value(page).run()
        assert not at.exception
    at.button(key="run_checks").click().run()
    assert not at.exception
    assert all(r["passed"] for r in at.session_state.check_results)
    at.radio(key="appearance").set_value("Light (روشن)").run()
    assert not at.exception


def test_english_labels_have_persian_parentheses():
    at = app()
    for element in [*at.button, *at.number_input, *at.selectbox, *at.radio, *at.metric]:
        label = element.label
        assert "(" in label and ")" in label, label
        assert any("\u0600" <= ch <= "\u06ff" for ch in label), label


def test_navigation_preserves_inputs_and_units():
    at = app()
    at.selectbox(key="temp_unit").set_value("K").run()
    at.selectbox(key="pressure_unit").set_value("bar").run()
    at.radio(key="page").set_value("tables").run()
    at.radio(key="page").set_value("calculator").run()
    assert at.number_input(key="temperature").value == pytest.approx(573.15)
    assert at.number_input(key="pressure").value == pytest.approx(5)
    at.selectbox(key="temp_unit").set_value("°C").run()
    at.button(key="calculate").click().run()
    assert not at.exception
    assert at.session_state.result.h == pytest.approx(3064.5962196258724)
