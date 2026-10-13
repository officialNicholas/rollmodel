# Read and write the runtime's 'axo7' mesh format (.bin + .json; see the AXO loader in the game, meshFrom):
#   position f32 x3, normal i8 x4, skinIndex u8 x4, skinWeight u8 x4 (normalized), index u16, cpos i16 x4 (normalized, x cpScale), jelly / fill /
#   mat u8 x4 (normalized), uv u16 x2 (normalized), tex (the encoded image bytes), each block 4-byte aligned, offsets in meta.off7
import json
import numpy as np
def read(base):
    m = json.load(open(base + '.json')); b = open(base + '.bin', 'rb').read(); o = m['off7']; n = m['n']; ni = m['ni']
    f = lambda k, dt, c: np.frombuffer(b, dt, n * c, o[k]).reshape(n, c)
    d = dict(meta=m, P=f('position', np.float32, 3).astype(np.float64), N=f('normal', np.int8, 4)[:, :3].astype(np.float64) / 127.0,
             si=f('skinIndex', np.uint8, 4).astype(np.int64), sw=f('skinWeight', np.uint8, 4).astype(np.float64) / 255.0,
             T=np.frombuffer(b, np.uint16, ni, o['index']).reshape(-1, 3).astype(np.int64),
             cpos=f('cpos', np.int16, 4).astype(np.float64) / 32767.0 * m.get('cpScale', 4.0),
             jelly=f('jelly', np.uint8, 4).astype(np.float64) / 255.0, fill=f('fill', np.uint8, 4).astype(np.float64) / 255.0, mat=f('mat', np.uint8, 4).astype(np.float64) / 255.0)
    if 'uv' in o: d['uv'] = f('uv', np.uint16, 2).astype(np.float64) / 65535.0
    if 'tex' in o and m.get('texLen'): d['tex'] = b[o['tex']:o['tex'] + m['texLen']]
    return d
def weights_dense(d, nb):
    W = np.zeros((len(d['P']), nb)); np.add.at(W, (np.repeat(np.arange(len(d['P'])), 4), d['si'].ravel()), d['sw'].ravel()); return W
def write(base, meta, P, N, si, sw, T, cpos, jelly, fill, mat, uv=None, tex=None, texMime='image/webp', texRes=None, cpScale=4.0):
    n = len(P); q8 = lambda a: np.clip(np.round(np.asarray(a, np.float64) * 255), 0, 255).astype(np.uint8)
    Nq = np.zeros((n, 4), np.int8); Nn = N / np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-12); Nq[:, :3] = np.clip(np.round(Nn * 127), -127, 127).astype(np.int8)
    wq = np.round(np.asarray(sw) * 255).astype(np.int32); wq[:, 0] += 255 - wq.sum(1); wq = np.clip(wq, 0, 255).astype(np.uint8)
    cq = np.clip(np.round(np.asarray(cpos) / cpScale * 32767), -32767, 32767).astype(np.int16)
    assert T.max() < 65536 and n < 65536
    parts = [('position', np.asarray(P, np.float32)), ('normal', Nq), ('skinIndex', np.asarray(si, np.uint8)), ('skinWeight', wq), ('index', np.asarray(T, np.uint16).ravel()),
             ('cpos', cq), ('jelly', q8(jelly)), ('fill', q8(fill)), ('mat', q8(mat))]
    if uv is not None: parts.append(('uv', np.clip(np.round(np.asarray(uv) * 65535), 0, 65535).astype(np.uint16)))
    off = {}; o = 0; blobs = []
    for k, a in parts:
        bb = a.tobytes(); off[k] = o; blobs.append((o, bb)); o += len(bb); o += (-o) % 4
    if tex is not None: off['tex'] = o; blobs.append((o, tex)); o += len(tex); o += (-o) % 4
    buf = bytearray(o)
    for of, bb in blobs: buf[of:of + len(bb)] = bb
    meta = dict(meta); meta.update({'fmt': 'axo7', 'n': int(n), 'ni': int(np.asarray(T).size), 'i32': False, 'off7': off, 'cpScale': cpScale,
                                    'bbox': [np.asarray(P).min(0).round(4).tolist(), np.asarray(P).max(0).round(4).tolist()]})
    if tex is not None: meta.update({'texLen': len(tex), 'texMime': texMime, 'texRes': texRes})
    else: [meta.pop(k, None) for k in ('texLen', 'texMime', 'texRes')]
    open(base + '.bin', 'wb').write(bytes(buf)); json.dump(meta, open(base + '.json', 'w'))
    return len(buf)
