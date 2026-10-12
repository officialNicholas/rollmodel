# The old gill stalks' caps repainted skin (v10). v9b retired the six stalks by collapsing each into a cap on the skull (its base ring and
# a centre), and their texels kept the sculpt's own red gill-root shading, which headtex.py left alone ("their colour belongs to the
# stalks"). With the slime's ears over them those reds peeked out beside the ear roots. Each cap's texels (the triangles on the cap verts
# slimehead.py lists) take the mean colour of the plain head texels in a ring 10 to 25 cm round the cap, with a tenth of their own detail.
# Reads the slimehead meshes (fable3/rt4) and the atlas they carry (the PNG headtex.py wrote, fable2/rt3/axo_{nm}_tex.png), rewrites the
# meshes with the repainted texture inside and the PNG beside them:
#   python3 -I capfix.py [--src S/fable3/rt4] [--tex S/fable2/rt3] [--out S/fable3/rt4]
import sys, os, json
import numpy as np
from scipy.spatial import cKDTree
from scipy.ndimage import binary_dilation
from PIL import Image
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
WORK = S + '/fable3'
sys.path.insert(0, '/home/user/rollmodel/axo/tools4')
import texbake as tb
import texbake as tb_
def lin(x): return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)
def srgb(x): x = np.clip(x, 0, 1); return np.where(x <= 0.0031308, x * 12.92, 1.055 * x ** (1 / 2.4) - 0.055)
# ---- v10e: the bridge's skin and the dorsal band (the lizard body) ----
# the bridge (slimehead's loft between the ball and the trunk) is laid with the texels its vertices brought along: the old chin, neck and
# head-underside charts, stretched. Its skin is made again from its surroundings: the texture's low-frequency colour (per vertex, smoothed
# over the welded mesh) filled across the bridge as a harmonic field from its edges (the ball's skin above, the trunk's below, each in its
# own direction round the neck), with a twelfth of the texels' own detail: as smooth and even as the cheeks, no band, no scales, no mottle.
# Then the back's darker shade carried on up (the user: "the darker shade of texture should continue upwards towards the top back of the
# head from the mid torso up"): along the dorsal midline (an angle about a point inside the upper body, from the mid torso over the nape
# and the crown toward the brow), the low-frequency colour drawn toward the band's own colour (measured on the mid torso's back), the
# texture's detail kept; full on the torso and the nape, narrowing and fading over the crown, gone before the brow; the face, the cheeks
# and the ears (out to the sides) untouched
# (per body: O the centre the angle is taken round (deg, 0 forward, 90 up, 180 back, in the body's middle plane); the band fades in from
# in0 to in1 (the mid torso: the crawl's own band is there already, the stand has none, so it takes the crawl's colour at `k`), is full
# from in1 to `full` (the nape) and fades out to `gone` (before the brow), hw its half width by angle (a soft gaussian edge: as wide as
# the crawl's own band where it meets the trunk, narrowing over the nape and the crown), meas where the crawl's band colour is measured)
DORSAL = {'stand': dict(O=[0.0, 1.0, 0.0], in0=218, in1=196, full=125, gone=60, hw=([60, 100, 125, 196], [0.06, 0.10, 0.15, 0.17]), k=0.7, colour=(0.99, 0.30, 0.42)),
          'crawl': dict(O=[0.0, 0.25, 0.15], in0=176, in1=162, full=125, gone=60, hw=([60, 100, 125, 150], [0.06, 0.10, 0.16, 0.30]), k=1.0, meas=(150, 166))}
