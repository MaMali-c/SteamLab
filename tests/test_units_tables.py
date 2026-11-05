import hashlib
import json
from pathlib import Path

import pytest

from steamlab.core.engine import solve_pt, solve_px, solve_tx
from steamlab.core.errors import InputError
from steamlab.core.units import pressure_to_mpa, temperature_to_k, volume_to_m3kg
from steamlab.tables.comparison import (
    TableEstimate,
    TableUnavailable,
    differences,
    estimate_for_state,
)
from steamlab.tables.interpolation import linear_step
from steamlab.tables.repository import load_rows


@pytest.mark.parametrize(
    "value,unit,expected",
    [(500, "kPa", 0.5), (5, "bar", 0.5), (0.5, "MPa", 0.5), (500000, "Pa", 0.5)],
)
def test_pressure_unit_equivalence(value, unit, expected):
    assert pressure_to_mpa(value, unit) == pytest.approx(expected)


def test_temperature_and_original_pdf_volume_units():
    assert temperature_to_k(100, "°C") == pytest.approx(373.15)
    assert temperature_to_k(373.15, "K") == pytest.approx(373.15)
    assert volume_to_m3kg(1.002, "cm³/g") == pytest.approx(0.001002)
    assert volume_to_m3kg(522.58, "cm³/g") == pytest.approx(0.52258)


@pytest.mark.parametrize(
    "function,args",
    [(temperature_to_k, (10, "F")), (pressure_to_mpa, (1, "psi")), (volume_to_m3kg, (1, "L"))],
)
def test_unknown_units_rejected(function, args):
    with pytest.raises(InputError):
        function(*args)


def test_exact_pdf_node_and_source_page(rows):
    est = estimate_for_state(solve_pt(573.15, 0.5), rows)
    assert est.source_rows[0].page == 6
    assert est.properties["v"] == pytest.approx(0.52258)
    assert est.properties["h"] == 3064.8
    assert not est.steps


def test_temperature_interpolation_shows_source_and_weights(rows):
    est = estimate_for_state(solve_pt(563.15, 0.5), rows)
    assert len(est.source_rows) == 2
    assert est.properties["h"] == pytest.approx((3023.4 + 3064.8) / 2)
    assert all(step.weight == pytest.approx(0.5) for step in est.steps)


def test_pressure_interpolation_at_constant_temperature(rows):
    est = estimate_for_state(solve_pt(623.15, 0.625), rows)
    assert est.properties["h"] == pytest.approx((3168.1 + 3163.4) / 2)
    assert all(step.coordinate == "pressure_kpa" for step in est.steps)


def test_mixture_interpolates_endpoints_before_mixing(rows):
    est = estimate_for_state(solve_tx(295.65, 0.4), rows)
    hf = (83.90 + 104.8) / 2
    hg = (2537.4 + 2546.7) / 2
    assert est.properties["h"] == pytest.approx(hf + 0.4 * (hg - hf))
    assert len(est.source_rows) == 4
    assert len(est.steps) == 12


def test_pressure_quality_uses_pressure_coordinate(rows):
    est = estimate_for_state(solve_px(0.002337, 0.5), rows)
    assert len(est.source_rows) == 2
    assert est.properties["h"] == pytest.approx((83.90 + 2537.4) / 2)


@pytest.mark.parametrize("t,p", [(323.15, 0.5), (573.15, 0.6), (673.15, 0.5), (650, 25)])
def test_no_wrong_phase_or_two_dimensional_extrapolation(rows, t, p):
    with pytest.raises(TableUnavailable):
        estimate_for_state(solve_pt(t, p), rows)


@pytest.mark.parametrize(
    "z,z1,z2", [(-1, 0, 1), (2, 0, 1), (0.5, 1, 0), (0, 0, 0), (float("nan"), 0, 1)]
)
def test_linear_interpolation_rejects_invalid_bounds(z, z1, z2):
    with pytest.raises(InputError):
        linear_step("h", "temperature_c", z, z1, z2, 1, 2)


def test_relative_difference_near_zero_is_not_infinite():
    state = solve_tx(293.15, 0)
    est = TableEstimate({"v": 0.0, "u": 1e-14, "h": 100, "s": 1}, (), (), "test")
    result = differences(state, est)
    assert result[0]["relative_percent"] is None
    assert result[1]["relative_percent"] is None
    assert result[2]["absolute"] == pytest.approx(abs(state.h - 100))


def test_unreviewed_rows_never_enter_computation(tmp_path):
    source = Path(__file__).resolve().parents[1] / "data/verified/steam_table_sample.csv"
    target = tmp_path / "unchecked.csv"
    target.write_text(source.read_text().replace("visually_checked", "unreviewed"))
    assert load_rows(target) == ()


def test_duplicate_source_rows_rejected(tmp_path):
    source = Path(__file__).resolve().parents[1] / "data/verified/steam_table_sample.csv"
    content = source.read_text()
    target = tmp_path / "duplicate.csv"
    target.write_text(content + content.splitlines()[1] + "\n")
    with pytest.raises(InputError):
        load_rows(target)


def test_original_pdf_hash_when_present():
    root = Path(__file__).resolve().parents[1]
    path = root / "data/reference/SteamTableSI.pdf"
    if not path.exists():
        pytest.skip("User-supplied PDF is optional and excluded from Git.")
    meta = json.loads((root / "data/verified/provenance.json").read_text())
    assert hashlib.sha256(path.read_bytes()).hexdigest() == meta["sha256"]
