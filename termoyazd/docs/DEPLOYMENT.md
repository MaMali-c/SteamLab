# Deployment guide — monorepository paths matter

The GitHub repository is named `SteamLab`; the application is in `termoyazd/`. Existing source publication is separate from public website deployment. No live site or paid service is created by this guide.

## Option A: a single static site with browser Python

This avoids maintaining a Python server. The production build packages the shared IF97 engine for Pyodide; visitors only need a browser with WebAssembly support. Initial runtime downloads are roughly 36 MB, so cold-start behavior should be checked on slower connections.

For Vercel, import the GitHub repository and set:

| Setting | Value |
|---|---|
| Root Directory | `termoyazd` |
| Framework | Vite / build settings from included `vercel.json` |
| Install | `npm --prefix frontend ci` |
| Build | `npm run build` |
| Output | `dist` |
| `VITE_BROWSER_ENGINE` | `true` (production default) |
| `VITE_BASE_PATH` | `/` |

The committed `vercel.json` deliberately has `git.deploymentEnabled=false`; enable Git deployment explicitly when you decide to publish, or perform an authorized manual deployment. Importing the repository alone may therefore not trigger a deployment. This documentation update leaves that safeguard unchanged.

Do not set a fake API URL for this mode. Build needs outbound access to the pinned official runtime artifacts. After deployment, open the real assigned HTTPS URL; test a calculation, all input modes, chart hover/zoom and actual PNG download. Never replace a failed engine with invented results.

## Option B: Vercel frontend + Render FastAPI

1. Create a Render Docker web service from this repository. Set **Root Directory `termoyazd`**, Dockerfile `backend/Dockerfile`, build context `.`. Alternatively use the Blueprint at `termoyazd/render.yaml` if the platform accepts its path; it is configured for the same root directory.
2. Set `TERMOYAZD_ENV=production`. Set `TERMOYAZD_CORS_ORIGINS` to the **exact actual Vercel HTTPS origin**. Set allowed hostnames explicitly with `TERMOYAZD_ALLOWED_HOSTS`, or use Render's supplied external hostname. Never use `*`.
3. Keep body limit 16384 and calculation limit 2 unless reviewed. Use the service's port environment and the included production entrypoint. Health endpoint: `/api/health`.
4. Copy the real Render HTTPS origin into frontend `VITE_API_BASE_URL`, with no `/api` suffix; set `VITE_BROWSER_ENGINE=false`.
5. Rebuild/redeploy frontend. If the frontend domain changes, update CORS and redeploy backend as needed.
6. Run the smoke script against the actual API and frontend origins. These checks do not replace browser checks.

The included Render template selects a paid `starter` plan and disables automatic deployment. Review service/pricing choices before creation. Docker image construction and a real cloud deployment have not been executed in the current environment.

## Environment reference

| Variable | Purpose |
|---|---|
| `VITE_BROWSER_ENGINE` | Build-time browser Python vs remote API transport |
| `VITE_API_BASE_URL` | Exact production remote API HTTPS origin |
| `VITE_BASE_PATH` | Frontend base path; `/` or e.g. `/SteamLab/` |
| `VITE_API_TARGET` | Local development proxy target only |
| `TERMOYAZD_ENV` | `development` or `production` |
| `TERMOYAZD_CORS_ORIGINS` | Comma-separated permitted exact origins |
| `TERMOYAZD_ALLOWED_HOSTS` | Comma-separated hostnames, without URL schemes |
| `TERMOYAZD_MAX_BODY_BYTES` | Default 16384 |
| `TERMOYAZD_MAX_CALCULATIONS` | Default 2 per process |
| `OPENBLAS_NUM_THREADS` | Template value 1 |

All `VITE_*` values are public. No thermodynamic API secret is required. Production disables debug/docs and rejects inappropriate host/origin settings. The semaphore does not provide global rate limiting or guaranteed CPU termination.

## GitHub Pages alternative

Pages can serve the **browser-engine static build**, not FastAPI. Build with `VITE_BROWSER_ENGINE=true VITE_BASE_PATH=/SteamLab/ npm run build` for a repository project site. For a custom-domain root site use `/` instead. Enable a Pages deployment workflow at repository-root `.github/workflows/` only after choosing to publish. The nested `termoyazd/.github/workflows/pages.yml` is a template and needs paths adapted to the monorepository before activation. Merely having that nested file does not deploy anything.

## macOS deployment preparation

```bash
git clone https://github.com/MaMali-c/SteamLab.git
cd SteamLab/termoyazd
npm --prefix frontend ci
npm run build
npm --prefix frontend run preview -- --port 4173
```

Use the preview URL only on your own machine. A professor on another computer needs the actual assigned public hosting URL. A GitHub source link and `localhost` are not substitutes for a hosted application.

Primary platform guides: [Vercel monorepositories](https://vercel.com/docs/monorepos), [Render monorepositories](https://render.com/docs/monorepo-support), [Render Blueprint specification](https://render.com/docs/blueprint-spec). Verify provider settings when deploying because service interfaces can change.
