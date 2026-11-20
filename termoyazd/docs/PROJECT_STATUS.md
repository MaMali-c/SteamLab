# Implemented scope and remaining work

| Capability | Status | Qualification |
|---|---|---|
| Eleven required input pairs | Implemented/tested on representative states | Physically invalid or ambiguous requests can be rejected |
| Real IF97 states | Implemented | Pure water/steam only |
| Numerical inverse residuals | Implemented | Global uniqueness is not mathematically certified |
| Unit selectors and normalization | Implemented/tested | Pressure is absolute |
| Dark responsive bilingual UI | Implemented | Fresh manual device review remains desirable |
| API integration and stale-result handling | Automated tests | Real API used by integration suite |
| Saturation plots and state marker rule | Implemented/tested | Final critical segment deliberately omitted |
| Plotly PNG export control | Implemented | Current physical browser download not freshly verified |
| Browser Python engine | Actual Node/Pyodide execution tested | Browser/device performance varies |
| Copy JSON and reset | Implemented | No retained history |
| macOS launcher | Implemented/tested components | Local developer dependencies required |
| Production configs | Prepared | No live website asserted |
| Source-table reference data | Recorded | 44/52 discrepancies exceed printed rounding |
| Excel import/export | Not implemented | Future work |
| Batch calculations | Not implemented | API accepts one state per request |
| PDF report / accounts / database | Not implemented | Future work |
| Industrial/experimental certification | Not established | Academic verification scope |

## Prioritized continuation

1. Identify the reference table formulation/edition and add independent dense-fluid reference points.
2. Improve interval completeness and uniqueness reasoning for inverse calculations.
3. Complete real desktop/mobile browser, image export and deployed-origin checks.
4. If requested, add bounded batch processing and explicit spreadsheet schemas with per-row errors.
5. Add reports/history only with clear persistence and unit contracts.

Do not change reference numbers or suppress scientific warnings to make outputs appear more complete.
