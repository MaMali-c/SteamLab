# Executed verification — 2026-11-20

This record describes actual local execution on macOS arm64 using Python 3.14.10, iapws 1.5.5, SciPy 1.18.1 and Node 22.14.0. Commands were executed from the current termoyazd source. Scientific engine source was not changed by the documentation update.

| Check | Actual outcome |
|---|---|
| `python -m pytest -q` in backend | **65 passed**, one dependency deprecation warning |
| Full `npm --prefix frontend test` with a real production-configured API | **22 passed**, five test files |
| `production_smoke.py` against localhost:18743 | **22 HTTP checks passed** |
| `validation/run_validation.py` | **25 scientific checks passed**; 13 reference states, 52 property comparisons |
| `npm run build` | **Passed**, including TypeScript, Vite, runtime preparation and site packaging |
| `verify-browser-engine.mjs` | **All 11 pairs passed** in real WebAssembly/Python; 161 saturation points and invalid quality checked |
| `verify-static-output.py` | **11 built assets downloaded** over local HTTP; Wasm signature and MIME checked |
| Real FastAPI TestClient example | HTTP 200, full response saved in `examples/T_P.response.json` |

The 25 reference-engine tests are also collected by the backend suite. These counts overlap and must not be summed as unique scientific coverage. All eleven pair selections are covered by the React/API integration scenarios, including the combined quality case.

An initial `test:unit` run returned 8 passing and 1 failing check because its real saturation-data request used an unrelated service at port 8000. No scientific code or test assertions were weakened. A dedicated production-configured termoyazd API was started at 18743; the complete frontend suite then passed. Development documentation now explicitly states that even the plotting check inside the script named `test:unit` requires a real API.

Known non-fatal warnings: a Starlette/httpx deprecation warning from dependencies, and the sizeable lazy Plotly chunk warning during Vite build. Neither was hidden or treated as a failed scientific calculation.

Reference-table agreement remains **8/52 within printed output rounding, 44/52 outside**. Passing execution checks does not resolve these source/model differences.

Not freshly verified here: interactive rendering on physical desktop/mobile browsers, actual browser PNG save dialog/download, a Docker image build, public HTTPS hosting/DNS and industrial/experimental accuracy. Node/Pyodide checks execute the real browser-target numerical runtime but do not exercise browser graphics. CI status for newer commits is available in GitHub Actions; the earlier successful source baseline is run 44477559246.
