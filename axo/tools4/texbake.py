# The original Meshy base-colour textures onto the v7 runtime meshes.
# Each runtime mesh (ws/axo/axo_*.bin + .json, format axo7, no UVs) gets its own UV atlas (xatlas, the thin gill fronds left out: they are
# hundreds of tiny sheets that would cost a third of the vertex budget in seam splits, and the shader colours them anyway), and a 2k / 1k
# base-colour texture baked from the model it was built from:
#   crawl: the user's crawl sculpt, straightened as the pipeline straightened it (axo3/crawl_straight2.npz in export units) with its own
#          baked texture (axo/crawl_tex0.png); the right arm and hand are mirror copies of the left, so they look up the mirror point
#   stand: the rigged biped the stand was built from (axo2/stand_src.npz + OFF) with its texture (axo2/stand_tex.png), colour-graded to
#          the crawl's palette (grade.py) so both bodies agree through the morph
# Every texel of the new atlas is a point on the runtime surface; that point is projected onto the source surface (closest point, the
# source's facing side preferred so a fin's two sides and the frills stay apart) and the source texture sampled there, so no runtime
# triangle ever straddles a seam of the source atlas. Vertices are split at the new atlas's chart borders (attributes copied), the gill
# fronds take the UV of the nearest textured vertex (the stalk root's skin colour, continuous at the join).
# Output: <out>/axo_{stand,crawl}.bin / .json (format axo7 + 'uv' and 'tex' sections; the texture (WebP) rides inside the .bin) and the
# textures as PNG / WebP files for viewing.
#   python3 -I texbake.py [out dir] [--res 2048,1024] [--png]
import sys, os, json, time, io
import numpy as np
from scipy.spatial import cKDTree
from scipy.ndimage import map_coordinates
from PIL import Image
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
sys.path.insert(0, S + '/axo2'); sys.path.insert(0, S + '/axo3'); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
RT = S + '/ws/axo'            # today's runtime meshes (the geometry and rig kept as they are)
OUT = S + '/look/rt1'
OFF = np.array([0.0091, -0.023, -0.6231])        # biped -> stand export coordinates (rig7stand.py)
SC, Z0 = 1.15, 0.75; Y0 = 0.418 * SC              # crawl sym -> export (rig7crawl.py)
def unit(v): v = np.asarray(v, float); return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)
def ss(t): t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)

# ---------------- the runtime mesh ----------------
def load_rt(nm, d=RT):
    meta = json.load(open(f'{d}/axo_{nm}.json')); b = open(f'{d}/axo_{nm}.bin', 'rb').read(); o = meta['off7']; n = meta['n']
    r = dict(meta=meta, n=n)
    r['P'] = np.frombuffer(b, np.float32, n * 3, o['position']).reshape(n, 3).copy()
    r['Nq'] = np.frombuffer(b, np.int8, n * 4, o['normal']).reshape(n, 4).copy()
    r['si'] = np.frombuffer(b, np.uint8, n * 4, o['skinIndex']).reshape(n, 4).copy(); r['sw'] = np.frombuffer(b, np.uint8, n * 4, o['skinWeight']).reshape(n, 4).copy()
    r['T'] = np.frombuffer(b, np.uint16, meta['ni'], o['index']).reshape(-1, 3).astype(np.int64)
    r['cp'] = np.frombuffer(b, np.int16, n * 4, o['cpos']).reshape(n, 4).copy()
    for k in ('jelly', 'fill', 'mat'): r[k] = np.frombuffer(b, np.uint8, n * 4, o[k]).reshape(n, 4).copy()
    names = [x['name'] for x in meta['bones']]; W = np.zeros((n, len(names)))
    for c in range(4): np.add.at(W, (np.arange(n), r['si'][:, c].astype(int)), r['sw'][:, c] / 255)
    r['W'] = W; r['names'] = names; r['N'] = unit(r['Nq'][:, :3] / 127.0)
    return r
def region_of(r):
    names = np.array(r['names']); nm = names[np.argmax(r['W'], 1)]
    def reg(k):
        if k.startswith('gill'): return 'gill'
        if k.startswith(('finger', 'toe')) and not k.startswith('toes'): return 'digit'
        if k.startswith(('upperarm', 'forearm', 'hand', 'shoulder')): return 'arm'
        if k.startswith(('thigh', 'shin', 'foot', 'toes')): return 'leg'
        if k.startswith('tail'): return 'tail'
        if k in ('head', 'headfront'): return 'head'
        return 'trunk'
    return np.array([reg(k) for k in nm])

