# termoyazd

Pure water/steam calculator: React/TypeScript/Tailwind dashboard, Python IAPWS-IF97/SciPy engine, eleven input pairs and interactive T–s, P–v and P–h diagrams. English labels include Persian explanations.

## Start on macOS

Install Node.js 22 and Python 3.11+ for the local FastAPI edition, then run `bash start.command` from this folder. For a browser-only production build, Python is not required on the frontend host:

```bash
npm --prefix frontend ci
npm run build
```

The prebuild hook restores the exact Pyodide/iapws runtime from official distributions with SHA-256 verification. Runtime binaries and node_modules are not committed. The first build needs internet access; downloaded assets are then self-hosted in the output. The personal ZIP includes these assets and the supplied reference PDF; this GitHub source tree retains the page-referenced validation dataset and original PDF hash, but does not redistribute the PDF. Place your own supplied copy at validation/SteamTableSI.pdf when inspecting the source tables.

## Scientific and deployment documentation

- [Scientific methods and numerical limitations](backend/SCIENCE.md)
- [Recorded verification results](deployment/TEST_RESULTS.md)
- [Source-table comparison](validation/REPORT.md)
- [macOS deployment guide in Persian](DEPLOYMENT_FA.md)
- [GitHub Pages guide in Persian](GITHUB_PAGES_FA.md)

All eleven pairs call the real engine; stale results clear on input changes. Quality is shown only where physically defined. Inverse finite searches do not certify global root completeness, and PDF differences exceeding source rounding remain documented. No exact-agreement or IAPWS-product certification is claimed. Excel import/export and batch calculations are not implemented.

For backend tests, install backend/requirements-ci.txt and run pytest from backend. For live React integration tests, start FastAPI then run `npm --prefix frontend test`. `node scripts/verify-browser-engine.mjs` independently exercises real IF97 in WebAssembly after a build.

## Source upload

This project is stored in the `termoyazd/` directory on the `termoyazd-source` branch of the existing SteamLab repository. The previous main branch is preserved. Uploading source does not itself publish a website. GitHub Pages and Vercel/Render configurations are provided for a separate deployment decision. No license is chosen on the owner's behalf.
