#!/bin/sh
# serve game/ on :8765 for the probes (idempotent: starts it only when nothing answers)
cd "$(dirname "$0")/../../game" && (curl -s -o /dev/null http://localhost:8765/ || (setsid nohup python3 -m http.server 8765 >/dev/null 2>&1 &)); sleep 1
