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
def geometry(mode='remesh'):
    """the crawl mesh in export coordinates: head on the stand's shell, the face cap exactly spherical, symmetric, the body refined"""
    z = np.load(O + 'crawl_head.npz', allow_pickle=True); P = z['P'].copy(); T = z['T']; src = z['src']; Cc = z['Cc']; R = float(z['R'])
    z0 = np.load(O + 'crawl_sym.npz', allow_pickle=True); mm = mirror_map(z0['P'])
    P = (P + P[mm] * np.array([-1, 1, 1])) / 2; P[np.abs(z0['P'][:, 0]) < 1e-9, 0] = 0   # exactly symmetric again (the stand shell is not quite)
    P, wcap = face_cap(P, Cc, R)
    # labels from the old crawl rig through the mirror / clip map
    m0, W0, names0, lab0 = load_old(); a = src[:, 0].astype(int); b = src[:, 1].astype(int); u = src[:, 2]; lab = np.where(u < 0.5, lab0[a], lab0[b])
    if mode == 'refine':   # the reference mesh of the joint analysis (limbs7.json): the body refined, no remesh
        body = np.array([l in ('trunk', 'tail') or l.startswith(('arm', 'leg')) for l in lab])
        P2, T2, at, par = refine(P, T, 0.045 / SC, mask=body, verbose=False); lab2 = list(lab)
        for i in range(len(P), len(P2)):
            pa, pb = par[i]; la, lb = lab2[pa], lab2[pb]; lab2.append(la if la == lb or not la.startswith(('finger', 'toe', 'gill')) else lb)
        lab2 = np.array(lab2)
    else:
        # isotropic remesh of the left half (remesh.py: regular triangles at a target size per region, the gill frills and the tail tip kept as
        # they are), mirrored back: exactly symmetric, no slivers along the seam
        from remesh import remesh, compact, edges_of
        from scipy.sparse import coo_matrix
        Lh = P[:, 0] >= -1e-9; Ph, Th, ex = compact(P, T[Lh[T].all(1)], {'lab': lab}); labh = ex['lab']
        isg = np.array([l.startswith('gill') for l in labh]); isd = np.array([l.startswith(('finger', 'toe')) and not l.startswith('toes') for l in labh])
        isl = np.array([l.startswith(('arm', 'leg')) for l in labh]); ish = labh == 'head'
        Lf = np.where(isd, 0.016, np.where(isl, 0.022, np.where(ish, 0.025, 0.03))) / SC
        E_, *_ = edges_of(Th); nh = len(Ph); A_ = coo_matrix((np.ones(2 * len(E_)), (np.r_[E_[:, 0], E_[:, 1]], np.r_[E_[:, 1], E_[:, 0]])), shape=(nh, nh)).tocsr(); dg = np.asarray(A_.sum(1)).ravel()
        for _ in range(8): Lf = 0.5 * Lf + 0.5 * (A_ @ Lf) / np.maximum(dg, 1)
        fr = isg | (A_ @ isg.astype(float) > 0); fr |= Ph[:, 2] < Ph[:, 2].min() + 0.03
        Pr, Tr, labr = remesh(Ph, Th, Lf, frozen=fr, iters=5, labels=labh, verbose=False)
        seam = np.abs(Pr[:, 0]) < 1e-9; nr = len(Pr); ns = np.where(~seam)[0]; mir = np.arange(nr); mir[ns] = nr + np.arange(len(ns))
        P2 = np.vstack([Pr, Pr[ns] * np.array([-1, 1, 1])]); T2 = np.vstack([Tr, mir[Tr][:, ::-1]]); lab2 = np.r_[labr, labr[ns]]
    Pe = P2 * SC + np.array([0, Y0, Z0]); Ce = Cc * SC + np.array([0, Y0, Z0])
    # sides: the mirrored half carries the left's labels; rename by the side it is on
    def sided(l, x):
        if '.L' in l or '.R' in l: return l.replace('.L', '.R').replace('.R', '.L' if x > 0 else '.R') if True else l
        return l
    lab3 = np.array([(l.replace('.R', '.L') if x > 1e-9 else l.replace('.L', '.R')) if ('.L' in l or '.R' in l) else l for l, x in zip(lab2, Pe[:, 0])])
    print(f'geometry: {len(Pe)} verts, {len(T2)} tris; face centre (export) {Ce.round(3)}; ground y {Pe[:, 1].min():+.3f}')
    if mode == 'remesh': np.savez(O + 'crawl7_geo.npz', P=Pe, T=T2, lab=lab3, C=Ce, R=R * SC)
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
def _fit(c):
    mu = c.mean(0); u, s, vt = np.linalg.svd(c - mu); return mu, vt[0] * np.sign(vt[0] @ (c[-1] - c[0]))
