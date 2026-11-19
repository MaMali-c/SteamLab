> Current status: see VERIFICATION.md and README.md. Runtime checks now pass; earlier unavailable-environment notes below are historical.

# Integration record — 2026-11-12

The React frontend now submits all eleven supported pairs as `{input_pair: "T_P", values: {T: 300, P: 1000}}`, converting display units to canonical backend units. A response adapter validates the new contract and supplies the existing diagram/cards with validated properties. No scientific values are produced by the browser.

Implemented: four adaptive output cards; separate original input receipt; phase/region/quality; saturation pressure at T and temperature at P; solver diagnostics and warnings; clear/reset; copying validated results and warnings; stale-result invalidation and request cancellation; error messages for ambiguity, unsupported domain and incomplete numerical search.

Live React integration cases cover all eleven pairs. Seed values come from actual API calculations, not test fixtures. Unique successful states must display results; reported ambiguity must display an error with no copyable result. These tests require a running backend at TERMOYAZD_TEST_API (default http://127.0.0.1:8000). The existing synthetic App test fixtures were removed. Pure unit-conversion tests remain independent of scientific calculations.

ACTUAL VERIFICATION: syntax parsing of all 16 source/test TS and TSX files passed. npm test and npm run build were attempted and failed before execution because npm is unavailable. The scientific dependencies remain unavailable, so the real API/UI tests and browser visual QA are NOT executed. This delivery implements integration but does not certify runtime correctness, numerical completeness, or every-pair UI behavior. No numerical success is fabricated.

The engine's finite root enumeration is still not a mathematical proof of uniqueness. Its scientific warnings are displayed and copied with the result. PDF validation remains pending. Previous backend/SCIENCE.md notes about frontend not being integrated are historical; integration now exists, but scientific validation is still incomplete.

Additional actual checks passed: all eleven request-pair configurations enabled, canonical unit conversions and malformed-response rejection for every pair, executed with the embedded Node runtime. Quality conversion is checked with a floating-point tolerance (35% becomes approximately 0.35). Backend pytest was attempted again and could not run because pytest is absent.
