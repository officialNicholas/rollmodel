# the pirate eye patch and its strap, fitted to the slime's own head (from the pack's mesh): a domed patch over its right eye (where the
# face sheet draws it) and a strap from it up across the forehead, over the crown between the ears and back down to the patch's far side.
# Everything is in the head's own frame (offsets from the head's middle, in model units). Also: where the flower sits by the ear
import base64, struct, json, math, sys
import numpy as np
PACK = '/home/claude/slime-pack.txt'; OUT = sys.argv[1]
b = base64.b64decode(open(PACK).read().strip()); n = struct.unpack('<I', b[4:8])[0]; J = json.loads(b[8:8 + n]); B = b[8 + n:]
M = J['meshes']['slime']; nv = M['v']; mn = np.array(M['mn']); mx = np.array(M['mx'])
P = np.frombuffer(B, dtype='<u2', count=nv * 3, offset=M['pos']).reshape(-1, 3).astype(float) / 65535 * (mx - mn) + mn
I = np.frombuffer(B, dtype='<u2', count=M['i'], offset=M['idx']).reshape(-1, 3).astype(int)
RIG = np.frombuffer(B, dtype='u1', count=nv * 4, offset=M['rig']).reshape(-1, 4)
meta = J['meta']['slime']; HC = np.array(meta['head'][:3]); FY = meta['face'][1]; FX = meta['face'][0]
V0, V1, V2 = P[I[:, 0]], P[I[:, 1]], P[I[:, 2]]; E1, E2 = V1 - V0, V2 - V0; FN = np.cross(E1, E2); FN /= np.linalg.norm(FN, axis=1, keepdims=True) + 1e-12
def cast(d):
    # nearest hit along the ray from the head's middle (the first time it leaves the head), and the face normal there
    d = d / np.linalg.norm(d); h = np.cross(d, E2); a = (E1 * h).sum(1); ok = np.abs(a) > 1e-9; f = np.where(ok, 1 / np.where(ok, a, 1), 0)
    s = HC - V0; u = f * (s * h).sum(1); q = np.cross(s, E1); v = f * (q * d).sum(1); t = f * (E2 * q).sum(1)
    hit = ok & (u >= 0) & (v >= 0) & (u + v <= 1) & (t > 1e-4)
    if not hit.any(): return None, None
    t2 = np.where(hit, t, 1e9); k = t2.argmin(); nrm = FN[k] if (FN[k] * d).sum() > 0 else -FN[k]
    return t2[k], nrm
def dirOf(psi, th): psi, th = math.radians(psi), math.radians(th); return np.array([math.sin(psi) * math.cos(th), math.sin(th), math.cos(psi) * math.cos(th)])
def earAt(d):
    # how much ear is near where this ray lands (to keep the strap off the ears)
    t, _ = cast(d); p = HC + d / np.linalg.norm(d) * t; k = np.linalg.norm(P - p, axis=1).argmin(); return RIG[k, 1] / 255, t
verts, norms, idx = [], [], []
def addV(p, nrm): verts.append([float(x) for x in p]); norms.append([float(x) for x in nrm]); return len(verts) - 1
# ---- the patch: over the right eye (the face sheet's eye: yaw 0.4, pitch 0.16 in face units) ----
E = dirOf(math.degrees(0.4 * FY), math.degrees(FX + 0.16 * FY)); R = np.cross([0, 1, 0], E); R /= np.linalg.norm(R); R = -R if R[0] < 0 else R; U = np.cross(E, R); U = U if U[1] > 0 else -U
A_, B_ = 0.37, 0.385   # half-widths, radians in the tangent plane (the eye is 0.26 x 0.28)
def outline(t):
    c, s = math.cos(t), math.sin(t); x = A_ * math.copysign(abs(c) ** 0.75, c) * (1 - 0.18 * max(0.0, -s)); y = B_ * math.copysign(abs(s) ** 0.85, s) * (1.0 if s > 0 else 0.92); return x, y - 0.02
NT, NRAD = 40, 7; BASE, DOME = 0.012, 0.022
grid = []
for i in range(NRAD + 1):
    row = []; rho = i / NRAD
    for j in range(NT):
        t = j / NT * 2 * math.pi; x, y = outline(t); d = E + R * x * rho + U * y * rho; d /= np.linalg.norm(d); tt, nrm = cast(d)
        off = BASE + DOME * (1 - rho * rho) ** 0.7; row.append(HC + d * (tt + off) - HC)
        if i == 0: break
    grid.append(row)
