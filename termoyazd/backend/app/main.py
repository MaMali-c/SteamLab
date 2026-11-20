"""FastAPI transport; physical equations live in engine.py and thermo.py."""
import logging
from threading import BoundedSemaphore

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .engine import solve
from .guard import RequestGuard
from .schemas import CalculationRequest, CalculationResponse
from .settings import Settings
from .thermo import StateError, saturation_diagram


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    app = FastAPI(title='termoyazd', version='0.1.0', debug=False,
                  docs_url=None if settings.production else '/docs',
                  redoc_url=None if settings.production else '/redoc',
                  openapi_url=None if settings.production else '/openapi.json')
    slots = BoundedSemaphore(settings.max_calculations)
    app.state.calculation_slots = slots
    app.state.settings = settings
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=list(settings.hosts))
    app.add_middleware(RequestGuard, max_body_bytes=settings.max_body_bytes)
    # CORS wraps guards as well, so readable error responses retain allowed origins.
    app.add_middleware(CORSMiddleware, allow_origins=list(settings.origins),
                       allow_credentials=False, allow_methods=['GET', 'POST'],
                       allow_headers=['Content-Type'], max_age=600)

    @app.exception_handler(StateError)
    async def state_error_handler(request: Request, exc: StateError):
        return JSONResponse(status_code=422, content={'error': {'code': exc.code, 'message': str(exc), 'candidates': getattr(exc, 'candidates', [])}})

    @app.get('/api/health')
    def health():
        return {'app': 'termoyazd', 'status': 'ok', 'api_version': '0.1.0'}

    @app.post('/api/calculate', response_model=CalculationResponse)
    def calculate(payload: CalculationRequest):
        if not slots.acquire(blocking=False):
            return JSONResponse(status_code=503, headers={'Retry-After': '2'}, content={'error': {'code': 'server_busy', 'message': 'Scientific engine is busy. Retry shortly.'}})
        try:
            return solve(payload.input_pair, payload.values)
        except StateError:
            raise
        except (ValueError, NotImplementedError, RuntimeError, OverflowError, ZeroDivisionError) as exc:
            raise StateError('numerical_failure', 'IF97 evaluation or numerical convergence failed; no state was accepted.') from exc
        finally:
            slots.release()

    @app.get('/api/diagram/ts')
    def diagram():
        try:
            return saturation_diagram()
        except Exception:
            logging.exception('Saturation diagram generation failed')
            return JSONResponse(status_code=503, content={'error': {'code': 'diagram_unavailable', 'message': 'The saturation boundary could not be generated.'}})

    @app.get('/api/diagrams/saturation')
    def diagram_saturation():
        from .plotting import saturation_data
        try:
            return JSONResponse(content=saturation_data(), headers={'Cache-Control': 'public, max-age=3600'})
        except Exception:
            logging.exception('IF97 saturation dataset failed')
            return JSONResponse(status_code=503, content={'error': {'code': 'diagram_unavailable', 'message': 'Verified saturation data is unavailable; no substitute curve is returned.'}})

    return app


app = create_app()
