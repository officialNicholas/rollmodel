# v7 crawl rig: the symmetric crawl mesh (crawlbuild.py + headmorph.py) refined, in export coordinates, rigged to the shared 73-bone layout.
# Joints are placed on the character's left side from the geometry and mirrored; weights are built for the left half and the midline, then
# mirrored bone-for-bone, so both sides deform identically.
import sys, os, json, time
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2'); sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo3')
import numpy as np
from scipy.spatial import cKDTree
from mesh import Mesh, mirror_map
from refine import refine
from crawlbuild import load_old
O = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo3/'
SC = 1.15; Z0 = 0.75; Y0 = 0.418 * SC          # sym -> export: P * SC + (0, Y0, Z0)
CS = np.array([0.021, 1.19, 0.041]); RS = 0.329  # the stand's face sphere (export)
ORDER = [b['name'] for b in json.load(open('/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2/stand_export.json'))['bones']]
def ss(t): t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)
def unit(v): v = np.asarray(v, float); return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)
def face_cap(P, C, R, yaw_max=50, pmin=-16, pmax=56, band=10):
    """the face region of a head moved exactly onto its sphere (yaw / pitch about C, forward +z), blending out over `band` degrees"""
    d = P - C; r = np.linalg.norm(d, axis=1); u = d / r[:, None]; yaw = np.degrees(np.arctan2(u[:, 0], u[:, 2])); pit = np.degrees(np.arcsin(np.clip(u[:, 1], -1, 1)))
    w = ss((yaw_max - np.abs(yaw)) / band + 1) * ss((pit - pmin) / band + 1) * ss((pmax - pit) / band + 1) * (u[:, 2] > 0) * (np.abs(r - R) < 0.25 * R)
    return P + (C + u * R - P) * w[:, None], w
def geometry():
    """the crawl mesh in export coordinates: head on the stand's shell, the face cap exactly spherical, symmetric, the body refined"""
    z = np.load(O + 'crawl_head.npz', allow_pickle=True); P = z['P'].copy(); T = z['T']; src = z['src']; Cc = z['Cc']; R = float(z['R'])
    z0 = np.load(O + 'crawl_sym.npz', allow_pickle=True); mm = mirror_map(z0['P'])
    P = (P + P[mm] * np.array([-1, 1, 1])) / 2; P[np.abs(z0['P'][:, 0]) < 1e-9, 0] = 0   # exactly symmetric again (the stand shell is not quite)
    P, wcap = face_cap(P, Cc, R)
    # labels from the old crawl rig through the mirror / clip map
    m0, W0, names0, lab0 = load_old(); a = src[:, 0].astype(int); b = src[:, 1].astype(int); u = src[:, 2]; lab = np.where(u < 0.5, lab0[a], lab0[b])
    # refine the body (not the head, gills or digits)
    body = np.array([l in ('trunk', 'tail') or l.startswith(('arm', 'leg')) for l in lab])
    P2, T2, at, par = refine(P, T, 0.045 / SC, mask=body, verbose=False)
    lab2 = list(lab)
    for i in range(len(P), len(P2)):
        pa, pb = par[i]; la, lb = lab2[pa], lab2[pb]; lab2.append(la if la == lb or not la.startswith(('finger', 'toe', 'gill')) else lb)
    lab2 = np.array(lab2)
    Pe = P2 * SC + np.array([0, Y0, Z0]); Ce = Cc * SC + np.array([0, Y0, Z0])
    # sides: the mirrored half carries the left's labels; rename by the side it is on
    def sided(l, x):
        if '.L' in l or '.R' in l: return l.replace('.L', '.R').replace('.R', '.L' if x > 0 else '.R') if True else l
        return l
    lab3 = np.array([(l.replace('.R', '.L') if x > 1e-9 else l.replace('.L', '.R')) if ('.L' in l or '.R' in l) else l for l, x in zip(lab2, Pe[:, 0])])
    print(f'geometry: {len(Pe)} verts, {len(T2)} tris; face centre (export) {Ce.round(3)}; ground y {Pe[:, 1].min():+.3f}')
    np.savez(O + 'crawl7_geo.npz', P=Pe, T=T2, lab=lab3, C=Ce, R=R * SC)
    return Pe, T2, lab3, Ce, R * SC
