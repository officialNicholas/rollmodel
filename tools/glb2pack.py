#!/usr/bin/env python3
"""A GLB to a pack entry for the game.

Default (the wear packs): one textured primitive; positions quantized to the box, normals, smoothed normals for the ink outline, uvs,
indices; the color and metal-rough maps as small jpegs.
  glb2pack.py in.glb out.json [--center] [--floor] [--tex 512] [--mr 256]

--v2 (the stage models, smaller): every primitive of every mesh node, with the node transforms applied, merged into one; positions
quantized to the box (u16), uvs (u16), normals octahedral (2 x i8), indices as zigzag varint deltas (vertices renumbered in the order
the triangles first use them, so the steps are small), an optional smoothed normal for the ink shell (--ink), the maps as webp (or
jpeg) with an optional normal map (--nrm size) and metal-rough map (--mr size). A rigged GLB keeps its skin (--skin): four joints and
weights per vertex (u8), the joint names, parents, rest pose and inverse bind matrices.
  glb2pack.py in.glb out.json --v2 [--floor|--center] [--tex 512] [--nrm 256] [--mr 0] [--ink] [--skin] [--jpeg] [--q 80] [--tint r,g,b]
Layout of b (v2): pos n*6, pad to 4, uv n*4, nrm n*2, [ink n*2], [joints n*4, weights n*4], then the index bytes (ib long)."""
import sys, struct, json, base64, io
import numpy as np
from PIL import Image

A = sys.argv
def opt(k, d):
    return A[A.index(k) + 1] if k in A else d

src, out = A[1], A[2]
b = open(src, 'rb').read(); cl = struct.unpack('<I', b[12:16])[0]; j = json.loads(b[20:20 + cl]); bin0 = 28 + cl
acc, bv = j['accessors'], j['bufferViews']
NC = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}
DT = {5126: '<f4', 5123: '<u2', 5125: '<u4', 5121: 'u1', 5122: '<i2', 5120: 'i1'}

def arr(ai, keep=False):
    a = acc[ai]; v = bv[a['bufferView']]; off = bin0 + v.get('byteOffset', 0) + a.get('byteOffset', 0); dt = DT[a['componentType']]; nc = NC[a['type']]
    stride = v.get('byteStride'); isz = np.dtype(dt).itemsize
    if stride and stride != isz * nc:
        raw = np.frombuffer(b, dtype=np.uint8, count=stride * (a['count'] - 1) + isz * nc, offset=off)
        x = np.stack([np.frombuffer(raw[i * stride:i * stride + isz * nc].tobytes(), dtype=dt) for i in range(a['count'])])
    else:
        x = np.frombuffer(b, dtype=dt, count=a['count'] * nc, offset=off).reshape(a['count'], nc)
    if keep: return x
    if a.get('normalized') and dt != '<f4': return x.astype(np.float64) / float(np.iinfo(np.dtype(dt)).max)
    return x.astype(np.float64) if dt == '<f4' else x.astype(np.int64)

def img_bytes(idx):
    im = j['images'][idx]; v = bv[im['bufferView']]; return b[bin0 + v.get('byteOffset', 0):bin0 + v.get('byteOffset', 0) + v['byteLength']]

