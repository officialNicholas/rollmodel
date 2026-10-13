# Stage 3: the new crawl body for the game's pack. Reads fable4/work/rig.npz (stage_rig.py) and the source texture; writes the runtime
# mesh (axo7 .bin + .json, the texture inside) to fable4/rt/axo_crawl.*, copies the v246 stand body (fable3/rt6/axo_stand.*) beside it
# as the pack's stand slot, and packs both into fable4/out (tools/mk_axo_pack.py).
#   python3 -I build.py [--face-r 0.33] [--face-d 0.29] [--tex-res 2048] [--tex-q 88] [--ygamma 0.75] [--cscale 0.85] [--no-pack]
#   (face-r: the head radius the game sizes hats and accessories by, and their anchors; face-d: how far the face plane sits ahead of the
#   face centre, which sets the drawn face's size)
import sys, os, json, io, shutil, subprocess, time; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import finalrig as fr, weights as wt, attrs as at, texture as tx, axo7io, meshkit as mk, dqs
S = fr.S; WK = S + '/fable4/work'; RT = S + '/fable4/rt'; OUT = S + '/fable4/out'
OLD = S + '/fable3/rt6'
FACE = dict(pitch=0.1, half=1.1)        # (look10's FACE: the face cell's centre pitch and half angle)
FACE_EYE = dict(x=0.4, y=0.16, rx=0.3, ry=0.33); MY = -0.5
def arg(k, d, cast=float):
    a = sys.argv; return cast(a[a.index(k) + 1]) if k in a else d
def face_meta(P, N, head_w, rig, r, D=None):
    """the face sphere (centre c, radius r) for the look shader's face projection, the hats (anchor 0.94 r above c) and the face
    accessories (glasses ~1.05 r in front of c): c sits r behind the flat face, so the drawn face lies on it, and 0.94 r under the crown"""
    hv = head_w > 0.95
    crown_ = hv & (np.abs(P[:, 0]) < 0.08); top_ = float(P[crown_, 1].max())
    # (the flat face: forward-facing skin over the head's middle, the band below the crown where the face sits; by shape alone, so the
    # skin weights near the chin do not move it)
    fv = (N[:, 2] > 0.92) & (np.abs(P[:, 0]) < 0.25) & (P[:, 1] > top_ - 0.47) & (P[:, 1] < top_ - 0.12) & (P[:, 2] > 0.3); zf = float(np.percentile(P[fv, 2], 60))
    nf = N[fv].mean(0); nf /= np.linalg.norm(nf)
    crown = hv & (np.abs(P[:, 0]) < 0.08); top = float(P[crown, 1].max())
    k = r / 0.3697; c = np.array([0.0, top - 0.013 * k - 0.94 * r, zf + 0.018 * k - r])
    if D is not None: c[2] = zf - D   # (the drawn face's size: the features land D tan(angle) from c's line, on the face plane D ahead of it)
    # where the drawn features land on the face plane (a ray from c at the feature's yaw and pitch, met with the plane z = zf)
    D = zf - c[2]
    def land(u, v):
        yaw = u * FACE['half']; pit = FACE['pitch'] + v * FACE['half']; x = D * np.tan(yaw); hd = D / np.cos(yaw); return np.array([x, c[1] + hd * np.tan(pit)])
    eye = land(FACE_EYE['x'], FACE_EYE['y']); eye_out = land(FACE_EYE['x'] + FACE_EYE['rx'], FACE_EYE['y']); eye_top = land(FACE_EYE['x'], FACE_EYE['y'] + FACE_EYE['ry']); eye_bot = land(FACE_EYE['x'], FACE_EYE['y'] - FACE_EYE['ry'])
    mouth = land(0, MY); mouth_lo = land(0, MY - 0.18 * 1.35)
    fx = np.abs(P[fv, 0]).max(); fy = (P[fv, 1].min(), P[fv, 1].max())
    info = dict(face_z=zf, face_normal=nf.round(3).tolist(), crown=top, flat_face_halfwidth=round(float(fx), 3), flat_face_y=[round(float(fy[0]), 3), round(float(fy[1]), 3)],
                eye_centre=eye.round(3).tolist(), eye_outer_x=round(float(eye_out[0]), 3), eye_y_span=[round(float(eye_bot[1]), 3), round(float(eye_top[1]), 3)], mouth_y=round(float(mouth[1]), 3), mouth_low_y=round(float(mouth_lo[1]), 3))
    return c, info
