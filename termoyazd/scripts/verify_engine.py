#!/usr/bin/env python3
"""Install and test the scientific engine; preserve an honest execution report."""
from __future__ import annotations
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--skip-install', action='store_true')
    args = parser.parse_args()
    runtime = ROOT / '.runtime'
    runtime.mkdir(exist_ok=True)
    report = {'timestamp_utc': datetime.now(timezone.utc).isoformat(), 'status': 'not_run', 'steps': [], 'numerical_tests_passed': False, 'demo': None}
    log_path = runtime / 'engine-verification.log'
    python = ROOT / '.venv' / 'bin' / 'python'
    def run(name: str, command: list[str], cwd: Path) -> None:
        print(name, flush=True)
        result = subprocess.run(command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        with log_path.open('a') as log:
            log.write('\n'+name+'\n'+result.stdout)
        print(result.stdout, end='', flush=True)
        report['steps'].append({'name': name, 'exit_code': result.returncode})
        if result.returncode:
            raise RuntimeError(name+' failed; later steps were not executed.')
    log_path.write_text('termoyazd scientific engine verification\n')
    try:
        if not python.exists():
            run('Create project virtual environment', [sys.executable, '-m', 'venv', str(ROOT / '.venv')], ROOT)
        if not args.skip_install:
            run('Install scientific and test dependencies', [str(python), '-m', 'pip', 'install', '-r', str(ROOT/'backend/requirements-dev.txt')], ROOT)
        run('Run scientific and API tests', [str(python), '-m', 'pytest', '-q', '--junitxml='+str(runtime/'engine-tests.xml')], ROOT/'backend')
        report['numerical_tests_passed'] = True
        code = '''import json
from fastapi.testclient import TestClient
from app.main import app
request = {"input_pair":"T_P","values":{"T":300,"P":1000}}
r = TestClient(app).post("/api/calculate",json=request)
r.raise_for_status()
result=r.json()
p=result["full_state"]
assert abs(p["h"]-p["u"]-p["P"]*p["v"])<1e-6
print(json.dumps({"request":request,"response":result,"energy_identity":"passed"},indent=2))
'''
        result = subprocess.run([str(python), '-c', code], cwd=ROOT/'backend', capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError('Live in-process API demonstration failed: '+result.stderr)
        report['demo'] = json.loads(result.stdout)
        report['status'] = 'passed'
        print(result.stdout)
        print('Scientific test suite passed. PDF validation and global inverse-root completeness still require review.')
        return 0
    except (OSError, RuntimeError, ValueError) as exc:
        report['status'] = 'failed'
        report['error'] = str(exc)
        print(str(exc), file=sys.stderr)
        return 1
    finally:
        destination = runtime/'engine-verification.json'
        destination.write_text(json.dumps(report, indent=2))
        print('Report: '+str(destination))
        print('Log: '+str(log_path))

if __name__ == '__main__':
    raise SystemExit(main())
