#!/bin/sh
set -eu
# TLS terminates at the host. Do not trust arbitrary forwarded client headers.
exec python -m uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" \
  --workers 1 --limit-concurrency 32 --backlog 64 --timeout-keep-alive 5 \
  --no-proxy-headers --no-server-header --log-level warning
