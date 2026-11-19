> Updated deployment verification: see deployment/TEST_RESULTS.md (2026-11-17). The record below is the prior release history.

# termoyazd verification — 2026-11-12

Actual execution in the Linux authoring environment:

| Check | Result |
|---|---|
| Python `pytest -q` from backend | 52 passed; two dependency deprecation warnings |
| Frontend `npm test -- --reporter=verbose` against running FastAPI | 18 passed, 3 test files; 9.03 seconds |
| TypeScript and Vite production build | Passed; advisory for large lazy Plotly chunk |
| Chromium: Python/WebAssembly worker | All 11 pairs produced real valid states |
| Chromium: T–s, P–v, P–h | All three chart projections rendered |
| Chromium: invalid x=1.2 | Error shown, no successful state |

Browser pair coverage: T_P at T=300 °C, P=500 kPa. The other ten pair tests used a two-phase state generated independently by native Python at P=500 kPa, x=0.35. Fields used the native engine's full-precision properties, not fixed display fixtures. Browser T_P outputs observed: h=3064.5962 kJ/kg, u=2803.2948 kJ/kg, s=7.461448 kJ/(kg·K), v=0.5226028 m³/kg (rounded UI values).

The React test suite additionally uses a superheated seed for inverse pairs, accepts an explicit ambiguity response where appropriate, verifies returned residuals and four outputs, and checks stale-result clearing and invalid quality. The scientific API is real. Only Plotly rendering is stubbed in jsdom; real chart rendering is checked separately in Chromium. Node fetch cannot consume jsdom's AbortSignal, so that test transport removes the foreign-realm signal. Actual network cancellation is not covered by those jsdom tests.

A browser-worker concurrency defect was found and fixed: simultaneous startup requests shared Python globals, so health and diagram responses could be confused. Requests now execute sequentially in the worker. The production website runs the identical scientific Python files; local mode retains FastAPI.

Limitations: native macOS Finder launching, Safari/mobile-device execution and actual PNG download were not executed here. No claim of exhaustive numerical coverage, mathematical global uniqueness, or exact agreement with the supplied PDF is made. The 44 reference comparisons exceeding printed rounding remain visible in validation/error_comparison.csv; scientific references have not been altered.