# ---------------- the sources ----------------
class Src:
    """an unwelded textured triangle mesh: positions P (per corner vertex), tris T, uv, its texture (float32 sRGB 0..1), face normals"""
    def __init__(s, P, T, UV, tex, label=None):
        s.P = np.asarray(P, float); s.T = np.asarray(T, np.int64); s.UV = np.asarray(UV, float); s.tex = tex; s.label = label
        s.c = s.P[s.T].mean(1); s.fn = unit(np.cross(s.P[s.T[:, 1]] - s.P[s.T[:, 0]], s.P[s.T[:, 2]] - s.P[s.T[:, 0]])); s.kd = cKDTree(s.c)
    def project(s, q, qn, k=48, side=8.0, tris=None):
        """closest point on the source for points q with normals qn: (tri, bary, dist). A candidate facing away from qn costs extra (side)"""
        from remesh import closest_on_tris
        if tris is None: kd, tmap = s.kd, None
        else: kd = cKDTree(s.c[tris]); tmap = np.asarray(tris)
        k = min(k, kd.n); _, cand = kd.query(q, k); cand = cand.reshape(len(q), -1)
        if tmap is not None: cand = tmap[cand]
        best = np.full(len(q), np.inf); bt = np.zeros(len(q), int); bp = q.copy()
        for j in range(cand.shape[1]):
            t = cand[:, j]; cp = closest_on_tris(q, s.P[s.T[t, 0]], s.P[s.T[t, 1]], s.P[s.T[t, 2]]); d = np.linalg.norm(cp - q, axis=1)
            d = d + side * np.maximum(0, 0.25 - (s.fn[t] * qn).sum(1))
            better = d < best; best[better] = d[better]; bt[better] = t[better]; bp[better] = cp[better]
        A, B, C = s.P[s.T[bt, 0]], s.P[s.T[bt, 1]], s.P[s.T[bt, 2]]; v0 = B - A; v1 = C - A; v2 = bp - A
        d00 = (v0 * v0).sum(1); d01 = (v0 * v1).sum(1); d11 = (v1 * v1).sum(1); d20 = (v2 * v0).sum(1); d21 = (v2 * v1).sum(1); den = np.maximum(d00 * d11 - d01 * d01, 1e-30)
        v = (d11 * d20 - d01 * d21) / den; w = (d00 * d21 - d01 * d20) / den; u = 1 - v - w
        bc = np.clip(np.stack([u, v, w], 1), 0, 1); bc /= bc.sum(1, keepdims=True)
        return bt, bc, np.linalg.norm(bp - q, axis=1)
    def uv_at(s, bt, bc): return (s.UV[s.T[bt]] * bc[:, :, None]).sum(1)
    def sample(s, uv):
        """bilinear sample of the texture at glTF uv (v down from the top row): (n, 3) sRGB 0..1"""
        H, W = s.tex.shape[:2]; x = uv[:, 0] * W - 0.5; y = uv[:, 1] * H - 0.5
        return np.stack([map_coordinates(s.tex[:, :, c], [y, x], order=1, mode='nearest') for c in range(3)], 1)
def load_tex(path):
    im = Image.open(path).convert('RGB'); return np.asarray(im, dtype=np.float32) / 255.0
def source_crawl():
    from geo import M
    mc = M('crawl'); z = np.load(S + '/axo3/crawl_straight2.npz'); Pw = z['P'] * SC + np.array([0, Y0, Z0])
    r = np.load(S + '/axo2/crawl_rig.npz', allow_pickle=True); labw = np.array([str(x) for x in r['labels']])
    I = mc.I0; P = Pw[mc.wid]; lab = labw[mc.wid]
    return Src(P, I, mc.UV.astype(float), load_tex(S + '/axo/crawl_tex0.png'), lab)
def source_stand():
    m = np.load(S + '/axo2/stand_src.npz'); P = m['P'].astype(float) + OFF; I = m['I'].reshape(-1, 3).astype(np.int64)
    # labels: the welded rig labels through the weld map
    key = np.round(m['P'].astype(float), 5); _, idx, inv = np.unique(key, axis=0, return_index=True, return_inverse=True)
    r = np.load(S + '/axo2/stand_rig.npz', allow_pickle=True); labw = np.array([str(x) for x in r['labels']]); lab = labw[inv.ravel()] if len(labw) == len(idx) else None
    return Src(P, I, m['UV'].astype(float), load_tex(S + '/axo2/stand_tex.png'), lab)

