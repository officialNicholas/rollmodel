import json, struct, sys, io, numpy as np
from PIL import Image
D = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo/'
CT = {5126: np.float32, 5125: np.uint32, 5123: np.uint16, 5121: np.uint8}; NC = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}
def load(p):
    b = open(p, 'rb').read(); o = 12; js = bn = None
    while o < len(b):
        cl, ct = struct.unpack('<II', b[o:o+8]); d = b[o+8:o+8+cl]
        if ct == 0x4E4F534A: js = json.loads(d)
        else: bn = d
        o += 8 + cl
    return js, bn
def acc(j, bn, i):
    a = j['accessors'][i]; bv = j['bufferViews'][a['bufferView']]; off = bv.get('byteOffset', 0) + a.get('byteOffset', 0); n = a['count'] * NC[a['type']]
    return np.frombuffer(bn, CT[a['componentType']], n, off).reshape(a['count'], NC[a['type']]) if NC[a['type']] > 1 else np.frombuffer(bn, CT[a['componentType']], n, off)
for nm in ('stand', 'crawl'):
    j, bn = load(D + 'in/' + nm + '.glb'); pr = j['meshes'][0]['primitives'][0]
    P = acc(j, bn, pr['attributes']['POSITION']).copy(); N = acc(j, bn, pr['attributes']['NORMAL']).copy(); UV = acc(j, bn, pr['attributes']['TEXCOORD_0']).copy(); I = acc(j, bn, pr['indices']).astype(np.uint32).copy()
    np.savez(D + nm + '_mesh.npz', P=P, N=N, UV=UV, I=I)
    for k, im in enumerate(j['images']):
        bv = j['bufferViews'][im['bufferView']]; data = bn[bv.get('byteOffset', 0): bv.get('byteOffset', 0) + bv['byteLength']]
        img = Image.open(io.BytesIO(data)); print(nm, 'image', k, img.size, img.mode)
        img.save(D + f'{nm}_tex{k}.png')
    print(nm, 'verts', len(P), 'tris', len(I) // 3, 'bbox', P.min(0).round(3), P.max(0).round(3))