if '--v2' not in A:
    # ---- the original wear-pack entry, unchanged ----
    center = '--center' in A; tex = int(opt('--tex', 512)); mrs = int(opt('--mr', 256))
    pr = j['meshes'][0]['primitives'][0]
    P = arr(pr['attributes']['POSITION']); N = arr(pr['attributes']['NORMAL']); UV = arr(pr['attributes']['TEXCOORD_0']); IX = arr(pr['indices']).reshape(-1)
    if center: P = P - (P.min(0) + P.max(0)) / 2
    if '--floor' in A: P = P - [(P.min(0)[0] + P.max(0)[0]) / 2, P.min(0)[1], (P.min(0)[2] + P.max(0)[2]) / 2]  # (centred, standing on y = 0, as the hats are)
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
        img = Image.open(io.BytesIO(img_bytes(idx))).convert('RGB'); img.thumbnail((size, size), Image.LANCZOS); bo = io.BytesIO(); img.save(bo, 'JPEG', quality=q, optimize=True); return base64.b64encode(bo.getvalue()).decode()
    mat = j['materials'][pr['material']]['pbrMetallicRoughness']
    col = jpg(j['textures'][mat['baseColorTexture']['index']]['source'], tex, 82); mr = jpg(j['textures'][mat['metallicRoughnessTexture']['index']]['source'], mrs, 70) if 'metallicRoughnessTexture' in mat else None
    entry = { 'n': n, 'ni': len(ix), 'mn': [round(float(x), 5) for x in mn], 'mx': [round(float(x), 5) for x in mx], 'umn': [round(float(x), 6) for x in umn], 'umx': [round(float(x), 6) for x in umx], 'b': base64.b64encode(bytes(buf)).decode(), 'col': col }
    if mr: entry['mr'] = mr
    json.dump(entry, open(out, 'w')); print('verts', n, 'tris', len(ix) // 3, 'bounds', entry['mn'], entry['mx'], 'bytes', len(json.dumps(entry)))
    sys.exit(0)

# ---------------- v2: the stage models ----------------
tex = int(opt('--tex', 512)); nrs = int(opt('--nrm', 0)); mrs = int(opt('--mr', 0)); q = int(opt('--q', 80)); jpeg = '--jpeg' in A; want_skin = '--skin' in A; want_ink = '--ink' in A

def quat_mat(qx, qy, qz, qw):
    return np.array([[1 - 2 * (qy * qy + qz * qz), 2 * (qx * qy - qz * qw), 2 * (qx * qz + qy * qw)], [2 * (qx * qy + qz * qw), 1 - 2 * (qx * qx + qz * qz), 2 * (qy * qz - qx * qw)], [2 * (qx * qz - qy * qw), 2 * (qy * qz + qx * qw), 1 - 2 * (qx * qx + qy * qy)]])

def local(nd):
    if 'matrix' in nd: return np.array(nd['matrix'], dtype=np.float64).reshape(4, 4).T
    M = np.eye(4); t = nd.get('translation', [0, 0, 0]); r = nd.get('rotation', [0, 0, 0, 1]); s = nd.get('scale', [1, 1, 1])
    M[:3, :3] = quat_mat(*r) * np.array(s)[None, :]; M[:3, 3] = t; return M

nodes = j.get('nodes', []); parent = {}
for i, nd in enumerate(nodes):
    for c in nd.get('children', []): parent[c] = i
def world(i):
    M = local(nodes[i])
    while i in parent: i = parent[i]; M = local(nodes[i]) @ M
    return M

# every mesh node's primitives, merged (a skinned mesh stays in its bind space: the skin's matrices carry it)
Ps, Ns, UVs, IXs, Js, Ws, mats = [], [], [], [], [], [], []; base = 0
for ni_, nd in enumerate(nodes):
    if 'mesh' not in nd: continue
    skinned = 'skin' in nd and want_skin; M = np.eye(4) if skinned else world(ni_)
    for pr in j['meshes'][nd['mesh']]['primitives']:
        at = pr['attributes']; P = arr(at['POSITION']); N = arr(at['NORMAL']) if 'NORMAL' in at else None
        UV = arr(at['TEXCOORD_0']) if 'TEXCOORD_0' in at else np.zeros((len(P), 2)); IX = arr(pr['indices']).reshape(-1) if 'indices' in pr else np.arange(len(P))
        P = P @ M[:3, :3].T + M[:3, 3]
        if N is None:
            N = np.zeros_like(P); tri = IX.reshape(-1, 3); fn = np.cross(P[tri[:, 1]] - P[tri[:, 0]], P[tri[:, 2]] - P[tri[:, 0]])
            for k in range(3): np.add.at(N, tri[:, k], fn)
        else: N = N @ np.linalg.inv(M[:3, :3]).T
        N /= np.maximum(1e-9, np.linalg.norm(N, axis=1))[:, None]
        Ps.append(P); Ns.append(N); UVs.append(UV); IXs.append(IX + base); mats.append(pr.get('material', 0)); base += len(P)
        if want_skin:
            Js.append(arr(at['JOINTS_0'], keep=True).astype(np.int64)); Ws.append(arr(at['WEIGHTS_0']))
P = np.concatenate(Ps); N = np.concatenate(Ns); UV = np.concatenate(UVs); IX = np.concatenate(IXs)
if len(set(mats)) > 1: print('note: %d materials; the first one\'s maps are used' % len(set(mats)))
shift = np.zeros(3)
if '--center' in A: shift = (P.min(0) + P.max(0)) / 2
if '--floor' in A: shift = np.array([(P.min(0)[0] + P.max(0)[0]) / 2, P.min(0)[1], (P.min(0)[2] + P.max(0)[2]) / 2])
if not want_skin: P = P - shift  # (a skinned mesh stays in its bind space; the game moves its holder by -shift instead)
# renumber the vertices in the order the triangles first use them (the index steps stay small; unused vertices go)
order = []; seen = np.full(len(P), -1, np.int64)
for v in IX:
    if seen[v] < 0: seen[v] = len(order); order.append(v)
order = np.array(order); IX = seen[IX]; P = P[order]; N = N[order]; UV = UV[order]
if want_skin: JJ = np.concatenate(Js)[order]; WW = np.concatenate(Ws)[order]
n = len(P); mn, mx = P.min(0), P.max(0)

def octa(v):
    v = v / np.maximum(1e-9, np.abs(v).sum(1))[:, None]; p = v[:, :2].copy(); neg = v[:, 2] < 0
    sx = np.where(p[neg, 0] >= 0, 1.0, -1.0); sy = np.where(p[neg, 1] >= 0, 1.0, -1.0); ox = p[neg, 0].copy()
    p[neg, 0] = (1 - np.abs(p[neg, 1])) * sx; p[neg, 1] = (1 - np.abs(ox)) * sy
    return np.clip(np.round(p * 127), -127, 127).astype(np.int8)

qp = np.round((P - mn) / np.maximum(1e-9, mx - mn) * 65535).astype(np.uint16)
umn, umx = UV.min(0), UV.max(0); qu = np.round((UV - umn) / np.maximum(1e-9, umx - umn) * 65535).astype(np.uint16)
buf = bytearray(qp.tobytes()); buf += b'\0' * ((4 - len(buf) % 4) % 4); lay = {'pos': 0, 'uv': len(buf)}; buf += qu.tobytes()
lay['nrm'] = len(buf); buf += octa(N).tobytes()
if want_ink:
    key = np.round(P, 4); _, inv = np.unique(key, axis=0, return_inverse=True); inv = inv.reshape(-1)
    NI = np.zeros_like(N); np.add.at(NI, inv, N); NI = NI[inv]; NI /= np.maximum(1e-9, np.linalg.norm(NI, axis=1))[:, None]
    lay['ink'] = len(buf); buf += octa(NI).tobytes()
if want_skin:
    WW = np.maximum(WW, 0); WW /= np.maximum(1e-9, WW.sum(1))[:, None]; qw = np.floor(WW * 255).astype(np.int64)
    rem = 255 - qw.sum(1); top = np.argmax(WW, 1); qw[np.arange(n), top] += rem  # (the weights sum to 255 exactly)
    lay['joints'] = len(buf); buf += JJ.astype(np.uint8).tobytes(); lay['weights'] = len(buf); buf += qw.astype(np.uint8).tobytes()
# the indices: zigzag deltas, 7 bits a byte (the top bit says another byte follows)
ib = bytearray(); prev = 0
for v in IX.tolist():
    d = v - prev; prev = v; z = (d << 1) ^ (d >> 63)
    while z >= 0x80: ib.append((z & 0x7F) | 0x80); z >>= 7
    ib.append(z)
lay['idx'] = len(buf); buf += ib

def enc(idx, size, kind):
    img = Image.open(io.BytesIO(img_bytes(idx))).convert('RGB'); img.thumbnail((size, size), Image.LANCZOS)
    if kind == 'col' and '--tint' in A:
        t = [float(x) for x in opt('--tint', '1,1,1').split(',')]; a = np.asarray(img).astype(np.float64) * np.array(t)[None, None, :]; img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    bo = io.BytesIO()
    if jpeg: img.save(bo, 'JPEG', quality=q, optimize=True)
    else: img.save(bo, 'WEBP', quality=q, method=6)
    return base64.b64encode(bo.getvalue()).decode()

mat = j['materials'][mats[0]] if j.get('materials') else {}; pbr = mat.get('pbrMetallicRoughness', {})
entry = {'v': 2, 'n': n, 'ni': len(IX), 'mn': [round(float(x), 5) for x in mn], 'mx': [round(float(x), 5) for x in mx], 'umn': [round(float(x), 6) for x in umn], 'umx': [round(float(x), 6) for x in umx],
         'lay': lay, 'ib': len(ib), 'b': base64.b64encode(bytes(buf)).decode(), 'mime': 'image/jpeg' if jpeg else 'image/webp'}
if 'baseColorTexture' in pbr: entry['col'] = enc(j['textures'][pbr['baseColorTexture']['index']]['source'], tex, 'col')
if nrs and 'normalTexture' in mat: entry['nrm'] = enc(j['textures'][mat['normalTexture']['index']]['source'], nrs, 'nrm')
if mrs and 'metallicRoughnessTexture' in pbr: entry['mr'] = enc(j['textures'][pbr['metallicRoughnessTexture']['index']]['source'], mrs, 'mr')
if want_skin:
    sk = j['skins'][0]; jn = sk['joints']; ibm = arr(sk['inverseBindMatrices']).reshape(-1, 16) if 'inverseBindMatrices' in sk else np.tile(np.eye(4).T.reshape(16), (len(jn), 1))
    entry['skel'] = {'names': [nodes[i].get('name', 'j%d' % i) for i in jn], 'parent': [jn.index(parent[i]) if i in parent and parent[i] in jn else -1 for i in jn],
                     'rest': [[round(float(x), 6) for x in (nodes[i].get('translation', [0, 0, 0]) + nodes[i].get('rotation', [0, 0, 0, 1]) + nodes[i].get('scale', [1, 1, 1]))] for i in jn],
                     'ibm': [[round(float(x), 6) for x in m] for m in ibm]}
    # the skeleton's root may sit under transformed nodes (an armature node): its world matrix, so the bones end up where the mesh is
    r0 = jn[[k for k in range(len(jn)) if entry['skel']['parent'][k] == -1][0]]
    entry['skel']['shift'] = [round(float(x), 6) for x in shift]
    entry['skel']['rootParent'] = [round(float(x), 6) for x in (world(parent[r0]).T.reshape(16) if r0 in parent else np.eye(4).reshape(16))]
json.dump(entry, open(out, 'w')); print('verts', n, 'tris', len(IX) // 3, 'bounds', entry['mn'], entry['mx'], 'bytes', len(json.dumps(entry)), 'mesh', len(entry['b']), 'idx', len(ib), 'col', len(entry.get('col', '')), 'nrm', len(entry.get('nrm', '')))
