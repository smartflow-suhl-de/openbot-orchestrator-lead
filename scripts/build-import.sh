#!/usr/bin/env bash
# Baut das Import-Zip für OpenBot (dünner Wrapper um build-import.py).
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
exec python3 scripts/build-import.py "$@"
