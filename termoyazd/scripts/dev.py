#!/usr/bin/env python3
"""Install local dependencies, start two services, await readiness, open browser.

No global packages, process killing by port, or reuse of unknown servers.
All child process groups are shut down when this launcher exits.
"""
import argparse
import errno
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser

ROOT = Path(__file__).resolve().parents[1]


def select_port(preferred: int) -> int:
    """Choose preferred IPv4 loopback port, or let the OS select a fallback."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind(("127.0.0.1", preferred))
        except OSError as exc:
            if exc.errno != errno.EADDRINUSE:
                raise
            sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def wait_ready(url, process, check, timeout=60):
    deadline = time.monotonic() + timeout
    # Ignore system HTTP proxies for local readiness checks.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"Service exited before readiness: {url}. See .runtime logs.")
        try:
            with opener.open(url, timeout=1) as response:
                if response.status == 200 and check(response.read()):
                    return
        except (OSError, urllib.error.URLError, ValueError):
            pass
        time.sleep(0.25)
    raise RuntimeError(f"Timed out waiting for {url}. See .runtime logs.")


def ensure_dependencies(install=True):
    if sys.version_info < (3, 11):
        raise RuntimeError("Python 3.11+ is required; Python 3.12 or 3.13 is recommended.")
    node, npm = shutil.which("node"), shutil.which("npm")
    if not node or not npm:
        raise RuntimeError("Node.js and npm were not found. Install Node.js 22 LTS from nodejs.org, reopen Terminal, then run bash start.command.")
    node_major = int(subprocess.check_output([node, "--version"], text=True).strip().lstrip("v").split(".")[0])
    if node_major < 20:
        raise RuntimeError("Use Node.js 20+; Node.js 22 LTS is recommended.")
    python = ROOT / ".venv" / "bin" / "python"
    requirements = ROOT / "backend" / "requirements.txt"
    marker = ROOT / ".venv" / ".termoyazd-requirements"
    digest = hashlib.sha256(requirements.read_bytes()).hexdigest()
    if install:
        if not python.exists():
            subprocess.run([sys.executable, "-m", "venv", str(ROOT / ".venv")], check=True)
        if not marker.exists() or marker.read_text() != digest:
            subprocess.run([str(python), "-m", "pip", "install", "-r", str(requirements)], check=True)
            marker.write_text(digest)
        frontend = ROOT / "frontend"
        package_hash = hashlib.sha256((frontend / "package.json").read_bytes()).hexdigest()
        npm_marker = frontend / "node_modules" / ".termoyazd-package"
        if not npm_marker.exists() or npm_marker.read_text() != package_hash:
            subprocess.run([npm, "ci" if (frontend / "package-lock.json").exists() else "install"], cwd=frontend, check=True)
            npm_marker.write_text(package_hash)
    if not python.exists() or not (ROOT / "frontend" / "node_modules" / ".bin" / "vite").exists():
        raise RuntimeError("Dependencies are missing. Run bash start.command without --no-install.")
    return python, npm


def stop(process):
    if process.poll() is None:
        try:
            os.killpg(process.pid, signal.SIGTERM)
            process.wait(timeout=5)
        except (ProcessLookupError, subprocess.TimeoutExpired):
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()


def main():
    parser = argparse.ArgumentParser(description="Start termoyazd locally")
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--no-install", action="store_true")
    args = parser.parse_args()
    def interrupted(signum, frame):
        raise KeyboardInterrupt
    for signum in (signal.SIGTERM, signal.SIGHUP):
        signal.signal(signum, interrupted)
    processes, logs = [], []
    try:
        python, npm = ensure_dependencies(not args.no_install)
        backend_port, frontend_port = select_port(8000), select_port(5173)
        backend_url, frontend_url = f"http://127.0.0.1:{backend_port}", f"http://localhost:{frontend_port}"
        runtime = ROOT / ".runtime"
        runtime.mkdir(exist_ok=True)
        for service, command, cwd, env in [
            ("backend", [str(python), "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(backend_port)], ROOT / "backend", os.environ.copy()),
            ("frontend", [npm, "run", "dev", "--", "--port", str(frontend_port), "--strictPort"], ROOT / "frontend", {**os.environ, "VITE_API_TARGET": backend_url}),
        ]:
            log = (runtime / f"{service}.log").open("w")
            logs.append(log)
            processes.append(subprocess.Popen(command, cwd=cwd, env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True))
        print("Waiting for termoyazd API and browser app…", flush=True)
        wait_ready(backend_url + "/api/health", processes[0], lambda body: json.loads(body).get("app") == "termoyazd")
        wait_ready(frontend_url, processes[1], lambda body: b"termoyazd" in body)
        # Verify the actual frontend proxy, not just the two servers separately.
        wait_ready(frontend_url + "/api/health", processes[1], lambda body: json.loads(body).get("app") == "termoyazd")
        (runtime / "session.json").write_text(json.dumps({"frontend": frontend_url, "backend": backend_url}, indent=2))
        print(f"\ntermoyazd is ready: {frontend_url}\nAPI documentation: {backend_url}/docs\nLogs: {runtime}\nKeep this Terminal window open. Press Ctrl+C to stop both services.\n", flush=True)
        if frontend_port != 5173:
            print(f"Port 5173 is busy; using {frontend_port}. The existing service was left running.", flush=True)
        if not args.no_browser:
            webbrowser.open(frontend_url)
        while all(p.poll() is None for p in processes):
            time.sleep(.5)
        raise RuntimeError("A service stopped unexpectedly. Inspect .runtime/backend.log and .runtime/frontend.log.")
    except KeyboardInterrupt:
        print("\nStopping termoyazd…")
        return 0
    except (RuntimeError, OSError, subprocess.CalledProcessError, ValueError) as exc:
        print(f"\ntermoyazd: {exc}", file=sys.stderr)
        return 1
    finally:
        for process in reversed(processes):
            stop(process)
        for log in logs:
            log.close()


if __name__ == "__main__":
    sys.exit(main())
