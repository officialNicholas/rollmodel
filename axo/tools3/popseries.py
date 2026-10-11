# per-frame event counts of one scenario: python3 popseries.py report.json label [bucket]
import json, sys, collections
R = json.load(open(sys.argv[1])); lab = sys.argv[2]; bk = int(sys.argv[3]) if len(sys.argv) > 3 else 10
for s in R:
    if s['label'] != lab: continue
    agg = collections.OrderedDict()
    for row in s['series']:
        f, w, st = row[0], row[1], row[2]; nv, nf, na = (row[4], row[5], row[6]) if len(row) > 6 else (0, 0, 0)
        key = (f // bk) * bk; a = agg.setdefault(key, [set(), 0, 0, 0]); a[0].add(f'{st}/{w}'); a[1] += nv; a[2] += nf; a[3] += na
    for k, (sts, nv, nf, na) in agg.items():
        if nv or nf or na: print(f'  f{k:5d}  vel {nv:6d} flip {nf:5d} area {na:5d}  {sorted(sts)}')