# ---------------- the atlas ----------------
def unwrap(P, T, keep, res, padding=4):
    """xatlas on the kept triangles; returns new vertex -> old vertex map, new tris (all, in the input order), uv per new vertex.
    Triangles left out reuse any copy of their vertices (a vertex only they use is added once); their uv is the nearest textured vertex's."""
    import xatlas
    kt = np.where(keep)[0]; atlas = xatlas.Atlas(); atlas.add_mesh(P.astype(np.float32), T[kt].astype(np.uint32))
    co = xatlas.ChartOptions(); co.max_cost = 32; co.roundness_weight = 0.001; co.normal_deviation_weight = 0.5
    po = xatlas.PackOptions(); po.resolution = res; po.padding = padding; po.bilinear = True
    atlas.generate(chart_options=co, pack_options=po); vm, idx, uv = atlas[0]; vm = vm.astype(np.int64); idx = idx.astype(np.int64); uv = uv.astype(float)
    n = len(P); first = -np.ones(n, np.int64); first[vm[::-1]] = np.arange(len(vm))[::-1]   # (the first copy of each old vertex)
    T2 = np.zeros_like(T); T2[kt] = idx
    extra = np.where(first < 0)[0]; ex_map = dict(zip(extra.tolist(), (len(vm) + np.arange(len(extra))).tolist()))
    vm2 = np.r_[vm, extra]; uv2 = np.vstack([uv, np.zeros((len(extra), 2))])
    lt = np.where(~keep)[0]
    for ti in lt:
        for k in range(3):
            v = T[ti, k]; T2[ti, k] = first[v] if first[v] >= 0 else ex_map[v]
    # uv for the untextured vertices: the nearest textured vertex's (3D)
    if len(extra):
        tv = np.arange(len(vm)); kd = cKDTree(P[vm]); _, j = kd.query(P[extra]); uv2[len(vm):] = uv[j]
    return vm2, T2, uv2, atlas.chart_count, (atlas.width, atlas.height)
def rasterize(uv, T, res, keep):
    """per texel of a res x res atlas covered by a kept triangle: (texel y, texel x, tri, bary). Texel centres at (i + 0.5); glTF v runs down"""
    ys, xs, ts, bs = [], [], [], []
    U = uv * res
    for ti in np.where(keep)[0]:
        a, b, c = U[T[ti]]
        x0 = int(np.floor(min(a[0], b[0], c[0]))); x1 = int(np.ceil(max(a[0], b[0], c[0]))); y0 = int(np.floor(min(a[1], b[1], c[1]))); y1 = int(np.ceil(max(a[1], b[1], c[1])))
        x0 = max(x0, 0); y0 = max(y0, 0); x1 = min(x1, res - 1); y1 = min(y1, res - 1)
        if x1 < x0 or y1 < y0: continue
        gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5); px = gx.ravel(); py = gy.ravel()
        det = (b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])
        if abs(det) < 1e-12: continue
        l1 = ((b[0] - px) * (c[1] - py) - (c[0] - px) * (b[1] - py)) / det   # weight of a
        l2 = ((c[0] - px) * (a[1] - py) - (a[0] - px) * (c[1] - py)) / det   # weight of b
        l3 = 1 - l1 - l2
        eps = -0.75 / max(1e-6, np.sqrt(abs(det)))   # a little outside the edges too (a texel's centre just past a border still belongs to it)
        ins = (l1 >= eps) & (l2 >= eps) & (l3 >= eps)
        if not ins.any(): continue
        bc = np.stack([l1[ins], l2[ins], l3[ins]], 1); bc = np.clip(bc, 0, 1); bc /= bc.sum(1, keepdims=True)
        ys.append((py[ins] - 0.5).astype(int)); xs.append((px[ins] - 0.5).astype(int)); ts.append(np.full(ins.sum(), ti)); bs.append(bc)
    return np.concatenate(ys), np.concatenate(xs), np.concatenate(ts), np.concatenate(bs)
def despeckle(img, cov, res, max_area=None):
    """small patches of frond red on the skin (a texel whose closest source point was a frill fused onto the neck) refilled from the skin
    round them; the dorsal band is as saturated but runs in one large piece, so only small connected patches go"""
    from scipy.ndimage import label
    max_area = max_area or int(1500 * (res / 2048) ** 2)
    mx = img.max(2); mn = img.min(2); sat = (mx - mn) / np.maximum(mx, 1e-3)
    frond = (sat > 0.75) & (mx > 0.6) & (img[:, :, 0] > img[:, :, 1]) & (img[:, :, 0] > img[:, :, 2]) & (cov > 0)
    lab, nl = label(frond)
    if nl == 0: return img, 0
    area = np.bincount(lab.ravel()); small = (area < max_area); small[0] = False; spk = small[lab]
    if not spk.any(): return img, 0
    # grow each speck by 2 texels (its soft edge), then fill from outside
    from scipy.ndimage import binary_dilation
    spk = binary_dilation(spk, iterations=2) & (cov > 0)
    out = dilate(img, (cov > 0) & ~spk, rounds=40); img = img.copy(); img[spk] = out[spk]
    return img, int(small.sum())
