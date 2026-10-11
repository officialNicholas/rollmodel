# where the pop events of one scenario sit (rest positions, dominant bones), read straight from a runtime's .bin/.json
#   python3 -I popwhere8.py report.json "label" [kinds] [frame-range a:b] [runtime dir]
import json, collections, sys, numpy as np
R = json.load(open(sys.argv[1])); lab = sys.argv[2]; kinds = (sys.argv[3] if len(sys.argv) > 3 else 'vel,flip,area,inv').split(',')
fr = sys.argv[4] if len(sys.argv) > 4 else ''; f0, f1 = (int(x) for x in fr.split(':')) if fr else (-1, 10 ** 9)
RT = sys.argv[5] if len(sys.argv) > 5 else '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo3/www/t10/'
def load(w):
    m = json.load(open(RT + f'axo_{w}.json')); b = open(RT + f'axo_{w}.bin', 'rb').read(); n, o = m['n'], m['off7']
    P = np.frombuffer(b, np.float32, n * 3, o['position']).reshape(-1, 3); si = np.frombuffer(b, np.uint8, n * 4, o['skinIndex']).reshape(-1, 4); sw = np.frombuffer(b, np.uint8, n * 4, o['skinWeight']).reshape(-1, 4) / 255
    T = np.frombuffer(b, np.uint16, m['ni'], o['index']).reshape(-1, 3); return dict(P=P, si=si, sw=sw, T=T, names=[x['name'] for x in m['bones']])
M = {w: load(w) for w in ('stand', 'crawl')}
s = [x for x in R if x['label'] == lab][0]; ev = [e for e in s['events'] if e[0] in kinds and f0 <= e[3] <= f1]
print(lab, len(s['events']), 'events stored;', len(ev), 'selected')
for kind in kinds:
    for w in ('stand', 'crawl'):
        g = collections.defaultdict(list)
        for e in ev:
            if e[0] == kind and e[4] == w: g[e[1]].append(e)
        for reg, es in sorted(g.items(), key=lambda kv: -len(kv[1])):
            m = M[w]; idx = [e[5] for e in es]
            pts = np.array([m['P'][i] if kind == 'vel' else m['P'][m['T'][i]].mean(0) for i in idx])
            frames = collections.Counter(e[3] for e in es)
            print(f'{kind:4s} {w:5s} {reg:10s} n={len(es):5d} max={max(e[2] for e in es):8.3f} at {pts.mean(0).round(3)} sd {pts.std(0).round(3)} frames {sorted(frames.items())[:12]}')
            c = collections.Counter(idx)
            for i, k in c.most_common(3):
                v = i if kind == 'vel' else m['T'][i][0]
                print(f'      #{i} x{k} at {(m["P"][v]).round(3)} w ' + ', '.join(f'{m["names"][m["si"][v][j]]}:{m["sw"][v][j]:.2f}' for j in range(4) if m['sw'][v][j] > 0.01))
