# Development and reproduction

All commands assume the current directory is `SteamLab/termoyazd`, not the repository root. Node 22.14.0 and Python 3.14.10 are exercised versions. The browser runtime is pinned separately to Pyodide 0.27.7 (Python 3.12 with its matching numerical packages).

## Two-service development

```bash
bash start.command
```

The launcher installs required packages, chooses available backend/frontend ports, checks both health and the actual Vite API proxy, then opens a browser. Use `bash start.command --no-browser` to keep browser opening manual; `--no-install` requires an already prepared environment. Logs are `.runtime/backend.log` and `.runtime/frontend.log`. `.runtime/session.json` contains actual addresses. Closing the launcher or Ctrl+C cleans up its subprocesses.

Manual alternative in two terminals, after dependency installation:

```bash
# Terminal 1
source .venv/bin/activate
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

```bash
# Terminal 2
VITE_API_TARGET=http://127.0.0.1:8000 npm --prefix frontend run dev -- --port 5173
```

Vite development uses `/api` proxying. A successful frontend page alone does not prove the API is ready; test `/api/health` through the frontend address.

## Browser-engine development and build

```bash
npm --prefix frontend ci
npm run dev
npm run build
npm --prefix frontend run preview -- --port 4173
```

Root `npm run dev` explicitly enables the browser engine; frontend `npm run dev` defaults to native HTTP in development. Production defaults to the browser engine. The prebuild script fetches only pinned runtime files, verifies SHA-256 and copies the actual Python sources. Keep `scripts/browser-runtime-manifest.json` and the source-copy process under review when changing numerical dependencies. Do not commit generated runtime binaries or `node_modules`.

For a remote API production build:

```bash
VITE_BROWSER_ENGINE=false VITE_API_BASE_URL=https://YOUR-REAL-API-HOST npm run build
```

Replace that placeholder with an actual exact HTTPS origin, without `/api`. Build-time configuration is public and requires a rebuild when changed.

## Tests

The plotting check in `test:unit` also calls a real API. Start the API first and set `TERMOYAZD_TEST_API`; the script name does not mean all selected tests are isolated.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements-ci.txt
(cd backend && python -m pytest -q)
TERMOYAZD_TEST_API=http://127.0.0.1:8000 npm --prefix frontend run test:unit
node scripts/verify-browser-engine.mjs
python validation/run_validation.py
```

For the complete React integration suite, run a real API in another terminal, then:

```bash
TERMOYAZD_TEST_API=http://127.0.0.1:8000 npm --prefix frontend test
```

For production guards and the 22-check HTTP script, start the API in production mode with explicit localhost hosts and the test frontend origin:

```bash
TERMOYAZD_ENV=production TERMOYAZD_ALLOWED_HOSTS=localhost,127.0.0.1 TERMOYAZD_CORS_ORIGINS=https://professor.example.org python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 18743 --no-proxy-headers
```

```bash
python scripts/production_smoke.py --api http://127.0.0.1:18743 --origin https://professor.example.org
TERMOYAZD_TEST_API=http://127.0.0.1:18743 npm --prefix frontend test
```

The example `.example.org` origin is a test origin, not a deployment URL. Testing public deployment requires the real HTTPS API and frontend origins.

## Troubleshooting

| Symptom | Next check |
|---|---|
| localhost refuses connection | Keep launcher alive; inspect its actual printed port and logs |
| Another application appears | Port is occupied; use the newly selected session URL |
| API errors while page loads | `/api/health`, proxy target, production API origin and allowed origins |
| Initial browser calculation is slow | First runtime download is large; inspect runtime asset loading |
| Runtime checksum failure | Retry official download; do not bypass the checksum |
| `search_incomplete` / multiple states | Scientific limitation; inspect diagnostics rather than force a result |
| Build on hosting finds no package | Set hosting root directory to `termoyazd` |
| Plotly chunk-size warning | Known sizeable lazy chart bundle; warning alone is not build failure |

No API credentials are required for thermodynamic calculations. Never place tokens in `VITE_*`, screenshots, logs or committed configuration.

## Windows / نصب روی ویندوز

[راهنمای مرحله‌به‌مرحله نصب و اجرای ویندوز](WINDOWS_FA.md) شامل Python و Node.js، دستورهای PowerShell، اجرای API و رابط، آزمون محاسبه و رفع خطاهای پورت و npm است. اجرای واقعی روی ویندوز در محیط فعلی تأیید نشده است.
