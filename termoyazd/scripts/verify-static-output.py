"""HTTP asset-download verification; does not substitute for visual browser QA."""
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from threading import Thread
from urllib.request import urlopen
from html.parser import HTMLParser
from pathlib import Path
import json

root = Path(__file__).resolve().parents[1]
dist = root / 'dist'

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

class Assets(HTMLParser):
    paths = []
    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == 'script' and 'src' in values:
            self.paths.append(values['src'])
        if tag == 'link' and values.get('rel') == 'stylesheet':
            self.paths.append(values['href'])

server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(dist)))
thread = Thread(target=server.serve_forever, daemon=True)
thread.start()
base = f'http://127.0.0.1:{server.server_port}'
checks = []
try:
    with urlopen(base + '/') as response:
        html = response.read().decode()
        assert response.status == 200 and 'termoyazd' in html
    parser = Assets()
    parser.feed(html)
    paths = parser.paths + ['/python/engine-worker.js', '/python/engine.py', '/python/thermo.py', '/python/plotting.py', '/python/iapws-1.5.5-py3-none-any.whl', '/pyodide/pyodide.mjs', '/pyodide/pyodide.asm.wasm', '/pyodide/python_stdlib.zip', '/pyodide/pyodide-lock.json']
    for path in paths:
        with urlopen(base + path) as response:
            body = response.read()
            assert response.status == 200 and len(body) == (dist/path.lstrip('/')).stat().st_size
            if path.endswith('.wasm'):
                assert body[:4] == b'\x00asm'
                assert response.headers.get_content_type() == 'application/wasm'
            checks.append({'path':path,'downloaded_bytes':len(body),'passed':True})
    (root/'deployment/static-downloads.json').write_text(json.dumps({'checks':checks,'browser_ui_test':False},indent=2))
    print(f'{len(checks)} built HTML/CSS/JavaScript/scientific assets downloaded successfully over local HTTP')
finally:
    server.shutdown()
    server.server_close()
