# Verification and reference comparison

## Distinguish the evidence

| Evidence | What it can establish | What it cannot establish |
|---|---|---|
| Published IF97 verification points | Agreement with selected formulation checkpoints | Exhaustive region coverage |
| Native/inverse round trips and residuals | Numerical internal consistency | Independent physical validation |
| Supplied steam-table comparison | Observed agreement/disagreement with transcribed values | Source formulation identity when unspecified |
| API/UI tests | Behavior for covered requests and state transitions | Manual visual quality on every browser |
| Node Pyodide execution | Real shared Python engine works in WebAssembly for tested cases | Safari/mobile rendering or image-download behavior |
| Production build | TypeScript and asset packaging succeed | Actual cloud hosting/DNS availability |

## PDF provenance

The supplied `SteamTableSI.pdf` was inspected during the original validation. Actual headings were **F.1** (saturated steam) and **F.2** (superheated steam), rather than E.1/E.2 from the requested label. Dataset pages refer to one-based PDF pages, not guessed printed textbook pagination.

[`reference_points.json`](../validation/reference_points.json) records the source hash, raw printed data, engineering-unit conversions, table/page, original inputs, rounding increments and transcription notes. The PDF is not redistributed in this public source tree. Reproducing the calculations needs the dataset; independently rechecking transcription needs the same PDF. If it is unavailable, ask its owner for the file rather than claim a new inspection.

- F.1, PDF page 2: saturated liquid/vapor at 100, 150 and 200 °C.
- Three 100 °C mixtures at qualities 0.25, 0.5 and 0.75 are **derived from endpoints**, not independently printed measurements.
- F.2, PDF page 4: four superheated points over 100–300 kPa and 150–250 °C.
- Total: 10 directly transcribed states + 3 derived states; four compared properties each = 52 comparisons.
- Printed specific-volume unit cm³/g is converted by multiplying by 0.001 to obtain m³/kg.

## Actual comparison result

**8 of 52** property comparisons lie within the output's half-last-digit printed rounding interval. **44 of 52** exceed it and remain flagged. All 52 values are retained unchanged in [`error_comparison.csv`](../validation/error_comparison.csv).

| Property | Maximum absolute error, canonical units | Maximum relative error (%) |
|---|---:|---:|
| h | 1.16156401 | 0.041619693 |
| u | 1.07259992 | 0.0413620207 |
| s | 0.00249677203 | 0.0388433373 |
| v | 0.00113939891 | 0.0681051348 |

Signed error is calculated minus reference; absolute error is its magnitude; relative error percent is `100 * abs(error) / abs(reference)`. The source's formulation, edition and rounding method are not established. Therefore, differences beyond printed rounding are unresolved source/model differences, not automatically solver bugs and not automatically explained by rounding. Input rounding is separate from output rounding. Passing broad scientific sanity tests must not relabel these 44 comparisons as exact agreement.

## Automated checks

The existing verification baseline contains 65 backend tests, 22 frontend checks and 22 production HTTP smoke checks. The real browser-Python script exercises all 11 pairs, 161 saturation points and invalid quality. Detailed current execution is recorded in [latest local results](TEST_RESULTS.md); cloud run [44477559246](https://github.com/MaMali-c/SteamLab/actions/runs/44477559246) is an immutable earlier successful baseline.

Coverage includes saturation endpoints/mixtures, superheated conditions, official IF97 region 1/2/5 points, inverse residuals, finite/range/quality rejection, saturation ambiguity, cold-water multiple-root behavior, exact-critical rejection, near-critical finite outputs, units, request guards, host/CORS policies and stale-result/error UI behavior. These are representative tests, not an exhaustive state-space proof.

## Defect found during original validation

The inverse pressure path reconstructed a search endpoint using `exp(log(P))`, yielding a value infinitesimally outside the permitted interval. The IF97 library correctly rejected it; four fixed-temperature inverse modes then reported incomplete searches. Clipping the reconstruction to its exact interval fixed that implementation defect. Reference table values were not changed to make a test pass.

## Reproduce

From `SteamLab/termoyazd`, with the documented dependencies installed:

```bash
(cd backend && python -m pytest -q)
python validation/run_validation.py
node scripts/verify-browser-engine.mjs
```

The validation script regenerates `validation/results.json` and `validation/error_comparison.csv`. It also executes its 25 scientific unittest cases; these are collected by pytest as well, so do not add overlapping counts as independent coverage.

Remaining: identify the table's primary formulation/edition; expand independent reference coverage (particularly dense/supercritical regions); strengthen global inverse completeness methods; perform fresh desktop/mobile browser and export-download checks; test an actual deployed HTTPS origin. No industrial certification or experimental plant validation is claimed.
