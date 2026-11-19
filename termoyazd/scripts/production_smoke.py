"""Run against a real HTTP API. No hardcoded scientific outputs or mock fallback."""
import argparse
import json
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

PAIRS = ('T_P', 'T_x', 'P_x', 'T_s', 'T_u', 'T_h', 'T_v', 'P_s', 'P_u', 'P_h', 'P_v')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--api', required=True, help='Actual API origin, no /api suffix')
    parser.add_argument('--origin', required=True, help='Exact allowed frontend origin')
    parser.add_argument('--report', default='deployment/production-smoke.json')
    args = parser.parse_args()
    results = []

    def call(path, payload=None, headers=None, method=None):
        data = None if payload is None else json.dumps(payload).encode()
        request = Request(args.api.rstrip('/') + path, data=data,
                          headers={'Content-Type': 'application/json', **(headers or {})}, method=method)
        try:
            response = urlopen(request, timeout=180)
        except HTTPError as error:
            response = error
        with response:
            raw = response.read()
            try:
                body = json.loads(raw)
            except ValueError:
                body = raw.decode(errors='replace')
            return response.status, body, {key.lower(): value for key, value in response.headers.items()}

    def check(name, passed, detail=None):
        results.append({'name': name, 'passed': bool(passed), 'detail': detail})
        if not passed:
            raise AssertionError(name + ': ' + str(detail))

    try:
        code, body, _ = call('/api/health')
        check('health', code == 200 and body['app'] == 'termoyazd')
        code, seed, _ = call('/api/calculate', {'input_pair': 'P_x', 'values': {'P': 500, 'x': .35}})
        check('real IF97 seed', code == 200, seed if code != 200 else None)
        state = seed['full_state'] | {'x': .35}
        for pair in PAIRS:
            values = {key: state[key] for key in pair.split('_')}
            if pair == 'T_P':  # T,P at saturation is intentionally underdetermined.
                values = {'T': 300, 'P': 500}
            code, answer, _ = call('/api/calculate', {'input_pair': pair, 'values': values})
            valid = code == 200 and len(answer['calculated_properties']) == 4
            valid = valid and answer['convergence']['converged']
            valid = valid and all(abs(r) <= answer['convergence']['tolerances'][k] for k, r in answer['convergence']['residuals'].items())
            check(pair, valid, {'status': code, 'method': answer.get('solver_method'), 'convergence': answer.get('convergence')})
        code, body, _ = call('/api/calculate', {'input_pair': 'P_x', 'values': {'P': 500, 'x': 1.2}})
        check('invalid quality', code == 422 and body['error']['code'] == 'invalid_quality')
        code, body, _ = call('/api/calculate', {'input_pair': 'T_P', 'values': {'T': state['T'], 'P': state['P']}})
        check('saturation ambiguity', code == 422 and body['error']['code'] == 'ambiguous_saturation')
        code, body, _ = call('/api/diagrams/saturation')
        check('161 real saturation samples', code == 200 and len(body['points']) == 161 and body['critical']['included'] is False)
        for path in ('/docs', '/openapi.json'):
            check('production hides ' + path, call(path)[0] == 404)
        code, _, headers = call('/api/calculate', method='OPTIONS', headers={'Origin': args.origin, 'Access-Control-Request-Method': 'POST'})
        check('exact allowed CORS origin', code == 200 and headers.get('access-control-allow-origin') == args.origin)
        code, _, headers = call('/api/calculate', method='OPTIONS', headers={'Origin': 'https://not-allowed.invalid', 'Access-Control-Request-Method': 'POST'})
        check('other origin rejected', code == 400 and 'access-control-allow-origin' not in headers)
        code, _, _ = call('/api/calculate', {'oversized': 'x' * 20000})
        check('oversized request rejected', code == 413)
        code, _, _ = call('/api/calculate', [{'input_pair': 'T_P', 'values': {'T': 300, 'P': 500}}])
        check('unsupported batch rejected', code == 422)
    finally:
        path = Path(args.report)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({'target': args.api, 'checks': results, 'passed': all(r['passed'] for r in results)}, indent=2))
    print(f'{len(results)} production HTTP checks passed')


if __name__ == '__main__':
    main()