def _meet(p1, d1, p2, d2):
    w = p1 - p2; a = d1 @ d1; b = d1 @ d2; cc = d2 @ d2; d = d1 @ w; e = d2 @ w; den = a * cc - b * b
    t = (b * e - cc * d) / den; s = (a * e - b * d) / den; return (p1 + t * d1 + p2 + s * d2) / 2
# which loops (counted from the digits) are the palm, the lower and the upper limb of this sculpt (read off dbg_loops2.jpg)
SEGS = {'arm': ((3, 8), (10, 18), (27, 37)), 'leg': ((0, 4), (8, 13), (14, 20))}   # loop indices on the reference mesh (geometry('refine'))
def limb_line(m, lab, side, kind):
    """the limb's axis from its digits to where it emerges from the body (exact cross-section loops, limbaxis.py) and its joints: the root
    (shoulder / hip) 0.75 of the limb's radius inside the body behind the emergence loop; the wrist / ankle where the palm's and the lower
    limb's axes meet; the elbow where the forearm's and upper arm's axes meet (the sculpt bends there); the knee half way from the hip to the
    ankle (the sculpted hind leg is nearly straight)"""
    from limbaxis import loops_along, emergence
    dig = np.array([l.startswith(('finger' if kind == 'arm' else 'toe')) and not l.startswith('toes') and l.endswith('.' + side) for l in lab])
    limb = lab == f'{kind}.{side}'; mask = limb | dig; d = m.geo(np.where(dig)[0], limit=1.2, mask=mask)
    trunkadj = np.zeros(m.n, bool); rows = m.rows(); tr = np.isin(lab, ['trunk', 'head', 'tail'])
    for v in np.where(limb)[0]:
        if any(tr[u] for u in rows[v]): trunkadj[v] = True
    junc = m.P[trunkadj].mean(0); dj = d[trunkadj]; dj = np.median(dj[np.isfinite(dj)])
    pts = []
    for t in np.arange(0.0, dj, 0.01):
        sel = limb & np.isfinite(d) & (np.abs(d - t) < 0.008)
        if sel.sum() < 4: continue
        pts.append(m.P[sel].mean(0))
    pts = np.array(pts)
    for _ in range(4): pts[1:-1] = 0.25 * pts[:-2] + 0.5 * pts[1:-1] + 0.25 * pts[2:]
    L = loops_along(m.P, m.T, pts); ie = emergence(L); nE = unit(np.gradient(pts, axis=0))[ie]; oE = pts[ie]
    c = np.array([L[i]['c'] if L[i] is not None else pts[i] for i in range(ie + 1)]); req = np.array([L[i]['req'] if L[i] is not None else np.nan for i in range(ie + 1)])
    sp, sl, su = SEGS[kind]; assert su[1] <= ie, (kind, ie)
    Fp, Fl, Fu = _fit(c[sp[0]:sp[1] + 1]), _fit(c[sl[0]:sl[1] + 1]), _fit(c[su[0]:su[1] + 1])
    knuck = m.P[dig].mean(0)
    E = c[-1]; rE = float(np.nanmedian(req[-3:])); root = E + Fu[1] * 0.75 * rE
    wrist = _meet(*Fp, *Fl)
    if kind == 'arm':
        X = _meet(*Fl, *Fu); k = int(np.argmin(np.linalg.norm(c - X, axis=1))); elbow = 0.5 * (X + c[k])
    else:
        # the point of the centre line half way (by distance along it, root included) from the hip to the ankle
        cl = np.vstack([root, c[::-1]]); cum = np.r_[0, np.cumsum(np.linalg.norm(np.diff(cl, axis=0), axis=1))]
        kw = int(np.argmin(np.linalg.norm(cl - wrist, axis=1))); sk = 0.5 * cum[kw]; elbow = np.array([np.interp(sk, cum, cl[:, q]) for q in range(3)])
    cum = np.r_[0, np.cumsum(np.linalg.norm(np.diff(c, axis=0), axis=1))]
    ik = int(np.argmin(np.linalg.norm(c - elbow, axis=1))); iw = int(np.argmin(np.linalg.norm(c - wrist, axis=1)))
    return dict(knuck=knuck, wrist=wrist, elbow=elbow, root=root, pts=c, rad=req, cum=cum, iw=iw, ie=ik, junc=junc, bend=0.0, E=E, rE=rE, oE=oE, nE=nE)
