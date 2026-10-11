import json, sys, collections
R = json.load(open(sys.argv[1])); only = sys.argv[2] if len(sys.argv) > 2 else ''
for s in R:
    if only and only not in s['label']: continue
    print('==', s['label'], 'frames', s['frames'], s['totals'])
    c = collections.defaultdict(dict)
    for k, v in s['counts'].items():
        kind, reg = k.split(':'); c[reg][kind] = v
    for reg in sorted(c):
        w = {kind: s['worst'].get(kind + ':' + reg, {}).get('v') for kind in ('vel', 'flip', 'area')}
        print(f"   {reg:12s} " + '  '.join(f"{kind} {c[reg].get(kind, 0):6d}" for kind in ('vel', 'flip', 'area', 'inv')) + f"   worst vel {w['vel']} flip {w['flip']} area {w['area']}")
    # how many frames have any vel event > 2 cm in a region
    ev = s.get('events', [])
    big = collections.Counter((e[1]) for e in ev if e[0] == 'vel' and e[2] > 0.02)
    if big: print('   vel>2cm events (first 1500):', dict(big))
