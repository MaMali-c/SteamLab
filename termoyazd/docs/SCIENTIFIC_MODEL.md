# Scientific model and numerical contract

## Fluid and primary formulation

The fluid is pure ordinary water/steam. The primary library is `iapws==1.5.5`, using `IAPWS97`. No ideal-gas fallback is substituted when a calculation fails. IF97 region number is a model-region identifier, not an interchangeable synonym for phase.

Primary references: [IAPWS Industrial Formulation 1997, revised release](https://www.iapws.org/relguide/IF97-Rev.html) and [iapws IAPWS97 documentation](https://iapws.readthedocs.io/en/latest/iapws.iapws97.html). The supplied steam tables are comparison evidence rather than the computational equation of state.

## Units and identities

| Property | API unit | Library conversion |
|---|---|---|
| T | °C | T[K] = T[°C] + 273.15 |
| P | kPa, absolute | P[MPa] = P[kPa] / 1000 |
| h, u | kJ/kg | unchanged |
| s | kJ/(kg·K) | unchanged |
| v | m³/kg | unchanged |
| x | mass fraction | unchanged |

The identity `h = u + P v` is consistent numerically in these public units because kPa·m³/kg = kJ/kg. Pressure selectors do not accept gauge pressure: convert it to absolute pressure before use. Quality is a mass fraction, not void/volume fraction.

## Pair strategies

| API pair | Primary calculation strategy |
|---|---|
| T_P | Native IF97 T/P, with saturation and critical exclusions |
| T_x | Native IF97 saturation T/x |
| P_x | Native IF97 saturation P/x |
| T_s, T_u, T_h, T_v | Mixture candidate where applicable; solve pressure on separated single-phase intervals |
| P_s, P_h | Native backward candidate plus mixture/forward search to detect alternative roots |
| P_u, P_v | Mixture candidate where applicable; solve temperature on separated single-phase intervals |

For an equilibrium saturated mixture, `q = (1-x) q_f + x q_g` for `q ∈ {h,u,s,v}`. The engine solves `x=(q-q_f)/(q_g-q_f)`, checks the saturation/quality domain and reconstructs a library state. This relation is not applied to single-phase or critical states.

## Inverse numerical method

The unknown is temperature in kelvin at fixed pressure, or log-pressure at fixed temperature. Search intervals follow software domain limits and are split at saturation and applicable IF97 region boundaries. Each interval uses 257 samples. Sign-changing brackets use SciPy `brentq`; bounded scalar minimization investigates extrema/tangent or near-zero behavior. Candidate roots are deduplicated, converted to full states and checked against the original input properties.

- Brent: `xtol=1e-11`, `rtol=1e-12`, `maxiter=150` in solver-coordinate units.
- Bounded extremum search: `xatol=1e-11`, `maxiter=150`.
- Reconstructed endpoint pressures are clipped to their exact search bounds to avoid floating-point `exp(log(P))` domain excursions.
- Any unresolved evaluation failure can produce `search_incomplete`, rather than silently skipping a potentially relevant region.
- No accepted candidate gives `no_verified_state`; multiple verified candidates give `ambiguous_state` with candidate information.

**Finite scanning does not prove global root completeness.** Inverse outputs use `uniqueness_certified=false`, even when one verified candidate is found. Their residuals measure local consistency; a small residual cannot prove global uniqueness. A cold-water density-anomaly test explicitly exercises two possible temperatures at fixed P/v.

## Residual acceptance

For each supplied property `k`, the absolute recomputation residual must satisfy:

`abs(recomputed[k] - input[k]) <= ATOL[k] + 2e-7 * abs(input[k])`.

| Property | ATOL, in API units |
|---|---:|
| T | 2e-6 |
| P | 2e-5 |
| h | 2e-5 |
| u | 2e-5 |
| s | 2e-8 |
| v | 2e-10 |
| x | 2e-8 |

Returned convergence diagnostics include the actual residuals and tolerances, evaluation count, accepted-candidate count and uniqueness flag. These numerical tolerances are not a claim of physical-model accuracy or measurement uncertainty.

## Software domain and exclusions

- Temperature: 0–2000 °C; pressure minimum approximately 0.611212677444 kPa.
- Up to 800 °C: maximum pressure 100000 kPa. Above 800 °C: maximum pressure 50000 kPa.
- These are implementation limits, not a claim that every combination is stable or every inverse state is resolvable.
- Saturation quality must lie in `[0,1]` and within the supported subcritical saturation domain. Exact critical quality is excluded.
- Critical constants: 647.096 K and 22.064 MPa. Exact critical T/P is rejected by a dedicated guard; use source guards for their precise local tolerance.
- Saturated T/P within pressure tolerance `1e-8 MPa` is underdetermined without a further independent property, and gives `ambiguous_saturation`.
- The low-temperature software endpoint is 273.15 K; the chart begins at 273.16 K. This endpoint convention is not independent experimental verification of the lowest-temperature strip.
- Ice, saline water, multicomponent fluids, chemical reactions and justified metastable/unstable extensions are outside scope.
- Single-phase `quality` is `null`. Saturation data may describe the boundary associated with an input pressure/temperature; it does not mean that the calculated state is saturated.

## Plotting contract

161 cosine-spaced temperatures cover 273.16 K through `Tc - 0.05 K`. For each temperature, separate saturated liquid and vapor IF97 states supply both branches. Non-finite or unordered values are rejected. The exact apex and final 0.05 K are omitted and labeled unavailable; the application does not invent a closing curve. T–s uses linear axes; P–v uses logarithmic pressure and volume; P–h uses logarithmic pressure. Region annotations are explanatory, not an exhaustive IF97 region map.

A state point requires converged output, one verified candidate and `uniqueness_certified=true`. Consequently, inverse solutions with unproved uniqueness can show property results and warnings but do not receive a misleading unique marker.
