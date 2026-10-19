#!/bin/sh
# Builds admin/dist/: exactly the files the dashboard needs, plus _headers (its security headers, for Cloudflare Pages).
# Upload that folder; never upload admin/ itself (dev/ and tests/ hold a mock with fake accounts).
set -eu
cd "$(dirname "$0")/.."
rm -rf dist
mkdir -p dist/js/pages
cp index.html app.css icon.svg catalog.json dist/
cp js/*.js dist/js/
cp js/pages/*.js dist/js/pages/
cp deploy/_headers dist/_headers
# a sanity check: the config must point at the real project and hold no test hooks
grep -q "^export const DEV = null;" dist/js/config.js || { echo "js/config.js has test hooks: not building" >&2; exit 1; }
if grep -rqiE "service_role|sb_secret_" dist; then echo "a secret key is in the files: not building" >&2; exit 1; fi
echo "built admin/dist ($(find dist -type f | wc -l | tr -d ' ') files)"
