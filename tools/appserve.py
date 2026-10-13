"""Serves the iOS app's Game folder the way the app does, including native/save.js built exactly like SaveBridge.restoreScript()
from a backup file (argv[2]), and logs every request."""
import http.server, json, os, sys
ROOT, BACKUP, PORT = sys.argv[1], sys.argv[2], int(sys.argv[3])
def restore_script():
    try:
        o = json.load(open(BACKUP)); save = o['save']; t = float(o['t']); assert isinstance(json.loads(save), dict)
    except Exception: return "/* no saved copy in the app yet */\n"
    lit = json.dumps(save)
    return ("(function () { try {\n  var k = 'paint-world-red.v1', T = %d, lt = +(localStorage.getItem(k + '.t') || 0);\n"
            "  if (!localStorage.getItem(k) || lt < T) { localStorage.setItem(k, %s); localStorage.setItem(k + '.t', String(T)); }\n} catch (e) {} })();\n\n") % (int(t), lit)
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(s, *a, **k): super().__init__(*a, directory=ROOT, **k)
    def log_message(s, fmt, *a): print('REQ', s.path, a[1] if len(a) > 1 else '', flush=True)
    def do_GET(s):
        if s.path.split('?')[0] == '/native/save.js':
            b = restore_script().encode(); s.send_response(200); s.send_header('Content-Type', 'text/javascript; charset=utf-8'); s.send_header('Content-Length', str(len(b))); s.end_headers(); s.wfile.write(b); return
        return super().do_GET()
http.server.ThreadingHTTPServer(('127.0.0.1', PORT), H).serve_forever()
