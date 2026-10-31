#!/usr/bin/env bash
# Rebuilds the whole dataset into $NEXA_OUT (default: ./output) and runs all checks.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
export NEXA_OUT="${NEXA_OUT:-$HERE}"
cd "$HERE/generator"
python3 gen_policies.py
python3 gen_catalog.py
python3 gen_customers.py > /dev/null
python3 gen_uploads.py
python3 gen_qa.py > /dev/null
python3 validate.py | tail -3
if [ -f "$NEXA_OUT/api/mock_server/test_mock_api.py" ]; then
  cd "$NEXA_OUT/api/mock_server" && python3 -m pytest -q 2>&1 | tail -2
fi
