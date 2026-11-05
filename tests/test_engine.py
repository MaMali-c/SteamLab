import json
from pathlib import Path

import pytest

from steamlab.core.engine import (
    saturation_pressure,
    saturation_temperature,
    solve_pt,
    solve_px,
    solve_tx,
)
from steamlab.core.errors import InputError, SaturationAmbiguity
from steamlab.core.validation import P_MIN_MPA, P_TRIPLE_MPA

DATA = json.loads(
    (Path(__file__).resolve().parents[1] / "data/verified/official_checks.json").read_text()
)


@pytest.mark.parametrize("case", DATA["states"], ids=lambda c: c["id"])
def test_published_if97_state(case):
    state = solve_pt(case["T"], case["P"])
    assert state.region == case["region"]
    assert state.quality is None
    for prop in ("v", "u", "h", "s"):
        assert getattr(state, prop) == pytest.approx(case[prop], rel=case["rtol"], abs=1e-10)


@pytest.mark.parametrize("case", DATA["saturation_temperatures"])
def test_published_saturation_temperature(case):
    assert saturation_temperature(case["P"]) == pytest.approx(case["T"], rel=1e-8)


@pytest.mark.parametrize("p", [0.1, 1, 20])
@pytest.mark.parametrize("x", [0.0, 0.25, 0.5, 1.0])
def test_saturated_mass_mixture_and_energy_identity(p, x):
    state, liquid, vapor = solve_px(p, x), solve_px(p, 0), solve_px(p, 1)
    assert state.quality == x
    for prop in ("v", "u", "h", "s"):
        expected = getattr(liquid, prop) + x * (getattr(vapor, prop) - getattr(liquid, prop))
        assert getattr(state, prop) == pytest.approx(expected, rel=2e-5, abs=1e-8)
    assert state.h == pytest.approx(state.u + state.pressure_mpa * 1000 * state.v, abs=1e-6)
    assert state.density == 1 / state.v


@pytest.mark.parametrize(
    "x,phase", [(0, "saturated_liquid"), (0.5, "two_phase"), (1, "saturated_vapor")]
)
def test_saturation_endpoint_labels_and_two_phase_region(x, phase):
    state = solve_tx(373.15, x)
    assert state.phase == phase
    if 0 < x < 1:
        assert state.region == 4


@pytest.mark.parametrize(
    "temperature,pressure,phase",
    [
        (323.15, 0.5, "compressed_liquid"),
        (573.15, 0.5, "superheated_vapor"),
        (650, 25, "supercritical"),
        (700, 1, "gas"),
        (640, 21, "compressed_liquid"),
        (640, 20, "superheated_vapor"),
        (647.096, 22.064, "critical"),
    ],
)
def test_physical_phase_not_equal_to_equation_region(temperature, pressure, phase):
    state = solve_pt(temperature, pressure)
    assert state.phase == phase
    assert state.quality is None


@pytest.mark.parametrize("offset", [0, 0.005, -0.005])
def test_near_saturation_never_assumes_quality(offset):
    tsat = saturation_temperature(0.5)
    with pytest.raises(SaturationAmbiguity):
        solve_pt(tsat + offset, 0.5)


@pytest.mark.parametrize(
    "offset,phase", [(-0.02, "compressed_liquid"), (0.02, "superheated_vapor")]
)
def test_outside_ambiguity_band(offset, phase):
    assert solve_pt(saturation_temperature(0.5) + offset, 0.5).phase == phase


@pytest.mark.parametrize(
    "t,p",
    [
        (273.15, 1),
        (2273.16, 1),
        (300, 0),
        (300, -1),
        (300, 101),
        (1500, 50.01),
        (300, P_MIN_MPA / 2),
        (float("nan"), 1),
        (300, float("inf")),
        (None, 1),
        (True, 1),
    ],
)
def test_invalid_pt_is_rejected(t, p):
    with pytest.raises(InputError):
        solve_pt(t, p)


@pytest.mark.parametrize("x", [None, -0.001, 1.001, float("nan"), float("inf"), True])
def test_quality_is_required_and_bounded(x):
    with pytest.raises(InputError):
        solve_px(0.5, x)


@pytest.mark.parametrize("t,p", [(273.16, 100), (1073.15, 100), (2273.15, 50), (300, P_MIN_MPA)])
def test_supported_domain_edges(t, p):
    assert solve_pt(t, p).v > 0


@pytest.mark.parametrize("t", [647.09, 647.096, 648])
def test_quality_critical_guard(t):
    with pytest.raises(InputError):
        solve_tx(t, 0.5)


def test_quality_above_critical_pressure_rejected():
    with pytest.raises(InputError):
        solve_px(25, 0.5)


def test_triple_point_and_inverse_saturation():
    assert solve_px(P_TRIPLE_MPA, 0).temperature_k == pytest.approx(273.16)
    for t in [293.15, 373.15, 623.15, 638.15]:
        assert saturation_temperature(saturation_pressure(t)) == pytest.approx(t, abs=1e-7)


def test_sample_image_is_replaced_by_actual_computation():
    state = solve_pt(573.15, 0.5)
    assert state.h == pytest.approx(3064.5962196, abs=1e-6)
    assert state.v == pytest.approx(0.52260276755, abs=1e-10)