# smooth normals for the dome: from the grid itself
def gp(i, j): return grid[i][0] if i == 0 else grid[i][j % NT]
base0 = len(verts); ids = {}
for i in range(NRAD + 1):
    for j in range(1 if i == 0 else NT):
        p = gp(i, j); ids[(i, j)] = addV(p, [0, 0, 0])
for i in range(NRAD):
    for j in range(NT):
        a = ids[(0, 0)] if i == 0 else ids[(i, j)]; b2 = ids[(0, 0)] if i == 0 else ids[(i, (j + 1) % NT)]; c = ids[(i + 1, j)]; d = ids[(i + 1, (j + 1) % NT)]
        if i == 0: idx += [a, c, d]
        else: idx += [a, c, d, a, d, b2]
# the side wall: the rim down into the skin
rim0 = len(verts)
for j in range(NT):
    t = j / NT * 2 * math.pi; x, y = outline(t); d = E + R * x + U * y; d /= np.linalg.norm(d); tt, nrm = cast(d)
    out = R * x + U * y; out = out - E * (out @ E); out /= np.linalg.norm(out) + 1e-9
    addV(gp(NRAD, j), out); addV(d * (tt - 0.006), out)
for j in range(NT):
    a, b2 = rim0 + 2 * j, rim0 + 2 * ((j + 1) % NT); idx += [a, a + 1, b2 + 1, a, b2 + 1, b2]
patchEnd = len(verts); patchTris = len(idx) // 3
# ---- the strap: a loop round the head (yaw, pitch in degrees), from under the patch up across the forehead and over the crown ----
CP = [(20, 8), (8, 20), (-6, 29), (-20, 37), (-38, 46), (-60, 55), (-90, 62), (-125, 65), (-180, 64), (-235, 63), (-265, 60), (-292, 54), (-308, 44), (-318, 32), (-326, 20), (-334, 12), (-340, 8)]
# (the loop closes back at 20 = -340)
def catmull(pts, n):
    out = []; m = len(pts)
    for i in range(m - 1):
        p0 = pts[max(0, i - 1)]; p1 = pts[i]; p2 = pts[i + 1]; p3 = pts[min(m - 1, i + 2)]
        for k in range(n):
            t = k / n; t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[c]) + (-p0[c] + p2[c]) * t + (2 * p0[c] - 5 * p1[c] + 4 * p2[c] - p3[c]) * t2 + (-p0[c] + 3 * p1[c] - 3 * p2[c] + p3[c]) * t3) for c in range(2)))
    out.append(pts[-1]); return out
path = catmull(CP, 7); W2, OFF, TH = 0.019, 0.007, 0.011
cen = []; worst = 0
for (ps, th) in path:
    d = dirOf(ps, th); tt, nrm = cast(d); ear, _ = earAt(d); worst = max(worst, ear); cen.append((d * tt, nrm, ear, tt))
print('strap samples', len(cen), 'max ear weight under it', round(worst, 3), 'radius', round(min(c[3] for c in cen), 3), round(max(c[3] for c in cen), 3))
# smooth the radius along the path a little (no bumps from the mesh's facets), then build a flat band with a top and two sides
rs = np.array([c[3] for c in cen]); rs2 = rs.copy()
for _ in range(3): rs2[1:-1] = (rs2[:-2] + rs2[1:-1] * 2 + rs2[2:]) / 4
strap0 = len(verts); CR, COFF, NS6 = 0.0125, 0.016, 8
# a cord (a thin round tube) riding just off the skin
for k, (ps, th) in enumerate(path):
    d = dirOf(ps, th); c = d * rs2[k]; nrm = cen[k][1]; nrm = (nrm + d) / np.linalg.norm(nrm + d)
    nxt = dirOf(*path[min(len(path) - 1, k + 1)]) * rs2[min(len(path) - 1, k + 1)]; prv = dirOf(*path[max(0, k - 1)]) * rs2[max(0, k - 1)]
    tg = nxt - prv; tg /= np.linalg.norm(tg); sd = np.cross(tg, nrm); sd /= np.linalg.norm(sd); up = np.cross(sd, tg)
    ctr = c + nrm * COFF
    for j in range(NS6):
        a = j / NS6 * 2 * math.pi; off = sd * math.cos(a) + up * math.sin(a); addV(ctr + off * CR, off)
