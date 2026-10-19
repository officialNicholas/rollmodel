#!/usr/bin/env python3
"""Try the website locally the way Cloudflare Pages serves it: every response gets the headers in site/_headers (so the
Content-Security-Policy applies), /privacy finds privacy.html, and an address that isn't there gets 404.html with a 404.

  python3 site/dev/serve.py [port]       (default 8798; it listens on 127.0.0.1 only)

site/dev/ is for trying the site out; it isn't uploaded (tools/site_build.py --dist leaves it out)."""
import http.server, os, re, sys, urllib.parse

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TYPES = {'.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.json': 'application/json',
         '.txt': 'text/plain; charset=utf-8', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.webp': 'image/webp',
         '.ico': 'image/x-icon', '.woff2': 'font/woff2'}

def read_headers(path):
    """The rules in a Cloudflare Pages _headers file: [(pattern, [(name, value)], [names to drop])], in order."""
    rules, cur = [], None
    for line in open(path, encoding='utf8'):
        line = line.rstrip('\n')
        if not line.strip() or line.lstrip().startswith('#'): continue
        if not line[0].isspace():
            cur = (line.strip(), [], []); rules.append(cur); continue
        assert cur, '_headers: a header before any address'
        t = line.strip()
        if t.startswith('!'): cur[2].append(t[1:].strip().lower()); continue
        name, _, value = t.partition(':'); cur[1].append((name.strip(), value.strip()))
    return rules

def matches(pattern, path):
    """A _headers address: * matches anything (a splat), :name one part of the path."""
    rx = '^' + ''.join('.*' if part == '*' else '[^/]+' if part.startswith(':') else re.escape(part) for part in re.split(r'(\*|:[A-Za-z]\w*)', pattern) if part) + '$'
    return re.match(rx, path) is not None

def headers_for(path):
    out = {}
    for pattern, add, drop in read_headers(os.path.join(SITE, '_headers')):
        if not matches(pattern, path): continue
        for n in drop: out.pop(n, None)
        for n, v in add:
            k = n.lower(); out[k] = (n, out[k][1] + ', ' + v) if k in out else (n, v)
    return list(out.values())

class Handler(http.server.BaseHTTPRequestHandler):
    server_version = 'rollmodel-dev'; sys_version = ''
    def find(self, path):
        """The file for an address, as Cloudflare Pages finds it; None if there isn't one."""
        rel = urllib.parse.unquote(path).lstrip('/')
        if '\0' in rel or any(p in ('..', '.') for p in rel.split('/')) or rel.startswith('dev/') or rel == 'dev': return None
        full = os.path.join(SITE, rel)
        for cand in ([os.path.join(full, 'index.html')] if (rel == '' or rel.endswith('/')) else [full, full + '.html', os.path.join(full, 'index.html')]):
            if os.path.isfile(cand) and os.path.commonpath([SITE, os.path.realpath(cand)]) == SITE and not os.path.basename(cand).startswith('_'): return cand
        return None
    def send(self, head_only):
        path = urllib.parse.urlsplit(self.path).path
        f = self.find(path); status = 200
        if f is None: f, status = os.path.join(SITE, '404.html'), 404
        body = open(f, 'rb').read()
        self.send_response(status)
        self.send_header('Content-Type', TYPES.get(os.path.splitext(f)[1], 'application/octet-stream'))
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        for n, v in headers_for(path): self.send_header(n, v)
        self.end_headers()
        if not head_only: self.wfile.write(body)
    def do_GET(self): self.send(False)
    def do_HEAD(self): self.send(True)
    def log_message(self, fmt, *args):
        if os.environ.get('RM_QUIET') != '1': sys.stderr.write('%s %s\n' % (self.log_date_time_string(), fmt % args))

def serve(port=8798, quiet=False):
    if quiet: os.environ['RM_QUIET'] = '1'
    return http.server.ThreadingHTTPServer(('127.0.0.1', port), Handler)

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8798
    httpd = serve(port); print('Roll Model website: http://127.0.0.1:%d/  (Ctrl+C to stop)' % port)
    try: httpd.serve_forever()
    except KeyboardInterrupt: pass