def main():
    t0 = time.time(); r_face = arg('--face-r', 0.33); tex_res = arg('--tex-res', 2048, int); tex_q = arg('--tex-q', 88, int)
    z = np.load(WK + '/rig.npz'); Pw, Tw, W, names = z['Pw'], z['Tw'], z['W'], json.loads(str(z['names'])); wid, UV, T = z['wid'], z['UV'], z['T']
    B = {k: (np.array(a), np.array(b)) for k, (a, b) in json.loads(str(z['B'])).items()}; J = {k: np.array(v) for k, v in json.loads(str(z['J'])).items()}
    ears = json.loads(str(z['ears']))
    # the skeleton object, rebuilt from the saved joints (for the frames)
    rig = fr.Rig.__new__(fr.Rig); rig.cur = json.load(open(fr.CUR)); rig.order = [(b['name'], b['parent']) for b in rig.cur['bones']]; rig.B = B; rig.J = J
    W = wt.rigid_head(W, names, Pw, rig); W = wt.top4(W, 0.012)
    jelly, fill, mat, cpos, Nw = at.compute(Pw, Tw, W, names, {k: (a, b) for k, (a, b) in B.items()}, ears)
    head_w = W[:, names.index('head')]
    c, finfo = face_meta(Pw, Nw, head_w, rig, r_face, arg('--face-d', 0.29))
    rig.set_headfront(c, finfo['face_z']); B = rig.B
    # (the hands' and feet's headings, from their own meshes: the wrist / ankle to the middle of the hand's / foot's vertices)
    rig.flat = {}
    for end, dig in (('hand', 'finger'), ('foot', 'toe')):
        for s in 'LR':
            hb = [i for i, n in enumerate(names) if n == f'{end}.{s}' or (n.startswith(dig) and f'.{s}.' in n) or n == f'toes.{s}' and end == 'foot']
            sel = W[:, hb].sum(1) > 0.6; v = Pw[sel].mean(0) - B[f'{end}.{s}'][0]; rig.flat[f'{end}.{s}'] = v
            print(f'  {end}.{s}: level frame, heading {np.degrees(np.arctan2(v[0] * (1 if s == "L" else -1), v[2])):+.1f} deg out from ahead ({int(sel.sum())} vertices)')
    bones = rig.meta_bones()
    hb = [b for b in bones if b['name'] == 'head'][0]
    meta = {'bones': bones, 'headc': np.round(c - np.array(hb['pos']), 4).tolist(), 'headr': round(r_face, 4), 'face': {'c': np.round(c, 4).tolist(), 'r': round(r_face, 4)}}
    # ---- the split mesh (Meshy's UV seams): each copy takes its welded vertex's place, normal, weights and data ----
    idx = np.argsort(-W, 1)[:, :4]; w4 = np.take_along_axis(W, idx, 1); w4 /= w4.sum(1, keepdims=True)
    P = Pw[wid]; N = Nw[wid]; si = idx[wid]; sw = w4[wid]
    # ---- the texture ----
    im, _ = tx.build(WK + '/texture_0.png', UV, T, res=tex_res, ygamma=arg('--ygamma', 0.75), cscale=arg('--cscale', 0.85))
    b = io.BytesIO(); im.save(b, 'WEBP', quality=tex_q, method=6); texb = b.getvalue()
    os.makedirs(RT, exist_ok=True); os.makedirs(OUT, exist_ok=True)
    nbytes = axo7io.write(RT + '/axo_crawl', meta, P, N, si, sw, T, cpos[wid], jelly[wid], fill[wid], mat[wid], uv=UV, tex=texb, texRes=tex_res)
    for ext in ('bin', 'json'): shutil.copy(f'{OLD}/axo_stand.{ext}', f'{RT}/axo_stand.{ext}')
    print(f'  crawl: {len(P)} verts ({len(Pw)} welded), {len(T)} tris; bin {nbytes} bytes (texture {len(texb)} bytes, {tex_res} webp q{tex_q}); bbox {P.min(0).round(3).tolist()} .. {P.max(0).round(3).tolist()}')
    print(f'  face: c {meta["face"]["c"]} r {r_face}; headc {meta["headc"]} (head joint {hb["pos"]}); {finfo}')
    json.dump({'face': meta['face'], 'headc': meta['headc'], 'info': finfo}, open(WK + '/face_meta.json', 'w'), default=float)
    if '--no-pack' not in sys.argv:
        subprocess.run(['python3', '-I', '/home/user/rollmodel/tools/mk_axo_pack.py', RT, OUT], check=True)
    print(f'  build done in {time.time() - t0:.1f}s')
if __name__ == '__main__':
    main()
