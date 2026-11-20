# HTTP API

All examples below use the native FastAPI transport. The browser worker exposes equivalent scientific results without requiring an HTTP Python service.

## Calculate

`POST /api/calculate`, `Content-Type: application/json`.

```json
{"input_pair":"T_P","values":{"T":300,"P":500}}
```

Exactly two numeric values corresponding to `input_pair` are required. JSON numeric strings, booleans, extra request fields, mismatched keys and non-finite values are rejected. All inputs use the canonical units in the [scientific model](SCIENTIFIC_MODEL.md). The supported enums are `T_P`, `T_x`, `P_x`, `T_s`, `T_u`, `T_h`, `T_v`, `P_s`, `P_u`, `P_h`, `P_v`.

| Successful response field | Meaning |
|---|---|
| `input_pair` | Requested pair identifier |
| `normalized_inputs` | Two canonical supplied values |
| `calculated_properties` | Four property-card values |
| `full_state` | All six properties T, P, h, u, s, v |
| `region` | IF97 region identifier |
| `phase` | Engineering phase description |
| `quality` | Vapor mass quality or null when undefined |
| `saturation` | Applicable `temperature_at_P_c` / `pressure_at_T_kpa` boundary information |
| `solver_method` | Calculation strategy used |
| `convergence` | Converged flag, residuals, tolerances, evaluations, verified candidates, uniqueness flag |
| `scientific_warnings` | Scientific qualifications that must remain visible |

The Pydantic source of truth is [`schemas.py`](../backend/app/schemas.py). See the complete [real response](../examples/T_P.response.json) and [input request](../examples/T_P.request.json). A client should check HTTP success, validate the full response and retain warnings; it must not treat a failed request as a successful result or reuse stale numbers.

## Errors

Scientific failures use HTTP 422 with an `error` object containing a code and message; ambiguity may also include candidate states. Request-schema failures use FastAPI/Pydantic's `detail` structure. These are distinct error envelopes and clients should handle both.

| Status / example code | Interpretation |
|---|---|
| 422 / `invalid_quality` | x is outside [0,1] |
| 422 / `quality_domain` | Quality requested outside supported saturation range |
| 422 / `ambiguous_saturation` | T/P specifies a saturation boundary without mixture quality |
| 422 / `ambiguous_state` | Multiple verified candidate states |
| 422 / `search_incomplete` | Search cannot responsibly rule out unresolved intervals |
| 422 / `no_verified_state` | No candidate passed original-input residual checks |
| 422 / `out_of_range`, `critical_point` | Unsupported model/software location |
| 413 | Body exceeds configured size limit |
| 415 | Unsupported body content/encoding |
| 503 | Calculation concurrency limit reached; inspect Retry-After |
| 400 | Host or preflight policy rejection, depending on request |

No endpoint accepts batch arrays. No Excel endpoint exists. Do not silently loop an unbounded batch through the server.

## Other endpoints

- `GET /api/health`: application readiness identifier.
- `GET /api/diagrams/saturation`: cached actual saturation data, metadata and critical-exclusion information.
- `GET /api/diagram/ts`: retained compatibility route.
- Development `/docs`, `/redoc`, `/openapi.json` are disabled in production.

## Production boundary

Default request limit is 16384 bytes, including streamed/chunked counting, and two simultaneous calculations per process. Calculation responses use no-store. Allowed origins and hosts are explicit; CORS is not authentication. No hard CPU cancellation deadline or distributed rate limiting is implemented. Configure infrastructure controls for a heavily exposed deployment.
