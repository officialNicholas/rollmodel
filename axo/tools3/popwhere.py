# where the pop events of one report sit on the crawl mesh (rest positions, labels, weights)
import json, collections, numpy as np, sys
R = json.load(open(sys.argv[1])); s = R[int(sys.argv[2]) if len(sys.argv) > 2 else 0]; ev = s['events']
z = np.load('/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo3/crawl7_rig.npz', allow_pickle=True); P, T, labels, names, idx, w = z['P'], z['T'], z['labels'], z['names'], z['idx'], z['w']
regs = sys.argv[3].split(',') if len(sys.argv) > 3 else None
for kind in ('flip', 'area', 'inv'):
    byreg = collections.defaultdict(list)
    for e in ev:
        if e[0] == kind and e[4] == 'crawl': byreg[e[1]].append(e[5])
    for reg, tl in sorted(byreg.items()):
        if regs and reg not in regs: continue
        c = collections.Counter(tl); cen = np.array([P[T[t]].mean(0) for t in tl])
        print(f'{kind} {reg}: {len(tl)} events on {len(c)} tris; mean {cen.mean(0).round(3)} sd {cen.std(0).round(3)}')
        for t, k in c.most_common(4):
            v = T[t][0]; dom = [(str(names[idx[v][j]]), round(float(w[v][j]), 2)) for j in range(4) if w[v][j] > 0.01]
            print(f'     tri {t} x{k} at {P[T[t]].mean(0).round(3)} lab {labels[v]} w {dom}')
