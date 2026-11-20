# Contributing

Work in `termoyazd/` for the current application. Preserve the historical root project unless the change explicitly concerns it. Open a focused branch and explain the observable problem, final behavior, scientific assumptions and actual checks run.

For numerical changes, include original-input residual checks, domain/ambiguity cases and an independent IF97 or traceable table reference where appropriate. Never alter reference values to fit the solver. Keep rounding, source formulation differences and implementation errors distinct. Changes to worker-runtime versions require checksum and real Pyodide verification.

For UI changes, preserve the 11-pair contract, engineering units, stale-result invalidation, accessible labels and visible scientific warnings. Do not replace API errors with demonstration output. Run the relevant backend, frontend and real-transport checks in [development](docs/DEVELOPMENT.md).

Avoid committing credentials, generated dependencies, runtime binaries, build outputs or privately supplied PDFs. Add clear provenance for new reference datasets. See [NOTICE](NOTICE.md) for licensing boundaries.
