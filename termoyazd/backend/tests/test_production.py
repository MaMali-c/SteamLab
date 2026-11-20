"""Production transport checks use real IF97 outputs, never numerical mocks."""
import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.settings import Settings

ORIGIN = 'https://professor.example.org'
REQUEST = {'input_pair': 'T_P', 'values': {'T': 300, 'P': 500}}


def production_app():
    return create_app(Settings(True, (ORIGIN,), ('testserver',), max_body_bytes=512, max_calculations=1))


def test_production_docs_and_security_headers():
    client = TestClient(production_app())
    for path in ('/docs', '/redoc', '/openapi.json'):
        assert client.get(path).status_code == 404
    response = client.post('/api/calculate', json=REQUEST)
    assert response.status_code == 200
    assert response.headers['x-content-type-options'] == 'nosniff'
    assert response.headers['x-frame-options'] == 'DENY'
    assert response.headers['cache-control'] == 'no-store'


def test_exact_cors_and_host_allowlist():
    client = TestClient(production_app())
    response = client.options('/api/calculate', headers={'Origin': ORIGIN, 'Access-Control-Request-Method': 'POST', 'Access-Control-Request-Headers': 'content-type'})
    assert response.status_code == 200
    assert response.headers['access-control-allow-origin'] == ORIGIN
    rejected = client.options('/api/calculate', headers={'Origin': 'https://other.example.org', 'Access-Control-Request-Method': 'POST'})
    assert rejected.status_code == 400
    assert 'access-control-allow-origin' not in rejected.headers
    assert client.get('/api/health', headers={'Host': 'other.example.org'}).status_code == 400


@pytest.mark.parametrize('stream', [False, True])
def test_request_size_limit_including_chunked_bodies(stream):
    client = TestClient(production_app())
    body = b' ' * 513
    response = client.post('/api/calculate', content=iter([body[:250], body[250:]]) if stream else body, headers={'Content-Type': 'application/json', 'Origin': ORIGIN})
    assert response.status_code == 413
    assert response.json()['error']['code'] == 'request_too_large'
    assert response.headers['access-control-allow-origin'] == ORIGIN


def test_bulk_and_compression_are_rejected():
    client = TestClient(production_app())
    assert client.post('/api/calculate', json=[REQUEST]).status_code == 422
    assert client.post('/api/calculate', content=b'{}', headers={'Content-Type': 'application/json', 'Content-Encoding': 'gzip'}).status_code == 415
    assert client.post('/api/calculate', content='{}', headers={'Content-Type': 'text/plain'}).status_code == 415


def test_busy_slot_is_released_and_retry_is_possible():
    app = production_app()
    client = TestClient(app)
    app.state.calculation_slots.acquire()
    try:
        response = client.post('/api/calculate', json=REQUEST)
        assert response.status_code == 503
        assert response.headers['retry-after'] == '2'
    finally:
        app.state.calculation_slots.release()
    assert client.post('/api/calculate', json=REQUEST).status_code == 200
    assert client.post('/api/calculate', json={'input_pair': 'P_x', 'values': {'P': 500, 'x': 2}}).status_code == 422
    assert client.post('/api/calculate', json=REQUEST).status_code == 200


@pytest.mark.parametrize('name,value', [
    ('TERMOYAZD_CORS_ORIGINS', '*'),
    ('TERMOYAZD_CORS_ORIGINS', 'http://frontend.example.org'),
    ('TERMOYAZD_CORS_ORIGINS', 'https://frontend.example.org/path'),
    ('TERMOYAZD_ALLOWED_HOSTS', '*'),
    ('TERMOYAZD_MAX_CALCULATIONS', '0'),
    ('TERMOYAZD_MAX_BODY_BYTES', '-1'),
])
def test_production_rejects_unsafe_configuration(monkeypatch, name, value):
    monkeypatch.setenv('TERMOYAZD_ENV', 'production')
    monkeypatch.setenv('TERMOYAZD_ALLOWED_HOSTS', 'api.example.org')
    monkeypatch.setenv('TERMOYAZD_CORS_ORIGINS', ORIGIN)
    monkeypatch.setenv(name, value)
    with pytest.raises(ValueError):
        Settings.from_env()


def test_render_hostname_default(monkeypatch):
    monkeypatch.setenv('TERMOYAZD_ENV', 'production')
    monkeypatch.setenv('RENDER_EXTERNAL_HOSTNAME', 'api.example.org')
    monkeypatch.delenv('TERMOYAZD_ALLOWED_HOSTS', raising=False)
    monkeypatch.delenv('TERMOYAZD_CORS_ORIGINS', raising=False)
    settings = Settings.from_env()
    assert settings.hosts == ('api.example.org',)
    assert settings.origins == ()
