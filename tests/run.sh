#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
"${OPKIT_PYTHON:-python3}" -m unittest discover -s "$ROOT/tests" -p "test_*.py" -v
exec "${OPKIT_PYTHON:-python3}" "$ROOT/tests/pilot.py"
