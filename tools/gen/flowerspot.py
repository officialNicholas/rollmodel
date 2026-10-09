# where the flower can sit just above its left ear without touching it: candidates round the head (yaw, pitch from the head's middle), the
# spot on the skin and how far it is from the nearest bit of ear
import base64, struct, json, math, sys
import numpy as np
PACK = '/home/claude/slime-pack.txt'
b = base64.b64decode(open(PACK).read().strip()); n = struct.unpack('<I', b[4:8])[0]; J = json.loads(b[8:8 + n]); B = b[8 + n:]
M = J['meshes']['slime']; nv = M['v']; mn = np.array(M['mn']); mx = np.array(M['mx'])
P = np.frombuffer(B, dtype='<u2', count=nv * 3, offset=M['pos']).reshape(-1, 3).astype(float) / 65535 * (mx - mn) + mn
I = np.frombuffer(B, dtype='<u2', count=M['i'], offset=M['idx']).reshape(-1, 3).astype(int)
RIG = np.frombuffer(B, dtype='u1', count=nv * 4, offset=M['rig']).reshape(-1, 4)
meta = J['meta']['slime']; HC = np.array(meta['head'][:3])
V0, V1, V2 = P[I[:, 0]], P[I[:, 1]], P[I[:, 2]]; E1, E2 = V1 - V0, V2 - V0; FN = np.cross(E1, E2); FN /= np.linalg.norm(FN, axis=1, keepdims=True) + 1e-12
def cast(d):
    d = d / np.linalg.norm(d); h = np.cross(d, E2); a = (E1 * h).sum(1); ok = np.abs(a) > 1e-9; f = np.where(ok, 1 / np.where(ok, a, 1), 0)
    s = HC - V0; u = f * (s * h).sum(1); q = np.cross(s, E1); v = f * (q * d).sum(1); t = f * (E2 * q).sum(1)
    hit = ok & (u >= 0) & (v >= 0) & (u + v <= 1) & (t > 1e-4)
    t2 = np.where(hit, t, 1e9); k = t2.argmin(); nrm = FN[k] if (FN[k] * d).sum() > 0 else -FN[k]
    return t2[k], nrm
def dirOf(psi, th): psi, th = math.radians(psi), math.radians(th); return np.array([math.sin(psi) * math.cos(th), math.sin(th), math.cos(psi) * math.cos(th)])
ear = P[(RIG[:, 1] > 25) & (P[:, 0] < 0)]  # the left ear's verts
print('left ear verts', len(ear), 'ear top y', round(ear[:, 1].max(), 3))
out = []
for yaw in range(-50, -125, -5):
    for pit in range(30, 80, 4):
        d = dirOf(yaw, pit); t, nrm = cast(d); p = HC + d * t; dist = np.linalg.norm(ear - p, axis=1).min()
        out.append((yaw, pit, round(float(dist), 3), [round(float(x), 4) for x in (p - HC)], [round(float(x), 4) for x in (nrm + d) / np.linalg.norm(nrm + d)]))
cur = json.loads(sys.argv[1]) if len(sys.argv) > 1 else None
if cur: p = HC + np.array(cur); print('current spot: distance to ear', round(float(np.linalg.norm(ear - p, axis=1).min()), 3))
for o in out:
    if o[2] > 0.16 and o[2] < 0.24: print(o)
for (yaw, pit) in [(-72, 60), (-75, 62), (-68, 60)]:
    d = dirOf(yaw, pit); t, nrm = cast(d); p = HC + d * t; dist = np.linalg.norm(ear - p, axis=1).min()
    print('PICK', yaw, pit, round(float(dist), 3), json.dumps({'p': [round(float(x), 4) for x in (p - HC)], 'n': [round(float(x), 4) for x in (nrm + d) / np.linalg.norm(nrm + d)]}))