if __name__ == '__main__':
    t0 = time.time(); P, T, lab, C, R = geometry(); print(f'{time.time() - t0:.1f}s')
    import collections; print(collections.Counter([l for l in lab]).most_common())
    m = Mesh(P, T); mm = mirror_map(P); print('mirror partner self-consistency', np.mean(mm[mm] == np.arange(len(P))))

# ======================== joints ========================
from meshslice import slice_z
def sec_centre(P, T, mask, z, band=0.0):
    """centre of the body section at z (triangles with all vertices in mask): x mid, y mid, and the section's half extents"""
    Tm = T[mask[T].all(1)]; sg = slice_z(P, Tm, z)
    if len(sg) < 3: return None
    q = sg.reshape(-1, 3); return np.array([(q[:, 0].min() + q[:, 0].max()) / 2, (q[:, 1].min() + q[:, 1].max()) / 2, z]), (q.max(0) - q.min(0)) / 2
def limb_line(m, lab, side, kind):
    """ring centroids up a limb from its digits to where it joins the trunk; returns knuckles, wrist, elbow, root, the polyline and the radii"""
    dig = np.array([l.startswith(('finger' if kind == 'arm' else 'toe')) and not l.startswith('toes') and l.endswith('.' + side) for l in lab])
    limb = lab == f'{kind}.{side}'; mask = limb | dig; d = m.geo(np.where(dig)[0], limit=1.2, mask=mask)
    trunkadj = np.zeros(m.n, bool); rows = m.rows(); tr = np.isin(lab, ['trunk', 'head', 'tail'])
    for v in np.where(limb)[0]:
        if any(tr[u] for u in rows[v]): trunkadj[v] = True
    junc = m.P[trunkadj].mean(0); dj = d[trunkadj]; dj = np.median(dj[np.isfinite(dj)])
    pts = []; rad = []
    for t in np.arange(0.0, dj, 0.01):
        sel = limb & np.isfinite(d) & (np.abs(d - t) < 0.008)
        if sel.sum() < 4: continue
        q = m.P[sel]; c = q.mean(0); pts.append(c); rad.append(np.percentile(np.linalg.norm(q - c, axis=1), 70))
    pts = np.array(pts); rad = np.array(rad)
    # smooth the polyline
    for _ in range(4): pts[1:-1] = 0.25 * pts[:-2] + 0.5 * pts[1:-1] + 0.25 * pts[2:]
    knuck = m.P[dig].mean(0)
    cum = np.r_[0, np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))]; Lt = cum[-1]
    # the wrist: the narrowest ring within the first 35% (the palm is wider, the forearm thickens above)
    i0 = np.where(cum <= 0.35 * Lt)[0]; iw = int(i0[np.argmin(rad[i0])]) if len(i0) else 0
    # the elbow / knee: the strongest bend between 30% and 75% of the way from the wrist to the root
    tang = unit(np.gradient(pts, axis=0)); bend = np.zeros(len(pts))
    for i in range(2, len(pts) - 2): bend[i] = np.degrees(np.arccos(np.clip(tang[i - 2] @ tang[i + 2], -1, 1)))
    lo = cum[iw] + 0.3 * (Lt - cum[iw]); hi = cum[iw] + 0.75 * (Lt - cum[iw]); cand = np.where((cum >= lo) & (cum <= hi))[0]
    ie = int(cand[np.argmax(bend[cand])]) if len(cand) else (iw + len(pts)) // 2
    root_ring = pts[-1]; rootdir = unit(pts[-1] - pts[max(0, len(pts) - 6)])
    root = root_ring + rootdir * 0.35 * rad[-1]   # a little inside the body, along the limb's axis
    return dict(knuck=knuck, wrist=pts[iw], elbow=pts[ie], root=root, pts=pts, rad=rad, cum=cum, iw=iw, ie=ie, junc=junc, bend=bend[ie])
