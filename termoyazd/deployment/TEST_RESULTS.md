# termoyazd production preparation — 2026-11-17

## Actual execution in this task

| Check | Actual result |
|---|---|
| Python scientific/API/production suite | **65 passed**, 1 Starlette/httpx dependency deprecation warning, 17.30 s |
| React/Vitest against a real Uvicorn API in production mode | **22 passed**, 5 files, 5.70 s |
| HTTP smoke checks against that production-mode API | **22 passed**, including all 11 pairs, quality rejection, saturation ambiguity, 161 saturation samples, CORS, size and unsupported batch rejection |
| Self-contained production TypeScript/Vite build | Passed; scientific worker/runtime assets present |
| Remote API production TypeScript/Vite build | Passed; HTTPS API origin compiled; browser worker branch removed; unused Pyodide assets excluded |
| Real Python/IF97 in Pyodide WebAssembly under Node.js | All **11 pairs**, residual checks, 161 saturation samples and invalid quality rejection passed |
| Built static assets downloaded over local HTTP | **11 downloads passed**; WebAssembly MIME and magic bytes verified |
| Python 3.14 Linux x86-64 production dependency resolution | All 17 pinned runtime distributions resolved as wheels in pip dry-run; this is not a container run |
| Core scientific source SHA-256 comparison | engine.py, thermo.py, plotting.py unchanged from the supplied project |
| Credential-pattern scan | No private key or known GitHub/live-key token patterns found in scanned source/configuration files; not an exhaustive secret audit |
| Configuration syntax | Python, JSON and startup-shell checks passed |

Environment: macOS arm64, Python 3.14.10, Node.js 22.14.0. Exact Python versions are in backend/requirements-production.txt and requirements-ci.txt; JS dependencies are locked in frontend/package-lock.json. The browser runtime retains its bundled Python 3.12 / SciPy 1.14.1 distributions.

## Scope and honest verification limits

- No public deployment or repository creation was performed. No hosting bill was incurred. The existing site's owner-only audience was read and preserved. Its previous live URL is not a public professor-accessible deployment.
- The Vercel and Render configuration files were prepared against official documentation; the cloud build/headers/custom domains have not been exercised on those services.
- Docker is unavailable here. The actual Linux container has not been built or run. Linux wheel resolution is a separate, narrower check.
- No browser-control capability was available for new desktop/mobile visual QA, Safari execution, clipboard permissions or actual PNG download. Responsive CSS and mobile menu interaction are preserved; the mobile menu passed a DOM interaction test. Do not treat that as a real mobile-device pass.
- Plotly is stubbed only in jsdom, which lacks SVG layout. Data and thermodynamic API requests are real. Real scientific WebAssembly execution is checked independently by scripts/verify-browser-engine.mjs; this does not verify the browser Worker transport or actual chart rendering.
- Excel import/export and batch calculations are not implemented in the inspected source. They were neither removed nor claimed tested. The API accepts one state per request and rejects array/bulk payloads.
- The inverse-solver global uniqueness limitation and unresolved PDF/table differences remain unchanged. Software test passes do not establish exact scientific agreement with the PDF.
- The lazy Plotly bundle is about 1.13 MB and triggers Vite's chunk-size advisory. It is not a build failure. First-load self-contained scientific runtime assets are relatively large (about 36 MB).

## New deployment controls

Exact production HTTPS CORS origins and allowed hosts; no wildcard origin/host; disabled production OpenAPI/debug pages; body limit 16 KiB including chunked requests; compressed API request bodies rejected; at most two concurrent calculations per process with explicit 503/Retry-After; production startup uses one worker and a 32-connection limit; browser queue limits; no auto-deployment on Git push; no repository visibility changes. These are bounded-resource controls, not distributed anti-abuse protection or hard CPU deadlines.

Raw results: production-smoke.json, wasm-verification.json, static-downloads.json, source-check.json and linux-resolution.json. The target localhost/example origins in these files are test addresses, not published URLs.

## Source publishing checks — 2026-11-19

The production build passed again after adding checksum-verified runtime restoration for a fresh GitHub clone. A missing runtime manifest asset was downloaded from its official distribution and verified byte-for-byte. Large runtime binaries are reconstructed by the prebuild hook; node_modules, environments, credentials, local state, and the supplied PDF are not part of the source upload. Scientific calculations were not changed and the full numerical suite above was not rerun for this packaging-only change. Remote GitHub Actions results must be checked independently.