def dilate(img, cov, rounds=12):
    """fill uncovered texels from covered neighbours, outward, so mipmaps and bilinear taps near chart borders stay in the chart's colour"""
    img = img.copy(); cov = cov.astype(np.float32).copy()
    for _ in range(rounds):
        acc = np.zeros_like(img); cnt = np.zeros(cov.shape, np.float32)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            sh = np.roll(np.roll(img, dy, 0), dx, 1); sc = np.roll(np.roll(cov, dy, 0), dx, 1)
            acc += sh * sc[:, :, None]; cnt += sc
        fill = (~cov.astype(bool)) & (cnt > 0)
        img[fill] = acc[fill] / cnt[fill][:, None]; cov[fill] = 1
        if cov.all(): break
    # whatever is still empty: the mean colour
    if not cov.all(): img[~cov.astype(bool)] = img[cov.astype(bool)].mean(0)
    return img

# ---------------- the bake ----------------
def bake(nm, src, res, lookup, verbose=True):
    t0 = time.time(); r = load_rt(nm); P, T, N = r['P'].astype(float), r['T'], r['N']; n = r['n']; reg = region_of(r)
    gillW = r['W'][:, [i for i, k in enumerate(r['names']) if k.startswith('gill')]].sum(1); thin = r['jelly'][:, 2] / 255.0
    frond = (gillW > 0.5) & (thin > 0.35)
    keep = ~frond[T].all(1)   # the thin gill fronds stay out of the atlas
    vm, T2, uv, nch, asz = unwrap(P, T, keep, res)
    if verbose: print(f'{nm}: {nch} charts ({asz[0]}x{asz[1]} packed), {len(vm)} verts from {n} (+{100 * (len(vm) / n - 1):.0f}%), {int((~keep).sum())} frond tris untextured ({time.time() - t0:.1f}s)')
    ty, tx, tt, tb = rasterize(uv, T2, res, keep)
    if verbose: print(f'  {len(ty)} texels ({100 * len(ty) / res / res:.0f}% of {res}x{res}) ({time.time() - t0:.1f}s)')
    # the texel's point on the runtime surface, its normal, its region (the corner it leans on most)
    V = vm[T2[tt]]; q = (P[V] * tb[:, :, None]).sum(1); qn = unit((N[V] * tb[:, :, None]).sum(1)); qreg = reg[V[np.arange(len(V)), np.argmax(tb, 1)]]
    col = np.zeros((len(q), 3), np.float32); dist = np.zeros(len(q))
    for kind, sel in lookup(q, qn, qreg, src):
        if not sel.any(): continue
        bt, bc, d = kind(q[sel], qn[sel]); col[sel] = src.sample(src.uv_at(bt, bc)); dist[sel] = d
        if verbose: print(f'  lookup {int(sel.sum())} texels: distance p50 {np.percentile(d, 50) * 1000:.1f} p95 {np.percentile(d, 95) * 1000:.1f} max {d.max() * 1000:.0f} mm ({time.time() - t0:.1f}s)')
    img = np.zeros((res, res, 3), np.float32); cov = np.zeros((res, res), np.float32)
    img[ty, tx] = col; cov[ty, tx] = 1
    img, nsp = despeckle(img, cov, res)
    if verbose: print(f'  despeckle: {nsp} frond-red specks refilled from the skin round them')
    img = dilate(img, cov)
    if verbose: print(f'  atlas done ({time.time() - t0:.1f}s)')
    return dict(r=r, vm=vm, T2=T2, uv=uv, img=img, cov=cov, keep=keep, dist=dist, ty=ty, tx=tx)
def skin_tris(src, near=0.12):
    """the source triangles that are skin: not labelled gill, and not frond-coloured sheets lying within `near` of the gills (the sculpt's
    frills fused onto the neck and shoulders are welded into the skin and labelled trunk; the texture tells them apart)"""
    isg = np.array([l.startswith('gill') for l in src.label])[src.T].any(1)
    col = src.sample(src.UV[src.T].mean(1)); mx = col.max(1); mn = col.min(1); sat = (mx - mn) / np.maximum(mx, 1e-3)
    frond = (sat > 0.72) & (mx > 0.6) & (col[:, 0] > col[:, 1]) & (col[:, 0] > col[:, 2])
    d, _ = cKDTree(src.c[isg]).query(src.c) if isg.any() else (np.full(len(src.T), np.inf), None)
    skin = ~isg & ~(frond & (d < near))
    return np.where(skin)[0]
