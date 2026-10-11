"""Read and write the axolotl's runtime meshes (fmt axo7: positions f32, normals i8x4, skin u8x4 x2, indices u16, cpos i16x4,
jelly/fill/mat u8x4) as numpy arrays."""
import json, numpy as np
FIELDS = [('position', np.float32, 3), ('normal', np.int8, 4), ('skinIndex', np.uint8, 4), ('skinWeight', np.uint8, 4), ('cpos', np.int16, 4), ('jelly', np.uint8, 4), ('fill', np.uint8, 4), ('mat', np.uint8, 4)]
def load(base):
    meta = json.load(open(base + '.json')); buf = open(base + '.bin', 'rb').read(); n, o = meta['n'], meta['off7']
    d = {'meta': meta, 'buf': bytearray(buf)}
    for k, t, c in FIELDS: d[k] = np.frombuffer(buf, dtype=t, count=n * c, offset=o[k]).reshape(n, c).copy()
    d['index'] = np.frombuffer(buf, dtype=np.uint16, count=meta['ni'], offset=o['index']).copy()
    return d
def save(d, base):
    meta, buf = d['meta'], d['buf']; n, o = meta['n'], meta['off7']
    for k, t, c in FIELDS: a = np.ascontiguousarray(d[k].astype(t)).tobytes(); buf[o[k]:o[k] + len(a)] = a
    a = np.ascontiguousarray(d['index'].astype(np.uint16)).tobytes(); buf[o['index']:o['index'] + len(a)] = a
    open(base + '.bin', 'wb').write(bytes(buf)); json.dump(meta, open(base + '.json', 'w'), separators=(',', ':'))
