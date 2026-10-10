#!/usr/bin/env python3
"""A GLB (one textured primitive) to a wear-pack entry: positions quantized to the box, normals, smoothed normals for the ink outline, uvs, indices; the color and metal-rough maps as small jpegs. Usage: glb2pack.py in.glb out.json [--center] [--tex 512] [--mr 256]"""
import sys, struct, json, base64, io
import numpy as np
from PIL import Image
src, out = sys.argv[1], sys.argv[2]; center = '--center' in sys.argv
tex = int(sys.argv[sys.argv.index('--tex') + 1]) if '--tex' in sys.argv else 512; mrs = int(sys.argv[sys.argv.index('--mr') + 1]) if '--mr' in sys.argv else 256
b = open(src, 'rb').read(); cl = struct.unpack('<I', b[12:16])[0]; j = json.loads(b[20:20 + cl]); bin0 = 28 + cl
acc, bv = j['accessors'], j['bufferViews']
def arr(ai):
    a = acc[ai]; v = bv[a['bufferView']]; off = bin0 + v['byteOffset'] + a.get('byteOffset', 0); dt = {5126: '<f4', 5123: '<u2', 5125: '<u4', 5121: 'u1'}[a['componentType']]; nc = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3}[a['type']]
    return np.frombuffer(b, dtype=dt, count=a['count'] * nc, offset=off).reshape(a['count'], nc).astype(np.float64 if dt == '<f4' else np.int64)
pr = j['meshes'][0]['primitives'][0]
P = arr(pr['attributes']['POSITION']); N = arr(pr['attributes']['NORMAL']); UV = arr(pr['attributes']['TEXCOORD_0']); IX = arr(pr['indices']).reshape(-1)
if center: P = P - (P.min(0) + P.max(0)) / 2
if '--floor' in sys.argv: P = P - [(P.min(0)[0] + P.max(0)[0]) / 2, P.min(0)[1], (P.min(0)[2] + P.max(0)[2]) / 2]  # (centred, standing on y = 0, as the hats are)
n = len(P); mn, mx = P.min(0), P.max(0)
# smoothed normals: the average over every vertex that shares a position (so the outline shell has no cracks)
key = np.round(P, 5); _, inv = np.unique(key, axis=0, return_inverse=True); inv = inv.reshape(-1)
NI = np.zeros_like(N); np.add.at(NI, inv, N); NI = NI[inv]; NI /= np.maximum(1e-9, np.linalg.norm(NI, axis=1))[:, None]
qp = np.round((P - mn) / np.maximum(1e-9, mx - mn) * 65535).astype(np.uint16)
qn = np.zeros((n, 4), np.int8); qn[:, :3] = np.clip(np.round(N * 127), -127, 127); qi = np.zeros((n, 4), np.int8); qi[:, :3] = np.clip(np.round(NI * 127), -127, 127)
umn, umx = UV.min(0), UV.max(0); qu = np.round((UV - umn) / np.maximum(1e-9, umx - umn) * 65535).astype(np.uint16)
ix = IX.astype(np.uint16)
buf = bytearray(qp.tobytes()); o = n * 6; pad = (4 - o % 4) % 4; buf += b'\0' * pad
buf += qn.tobytes() + qi.tobytes() + qu.tobytes() + ix.tobytes()
def jpg(idx, size, q):
    im = j['images'][idx]; v = bv[im['bufferView']]; d = b[bin0 + v['byteOffset']:bin0 + v['byteOffset'] + v['byteLength']]
    img = Image.open(io.BytesIO(d)).convert('RGB'); img.thumbnail((size, size), Image.LANCZOS); bo = io.BytesIO(); img.save(bo, 'JPEG', quality=q, optimize=True); return base64.b64encode(bo.getvalue()).decode()
mat = j['materials'][pr['material']]['pbrMetallicRoughness']
col = jpg(j['textures'][mat['baseColorTexture']['index']]['source'], tex, 82); mr = jpg(j['textures'][mat['metallicRoughnessTexture']['index']]['source'], mrs, 70) if 'metallicRoughnessTexture' in mat else None
entry = { 'n': n, 'ni': len(ix), 'mn': [round(float(x), 5) for x in mn], 'mx': [round(float(x), 5) for x in mx], 'umn': [round(float(x), 6) for x in umn], 'umx': [round(float(x), 6) for x in umx], 'b': base64.b64encode(bytes(buf)).decode(), 'col': col }
if mr: entry['mr'] = mr
json.dump(entry, open(out, 'w')); print('verts', n, 'tris', len(ix) // 3, 'bounds', entry['mn'], entry['mx'], 'bytes', len(json.dumps(entry)))