for k in range(len(path) - 1):
    a0 = strap0 + NS6 * k; b0 = a0 + NS6
    for j in range(NS6):
        j1 = (j + 1) % NS6; idx += [a0 + j, b0 + j, b0 + j1, a0 + j, b0 + j1, a0 + j1]
# ---- normals: the dome's from its faces (smooth), everything else as set ----
Vn = np.array(verts); Ix = np.array(idx).reshape(-1, 3); Nn = np.array(norms)
acc = np.zeros_like(Vn)
for (a, b2, c) in Ix[:patchTris]:
    fn = np.cross(Vn[b2] - Vn[a], Vn[c] - Vn[a]); acc[a] += fn; acc[b2] += fn; acc[c] += fn
for i in range(base0, rim0):
    l = np.linalg.norm(acc[i]); Nn[i] = acc[i] / l if l > 0 else E
# make sure the dome's normals face out
for i in range(base0, rim0):
    if Nn[i] @ (Vn[i] / np.linalg.norm(Vn[i])) < 0: Nn[i] = -Nn[i]
# the patch's triangles wound to face out
for t in range(patchTris):
    a, b2, c = Ix[t]; fn = np.cross(Vn[b2] - Vn[a], Vn[c] - Vn[a])
    if fn @ Vn[a] < 0: Ix[t] = [a, c, b2]
for t in range(patchTris, len(Ix)):
    a, b2, c = Ix[t]; fn = np.cross(Vn[b2] - Vn[a], Vn[c] - Vn[a]); ctr = (Vn[a] + Vn[b2] + Vn[c]) / 3
    if fn @ (Nn[a] + Nn[b2] + Nn[c]) < 0: Ix[t] = [a, c, b2]
# outline normals: averaged over each spot
key = lambda p: (round(p[0], 4), round(p[1], 4), round(p[2], 4)); sm = {}
for p, nn in zip(Vn, Nn): s = sm.setdefault(key(p), np.zeros(3)); s += nn
NS = np.array([sm[key(p)] / (np.linalg.norm(sm[key(p)]) + 1e-9) for p in Vn])
# ---- the flower's spot: in front of the left ear's root, a little up ----
fd = dirOf(-63, 37); ft, fnrm = cast(fd); fl = {'p': [round(float(x), 4) for x in fd * ft], 'n': [round(float(x), 4) for x in (fnrm + fd) / np.linalg.norm(fnrm + fd)]}
fd2 = dirOf(-68, 23); ft2, fnrm2 = cast(fd2); fl2 = {'p': [round(float(x), 4) for x in fd2 * ft2], 'n': [round(float(x), 4) for x in (fnrm2 + fd2) / np.linalg.norm(fnrm2 + fd2)]}
ear1, _ = earAt(fd); print('flower spot', fl, 'ear weight', round(ear1, 2), 'low spot', fl2)
# pack as the game's asset format (positions quantized to the box, normals and outline normals as bytes, no uvs or maps)
mnb = Vn.min(0); mxb = Vn.max(0); q = lambda v, a, b: max(0, min(65535, round((v - a) / ((b - a) or 1) * 65535)))
blob = bytearray()
for p in Vn: blob += struct.pack('<3H', *[q(p[i], mnb[i], mxb[i]) for i in range(3)])
blob += b'\0' * ((4 - len(blob) % 4) % 4)
for nn in Nn: blob += struct.pack('<4b', *[max(-127, min(127, round(c * 127))) for c in nn], 0)
for nn in NS: blob += struct.pack('<4b', *[max(-127, min(127, round(c * 127))) for c in nn], 0)
for p in Vn: blob += struct.pack('<2H', 0, 0)
for i in Ix.flatten(): blob += struct.pack('<H', int(i))
asset = {'n': len(Vn), 'ni': int(Ix.size), 'mn': [round(float(v), 5) for v in mnb], 'mx': [round(float(v), 5) for v in mxb], 'umn': [0, 0], 'umx': [1, 1], 'b': base64.b64encode(bytes(blob)).decode(), 'split': [int(patchTris * 3)], 'flower': fl, 'flowerLow': fl2}
open(OUT, 'w').write(json.dumps(asset, separators=(',', ':'))); print('patch verts', len(Vn), 'tris', len(Ix), 'patch tris', patchTris, 'json', len(json.dumps(asset)))
