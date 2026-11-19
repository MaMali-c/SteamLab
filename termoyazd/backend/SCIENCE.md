# termoyazd scientific engine — implementation awaiting numerical validation

The primary engine is iapws 1.5.5 / IAPWS-IF97. No ideal-gas replacement is used. SteamTableSI is a validation reference only; its scanned numerical rows have not been verified in this environment.

## API
POST /api/calculate accepts {"input_pair":"T_P","values":{"T":300,"P":1000}}.
Exactly T_P, T_x, P_x, T_s, T_u, T_h, T_v, P_s, P_u, P_h, P_v are accepted. T is °C, P kPa, h/u kJ/kg, s kJ/(kg·K), v m³/kg, x mass fraction. Internal library units are kelvin and MPa.

The response includes normalized_inputs, calculated_properties, full_state, region, phase, quality, saturation, solver_method, convergence, scientific_warnings. Quality pairs mathematically leave five properties unknown among T/P/h/u/s/v: h/u/s/v occupy the four calculated-property slots, and the dependent saturation coordinate appears in full_state and saturation. Saturation information describes the boundary at the state temperature or pressure; it does not imply the state itself is saturated.

## Algorithms and limits
Native TP, Tx, Px, Ph and Ps calls are used where supported. Inverses additionally search forward IF97 states to identify other candidate solutions. Two-phase values use the mass-weighted saturated liquid/vapor balance, followed by library reconstruction. Single-phase search intervals split at saturation and IF97 boundaries. Pressure searches use logarithmic pressure; temperature searches use kelvin. The search scans 257 samples per interval, refines sign changes with scipy.optimize.brentq and stationary points with minimize_scalar. Identified extrema are checked for tangent and nearby paired roots. Candidates are deduplicated and every candidate must reproduce the original two inputs.

IMPORTANT: finite scanning plus stationary-point refinement does not prove global root completeness. Narrow extrema and near-critical states may escape detection. Inverse responses explicitly set uniqueness_certified=false and include a warning. This is an implementation candidate, not a certified complete scientific engine. Broader numerical validation and stronger monotonic branch isolation remain required before declaring the milestone complete. Multiple detected states produce ambiguous_state with candidate states; failed evaluations produce search_incomplete, never a selected best-effort state.

Bounds: 273.15–1073.15 K up to 100 MPa; 1073.15–2273.15 K up to 50 MPa; minimum pressure 0.000611212677444 MPa. Quality requires T<Tc or P<Pc. Exact critical states are excluded. No metastable extension is deliberately invoked. Saturated TP is rejected without another independent property. Quality is null for single-phase states.

Residual tolerance = absolute + 2e-7 * |input|, in public units. Absolute tolerances: T 2e-6, P 2e-5, h/u 2e-5, s 2e-8, v 2e-10, x 2e-8. Brent xtol=1e-11 in the search coordinate, rtol=1e-12, maxiter=150. Extrema xatol=1e-11, maxiter=150. Candidate merging uses temperature difference <1e-5 K, pressure difference <1e-7 MPa and volume residual tolerance; very close roots require further conditioning analysis.

## Validation status
On 2026-11-12 the Linux execution environment ran all 52 pytest scientific/API tests successfully and all 18 frontend live integration/unit tests successfully. All eleven pairs also produced real calculated states in Chromium through the Pyodide worker. See ../VERIFICATION.md and ../validation/REPORT.md. Coverage remains representative; inverse global uniqueness is not certified.

## Automated acceptance command
Run `bash verify-engine.command` from the project root on a Mac with network access. It creates .venv, installs requirements, runs all scientific/API tests, and only after a successful test suite executes a real in-process API example at 300 °C and 1000 kPa. It records .runtime/engine-verification.json, .runtime/engine-verification.log, and a JUnit report. A failed installation/test aborts later stages and is recorded as failed, never passed. Passing this suite does not establish mathematically complete root enumeration or PDF validation.