def digit_frame(m, vs, palm_c):
    q = m.P[vs]; dp = np.linalg.norm(q - palm_c, axis=1); o = np.argsort(dp); base = q[o[:max(3, len(vs) // 5)]].mean(0); tip = q[o[-max(3, len(vs) // 6):]].mean(0)
    ax = unit(tip - base); L = float(((q - base) @ ax).max()); return base, base + ax * L * 0.48, base + ax * L
def joints(P, T, lab, C, R):
    m = Mesh(P, T); J = {}; END = {}; PAR = {}
    def add(k, p, par, end=None):
        J[k] = np.asarray(p, float); PAR[k] = par
        if end is not None: END[k] = np.asarray(end, float)
    trunk = np.isin(lab, ['trunk']); tail = lab == 'tail'
    LA = limb_line(m, lab, 'L', 'arm'); LL = limb_line(m, lab, 'L', 'leg')
    for nm, L_ in (('arm', LA), ('leg', LL)):
        print(f'  {nm}.L: root {L_["root"].round(3)} elbow {L_["elbow"].round(3)} (bend {L_["bend"]:.0f} deg) wrist {L_["wrist"].round(3)} knuckles {L_["knuck"].round(3)}; '
              f'upper {np.linalg.norm(L_["elbow"] - L_["root"]):.3f} lower {np.linalg.norm(L_["wrist"] - L_["elbow"]):.3f} palm {np.linalg.norm(L_["knuck"] - L_["wrist"]):.3f}')
    zs, zc = LL['root'][2], LA['root'][2]
    def trunkpt(z):
        r = sec_centre(P, T, trunk | tail, z); return r[0] if r is not None else np.array([0, 0.3, z])
    hips = trunkpt(zs); chest = trunkpt(zc); hips[0] = chest[0] = 0
    hips[1] = trunkpt(zs)[1] + 0.0; spine = trunkpt(zs + (zc - zs) / 3); spine1 = trunkpt(zs + 2 * (zc - zs) / 3); spine[0] = spine1[0] = 0
    headj = C + np.array([0, -0.06, -0.21]); neck = (chest * 0.45 + headj * 0.55); neck[1] = max(neck[1], chest[1]); neck[0] = 0
    add('hips', hips, None, spine); add('spine', spine, 'hips'); add('spine1', spine1, 'spine'); add('chest', chest, 'spine1', neck); add('neck', neck, 'chest'); add('head', headj, 'neck', headj + np.array([0, 0.3, 0]))
    add('headfront', C + np.array([0, 0, R * 0.8]), 'head', C + np.array([0, 0, R]))
    for sd, mx in (('L', 1), ('R', -1)):
        M_ = np.array([mx, 1, 1]); A = LA
        sh = chest * 0.55 + A['root'] * M_ * 0.45; sh[1] = chest[1] * 0.5 + A['root'][1] * 0.5
        add('shoulder.' + sd, sh, 'chest'); add('upperarm.' + sd, A['root'] * M_, 'shoulder.' + sd); add('forearm.' + sd, A['elbow'] * M_, 'upperarm.' + sd); add('hand.' + sd, A['wrist'] * M_, 'forearm.' + sd, A['knuck'] * M_)
        Lg = LL; add('thigh.' + sd, Lg['root'] * M_, 'hips'); add('shin.' + sd, Lg['elbow'] * M_, 'thigh.' + sd); add('foot.' + sd, Lg['wrist'] * M_, 'shin.' + sd)
        tb = Lg['wrist'] * 0.5 + Lg['knuck'] * 0.5; add('toes.' + sd, tb * M_, 'foot.' + sd, Lg['knuck'] * M_)
    # tail: the fleshy core (the section's widest y) from just behind the hips to the tip, six bones
    tz0 = hips[2] - 0.12; tz1 = P[tail, 2].min() + 0.01; core = []
    for z in np.linspace(tz0, tz1, 40):
        Tm = T[(tail | trunk)[T].all(1)]; sg = slice_z(P, Tm, z)
        if len(sg) < 3: continue
        q = sg.reshape(-1, 3); ys = np.linspace(q[:, 1].min(), q[:, 1].max(), 12); wbest = -1; yb = q[:, 1].mean()
        for y in ys:
            s = q[np.abs(q[:, 1] - y) < (ys[1] - ys[0])]
            if len(s) >= 2 and np.ptp(s[:, 0]) > wbest: wbest = np.ptp(s[:, 0]); yb = y
        core.append([0, yb, z])
    core = np.array(core)
    for _ in range(6): core[1:-1] = 0.25 * core[:-2] + 0.5 * core[1:-1] + 0.25 * core[2:]
    tipv = P[tail][np.argmin(P[tail, 2])]; core = np.vstack([core, [0, tipv[1], tipv[2]]])
    cum = np.r_[0, np.cumsum(np.linalg.norm(np.diff(core, axis=0), axis=1))]; at = lambda f: np.array([np.interp(f * cum[-1], cum, core[:, k]) for k in range(3)])
    fr = [0, 0.2, 0.38, 0.54, 0.69, 0.84, 1.0]; prev = 'hips'
    for k in range(6): add(f'tail{k + 1}', at(fr[k]), prev); prev = f'tail{k + 1}'
    END['tail6'] = at(1.0)
    # digits (left side, mirrored)
    for sd, mx in (('L', 1), ('R', -1)):
        M_ = np.array([mx, 1, 1])
        for kind, par, pre in (('finger', 'hand', LA), ('toe', 'toes', LL)):
            for k in range(4):
                vs = np.where(lab == f'{kind}{k}.L')[0]
                if len(vs) < 4: print('  !! missing', kind, k); continue
                b0, mid, tip = digit_frame(m, vs, pre['wrist'])
                add(f'{kind}{k}.{sd}.1', b0 * M_, f'{par}.{sd}'); add(f'{kind}{k}.{sd}.2', mid * M_, f'{kind}{k}.{sd}.1', tip * M_)
    # gills (left side stalks = old gill labels that are thin), mirrored
    thin = thin_verts(m, np.array([l.startswith('gill') for l in lab]))
    for k in range(3):
        vs = np.where((lab == f'gill{k}.L') & thin & (P[:, 0] > 0))[0]
        q = P[vs]; dsk, _ = cKDTree(P[~np.array([l.startswith('gill') for l in lab])]).query(q); root = q[dsk <= np.quantile(dsk, 0.08)].mean(0)
        far = q[np.argmax(np.linalg.norm(q - root, axis=1))]; ax = unit(far - root); Lg_ = np.quantile((q - root) @ ax, 0.97)
        for sd, mx in (('L', 1), ('R', -1)):
            M_ = np.array([mx, 1, 1]); add(f'gill{k}.{sd}.1', root * M_, 'head'); add(f'gill{k}.{sd}.2', (root + ax * Lg_ * 0.5) * M_, f'gill{k}.{sd}.1', (root + ax * Lg_) * M_)
        print(f'  gill{k}: {len(vs)} verts root {root.round(3)} length {Lg_:.3f}')
    missing = set(ORDER) - set(J); assert not missing, missing
    return J, END, PAR, LA, LL
def thin_verts(m, cand, r=0.04, dot=-0.3):
    kd = cKDTree(m.P); out = np.zeros(m.n, bool)
    for i in np.where(cand)[0]:
        j = kd.query_ball_point(m.P[i], r)
        if len(j) > 1 and (m.N[j] @ m.N[i]).min() < dot: out[i] = True
    return out
def endp(J, END, PAR, k):
    if k in END: return END[k]
    ch = [c for c in J if PAR[c] == k]
    return np.mean([J[c] for c in ch], 0) if ch else J[k] + np.array([0, 0.02, 0])
def view_export(P, T, J, END, PAR, nm, cats=None, catnames=None):
    """runtime-format mesh (no skin yet) with the real bones, for the joint check in view.html"""
    from straighten import write_view
    class MM: pass
    mm = MM(); mm.T = T; write_view(O + 'www/rb/', nm, mm, P)
    meta = json.load(open(O + f'www/rb/{nm}.json')); meta['bones'] = [{'name': k, 'parent': PAR[k], 'pos': J[k].round(5).tolist(), 'end': endp(J, END, PAR, k).round(5).tolist(), 'q': [0, 0, 0, 1]} for k in ORDER]
    if cats is not None:
        buf = bytearray(open(O + f'www/rb/{nm}.bin', 'rb').read()); o = meta['off']; si = np.zeros((len(P), 4), np.uint8); si[:, 0] = cats; buf[o[3]:o[3] + si.nbytes] = si.tobytes(); open(O + f'www/rb/{nm}.bin', 'wb').write(buf)
    json.dump(meta, open(O + f'www/rb/{nm}.json', 'w'))

# ======================== weights ========================
from rigcore import chain_weights, digit_weights, laplacian_smooth_weights, finalize, mkframe, quat, smooth as rsmooth
def mirror_name(k): return k.replace('.L', '.#').replace('.R', '.L').replace('.#', '.R')
def weights(P, T, lab, J, END, PAR, LA, LL, C, R):
    m = Mesh(P, T); n = m.n; bi = {k: i for i, k in enumerate(ORDER)}; W = np.zeros((n, len(ORDER)))
    isg = np.array([l.startswith('gill') for l in lab]); thin = thin_verts(m, isg)
    # gill-labelled skin lying on the trunk (the sculpt's lowest stalk is fused onto the neck) is body; everything else of a stalk is the stalk
    dtr, _ = cKDTree(P[lab == 'trunk']).query(P); onbody = isg & ~thin & (dtr < 0.012); gill = isg & ~onbody
    left = P[:, 0] >= -1e-9
    # limb regions are cut at a junction plane through each root joint (the old limb labels ran onto the belly between the legs)
    dig = np.array([l.startswith(('finger', 'toe')) and not l.startswith('toes') for l in lab])
    limbreg = {}
    for kind, L_ in (('arm', LA), ('leg', LL)):
        ax = unit(L_['elbow'] - L_['root']); h = (P - L_['root']) @ ax
        reg = ((lab == f'{kind}.L') | (dig & np.array([l.endswith('.L') and l.startswith('finger' if kind == 'arm' else 'toe') for l in lab]))) & (h > -0.035)
        limbreg[kind] = (reg, ax, h)
    inlimb = limbreg['arm'][0] | limbreg['leg'][0]
    # 1. trunk + tail + neck + head base: one chain from the face to the tail tip (every vertex that is not a free limb / stalk)
    chain = ['headfront', 'head', 'neck', 'chest', 'spine1', 'spine', 'hips', 'tail1', 'tail2', 'tail3', 'tail4', 'tail5', 'tail6']
    pts = np.array([J[k] for k in chain] + [END['tail6']]); bones = ['head', 'neck', 'chest', 'spine1', 'spine', 'hips', 'hips', 'tail1', 'tail2', 'tail3', 'tail4', 'tail5', 'tail6']
    body = ~inlimb & ~gill
    vs = np.where(body)[0]; chain_weights(P, vs, pts, [bi[b] for b in bones], W, band=0.11)
    # the skull is rigid with the head bone: inside the head's dome, away from where the neck comes in (behind and below)
    dC = P - C; rC = np.linalg.norm(dC, axis=1) / R; nax = unit(np.array([0, -0.55, -1.0])); ang = np.degrees(np.arccos(np.clip((dC / np.maximum(rC[:, None] * R, 1e-9)) @ nax, -1, 1)))
    hw = ss((1.16 - rC) / 0.14) * ss((ang - 38) / 30); hw[gill] = 0
    W[body] = W[body] * (1 - hw[body, None]); W[body, bi['head']] += hw[body]
    sk = hw > 0.999
    # 2. limbs (left side): chain along root - elbow - wrist - knuckles, crossfades scaled to the limb's thickness, the root easing into the trunk
    for kind, L_, names, base in (('arm', LA, ('upperarm', 'forearm', 'hand'), 'chest'), ('leg', LL, ('thigh', 'shin', 'foot'), 'hips')):
        reg, ax, h = limbreg[kind]; vs = np.where(reg & ~dig)[0]; r_el = float(np.interp(L_['cum'][L_['ie']], L_['cum'], L_['rad']))
        p4 = np.array([L_['root'], L_['elbow'], L_['wrist'], L_['knuck']])
        s_ = chain_weights(P, vs, p4, [bi[f'{nm}.L'] for nm in names], W, band=max(0.05, 1.3 * r_el))
        # into the trunk across the junction: from 3.5 cm inside the root plane to 7 cm out along the limb
        wb = 1 - ss((h[vs] + 0.035) / 0.105); trunkw = np.zeros((len(vs), W.shape[1])); trunkw[:, bi[base]] = 1
        W[vs] = W[vs] * (1 - wb[:, None]) + trunkw * wb[:, None]
        if kind == 'leg':   # the ball of the foot follows the toes bone (only past the ankle)
            cum = np.r_[0, np.cumsum(np.linalg.norm(np.diff(p4, axis=0), axis=1))]; fl = cum[3] - cum[2]
            fv = vs[(s_ > cum[2] + 0.45 * fl)]; wf = W[fv, bi['foot.L']].copy(); W[fv, bi['foot.L']] = wf * 0.45; W[fv, bi['toes.L']] = wf * 0.55
    # 3. digits (left side): proximal / distal by the parameter along the digit, a smooth knuckle into the hand / toes
    for kind, par in (('finger', 'hand'), ('toe', 'toes')):
        for k in range(4):
            vs = np.where(lab == f'{kind}{k}.L')[0]
            if len(vs) < 4: continue
            b0 = J[f'{kind}{k}.L.1']; tip = END[f'{kind}{k}.L.2']; ax = unit(tip - b0); Ld = float(np.linalg.norm(tip - b0))
            digit_weights(m, {'verts': vs, 'base': b0, 'axis': ax, 'L': Ld}, [bi[f'{kind}{k}.L.1'], bi[f'{kind}{k}.L.2']], bi[f'{par}.L'], W, blend=0.4)
    # 4. gills (left side): each thin stalk along its own two bones, rooted in the head
    for k in range(3):
        vs = np.where((lab == f'gill{k}.L') & gill & (P[:, 0] > 0))[0]; root = J[f'gill{k}.L.1']; tip = END[f'gill{k}.L.2']; ax = unit(tip - root); Lg = float(np.linalg.norm(tip - root))
        u = np.clip(((P[vs] - root) @ ax) / Lg, 0, 1); w2 = rsmooth((u - 0.5) / 0.3 + 0.5); wh = 1 - rsmooth(u / 0.25)
        W[vs] = 0; W[vs, bi['head']] = wh; W[vs, bi[f'gill{k}.L.1']] = (1 - wh) * (1 - w2); W[vs, bi[f'gill{k}.L.2']] = (1 - wh) * w2
    # zero rows (unlabelled bits): nearest labelled neighbour's weights
    empty = np.where(W.sum(1) < 1e-6)[0]
    if len(empty):
        full = np.where(W.sum(1) >= 1e-6)[0]; _, j = cKDTree(P[full]).query(P[empty]); W[empty] = W[full[j]]; print(f'  {len(empty)} unweighted vertices took their nearest neighbour')
    # 5. smoothing: the body and limb junctions (not the skull, gills or digits)
    soft = np.where(~(sk | gill | dig))[0]; laplacian_smooth_weights(m, W, soft, iters=10, lam=0.5)
    # the gills with a ring of the skin around their roots: no hard edge between a stalk and the head
    gz = gill.copy(); rows = m.rows()
    for _ in range(2):
        add = [u for v in np.where(gz)[0] for u in rows[v]]; gz[add] = True
    laplacian_smooth_weights(m, W, np.where(gz & ~sk | gill)[0], iters=5, lam=0.5)
    knuck = np.where(dig)[0]
    from rigcore import knuckle_smooth
    knuckle_smooth(m, W, knuck, iters=6, lam=0.5)
    # 6. mirror: the right half takes its partner's weights with .L / .R bones swapped; the midline averages itself with its mirror
    mm = mirror_map(P); swap = np.array([bi[mirror_name(k)] for k in ORDER])
    Wm = np.zeros_like(W); Wm[:, swap] = W[mm]   # Wm[i] = mirrored weights of i's partner
    right = P[:, 0] < -1e-9; mid = np.abs(P[:, 0]) <= 1e-9
    W[right] = Wm[right]; W[mid] = 0.5 * (W[mid] + Wm[mid])
    idx, w = finalize(W, P=P, joints=np.array([J[k] for k in ORDER]))
    # symmetry check
    wsw = np.zeros((n, len(ORDER))); np.put_along_axis(wsw, idx.astype(int), w, 1); d = np.abs(wsw[right][:, swap] - 0) if False else None
    labels = np.array(lab, dtype=object)
    return idx, w, labels, gill
def frames(J, END, PAR):
    F = {}; up = np.array([0, 1.0, 0]); fwd = np.array([0, 0, 1.0]); down = -up
    dirn = lambda k: unit(endp(J, END, PAR, k) - J[k])
    for k in ORDER:
        y = dirn(k)
        if k in ('hips', 'spine', 'spine1', 'chest', 'neck'): F[k] = mkframe(y, down)
        elif k == 'head': F[k] = mkframe(up, fwd)
        elif k == 'headfront': F[k] = mkframe(fwd, up)
        elif k.startswith(('shoulder', 'upperarm', 'thigh')): F[k] = mkframe(y, fwd)
        elif k.startswith(('forearm', 'shin')):
            yu = dirn(PAR[k]); X = np.cross(yu, y)
            if np.linalg.norm(X) > np.sin(np.radians(10)): X = unit(X); F[k] = mkframe(y, np.cross(X, y))
            else: F[k] = mkframe(y, fwd if k.startswith('forearm') else -fwd)
        elif k.startswith(('hand', 'foot', 'toes')): F[k] = mkframe(y, down)
        elif k.startswith(('finger', 'toe')): F[k] = F[PAR[k]].copy()
        elif k.startswith('tail'): F[k] = mkframe(y, down)
        elif k.startswith('gill'): F[k] = mkframe(y, fwd)
        else: raise Exception(k)
    # the right side's frames are the mirror of the left's (x -> -x on the basis, then x axis = y x z)
    for k in ORDER:
        if '.R' in k:
            Fl = F[mirror_name(k)]; Mx = np.diag([-1, 1, 1]); y = Mx @ Fl[:, 1]; z = Mx @ Fl[:, 2]; F[k] = np.stack([np.cross(y, z), y, z], 1)
    return F
def export_runtime(P, T, idx, w, J, END, PAR, F, out, extra=None):
    """the current runtime format (positions, normals, uv16 placeholder, skin, uint16 indices); extras.py-style attributes appended later"""
    m = Mesh(P, T); N = m.N.astype(np.float32); n = len(P)
    wq = np.round(w * 255).astype(np.int32); wq[:, 0] += 255 - wq.sum(1); wq = np.clip(wq, 0, 255).astype(np.uint8)
    parts = [P.astype(np.float32).tobytes(), N.tobytes(), np.zeros((n, 2), np.uint16).tobytes(), idx.astype(np.uint8).tobytes(), wq.tobytes(), T.astype(np.uint16).ravel().tobytes()]
    off = []; o = 0
    for b in parts: off.append(o); o += len(b); o += (-o) % 4
    buf = bytearray(o)
    for b, of in zip(parts, off): buf[of:of + len(b)] = b
    bones = [{'name': k, 'parent': PAR[k], 'pos': [round(float(x), 5) for x in J[k]], 'end': [round(float(x), 5) for x in endp(J, END, PAR, k)], 'q': [round(float(x), 6) for x in quat(F[k])]} for k in ORDER]
    meta = {'n': n, 'ni': int(T.size), 'i32': False, 'uv16': True, 'off': off, 'bones': bones, 'bbox': [P.min(0).round(4).tolist(), P.max(0).round(4).tolist()]}
    if extra: meta.update(extra)
    open(out + '.bin', 'wb').write(buf); json.dump(meta, open(out + '.json', 'w')); print(' exported', out, len(buf), 'bytes', n, 'verts')
def build():
    t0 = time.time(); P, T, lab, C, R = geometry(); J, END, PAR, LA, LL = joints(P, T, lab, C, R)
    idx, w, labels, gill = weights(P, T, lab, J, END, PAR, LA, LL, C, R); F = frames(J, END, PAR)
    hb = J['head']; extra = {'headc': (C - hb).round(4).tolist(), 'headr': round(float(R), 4), 'face': {'c': C.round(4).tolist(), 'r': round(float(R), 4)}}
    export_runtime(P, T, idx, w, J, END, PAR, F, O + 'www/c7/axo_crawl', extra)
    np.savez(O + 'crawl7_rig.npz', P=P, T=T, idx=idx, w=w, labels=labels.astype(str), names=np.array(ORDER), gill=gill, C=C, R=R)
    print(f'built in {time.time() - t0:.1f}s')