LIMBS = O + 'limbs7.json'
def analyse_reference():
    """the joint analysis on the reference mesh (geometry('refine')): limb axes, joints, emergence planes and the digits, saved to limbs7.json
    (the production mesh is a remesh of the same surface, so the analysis holds for it; its regions are re-derived from these planes)"""
    from digits import find_digits
    P, T, lab, C, R = geometry('refine'); m = Mesh(P, T); out = {}
    for kind in ('arm', 'leg'):
        L_ = limb_line(m, lab, 'L', kind); ds = find_digits(m, L_['wrist'], L_['knuck'])
        if len(ds) < 4: raise Exception(f'{kind}: only {len(ds)} digits')
        dd = []
        for d in ds:
            r = d['rad']; kn = d['base'] - d['bdir'] * 1.0 * r; end = d['tipP'] - d['bdir'] * 0.4 * r
            ax = np.vstack([kn, d['axis']]); cum = np.r_[0, np.cumsum(np.linalg.norm(np.diff(ax, axis=0), axis=1))]
            mid = np.array([np.interp(0.5 * cum[-1], cum, ax[:, q]) for q in range(3)])
            dd.append(dict(knuckle=kn.tolist(), mid=mid.tolist(), end=end.tolist(), tip=d['tipP'].tolist(), bdir=d['bdir'].tolist(), rad=r, L=float(cum[-1]), axis=ax.tolist()))
        dd.sort(key=lambda d: -d['knuckle'][0])
        out[kind] = dict(root=L_['root'].tolist(), elbow=L_['elbow'].tolist(), wrist=L_['wrist'].tolist(), knuck=np.mean([d['knuckle'] for d in dd], 0).tolist(),
                         E=L_['E'].tolist(), rE=L_['rE'], oE=L_['oE'].tolist(), nE=L_['nE'].tolist(), rad=float(np.nanmedian(L_['rad'])), digits=dd)
        print(f'  {kind}.L reference: root {np.round(out[kind]["root"], 3)} elbow {np.round(out[kind]["elbow"], 3)} wrist {np.round(out[kind]["wrist"], 3)}; digits ' + ' '.join(f"{np.round(d['knuckle'], 3)}/{d['L']:.3f}" for d in dd))
    json.dump(out, open(LIMBS, 'w'), indent=1); return out
def limb_table(m, kind, side_digits=True):
    """the saved analysis as the dict joints() / weights() use, with the digit regions found on this mesh: the vertices past each digit's base
    plane connected to the vertex nearest its tip"""
    t = json.load(open(LIMBS))[kind]; L_ = {k: (np.array(v) if isinstance(v, list) and k != 'digits' else v) for k, v in t.items()}
    L_['rad'] = np.array([t['rad']]); P = m.P; ds = []
    for d in t['digits']:
        d = {k: (np.array(v) if isinstance(v, list) else v) for k, v in d.items()}
        base = d['knuckle'] + d['bdir'] * d['rad']; pos = (P - base) @ d['bdir']; nc, comp = m.comps((pos > 0) & (np.linalg.norm(P - base, axis=1) < d['L'] * 1.6 + 0.03))
        tipv = m.near(d['tip']); d['verts'] = np.where(comp == comp[tipv])[0] if comp[tipv] >= 0 else np.array([], int); ds.append(d)
    L_['digits'] = ds; return L_
