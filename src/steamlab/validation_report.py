"""Reproducible independent checkpoints and a separate PDF comparison report."""

import json
import math
from pathlib import Path

from .core.engine import saturation_temperature, solve_pt, solve_tx
from .tables.comparison import PROPERTIES
from .tables.repository import load_rows


def official_report(path: Path) -> list[dict]:
    checks = json.loads(path.read_text(encoding="utf-8"))
    records = []
    for case in checks["states"]:
        state = solve_pt(case["T"], case["P"])
        for prop in PROPERTIES:
            actual, expected = getattr(state, prop), case[prop]
            records.append(
                {
                    "case": case["id"],
                    "table": case["table"],
                    "property": prop,
                    "expected": expected,
                    "actual": actual,
                    "absolute_difference": abs(actual - expected),
                    "rtol": case["rtol"],
                    "passed": math.isclose(actual, expected, rel_tol=case["rtol"], abs_tol=1e-10)
                    and state.region == case["region"],
                }
            )
    for case in checks["saturation_temperatures"]:
        actual = saturation_temperature(case["P"])
        records.append(
            {
                "case": f"R4_P{case['P']}",
                "table": 36,
                "property": "T",
                "expected": case["T"],
                "actual": actual,
                "absolute_difference": abs(actual - case["T"]),
                "rtol": 1e-8,
                "passed": math.isclose(actual, case["T"], rel_tol=1e-8),
            }
        )
    return records


def pdf_report(path: Path) -> list[dict]:
    records = []
    for row in load_rows(path):
        if row.quality is None:
            state = solve_pt(row.temperature_c + 273.15, row.pressure_kpa / 1000)
        else:
            # Compare saturated endpoints at the same T, never feed rounded PDF P,T together.
            state = solve_tx(row.temperature_c + 273.15, row.quality)
        for prop in PROPERTIES:
            reference, actual = row.properties[prop], getattr(state, prop)
            records.append(
                {
                    "row_id": row.row_id,
                    "page": row.page,
                    "property": prop,
                    "pdf": reference,
                    "if97": actual,
                    "absolute_difference": abs(actual - reference),
                    "relative_percent": 100 * abs(actual - reference) / abs(reference)
                    if abs(reference) > 1e-12
                    else None,
                }
            )
    return records