def lizard_paint(nm, img2, P, T, uv, nb, body, small, caps, res, W, names, verbose=True):
    from scipy.sparse import coo_matrix, diags
    from scipy.sparse.linalg import splu
    n = len(P); tv = np.full(n, np.nan); nv_ = np.array(caps['neck_verts'], int); tv[nv_] = np.array(caps['neck_t'], float)
    # the welded body (the textured mesh splits its vertices along the atlas seams)
    key = np.round(P[:nb] * 1e5).astype(np.int64); _, inv = np.unique(key, axis=0, return_inverse=True); inv = inv.ravel(); nw = inv.max() + 1
    wid = np.full(n, -1); wid[:nb] = inv
    Tb = T[body[T].all(1)]; Tw = wid[Tb]; E = np.concatenate([Tw[:, [0, 1]], Tw[:, [1, 2]], Tw[:, [2, 0]]]); E = E[E[:, 0] != E[:, 1]]; E = np.unique(np.sort(E, 1), axis=0)
    Aw = coo_matrix((np.ones(2 * len(E)), (np.r_[E[:, 0], E[:, 1]], np.r_[E[:, 1], E[:, 0]])), shape=(nw, nw)).tocsr(); dw = np.asarray(Aw.sum(1)).ravel()
    # each welded vertex's colour: the texels of its own triangles near it (barycentric share over a half: never a gutter texel off the
    # chart), over all its copies; then smoothed over the mesh by `rounds` (the low-frequency colour)
    ay_, ax2, at_, ab_ = tb_.rasterize(uv, T, res, body[T].all(1) & small)
    def lowpass(rounds):
        col = lin(img2[ay_, ax2].astype(np.float64)); cw = np.zeros((nw, 3)); cn = np.zeros(nw)
        for k in range(3):
            m = ab_[:, k] > 0.5; wv = wid[T[at_[m], k]]; np.add.at(cw, wv, col[m] * ab_[m, k][:, None]); np.add.at(cn, wv, ab_[m, k])
        cw /= np.maximum(cn, 1e-9)[:, None]; cw[cn < 1e-9] = col.mean(0)
        for _ in range(rounds): cw = 0.5 * cw + 0.5 * (Aw @ cw) / np.maximum(dw, 1)[:, None]
        return cw
    low = lowpass(2)                                                              # (a vertex samples one texel: a touch smoothed)
    tw = np.full(nw, np.nan); okt = np.isfinite(tv[:nb]); tw[inv[okt]] = tv[:nb][okt]
    # (the fill runs on past the trunk's plane over the band, t up to 1 + EXT, and fades out over it: the colour's slope has no kink at
    # the plane, where the trunk's red back met the pinker bridge)
    EXT = 0.6; zone = np.isfinite(tw) & (tw >= 0) & (tw <= 1 + EXT) & (dw > 0)
    # (a piece of the zone with no edge of its own (no vertex outside the zone next to it) has nothing to fill from: left as it is)
    from scipy.sparse.csgraph import connected_components
    iz_ = np.where(zone)[0]; ncc, lab_ = connected_components(Aw[iz_][:, iz_], directed=False); touch = np.zeros(ncc, bool)
    np.logical_or.at(touch, lab_, ((Aw @ (~zone).astype(float)) > 0)[iz_]); zone[iz_[~touch[lab_]]] = False
    # the harmonic fill across the bridge from its edges' own colours
    edge = (~zone) & ((Aw @ zone.astype(float)) > 0); dom = zone | edge; idx = np.where(dom)[0]; L = (diags(dw) - Aw).tocsr()[idx][:, idx]
    fz = zone[idx]; lu = splu(L[fz][:, fz].tocsc()); rhs = -L[fz][:, ~fz] @ low[idx][~fz]; fill = low.copy(); fill[idx[fz]] = np.stack([lu.solve(np.ascontiguousarray(rhs[:, j])) for j in range(3)], 1)
    # the bridge's texels: the filled colour with a twelfth of their own detail in the middle of the bridge, all of it at its two edges (where
    # the fill is their own colour), so it meets the ball's skin and the trunk's with no seam. On the trunk's side the detail comes back over
    # the last 0.07 of t only: the old neck's own texels there carry a crisp edge across the back a little before the plane
    tw2 = np.where(np.isfinite(tw), tw, np.where(zone, 0.5, -1.0)); selT = body[T].all(1) & small & dom[np.maximum(wid[T], 0)].all(1) & zone[np.maximum(wid[T], 0)].any(1)
    ny_, nx_, nt_, nb_ = tb_.rasterize(uv, T, res, selT); Wt = wid[T[nt_]]
    ct = (fill[Wt] * nb_[:, :, None]).sum(1); cl = (low[Wt] * nb_[:, :, None]).sum(1); tt_ = (tw2[Wt] * nb_).sum(1)
    sm_ = lambda x: np.clip(x, 0, 1) ** 2 * (3 - 2 * np.clip(x, 0, 1))
    wt_ = (sm_((tt_ + 0.05) / 0.05) * (1 - sm_((tt_ - 1) / EXT)))[:, None]; tc = np.clip(tt_, 0, 1); al = (1 / 12 + (11 / 12) * (1 - sm_(np.minimum(tc / 0.2, (1 - tc) / 0.07))))[:, None]
    old = lin(img2[ny_, nx_].astype(np.float64)); det = np.clip(old / np.maximum(cl, 1e-4), 0.2, 5.0)
    img2[ny_, nx_] = srgb(old + wt_ * (ct * det ** al - old)).astype(np.float32)
    if verbose: print(f'{nm}: the bridge skin made again over {len(ny_)} texels ({int(zone.sum())} welded zone verts)')
    # (the old gill roots' red specks left round the ear roots (the cap repaint misses a few, and the lowered crawl head shows one
    # beside an ear): any deep red texel on the head away from the midline goes to the skin round it)
    hwv = np.zeros(nw); hwc = np.zeros(nw); hsel = W[:nb, [i for i, k in enumerate(names) if k in ('head', 'headfront')]].sum(1); np.add.at(hwv, inv, hsel); np.add.at(hwc, inv, 1); hwv /= np.maximum(hwc, 1)
    selH = body[T].all(1) & small & (hwv[np.maximum(wid[T], 0)] > 0.9).all(1); hy_, hx_, ht_, hb2 = tb_.rasterize(uv, T, res, selH)
    qh = (P[T[ht_]] * hb2[:, :, None]).sum(1); colh = lin(img2[hy_, hx_].astype(np.float64)); far = lowpass(30); ch = (far[wid[T[ht_]]] * hb2[:, :, None]).sum(1)
    sp = (srgb(colh)[:, 1] < 0.4) & (np.abs(qh[:, 0]) > 0.1)
    if sp.any(): img2[hy_[sp], hx_[sp]] = srgb(ch[sp]).astype(np.float32)
    if verbose: print(f'{nm}: {int(sp.sum())} red specks on the head repainted skin')
    # the dorsal band
    D = DORSAL[nm]; O = np.array(D['O']); selD = body[T].all(1) & small; low = lowpass(8)   # (the colour as it is now, the bridge's new skin in it)
    dy_, dx_, dt_, db_ = tb_.rasterize(uv, T, res, selD); Wd = wid[T[dt_]]; q = (P[T[dt_]] * db_[:, :, None]).sum(1); cl = (low[Wd] * db_[:, :, None]).sum(1)
    th = np.degrees(np.arctan2(q[:, 1] - O[1], q[:, 2] - O[2])) % 360.0; ax_ = np.abs(q[:, 0])
    oth = W[:, [i for i, k in enumerate(names) if k.startswith(('tail', 'thigh', 'shin', 'foot', 'toe', 'upperarm', 'forearm', 'hand', 'finger'))]].sum(1)
    otx = (oth[T[dt_]] * db_).sum(1)                                             # (the tail's and the limbs' share: never in the band)
    if 'meas' in D: meas = (th > D['meas'][0]) & (th < D['meas'][1]) & (ax_ < 0.05) & (otx < 0.05); band = cl[meas].mean(0) if meas.sum() > 50 else None
    else: band = lin(np.array(D['colour'], float))
    if band is not None:
        sm = lambda x: np.clip(x, 0, 1) ** 2 * (3 - 2 * np.clip(x, 0, 1))
        kout = sm((th - D['gone']) / (D['full'] - D['gone']))                     # (full from the nape down, nothing before the brow)
        kin = 1 - sm((th - D['in1']) / (D['in0'] - D['in1']))                     # (fading in from the mid torso)
        kk = kout * kin * (1 - sm(otx / 0.3))                                     # (never on the tail or the limbs)
        hw_ = np.interp(th, *D['hw'])                                             # (its half width: narrowing over the nape and the crown)
        wd = D['k'] * kk * np.exp(-2.0 * (ax_ / hw_) ** 4)                       # (flat-topped, soft-edged: like the trunk's own band)
        old = lin(img2[dy_, dx_].astype(np.float64)); ratio = np.clip(band[None, :] / np.maximum(cl, 1e-4), 0.08, 1.6)
        img2[dy_, dx_] = srgb(old * (1 + (ratio - 1) * wd[:, None])).astype(np.float32)
        if verbose: print(f'{nm}: dorsal band colour {np.round(srgb(band), 3).tolist()} (sRGB) at {D["k"]} over {int((wd > 0.05).sum())} texels; from {D["in0"]} deg round O {O.tolist()} to {D["gone"]} (the brow); {int((~small & body[T].all(1)).sum())} body triangles too wide in the atlas to paint')
        dsel = wd > 0.002; dy_, dx_ = dy_[dsel], dx_[dsel]
    return (ny_, nx_), (dy_, dx_)
