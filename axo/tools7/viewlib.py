# Helpers for the raw mesh viewer (fable4/view/index.html on 8767): write a mesh (with optional per-vertex colours and line segments, e.g.
# a skeleton) for it, and shoot sheets of perspective or orthographic views.
import json, subprocess, os
import numpy as np
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'; VIEW = S + '/fable4/view'; HERE = os.path.dirname(os.path.abspath(__file__))
def write(base, P, N, UV, T, col=None, lines=None, lcol=None, tex=None):
    meta = {'n': int(len(P)), 'nt': int(len(T))}
    parts = [np.asarray(P, np.float32), np.asarray(N, np.float32), np.asarray(UV, np.float32), np.asarray(T, np.uint32)]
    if col is not None: parts.append(np.asarray(col, np.float32)); meta['col'] = 1
    if lines is not None:
        L = np.asarray(lines, np.float32).reshape(-1, 6); C = np.asarray(lcol if lcol is not None else np.tile([1, 0, 0], (len(L) * 2, 1)), np.float32).reshape(-1, 6)
        parts += [L, C]; meta['lines'] = int(len(L))
    open(f'{VIEW}/{base}.bin', 'wb').write(b''.join(p.tobytes() for p in parts)); json.dump(meta, open(f'{VIEW}/{base}.json', 'w'))
    if tex is not None:
        import shutil; shutil.copy(tex, f'{VIEW}/{base}_tex.jpg')
def shoot(base, out, cells, W=520, H=520, ncol=4, title=None, tex=None):
    url = f'http://localhost:8767/fable4/view/index.html?m={base}' + (f'&t={tex}' if tex else '')
    spec = {'out': out, 'W': W, 'H': H, 'ncol': ncol, 'title': title or base, 'pages': {'v': {'url': url, 'ready': 'window.ready', 'shot': 'screenshot'}}, 'cells': [['v', js, lab] for lab, js in cells]}
    json.dump(spec, open(out + '.json', 'w')); env = dict(os.environ, PLAYWRIGHT_BROWSERS_PATH='/opt/pw-browsers')
    subprocess.run(['python3', '-I', HERE + '/shoot.py', out + '.json'], check=True, env=env)
def ortho(view, c, h, mode='grey', axes=False, lines=True): return f"V.mode('{mode}'); V.show({str(axes).lower()}, {str(lines).lower()}); V.ortho('{view}', {json.dumps(list(c))}, {h})"
def persp(pos, at, mode='tex', axes=False, lines=True): return f"V.mode('{mode}'); V.show({str(axes).lower()}, {str(lines).lower()}); V.cam({json.dumps(list(pos))}, {json.dumps(list(at))})"
def ortho_axes(view):
    """(screen-right axis, screen-up axis) as (index, sign) pairs for an orthographic view of index.html's V.ortho"""
    return {'top': ((0, 1), (2, -1)), 'bottom': ((0, -1), (2, -1)), 'side': ((2, -1), (1, 1)), 'sidel': ((2, 1), (1, 1)), 'front': ((0, 1), (1, 1)), 'back': ((0, -1), (1, 1))}[view]
def ortho_centre(view, c):
    """V.ortho's centre c is in world coordinates of the view plane's two axes (top: x, z; side: z, y; front: x, y): as screen (a, b)"""
    (ia, sa), (ib, sb) = ortho_axes(view); w = {'top': (0, 2), 'bottom': (0, 2), 'side': (2, 1), 'sidel': (2, 1), 'front': (0, 1), 'back': (0, 1)}[view]
    p = [0.0, 0.0, 0.0]; p[w[0]] = c[0]; p[w[1]] = c[1]; return sa * p[ia], sb * p[ib]
def measure_sheet(base, out, views, W=1000, H=1000, mode='grey', tex=None, marks=None):
    """orthographic views with the grid labelled (every 0.1; numbers every 0.2) and optional marked points {name: xyz} drawn as dots"""
    from PIL import Image, ImageDraw, ImageFont
    cells = [(f'{v} c={c} h={h}', ortho(v, c, h, mode)) for v, c, h in views]
    shoot(base, out, cells, W=W, H=H, ncol=len(views), title=base, tex=tex)
    im = Image.open(out).convert('RGB'); dr = ImageDraw.Draw(im)
    try: font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 12)
    except Exception: font = None
    for k, (v, c, h) in enumerate(views):
        ox, oy = k * W, 22; s = H / (2 * h); (ia, sa), (ib, sb) = ortho_axes(v); ca, cb = ortho_centre(v, c)
        def px(p): return ox + W / 2 + (sa * p[ia] - ca) * s, oy + H / 2 - (sb * p[ib] - cb) * s
        for g in np.arange(-4, 4.001, 0.2):
            X = ox + W / 2 + (g - ca) * s; Y = oy + H / 2 - (g - cb) * s
            if ox < X < ox + W: dr.text((X + 2, oy + H - 16), f'{sa * g:+.1f}', fill=(120, 0, 0), font=font)
            if oy < Y < oy + H: dr.text((ox + 3, Y - 14), f'{sb * g:+.1f}', fill=(0, 0, 140), font=font)
        dr.text((ox + 6, oy + 20), f'right: {"xyz"[ia]}{"+" if sa > 0 else "-"}  up: {"xyz"[ib]}{"+" if sb > 0 else "-"}', fill=(0, 0, 0), font=font)
        for nm, p in (marks or {}).items():
            x, y = px(p); dr.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(255, 255, 0), outline=(0, 0, 0)); dr.text((x + 5, y - 6), nm, fill=(0, 0, 0), font=font)
    im.save(out, quality=90)
