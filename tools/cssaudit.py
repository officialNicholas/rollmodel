"""Static CSS audit: every @keyframes that animates something other than transform/opacity (those make the page repaint each frame on
iPhone), and the rules that run it forever. usage: cssaudit.py <html>"""
import re, sys
s = open(sys.argv[1]).read()
css = ''.join(m.group(1) for m in re.finditer(r'<style[^>]*>(.*?)</style>', s, re.S))
def scan(text):
    out = []; i = 0; L = len(text)
    while i < L:
        j = text.find('{', i)
        if j < 0: break
        sel = text[i:j].strip(); d = 1; k = j + 1
        while k < L and d > 0:
            c = text[k]
            if c == '{': d += 1
            elif c == '}': d -= 1
            k += 1
        out.append((sel, text[j + 1:k - 1])); i = k
    return out
kf = {}; rules = []
for sel, body in scan(css):
    if sel.startswith('@keyframes'): kf.setdefault(sel.split()[1], set()).update(p for _, b in scan(body) for p in re.findall(r'([a-zA-Z-]+)\s*:', b))
    elif sel.startswith('@media') or sel.startswith('@supports'): rules += scan(body)
    else: rules.append((sel, body))
cheap = {'transform', 'opacity', 'translate', 'rotate', 'scale'}
bad = {k: v - cheap for k, v in kf.items() if v - cheap}
uses = {}
for sel, body in rules:
    for an in re.findall(r'animation(?:-name)?\s*:\s*([^;]+)', body):
        for part in an.split(','):
            for t in part.split():
                if t in bad: uses.setdefault(t, []).append((sel.split('\n')[-1].strip()[-70:], 'infinite' in part))
for k in sorted(bad):
    u = uses.get(k, []); inf = [x for x in u if x[1]]
    print('%-15s %-40s %s' % (k, ','.join(sorted(bad[k]))[:40], ('INF: ' + ' | '.join(x[0][-60:] for x in inf[:4])) if inf else ('once: ' + ' | '.join(x[0][-40:] for x in u[:2]))))
