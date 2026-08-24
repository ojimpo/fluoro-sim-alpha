#!/usr/bin/env bash
# Runs the marker tests against index.html itself, in a real browser, so what
# gets tested is what ships. Served over http rather than file:// because the
# app keeps its alignment in localStorage and file:// origins are opaque.
# Needs google-chrome and a python with opencv (for the fixtures).
set -euo pipefail
cd "$(dirname "$0")"
[ -f fixtures/truth.json ] || python3 make_fixtures.py >/dev/null

port=${PORT:-8731}
python3 -m http.server "$port" --bind 127.0.0.1 --directory ../.. >/dev/null 2>&1 &
server=$!
trap 'kill $server 2>/dev/null || true' EXIT
for _ in $(seq 50); do curl -sf "http://127.0.0.1:$port/index.html" -o /dev/null && break; sleep 0.1; done

out=$(timeout 300 google-chrome --headless=new --disable-gpu --no-sandbox \
  --virtual-time-budget=180000 \
  --dump-dom "http://127.0.0.1:$port/tools/test/harness.html" 2>/dev/null \
  | grep -o 'RESULT .*' | head -1)
[ -n "$out" ] || { echo "harness produced no output"; exit 1; }
echo "${out#RESULT }" | python3 report.py
