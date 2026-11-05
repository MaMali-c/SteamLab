# Technical Design (طراحی فنی)

## Model and assumptions (مدل و فرضیات)

SteamLab calculates equilibrium fluid properties of pure ordinary water using the
industrial IAPWS-IF97 formulation through `iapws==1.5.5`. It does not fit an equation
to the supplied PDF, approximate all vapor as ideal gas, or use ML predictions.
The reference formulation partitions its domain into regions: Gibbs equations
for regions 1, 2 and 5; a Helmholtz equation for region 3; a saturation relation for region 4.

All main outputs are mass-specific. Backend units are K, MPa, m³/kg, kJ/kg and
kJ/(kg·K). Native Python floats are used without intermediate rounding. Display
precision does not imply the same physical accuracy in all regions.

Reference: International Association for the Properties of Water and Steam,
[R7-97(2012), Revised Release on IF97](https://iapws.org/technical-guidance/release/IF97-Rev).
Implementation documentation: [iapws97](https://iapws.readthedocs.io/en/stable/iapws.iapws97.html).

## Scientific identities (روابط علمی)

```text
T_K = T_C + 273.15
P_MPa = P_kPa / 1000 = P_bar / 10
v_m3kg = 0.001 × v_cm3g
rho = 1 / v
h_kJkg = u_kJkg + 1000 × P_MPa × v_m3kg
```

The engine checks the energy identity with an absolute tolerance of `1e-5 kJ/kg`.
This is a consistency check, not independent physical validation.

For saturated equilibrium below the critical point:

```text
x = m_vapor / (m_liquid + m_vapor)
y = y_f + x × (y_g - y_f), y in {v, u, h, s}
```

Quality is a **mass fraction**. It is not a volume fraction. Density must be derived
from mixed specific volume; it is not linearly averaged. Mixture cp is omitted
because a naive endpoint interpolation is not the required two-phase derivative.

## State identification (تشخیص حالت)

The equation region and physical phase are returned separately. Region 3 can
represent liquid-like, vapor-like or supercritical states. No rule equates
region 3 with one physical phase.

For subcritical temperatures, compare pressure with the saturation pressure.
For `T >= Tc`, use the gas/supercritical distinction with critical pressure.
The exact critical point (`Tc=647.096 K`, `Pc=22.064 MPa`) is treated separately.

`iapws` may assign x=0 or x=1 to single-phase states as an internal label. SteamLab
does not expose those values as physical quality. TP quality is always `None`.
For explicitly specified saturated endpoints, x is valid, while the equation
region can be 1, 2 or 3 rather than 4. Interior mixtures use region 4.

## Saturation ambiguity (ابهام اشباع)

At a subcritical saturation pressure, TP input within `0.01 K` of `Tsat(P)` is
rejected with a specific information request. This is a deliberately conservative
UI ambiguity band, not the IF97 equation accuracy or a physical two-phase thickness.
Even if the supplied pair is slightly off the curve, SteamLab does not silently
snap it onto saturation or choose an endpoint. The user must explicitly select
PX/TX or provide a more clearly single-phase pair.

The quality field starts empty. Invalid and missing quality never becomes 0, 0.5 or 1.
An example button explicitly loads its stated example quality.

The boundary equations `_PSat_T` and `_TSat_P` (IF97 Eqs. 30 and 31) are isolated
inside the adapter. They are documented underscore APIs of the pinned dependency.
Using the endpoint region-3 EOS to infer a boundary pressure introduces small
iteration residuals; boundary decisions instead use the actual region-4 equations.
Inverse-boundary tests cover high-pressure saturation as well as low-pressure states.

## Domain and numerical guards (دامنه و کنترل عددی)

| Condition | Policy |
|---|---|
| T below 273.16 K | Reject; ice stability not modeled |
| T up to 1073.15 K | P at most 100 MPa |
| T above 1073.15 K and up to 2273.15 K | P at most 50 MPa |
| P below 0.000611212677444 MPa | Reject; pinned TP solver lower bound |
| Saturation input P | At least triple-point pressure; no greater than critical pressure |
| Quality input T | At least 273.16 K; no greater than Tc−0.01 K |
| NaN, infinity, booleans, missing inputs | Reject with a bilingual error |
| Backend non-convergence/nonfinite output | Show calculation error; clear old result |

The 0.01 K critical-quality guard is a conservative **software** restriction because
endpoints coalesce; it is not the standard's critical boundary. Single-phase TP
calculation near criticality remains available with a precision warning. Numerical
failure is surfaced instead of substituting an approximate state. Tiny differences
between requested and returned P/T can arise from the backend's region-3 solver.

No general ice, saline-water, dissociation or metastable-state selection is provided.
Passing reference points is not certification for plant control or every state in the continuum.

## Data and interpolation (داده و درون‌یابی)

The CSV stores PDF volume in cm³/g and converts only on access. Original numbers
are retained even if IF97 produces different values. The PDF's historical equation
and bibliographic origin have not been established.

For `z1 <= z <= z2`:

```text
w = (z - z1) / (z2 - z1)
y = y1 + w × (y2 - y1)
```

Every interpolation returns an audit record containing z, both source coordinates,
both property values, weight and result. Bounds must increase and all values must
be finite. Exact source nodes bypass interpolation. There is no extrapolation.

Superheated comparison first tries fixed-pressure temperature interpolation;
otherwise it tries fixed-temperature pressure interpolation. It does not perform
bilinear interpolation or move to a nearby pressure. Only checked superheated rows
are used; compressed liquid, critical and supercritical PDF comparison are unavailable.

Saturated comparison uses T for TX and P for PX, independently interpolates the
checked f/g endpoints, then applies the mass mixture. The other saturation coordinate
is not assumed identical in the historical PDF and modern IF97. Across the limited
table intervals, linear interpolation remains a teaching approximation with unknown
truncation error; the displayed difference is not an interpolation uncertainty estimate.

```text
absolute_difference = abs(if97 - table)
relative_difference_percent = 100 × absolute_difference / abs(table)
```

When `abs(table) <= 1e-12` in its documented engineering unit, relative difference
is undefined and omitted. No universal PDF pass/fail percentage is asserted.

## Software architecture (معماری نرم‌افزار)

`ui` depends on `core` and `tables`. `tables` consumes immutable `State` objects;
it never alters the engine result. `core` does not import the UI or load a PDF.
`validation_report` compares fixed external references with the public engine API.

`State` records units in its field contract. `SteamLabError` carries English and
Persian messages. `SaturationAmbiguity` is distinct from a calculation failure.
`TableUnavailable` is a comparison-coverage issue, not an invalid physical state.

UI session state stores the last successful state and an explicit stale flag.
Input callbacks invalidate its freshness. A failed calculation clears it. Unit
callbacks preserve the physical value. State cards, comparison and validation
messages derive from these states; no screenshot numbers are hardcoded into cards.

## Extensions (توسعه آینده)

Add PH/PS methods to the adapter with the same State contract, add dedicated tests,
then expose the inputs in UI. Plotly diagrams should sample the real saturation
curve and plot actual computed states; region boundaries must not be decorative.
Equipment and cycle calculations should form a separate module consuming State
objects and documenting steady-state, heat-loss and efficiency assumptions.
