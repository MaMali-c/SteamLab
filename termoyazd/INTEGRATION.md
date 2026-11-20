# Frontend/engine integration

See [Architecture](docs/ARCHITECTURE.md), [API contract](docs/API.md) and [Development checks](docs/DEVELOPMENT.md). All eleven input pairs use real Python calculations through FastAPI or the shared Pyodide worker engine. Invalidated inputs clear old results. Scientific failures stay errors, and returned warnings remain part of the result.

Current execution evidence is in [Validation](docs/VALIDATION.md) and [test results](docs/TEST_RESULTS.md). This supersedes earlier environment-specific integration milestone notes.