def lookup_crawl(q, qn, qreg, src):
    """the body straight onto the source's skin; the right arm and hand (mirror copies of the left) through their mirror image; the gill
    stalks onto the skin too (their roots' pink: the shader paints the fronds)"""
    mir = (qreg == 'arm') | (qreg == 'digit'); mir = mir & (q[:, 0] < 0)
    sk = skin_tris(src); M = np.array([-1, 1, 1])
    yield (lambda a, b: src.project(a, b, tris=sk)), ~mir
    yield (lambda a, b: src.project(a * M, b * M, tris=sk)), mir
def lookup_stand(q, qn, qreg, src):
    sk = skin_tris(src) if src.label is not None else np.arange(len(src.T))
    yield (lambda a, b: src.project(a, b, tris=sk)), np.ones(len(q), bool)

# ---------------- export ----------------
def export(nm, B, out, tex_bytes, mime='image/webp', extra_meta=None):
    r = B['r']; vm = B['vm']; T2 = B['T2']; n2 = len(vm); meta = dict(r['meta'])
    uvq = np.clip(np.round(B['uv'] * 65535), 0, 65535).astype(np.uint16)
    parts = [('position', r['P'][vm]), ('normal', r['Nq'][vm]), ('skinIndex', r['si'][vm]), ('skinWeight', r['sw'][vm]), ('index', T2.astype(np.uint16).ravel()),
             ('cpos', r['cp'][vm]), ('jelly', r['jelly'][vm]), ('fill', r['fill'][vm]), ('mat', r['mat'][vm]), ('uv', uvq), ('tex', np.frombuffer(tex_bytes, np.uint8))]
    off = {}; o = 0; blobs = []
    for k, a in parts:
        b = np.ascontiguousarray(a).tobytes(); off[k] = o; blobs.append((o, b)); o += len(b); o += (-o) % 4
    buf = bytearray(o)
    for of, b in blobs: buf[of:of + len(b)] = b
    meta.update({'n': n2, 'ni': int(T2.size), 'off7': off, 'texLen': len(tex_bytes), 'texMime': mime, 'texRes': int(B['img'].shape[0])})
    if extra_meta: meta.update(extra_meta)
    open(out + '.bin', 'wb').write(buf); json.dump(meta, open(out + '.json', 'w'))
    print(f'  {out}.bin {len(buf)} bytes ({len(buf) / 1024:.0f} KB: texture {len(tex_bytes) / 1024:.0f} KB), {n2} verts, {len(T2)} tris')
def encode(img, quality=88, fmt='WEBP'):
    im = Image.fromarray(np.clip(np.round(img * 255), 0, 255).astype(np.uint8)); bio = io.BytesIO()
    if fmt == 'WEBP': im.save(bio, 'WEBP', quality=quality, method=6)
    else: im.save(bio, 'JPEG', quality=quality, subsampling=0)
    return bio.getvalue()
if __name__ == '__main__':
    args = sys.argv[1:]; out = OUT; res = {'crawl': 2048, 'stand': 1024}; png = False; which = ['crawl', 'stand']
    while args:
        a = args.pop(0)
        if a == '--res': c, s_ = args.pop(0).split(','); res = {'crawl': int(c), 'stand': int(s_)}
        elif a == '--png': png = True
        elif a == '--only': which = args.pop(0).split(',')
        else: out = a
    os.makedirs(out, exist_ok=True)
    for nm in which:
        src = source_crawl() if nm == 'crawl' else source_stand()
        B = bake(nm, src, res[nm], lookup_crawl if nm == 'crawl' else lookup_stand)
        np.savez(f'{out}/bake_{nm}.npz', vm=B['vm'], T2=B['T2'], uv=B['uv'], keep=B['keep'], cov=B['cov'])
        im = Image.fromarray(np.clip(np.round(B['img'] * 255), 0, 255).astype(np.uint8)); im.save(f'{out}/axo_{nm}_tex.png'); im.save(f'{out}/axo_{nm}_tex_raw.png')   # (raw: before any grade)
        tb = encode(B['img']); open(f'{out}/axo_{nm}_tex.webp', 'wb').write(tb)
        export(nm, B, f'{out}/axo_{nm}', tb)
