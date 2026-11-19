"""Bound request bodies before JSON parsing, including chunked requests."""
from starlette.responses import JSONResponse


class RequestGuard:
    def __init__(self, app, max_body_bytes: int):
        self.app, self.maximum = app, max_body_bytes

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http':
            return await self.app(scope, receive, send)

        async def guarded_send(message):
            if message['type'] == 'http.response.start':
                headers = list(message.get('headers', []))
                headers.extend([(b'x-content-type-options', b'nosniff'),
                                (b'x-frame-options', b'DENY'),
                                (b'referrer-policy', b'no-referrer')])
                if scope.get('path') == '/api/calculate':
                    headers.append((b'cache-control', b'no-store'))
                message = {**message, 'headers': headers}
            await send(message)

        async def reject(status, code, message):
            return await JSONResponse({'error': {'code': code, 'message': message}}, status_code=status)(scope, receive, guarded_send)

        if scope['method'] not in ('POST', 'PUT', 'PATCH'):
            return await self.app(scope, receive, guarded_send)
        headers = dict(scope['headers'])
        try:
            length = int(headers.get(b'content-length', b'0'))
            if length < 0:
                raise ValueError()
        except ValueError:
            return await reject(400, 'invalid_length', 'Invalid Content-Length.')
        if length > self.maximum:
            return await reject(413, 'request_too_large', 'Request exceeds the configured byte limit.')
        if headers.get(b'content-encoding', b'identity').lower() != b'identity':
            return await reject(415, 'unsupported_encoding', 'Compressed request bodies are not accepted.')
        if scope.get('path') == '/api/calculate' and headers.get(b'content-type', b'').split(b';')[0].strip().lower() != b'application/json':
            return await reject(415, 'json_required', 'Use application/json.')
        body = bytearray()
        while True:
            message = await receive()
            if message['type'] == 'http.disconnect':
                return
            body.extend(message.get('body', b''))
            if len(body) > self.maximum:
                return await reject(413, 'request_too_large', 'Request exceeds the configured byte limit.')
            if not message.get('more_body', False):
                break
        delivered = False

        async def replay():
            nonlocal delivered
            if delivered:
                return await receive()
            delivered = True
            return {'type': 'http.request', 'body': bytes(body), 'more_body': False}

        await self.app(scope, replay, guarded_send)
