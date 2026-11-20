# Original scientific validation record — 2026-11-12

This file preserves the original reference-comparison record. For the current complete suite and precise verification limits, see [current evidence](../docs/VALIDATION.md) and [2026-11-20 execution](../docs/TEST_RESULTS.md). Historical environment and browser statements below are not a fresh browser verification claim.

## Results
25 engine tests executed with unittest: 25 passed, 0 failures, 0 errors. They are also pytest-collectable via backend/tests/test_reference_validation.py. This earlier run has since been supplemented by 52 passing pytest cases in the Linux environment (see ../VERIFICATION.md). Runtime: Python 3.14.10, iapws 1.5.5, SciPy 1.18.1, reused from an existing local SteamLab virtual environment.

Covered: every one of the eleven pairs at a representative real IF97 state; inverse residuals; published IF97 region 1/2/5 verification points; invalid quality, pressure, volume and temperature; saturated TP ambiguity; exact critical exclusion; two near-critical states; the two-solution cold-water density anomaly; and generation/caching of 161 saturation samples. This does not prove all possible roots are enumerated globally.

## PDF evidence and comparison
The provided PDF was found locally and rendered. Headings read F.1 and F.2, not E.1 and E.2. Page references below are PDF page indices (1-based), not inferred printed book page numbers. F.1 page 2: saturated endpoints at 100, 150 and 200 °C; mixtures x=.25/.5/.75 derived from the transcribed 100 °C endpoints. F.2 page 4: four superheated states at P=100–300 kPa and T=150–250 °C. Total: 10 directly transcribed states plus 3 derived mixtures, 52 property comparisons.

The PDF page 1 legend states specific volume in cm³/g. Conversion to m³/kg multiplies by 0.001. Raw printed values, canonical values, table/page/input provenance and half-last-digit rounding increments are retained in reference_points.json. Source SHA-256 is recorded. The source PDF is included unchanged in the personal archive; the GitHub tree retains its hash and transcribed references. No reference values were adjusted to match the calculation; an initial reading of the 150 °C vapor volume/entropy was corrected by enlarging that exact row, as recorded in the dataset.

8 of 52 comparisons are within the source's printed rounding half-step; 44 exceed it. Exceeding the rounding interval is flagged for investigation, not silently treated as numerical success. The original source's equation formulation, edition and rounding method are not established, so differences cannot be definitively attributed to reference-formulation changes. Maximum observed relative errors:

| Property | Maximum absolute error | Maximum relative error (%) |
|---|---:|---:|
| h | 1.16156401 | 0.041619693 |
| u | 1.07259992 | 0.0413620207 |
| s | 0.00249677203 | 0.0388433373 |
| v | 0.00113939891 | 0.0681051348 |

The CSV contains signed, absolute and relative errors for every comparison, including each source-page reference. Rounding classification concerns output rounding only; input and source formulation uncertainty remain separate. Round-trip tests using IF97-generated inputs measure internal numerical consistency, not agreement with independent tables.

## Defect discovered and fixed
At inverse pressure-search endpoints, exp(log(Pmin)) fell infinitesimally below Pmin and exp(log(100)) could exceed 100 MPa. The IF97 library rejected those out-of-domain evaluations, causing T_s, T_u, T_h and T_v to return search_incomplete. Pressure reconstruction is now clipped to the exact documented search interval. Before correction those four representative inverse cases failed; after correction all eleven representative pair tests passed. This is a floating-point implementation defect, distinct from table/reference discrepancies.

## Remaining limitations
FastAPI/pytest, React live integration tests, production build and Chromium interaction have now been executed; see ../VERIFICATION.md. Inverse global uniqueness is not mathematically certified. The source formulation remains unidentified and 44 table/property discrepancies exceed printed rounding; no exact-agreement claim is made. Coverage is representative, not exhaustive. Previous reports that no scientific calculations could run are superseded by this report; they accurately describe earlier attempts.

## Reproduce
From the project root with iapws and SciPy installed: `python3 validation/run_validation.py`. This executes the scientific checks and regenerates results.json, error_comparison.csv. With pytest installed, run `python3 -m pytest backend/tests/test_reference_validation.py` to collect the same scientific checks. Full API tests still need all requirements-dev dependencies.
