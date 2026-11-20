# Production and reporting

The application contains no built-in account system. Production uses explicit allowed hosts and CORS origins, disabled debug/API docs, request-size checks, JSON-only calculation requests and bounded concurrent calculations. These controls are not authentication or distributed denial-of-service protection.

`VITE_*` variables are public build-time values. Do not place GitHub, hosting or other credentials there. Browser-runtime artifacts are pinned and checksum-verified during preparation. Never disable checksum validation to work around a failed download.

Report reproducible issues to the repository maintainer. Do not publish secrets or private user data in an issue. No dedicated private vulnerability-reporting channel or response-time promise is asserted by this file. When reporting a scientific defect, include the pair, canonical inputs, runtime, commit, response and expected reference provenance.

Current limits and deployment responsibilities are documented in [deployment](docs/DEPLOYMENT.md) and [API](docs/API.md).
