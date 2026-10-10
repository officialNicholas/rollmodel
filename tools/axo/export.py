import numpy as np, json, sys
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo')
from geo import M, D
OUT = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/axo/'
names = None
for nm in ('stand', 'crawl'):
    m = M(nm); r = np.load(D + nm + '_rig.npz'); sk = json.load(open(D + nm + '_skel.json'))
    nn = [b['name'] for b in sk['bones']]
    if names is None: names = nn
    assert nn == names, ('bone order differs', set(nn) ^ set(names))
    idx = r['idx'][m.wid]; w = r['w'][m.wid]; wq = np.round(w * 255).astype(np.int32); wq[:, 0] += 255 - wq.sum(1); wq = np.clip(wq, 0, 255).astype(np.uint8)
    P = m.P0.astype(np.float32); N = m.N0.astype(np.float32); UV = m.UV.astype(np.float32); I = m.I0.reshape(-1).astype(np.uint16 if len(P) < 65536 else np.uint32)
    parts = [P.tobytes(), N.tobytes(), UV.tobytes(), idx.astype(np.uint8).tobytes(), wq.tobytes(), I.tobytes()]
    off = []; o = 0
    for b in parts: off.append(o); o += len(b); o += (-o) % 4
    buf = bytearray(o)
    for b, of in zip(parts, off): buf[of:of + len(b)] = b
    open(OUT + f'{nm}.bin', 'wb').write(buf)
    meta = {'n': len(P), 'ni': len(I), 'i32': len(P) >= 65536, 'off': off, 'bones': sk['bones']}
    json.dump(meta, open(OUT + f'{nm}.json', 'w'))
    print(nm, 'bin', len(buf), 'verts', len(P), 'bones', len(nn))
