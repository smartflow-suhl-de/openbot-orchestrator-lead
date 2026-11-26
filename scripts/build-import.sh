#!/usr/bin/env bash
# Build the import zip for OpenBot (thin wrapper around build-import.py).
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
exec python3 scripts/build-import.py "$@"
