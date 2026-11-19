> Current status: see VERIFICATION.md and README.md. Runtime checks now pass; earlier unavailable-environment notes below are historical.

# Interactive scientific diagrams

Three projections use one real IF97 saturation dataset: T–s with linear axes, P–v with logarithmic pressure and specific volume, and P–h with logarithmic pressure and linear enthalpy. Canonical engineering units are °C, kPa, kJ/(kg·K), m³/kg and kJ/kg.

Backend: app/plotting.py computes 161 saturated liquid/vapor pairs between 273.16 K and Tc−0.05 K. Cosine spacing concentrates samples near endpoints. All points are checked for finite values, positive pressure/volume and correct liquid/vapor ordering. A failure returns HTTP 503, never a fallback curve. A lock and one-entry cache avoid duplicate concurrent calculations. GET /api/diagrams/saturation returns all three projections' source data with units, domain, critical metadata and warnings; Cache-Control permits an hour of browser reuse.

The final 0.05 K below critical and the exact critical endpoint are explicitly excluded. No artificial apex is appended. The shaded two-phase polygon stops at the last computed temperature/pressure; its horizontal closure is a truncation boundary, not a critical point. Straight line segments between samples are visual interpolation only. Ice, metastable branches and the complete IF97 validity envelope are not plotted. Single-phase area labels apply below critical conditions, not universally across all chart coordinates.

Frontend: plotting/data.ts validates and caches the dataset; plotting/specification.ts constructs independent chart projections; Diagram.tsx owns Plotly loading and controls. The lazy-loaded plotly.js-basic-dist-min distribution supports the scatter plots used here. Its APIs are documented at https://plotly.com/javascript/plotlyjs-function-reference/ and https://plotly.com/javascript/configuration-options/ .

Hover includes coordinate units. Plotly's mode bar and explicit buttons provide zoom, pan, reset and PNG export. Drag-to-zoom is enabled; scroll-wheel zoom is off to avoid capturing page scroll on mobile. The host resizes with ResizeObserver. Browser downloads can depend on browser permissions; failures are surfaced. Export filenames are termoyazd-Ts/Pv/Ph.

A marker is shown only for a converged response with exactly one verified candidate AND uniqueness_certified=true. Consequently inverse results whose global uniqueness is uncertified are deliberately not marked. An explanatory warning appears. Empty, failed or ambiguous calculations have no marker. This conservative plotting rule does not change the calculation engine.

Verification actually performed: frontend syntax parsing passed for 20 TS/TSX/declaration files; backend Python syntax compilation passed. Plotting pytest was attempted but pytest is absent. npm build was attempted but npm is absent. The scientific dataset, Plotly rendering, hover/zoom/pan/export and responsive behavior have NOT been executed or visually verified here. No successful live scientific rendering is claimed.

Tests supplied: backend tests recompute actual IF97 samples, confirm order/domain/cache/API headers. A live frontend test requests actual saturation data and a TP state, checks all projections and marker eligibility. Run bash start.command, then from frontend run npm test and npm run build; use TERMOYAZD_TEST_API for an alternate backend port. Run backend pytest using verify-engine.command. Installing frontend dependencies will add Plotly. Complete these runtime checks before relying on this module for a presentation.