def fix(nm, src, texdir, out, verbose=True):
    meta = json.load(open(f'{src}/axo_{nm}.json')); b = bytearray(open(f'{src}/axo_{nm}.bin', 'rb').read()); o = meta['off7']; n = meta['n']
    caps = json.load(open(f'{src}/axo_{nm}_caps.json')); cv = np.zeros(n, bool); cv[caps['cap_verts']] = True; nb = caps['n_body']
    P = np.frombuffer(bytes(b), np.float32, n * 3, o['position']).reshape(n, 3).astype(float)
    T = np.frombuffer(bytes(b), np.uint16, meta['ni'], o['index']).reshape(-1, 3).astype(np.int64)
    uv = np.frombuffer(bytes(b), np.uint16, n * 2, o['uv']).reshape(n, 2).astype(float) / 65535
    si = np.frombuffer(bytes(b), np.uint8, n * 4, o['skinIndex']).reshape(n, 4); sw = np.frombuffer(bytes(b), np.uint8, n * 4, o['skinWeight']).reshape(n, 4)
    names = [x['name'] for x in meta['bones']]; W = np.zeros((n, len(names)))
    for c in range(4): np.add.at(W, (np.arange(n), si[:, c].astype(int)), sw[:, c] / 255)
    bi = {k: i for i, k in enumerate(names)}; hw = W[:, bi['head']] + W[:, bi['headfront']]
    body = np.arange(n) < nb; span = np.max(np.max(uv[T], 1) - np.min(uv[T], 1), 1); small = span < 0.05   # (never a triangle straddling the atlas)
    capT = cv[T].any(1) & body[T].all(1) & small; headT = (hw[T] > 0.5).all(1) & ~cv[T].any(1) & body[T].all(1) & small
    res = meta['texRes']; img = tb.load_tex(f'{texdir}/axo_{nm}_tex.png', fill_gutters=False); assert img.shape[0] == res
    ty, tx, tt, tb_ = tb.rasterize(uv, T, res, capT); hy, hx, ht, hb_ = tb.rasterize(uv, T, res, headT)
    qc = (P[T[tt]] * tb_[:, :, None]).sum(1); qh = (P[T[ht]] * hb_[:, :, None]).sum(1); colh = lin(img[hy, hx].astype(np.float64)); colc = lin(img[ty, tx].astype(np.float64))
    kd = cKDTree(qh); new = colc.copy()
    # per hole (its texels are those nearest its centre): the plain head texels in a ring 10 to 25 cm round it
    cen = P[caps['centres']]
    if len(qc) and len(cen):
        _, labels = cKDTree(cen).query(qc)
        for k in range(len(cen)):
            m = labels == k
            if not m.any(): continue
            c = cen[k]; near = kd.query_ball_point(c, 0.25); near = [j for j in near if np.linalg.norm(qh[j] - c) > 0.1]
            target = colh[near].mean(0) if len(near) > 50 else colh.mean(0)
            new[m] = target[None, :] + (colc[m] - colc[m].mean(0)) * 0.1
    img2 = img.copy(); img2[ty, tx] = srgb(new).astype(np.float32)
    # the join's texels (v10b): the skin there takes the colour between the head's just above and the body's just below, by height, in
    # its own direction round the neck, with a quarter of its own detail kept: no darker band under the chin or at the nape
    ny_ = nx_ = np.zeros(0, int)
    if caps.get('neck_verts') and caps.get('neck_t') is None:
        zv = np.zeros(n, bool); zv[caps['neck_verts']] = True; ax = caps['neck_axis']; o_, nx = np.array(ax['o']), np.array(ax['n'])
        fwdv = np.array([0.0, 0.0, 1.0]) - nx * nx[2]; fwdv /= np.linalg.norm(fwdv); sidev = np.cross(nx, fwdv)
        zT = zv[T].any(1) & body[T].all(1) & small; ny_, nx_, nt_, nb2 = tb.rasterize(uv, T, res, zT); qz = (P[T[nt_]] * nb2[:, :, None]).sum(1); colz = lin(img[ny_, nx_].astype(np.float64))
        refT = ((hw[T] > 0.3).all(1) | zv[T].any(1)) & body[T].all(1) & small & ~zT; ry, rx, rt_, rb = tb.rasterize(uv, T, res, refT); qr = (P[T[rt_]] * rb[:, :, None]).sum(1); colr = lin(img[ry, rx].astype(np.float64))
        def frame(q): rel = q - o_; al = rel @ nx; rad = rel - np.outer(al, nx); return al, np.degrees(np.arctan2(rad @ sidev, rad @ fwdv))
        alz, phz = frame(qz); alr, phr = frame(qr); newz = colz.copy()
        for s0 in range(-180, 180, 45):
            inz = (phz >= s0) & (phz < s0 + 45)
            if not inz.any(): continue
            sec = (phr >= s0 - 20) & (phr < s0 + 65); up = sec & (alr > 0.07) & (alr < 0.16); dn = sec & (alr > -0.46) & (alr < -0.34)
            cu = colr[up].mean(0) if up.sum() > 40 else colr[sec].mean(0); cd = colr[dn].mean(0) if dn.sum() > 40 else cu
            t = np.clip((0.07 - alz[inz]) / 0.41, 0, 1)[:, None]; t = t * t * (3 - 2 * t)
            wt = np.clip((0.10 - alz[inz]) / 0.06, 0, 1); wb_ = np.clip((alz[inz] + 0.30) / 0.08, 0, 1); wgt = (wt * wt * (3 - 2 * wt) * wb_ * wb_ * (3 - 2 * wb_))[:, None]   # (fading into the skin above and below)
            newz[inz] = colz[inz] + (cu * (1 - t) + cd * t + (colz[inz] - colz[inz].mean(0)) * (0.08 if caps.get('lizard') else 0.25) - colz[inz]) * wgt
        img2[ny_, nx_] = srgb(newz).astype(np.float32)
    # the dorsal band carried up the head (v10d, the user: "the darker shade of texture should continue upwards towards the top back of
    # the head from the mid torso up"): the back's darker band, which stopped at the shoulders, runs on from the mid trunk up the nape
    # and over the crown to the top back of the head, narrowing and fading, gone before the brow; the face oval, the cheeks and the ears
    # untouched. The shade is the back band's own colour ratio to the plain side skin (measured on the trunk), so it stays in the back's
    # hue family and keeps the texture's detail; soft edges in height and round the back
    dy_ = dx_ = np.zeros(0, int)
    if caps.get('lizard') and caps.get('neck_axis') and caps.get('neck_t') is None:
        ax = caps['neck_axis']; o_, nx = np.array(ax['o']), np.array(ax['n']); fwdv = np.array([0.0, 0.0, 1.0]) - nx * nx[2]; fwdv /= np.linalg.norm(fwdv); sidev = np.cross(nx, fwdv)
        Cb = np.array(caps['lizard']['C']); alc = float((Cb - o_) @ nx); bones = {x['name']: x for x in meta['bones']}; a_mid = float((np.array(bones['spine1']['pos']) - o_) @ nx)
        trunkw = W[:, bi['chest']] + W[:, bi['spine1']] + W[:, bi['spine']] + W[:, bi['neck']] + hw
        bT = (trunkw[T] > 0.3).all(1) & body[T].all(1) & small; dy_, dx_, dt_, db_ = tb.rasterize(uv, T, res, bT); qd = (P[T[dt_]] * db_[:, None]).sum(1) if False else (P[T[dt_]] * db_[:, :, None]).sum(1)
        rel = qd - o_; al = rel @ nx; rad = rel - np.outer(al, nx); ph = np.degrees(np.abs(np.arctan2(rad @ sidev, rad @ fwdv))); cold = lin(img2[dy_, dx_].astype(np.float64))
        trunk_band = (al > a_mid - 0.12) & (al < a_mid + 0.04); dark = trunk_band & (ph > 150); plain = trunk_band & (ph > 60) & (ph < 120)
        meas = np.minimum(cold[dark].mean(0) / np.maximum(cold[plain].mean(0), 1e-4), 1.0) if dark.sum() > 100 and plain.sum() > 100 else np.array([1.0, 0.4, 0.45])
        ratio = np.array([1.0, 0.40, 0.45])   # (the back band's family on both bodies: the crawl's own measures (1.0, 0.11, 0.19), the stand's band is faint; a red shift, never black)
        sm = lambda x: np.clip(x, 0, 1) ** 2 * (3 - 2 * np.clip(x, 0, 1))
        half = 65 - 40 * sm((al - (alc - 0.25)) / 0.45)                                    # the band's half width round the back: 65 deg on the trunk, 25 on the crown
        wb = 0.7 * sm((al - a_mid) / 0.14) * (1 - sm((al - (alc + 0.08)) / 0.22)) * sm((ph - (180 - half)) / 26)   # (strongest from the mid trunk to the nape, fading over the back of the crown, gone at the top)
        cold2 = cold * (1 + (ratio[None, :] - 1) * wb[:, None]); img2[dy_, dx_] = srgb(cold2).astype(np.float32)
        if verbose: print(f'{nm}: dorsal band ratio {np.round(ratio, 3).tolist()} (measured {np.round(meas, 3).tolist()}) over {int((wb > 0.05).sum())} texels (of {len(dy_)} trunk and head texels), from al {a_mid:.2f} to {alc + 0.32:.2f}')
    if caps.get('neck_t') is not None:
        (ny_, nx_), (dy_, dx_) = lizard_paint(nm, img2, P, T, uv, nb, body, small, caps, res, W, names, verbose)
    cov = np.zeros((res, res), np.float32); cov[ty, tx] = 1; cov[hy, hx] = 1; cov[ny_, nx_] = 1; cov[dy_, dx_] = 1
    ring = binary_dilation(cov > 0, iterations=6) & (cov == 0); fill = tb.dilate(img2, cov, rounds=8); img2[ring] = fill[ring]
    os.makedirs(out, exist_ok=True); Image.fromarray(np.clip(np.round(img2 * 255), 0, 255).astype(np.uint8)).save(f'{out}/axo_{nm}_tex.png')
    tbytes = tb.encode(img2); open(f'{out}/axo_{nm}_tex.webp', 'wb').write(tbytes)
    assert o['tex'] + meta['texLen'] <= len(b) and max(v for k2, v in o.items() if k2 != 'tex') < o['tex']
    b2 = bytes(b[:o['tex']]) + tbytes; b2 += b'\0' * ((-len(b2)) % 4)
    meta2 = dict(meta); meta2['texLen'] = len(tbytes)
    open(f'{out}/axo_{nm}.bin', 'wb').write(b2); json.dump(meta2, open(f'{out}/axo_{nm}.json', 'w'))
    if verbose: print(f'{nm}: {int(capT.sum())} cap triangles, {len(ty)} texels repainted from {len(hy)} head texels; join {len(ny_)} texels blended; {out}/axo_{nm}.bin {len(b2)} bytes (texture {len(tbytes) // 1024} KB)')
if __name__ == '__main__':
    a = sys.argv[1:]; src = WORK + '/rt4'; texdir = S + '/fable2/rt3'; out = WORK + '/rt4'
    while a:
        k = a.pop(0)
        if k == '--src': src = a.pop(0)
        elif k == '--tex': texdir = a.pop(0)
        elif k == '--out': out = a.pop(0)
    for nm in ('stand', 'crawl'): fix(nm, src, texdir, out)