def digit_frame(m, vs, palm_c):
    q = m.P[vs]; dp = np.linalg.norm(q - palm_c, axis=1); o = np.argsort(dp); base = q[o[:max(3, len(vs) // 5)]].mean(0); tip = q[o[-max(3, len(vs) // 6):]].mean(0)
    ax = unit(tip - base); L = float(((q - base) @ ax).max()); return base, base + ax * L * 0.48, base + ax * L
def joints(P, T, lab, C, R):
    m = Mesh(P, T); J = {}; END = {}; PAR = {}
    def add(k, p, par, end=None):
        J[k] = np.asarray(p, float); PAR[k] = par
        if end is not None: END[k] = np.asarray(end, float)
    trunk = np.isin(lab, ['trunk']); tail = lab == 'tail'
    LA = limb_table(m, 'arm'); LL = limb_table(m, 'leg'); DIG = {'finger': LA['digits'], 'toe': LL['digits']}   # the reference analysis (limbs7.json)
    for nm, L_ in (('arm', LA), ('leg', LL)):
        print(f'  {nm}.L: root {L_["root"].round(3)} elbow {L_["elbow"].round(3)} wrist {L_["wrist"].round(3)} knuckles {L_["knuck"].round(3)}; '
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
    for sd, mx in (('L', 1), ('R', -1)):
        M_ = np.array([mx, 1, 1])
        for kind, par in (('finger', 'hand'), ('toe', 'toes')):
            for k, d in enumerate(DIG[kind]):
                add(f'{kind}{k}.{sd}.1', d['knuckle'] * M_, f'{par}.{sd}'); add(f'{kind}{k}.{sd}.2', d['mid'] * M_, f'{kind}{k}.{sd}.1', d['end'] * M_)
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
    return J, END, PAR, LA, LL, DIG
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
def weights(P, T, lab, J, END, PAR, LA, LL, C, R, DIG):
    m = Mesh(P, T); n = m.n; bi = {k: i for i, k in enumerate(ORDER)}; W = np.zeros((n, len(ORDER)))
    isg = np.array([l.startswith('gill') for l in lab]); thin = thin_verts(m, isg)
    # gill-labelled skin lying on the trunk (the sculpt's lowest stalk is fused onto the neck) is body; everything else of a stalk is the stalk
    dtr, _ = cKDTree(P[lab == 'trunk']).query(P); onbody = isg & ~thin & (dtr < 0.012); gill = isg & ~onbody
    left = P[:, 0] >= -1e-9
    dig = np.zeros(n, bool)
    for kind in DIG:
        for d in DIG[kind]: dig[d['verts']] = True
    diglab = np.array([l.startswith(('finger', 'toe')) and not l.startswith('toes') for l in lab])
    # limb regions (left side): the side of the emergence loop's plane that holds the digits (the old limb labels ran far onto the body);
    # a signed geodesic distance from that loop (+ out along the limb, - into the body) sets the blend from the body's weights to the limb's
    rows = m.rows(); limbreg = {}
    for kind, L_ in (('arm', LA), ('leg', LL)):
        nout = -L_['nE'] if (L_['root'] - L_['oE']) @ L_['nE'] > 0 else L_['nE']
        pos = (P - L_['oE']) @ nout; nc, comp = m.comps(pos > 0)
        digk = np.where(np.array([l.startswith('finger' if kind == 'arm' else 'toe') and not l.startswith('toes') and l.endswith('.L') for l in lab]))[0]
        side = comp == np.bincount(comp[digk][comp[digk] >= 0]).argmax()
        e = m.E; cut = side[e[:, 0]] != side[e[:, 1]]; seeds = np.unique(e[cut].ravel())
        g = m.geo(seeds, limit=0.25); gs = np.where(side, g, -g)
        print(f'  {kind}.L region: {int(side.sum())} verts on the limb side, {len(seeds)} loop verts')
        limbreg[kind] = (side, gs)
    # 1. trunk + tail + neck + head base: one chain from the face to the tail tip, for every vertex but the gill stalks (the limbs blend
    # out of these body weights below)
    chain = ['headfront', 'head', 'neck', 'chest', 'spine1', 'spine', 'hips', 'tail1', 'tail2', 'tail3', 'tail4', 'tail5', 'tail6']
    pts = np.array([J[k] for k in chain] + [END['tail6']]); bones = ['head', 'neck', 'chest', 'spine1', 'spine', 'hips', 'hips', 'tail1', 'tail2', 'tail3', 'tail4', 'tail5', 'tail6']
    body = ~gill
    vs = np.where(body)[0]; chain_weights(P, vs, pts, [bi[b] for b in bones], W, band=0.11)
    # the skull is rigid with the head bone: inside the head's dome, away from where the neck comes in (behind and below)
    dC = P - C; rC = np.linalg.norm(dC, axis=1) / R; nax = unit(np.array([0, -0.55, -1.0])); ang = np.degrees(np.arccos(np.clip((dC / np.maximum(rC[:, None] * R, 1e-9)) @ nax, -1, 1)))
    hw = ss((1.16 - rC) / 0.14) * ss((ang - 38) / 30); hw[gill] = 0
    W[body] = W[body] * (1 - hw[body, None]); W[body, bi['head']] += hw[body]
    sk = hw > 0.999
    # 2. limbs (left side): a chain root - elbow / knee - wrist / ankle (- ball of the foot) - knuckles, crossfades scaled to the limb's
    # thickness; blended into the body's weights across the emergence loop (b_in into the body, b_out out along the limb)
    limbzone = np.zeros(n, bool)
    for kind, L_, names, base in (('arm', LA, ('upperarm', 'forearm', 'hand'), 'shoulder.L'), ('leg', LL, ('thigh', 'shin', 'foot', 'toes'), 'hips')):
        side, gs = limbreg[kind]; rE = L_['rE']; b_in, b_out = 0.45 * rE, 0.4 * rE
        gs = np.where(np.isfinite(gs), gs, np.where(side, 9.0, -9.0))
        # the girdle: body skin around the limb's base follows the girdle bone (hips / shoulder), not the tail or the spine segments
        wa = 1 - ss((-gs - b_in) / (1.6 * b_in)); wa[gill | dig] = 0
        av = np.where(wa > 0)[0]; Wb = np.zeros((len(av), W.shape[1])); Wb[:, bi[base]] = 1; W[av] = W[av] * (1 - wa[av, None]) + Wb * wa[av, None]
        wl = ss((gs + b_in) / (b_in + b_out)); wl[gill] = 0
        vs = np.where(wl > 0)[0]
        r_el = float(np.nanmedian(L_['rad'])); band = max(0.045, 0.9 * r_el)
        if kind == 'arm': p4 = np.array([L_['root'], L_['elbow'], L_['wrist'], L_['knuck']])
        else: p4 = np.array([L_['root'], L_['elbow'], L_['wrist'], 0.5 * (L_['wrist'] + L_['knuck']), L_['knuck']])
        Wt = np.zeros((m.n, W.shape[1])); chain_weights(P, vs, p4, [bi[f'{nm}.L'] for nm in names], Wt, band=band); Wl = Wt[vs]
        W[vs] = W[vs] * (1 - wl[vs, None]) + Wl * wl[vs, None]
        limbzone |= (wa > 0.01)
        print(f'  {kind}.L: {len(vs)} verts weighted to the limb, {len(av)} to the girdle (b_in {b_in:.3f} b_out {b_out:.3f}, crossfade {band:.3f})')
    # 3. digits (left side): proximal / distal along the digit's axis from its knuckle, the knuckle blending into the hand / toes bone from
    # half a digit radius inside the palm to 0.7 radius out along the digit
    for kind, par in (('finger', 'hand'), ('toe', 'toes')):
        own = [np.zeros(n, bool) for _ in DIG[kind]]
        for k, d in enumerate(DIG[kind]): own[k][d['verts']] = True
        for k, d in enumerate(DIG[kind]):
            r = d['rad']; sgn = (P - d['knuckle']) @ d['bdir']
            ax = np.vstack([d['knuckle'], d['axis']]); dax = np.min(np.linalg.norm(P[:, None, :] - ax[None, ::2, :], axis=2), axis=1)
            others = np.zeros(n, bool)
            for j in range(len(own)):
                if j != k: others |= own[j]
            zone = own[k] | ((sgn > -0.6 * r) & (dax < 1.6 * r) & ~others & limbreg['arm' if kind == 'finger' else 'leg'][0])
            vs = np.where(zone)[0]; sv = sgn[vs]
            wk = ss((sv + 0.5 * r) / (1.2 * r)); u = np.clip(sv / d['L'], 0, 1); w2 = ss((u - 0.5) / 0.3 + 0.5)
            Wd = np.zeros((len(vs), W.shape[1])); Wd[:, bi[f'{kind}{k}.L.1']] = 1 - w2; Wd[:, bi[f'{kind}{k}.L.2']] = w2
            W[vs] = W[vs] * (1 - wk[:, None]) + Wd * wk[:, None]
            dig[vs[wk > 0.5]] = True
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
    soft = ~(sk | gill | dig); laplacian_smooth_weights(m, W, np.where(soft & ~limbzone)[0], iters=10, lam=0.5)
    lz = limbzone.copy()
    for _ in range(2): lz[np.unique(m.E[lz[m.E[:, 0]] | lz[m.E[:, 1]]].ravel())] = True
    laplacian_smooth_weights(m, W, np.where(soft & lz)[0], iters=3, lam=0.5)
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
        elif k.startswith(('upperarm', 'thigh', 'forearm', 'shin')):
            # the two-bone IK (axo.js ik2) builds these frames from the hinge X = n x p (n root -> end, p the pole = the bind's knee / elbow
            # offset): upper bone x = sU X (sU +1 legs, -1 arms), lower bone x = -X. The bind frames are built the same way, so the IK
            # reproduces the bind with no twist about the bone (a twist offset collapses the skin where the limb blends into the body)
            arm = k.startswith(('upperarm', 'forearm')); sd = k[-1]; up = ('upperarm.' if arm else 'thigh.') + sd; lo = ('forearm.' if arm else 'shin.') + sd; en = ('hand.' if arm else 'foot.') + sd
            n = unit(J[en] - J[up]); p_ = J[lo] - J[up]; p_ = unit(p_ - n * (p_ @ n)); X = unit(np.cross(n, p_))
            Xb = (-X if arm else X) if k.startswith(('upperarm', 'thigh')) else -X
            F[k] = mkframe(y, np.cross(Xb, y))
        elif k.startswith('shoulder'): F[k] = mkframe(y, fwd)
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
    t0 = time.time(); P, T, lab, C, R = geometry(); J, END, PAR, LA, LL, DIG = joints(P, T, lab, C, R)
    idx, w, labels, gill = weights(P, T, lab, J, END, PAR, LA, LL, C, R, DIG); F = frames(J, END, PAR)
    hb = J['head']; extra = {'headc': (C - hb).round(4).tolist(), 'headr': round(float(R), 4), 'face': {'c': C.round(4).tolist(), 'r': round(float(R), 4)}}
    export_runtime(P, T, idx, w, J, END, PAR, F, O + 'www/c7/axo_crawl', extra)
    np.savez(O + 'crawl7_rig.npz', P=P, T=T, idx=idx, w=w, labels=labels.astype(str), names=np.array(ORDER), gill=gill, C=C, R=R)
    print(f'built in {time.time() - t0:.1f}s')
