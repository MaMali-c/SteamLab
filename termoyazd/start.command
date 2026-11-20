#!/bin/bash
# Double-click in Finder, or run: bash start.command
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
# Finder may not inherit a shell's nvm installation.
if ! command -v node >/dev/null 2>&1 && [ -s "$HOME/.nvm/nvm.sh" ]; then
  set +u
  . "$HOME/.nvm/nvm.sh"
  set -u
fi
if ! command -v python3 >/dev/null 2>&1; then
  echo "termoyazd requires Python 3.11 or newer. Install Python from python.org."
  read -r -p "Press Enter to close… " || true
  exit 1
fi
if python3 scripts/dev.py "$@"; then
  exit 0
else
  status=$?
  echo "termoyazd stopped with an error. Read the message above and .runtime logs."
  read -r -p "Press Enter to close… " || true
  exit "$status"
fi
