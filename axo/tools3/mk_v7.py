# the v7 review sheets: python3 -I mk_v7.py [names...] [--url URL] [--out DIR]
import json, sys, os, subprocess, math
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
HERE = S + '/axo3'
args = sys.argv[1:]; URL = 'http://localhost:8811/merged/preview.html?manual'; OUT = S + '/axo3/out/v7/'   # the final merged runtime (ws/axo)
if '--url' in args: i = args.index('--url'); URL = args[i + 1]; del args[i:i + 2]
if '--out' in args: i = args.index('--out'); OUT = args[i + 1]; del args[i:i + 2]
os.makedirs(OUT, exist_ok=True)
def cells_run(name, cells, W=400, H=400, ncol=4, title=None, init=None):
    spec = dict(url=URL, out=OUT + f'v7_{name}.jpg', cells=cells, W=W, H=H, ncol=ncol, title=title, init=init)
    p = OUT + f'_{name}.json'; json.dump(spec, open(p, 'w'))
    subprocess.run([sys.executable, '-I', HERE + '/v_cells.py', p], check=True)
def frames_run(name, state, settle, cells, W=300, H=300, ncol=8, pre=''):
    # cells: [frame, yaw, pitch, dist, joint, [ox, oy, oz], label]; frames increasing
    spec = dict(url=URL, out=OUT + f'v7_{name}.jpg', state=state, settle=settle, cells=cells, W=W, H=H, ncol=ncol, pre=pre)
    subprocess.run([sys.executable, '-I', HERE + '/v_frames.py', json.dumps(spec)], check=True)
RESET = "axo.setLook(0,0); axo.look.setExpression('neutral'); axo.A.motion.speed=1; axo.A.motion.turn=0; axo.A.motion.exert=0"
def pose_sheet(name, st, title):
    c = []
    for yaw, pitch, dist, lab in ((0.0, 0.12, 3.4, 'front'), (math.pi / 2, 0.1, 3.4, 'side (left)'), (math.pi, 0.15, 3.4, 'back'), (-0.8, 0.35, 3.4, 'front 3/4 right, above'),
                                  (2.3, 0.05, 3.0, 'back 3/4 left, low'), (0.0, 1.35, 3.4, 'top'), (math.pi / 2, -0.05, 1.9, 'side close'), (0.5, 0.2, 1.6, 'front 3/4 close')):
        c.append([RESET if not c else '', st if not c else None, 150 if not c else 0, [yaw, pitch, dist, 'hips', 0, 0.1, 0], f'{st}: {lab}'])
    cells_run(name, c, 420, 420, 4, title)
SHEETS = {}
def sheet(f): SHEETS[f.__name__] = f; return f
@sheet
def pound(): pose_sheet('pound', 'pound', 'ground-pound wind-up: fists tucked by the hips (never in front of the face), gills folded back and in, tail curled under the groin between the legs')
@sheet
def jetpack(): pose_sheet('jetpack', 'jetpack', 'jetpack: arms down along the sides, fists closed, looking down at the ground, tail hanging straight down')
@sheet
def crouch():
    pose_sheet('crouch', 'crouch', 'crouch: palms flat on the floor, the tail curving down to lie along the floor')

STILL = "axo.look.blinkT=1e9; axo.look.blinkK=0; axo.look.att.t=1e9; axo.look.att.eye=[0,0]; axo.look.dartT=1e9; axo.look.dart=[0,0]; axo.A.neck.glanceT=1e9; axo.A.neck.glance=[0,0,0]; axo.A.flickT=1e9"
LIVE = "axo.look.blinkT=2; axo.look.att.t=1; axo.look.dartT=0.5; axo.A.neck.glanceT=1; axo.A.flickT=2"
REC1 = [2.55, 0.12, 0.95, 'thigh.L', [0.06, -0.05, -0.05]]
@sheet
def hindleg():
    # the left hind leg from the rec1 angle, every frame of one full crawl cycle (1.1 Hz: 55 frames); then the right from the mirrored angle
    y, p, d, j, o = REC1
    frames_run('hindleg', 'crawl', 150, [[f, y, p, d, j, o, f'hind leg L, rec1 angle, f{f}'] for f in range(0, 56)], 250, 250, 8, pre=RESET)
    frames_run('hindleg_R', 'crawl', 150, [[f, -y, p, d, 'thigh.R', [-o[0], o[1], o[2]], f'hind leg R, mirrored rec1, f{f}'] for f in range(0, 56)], 250, 250, 8, pre=RESET)
    # both legs from behind / above through the cycle (every 4 frames)
    frames_run('hindleg_both', 'crawl', 150, [[f, 3.14, 0.45, 1.5, 'hips', [0, -0.1, 0], f'both hind legs from behind, f{f}'] for f in range(0, 56, 4)] +
               [[f, 3.14, -0.02, 1.4, 'hips', [0, -0.15, 0], f'both hind legs low behind, f{f}'] for f in range(56, 112, 4)], 280, 260, 7, pre=RESET)
@sheet
def feet():
    c = [[f, 1.75, 0.05, 0.75, 'foot.L', [0.02, 0.0, 0.0], f'hind foot L, rec2 angle, f{f}'] for f in range(0, 56, 2)]
    frames_run('feet', 'crawl', 150, c, 250, 230, 7, pre=RESET)
    c = [[f, -1.75, 0.05, 0.75, 'foot.R', [-0.02, 0.0, 0.0], f'hind foot R, mirrored, f{f}'] for f in range(0, 56, 2)]
    frames_run('feet_R', 'crawl', 150, c, 250, 230, 7, pre=RESET)
    c = [[f, 1.45, 0.05, 0.75, 'hand.L', [0.02, 0.0, 0.0], f'front hand L, rec2-style angle, f{f}'] for f in range(0, 56, 2)]
    frames_run('hands', 'crawl', 150, c, 250, 230, 7, pre=RESET)
    c = [[f, -1.45, 0.05, 0.75, 'hand.R', [-0.02, 0.0, 0.0], f'front hand R, mirrored, f{f}'] for f in range(0, 56, 2)]
    frames_run('hands_R', 'crawl', 150, c, 250, 230, 7, pre=RESET)
    # the stand's feet and hands
    c = []
    for st in ('stand', 'power', 'victory', 'crouch'):
        c.append([RESET, st, 150, [0.0, 0.25, 0.9, None, 0, 0.1, 0.1], f'{st}: feet front'])
        c.append(['', None, 0, [1.3, 0.1, 0.7, 'foot.L', 0.03, 0, 0], f'{st}: foot L side'])
        c.append(['', None, 0, [-1.3, 0.1, 0.7, 'foot.R', -0.03, 0, 0], f'{st}: foot R side'])
    cells_run('feet_stand', c, 330, 300, 6, 'stand mesh: feet in the standing states (front, left side, right side)')
@sheet
def arms():
    c = []
    for st, d in (('stand', 1.2), ('power', 1.2), ('victory', 1.4), ('pound', 1.2), ('jetpack', 1.2), ('crouch', 1.3), ('crawl', 1.2)):
        pre = RESET + (';axo.A.motion.speed=0' if st == 'crawl' else '')
        c.append([pre + ';' + STILL, st, 150, [0.95, 0.15, d, 'upperarm.L', 0.1, -0.15, 0.05], f'{st}: left arm'])
        c.append(['', None, 0, [-0.95, 0.15, d, 'upperarm.R', -0.1, -0.15, 0.05], f'{st}: right arm (mirrored camera)'])
    cells_run('arms', c, 360, 340, 4, 'left vs right arm, mirrored cameras, same frame (life frozen: no glances or blinks)')
@sheet
def poseL():
    pass

def chart(series, out, title, W=1200, H=300, rng=(-20, 20), labels=('yaw', 'pitch', 'roll'), cols=((220, 60, 60), (40, 140, 60), (50, 90, 220)), dt=1 / 60, marks=None):
    from PIL import Image, ImageDraw, ImageFont
    try: F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 13)
    except Exception: F = None
    im = Image.new('RGB', (W, H), (255, 255, 255)); d = ImageDraw.Draw(im); L, R, T, B = 50, 20, 28, 30; n = len(series)
    X = lambda i: L + (W - L - R) * i / max(1, n - 1); Y = lambda v: T + (H - T - B) * (rng[1] - v) / (rng[1] - rng[0])
    for v in range(rng[0], rng[1] + 1, 5): d.line([(L, Y(v)), (W - R, Y(v))], fill=(225, 225, 225) if v else (150, 150, 150)); d.text((8, Y(v) - 7), f'{v:+d}', fill=(90, 90, 90), font=F)
    for s_ in range(0, int(n * dt) + 1): d.line([(X(s_ / dt), T), (X(s_ / dt), H - B)], fill=(235, 235, 235)); d.text((X(s_ / dt) - 6, H - B + 6), f'{s_}s', fill=(90, 90, 90), font=F)
    if marks:
        for i, m in enumerate(marks):
            if m: d.line([(X(i), H - B - 8), (X(i), H - B)], fill=(120, 120, 120))
    for k, (lab, c) in enumerate(zip(labels, cols)):
        pts = [(X(i), Y(max(rng[0], min(rng[1], row[k])))) for i, row in enumerate(series)]; d.line(pts, fill=c, width=2); d.text((L + 10 + 90 * k, 6), lab + ' (deg)', fill=c, font=F)
    d.text((L + 300, 6), title, fill=(20, 20, 20), font=F); im.save(out); return im
@sheet
def neck():
    import subprocess, json as J
    probe = HERE + '/out/probe_neck.js'
    subprocess.run([sys.executable, '-I', HERE + '/jsprobe_f.py', URL, probe, HERE + '/out/neck_series.json'], check=True)
    d = J.load(open(HERE + '/out/neck_series.json'))
    from PIL import Image
    ims = []
    for st in ('stand', 'crawl'):
        ser = d[st]; base = [sum(r[k] for r in ser) / len(ser) for k in range(3)]
        rows = [[r[0] - base[0], r[1] - base[1], r[2] - base[2]] for r in ser]
        ims.append(chart(rows, HERE + f'/out/neck_{st}.png', f'{st}: the head relative to its mean over 10 s (glances, overshoot settles, breath bob, drift); ticks = blinks', marks=[r[5] for r in ser]))
    # frame strips: a fixed camera on the head, every 10 frames
    c = []
    for st, yaw, dist in (('stand', 0.35, 1.3), ('crawl', 0.35, 1.3)):
        pre = RESET + ';' + LIVE + (';axo.A.motion.speed=0.4' if st == 'crawl' else '')
        for i in range(16): c.append([pre if i == 0 else '', st if i == 0 else None, 150 if i == 0 else 10, [yaw, 0.12, dist, '@head', 0, 0.1, 0], f'{st} +{i * 10} f (fixed camera)'])
    cells_run('neck_frames', c, 300, 280, 8, 'neck micro-animation: a fixed camera on the head, every 10 frames (1/6 s)')
    strip = Image.open(OUT + 'v7_neck_frames.jpg'); Wd = max(strip.width, 1200)
    sh = Image.new('RGB', (Wd, strip.height + 600), (255, 255, 255)); sh.paste(ims[0], (0, 0)); sh.paste(ims[1], (0, 300)); sh.paste(strip, (0, 600)); sh.save(OUT + 'v7_neck.jpg', quality=88)
    os.remove(OUT + 'v7_neck_frames.jpg'); print(OUT + 'v7_neck.jpg')

def seq_run(out, frm, to, settle, n, every, cam, W, H, ncol, slow=1, first=None, pre='', title=None):
    a = dict(url=URL, out=out, **{'from': frm, 'to': to}, settle=settle, n=n, every=every, cam=cam, W=W, H=H, ncol=ncol, slow=slow, pre=pre, title=title)
    if first is not None: a['first'] = first
    subprocess.run([sys.executable, '-I', HERE + '/v_seq.py', json.dumps(a)], check=True)
def stack(parts, out, quality=86):
    from PIL import Image
    ims = [Image.open(p) for p in parts]; W = max(i.width for i in ims); H = sum(i.height for i in ims)
    sh = Image.new('RGB', (W, H), (255, 255, 255)); y = 0
    for i in ims: sh.paste(i, (0, y)); y += i.height
    sh.save(out, quality=quality)
    for p in parts: os.remove(p)
    print(out, sh.size)
@sheet
def transition():
    pre = RESET + ';' + LIVE
    side = [0.9, 0.22, 3.6, 0.5, 0, -0.3, 30]; back = [2.4, 0.3, 3.4, 0.45, 0, -0.35, 30]
    P = []
    for k, (frm, to, settle) in enumerate((('stand', 'crawl', 120), ('crawl', 'stand', 150))):
        o = OUT + f'_t{k}a.jpg'; seq_run(o, frm, to, settle, 35, 2, side, 290, 240, 9, pre=pre, title=f'{frm} -> {to}, full speed, every 2nd frame (1/30 s), front 3/4'); P.append(o)
        o = OUT + f'_t{k}b.jpg'; seq_run(o, frm, to, settle, 26, 3, back, 290, 240, 9, pre=pre, title=f'{frm} -> {to}, full speed, every 3rd frame, back 3/4 (legs and tail)'); P.append(o)
    stack(P, OUT + 'v7_transition.jpg')
    # slowed x4 through the morph (the dither change-over of the hips, legs and tail, then of the chest, arms and head), close on the body
    P = []
    hip = [1.25, 0.18, 2.0, 0.35, 0, -0.45, 30]
    for k, (frm, to, settle) in enumerate((('stand', 'crawl', 120), ('crawl', 'stand', 150))):
        o = OUT + f'_s{k}.jpg'; seq_run(o, frm, to, settle, 40, 2, hip, 290, 240, 8, slow=4, first=60, pre=pre, title=f'{frm} -> {to}, slowed x4 (dt 1/240 s), every 2nd sub-frame from t=0.25 s through the morph'); P.append(o)
    stack(P, OUT + 'v7_transition_slow.jpg')

EXPRS = ['neutral', 'happy', 'angry', 'hurt', 'glee', 'scared', 'yawn', 'dizzy', 'peek', 'leap', 'brace']
def mesh_pre(st):
    return RESET + ';' + STILL + (';axo.A.motion.speed=0' if st == 'crawl' else '')
@sheet
def face():
    c = []
    # stand vs crawl at the same distance from the face, same camera, neutral; then the same from 3/4
    for st in ('stand', 'crawl'):
        c.append([mesh_pre(st), st, 160, [0.0, 0.05, 1.5, 'HC', 0, 0, 0], f'{st}: face front, 1.5 m from the face centre'])
        c.append(['', None, 0, [0.6, 0.12, 1.5, 'HC', 0, 0, 0], f'{st}: face 3/4, 1.5 m'])
    cells_run('face_pair', c, 480, 440, 4, 'the same face on both bodies: stand vs crawl at the same camera distance from the face centre')
    c = []
    for st in ('stand', 'crawl'):
        for i, e in enumerate(EXPRS):
            c.append([(mesh_pre(st) if i == 0 else '') + f";axo.look.setExpression('{e}')", st if i == 0 else None, 160 if i == 0 else 20, [0.25, 0.05, 1.25, 'HC', 0, 0, 0], f'{st}: {e}'])
    cells_run('face_expr', c, 300, 290, 11, 'expressions (the game slime\'s face sheets), stand row then crawl row')
    c = []
    for st in ('stand', 'crawl'):
        for i, (k, nm) in enumerate((('round', 'Round'), ('edgy', 'Squid'), ('dot', 'Dot'), ('zombie', 'Zombie'))):
            c.append([(mesh_pre(st) if i == 0 else '') + f";axo.look.setExpression('neutral'); axo.look.setIris('violet'); axo.look.setEyeStyle('{k}')", st if i == 0 else None, 160 if i == 0 else 10, [0.15, 0.05, 1.1, 'HC', 0, 0.02, 0], f'{st}: eyes {nm}'])
        for i, (k, nm) in enumerate((('brown', 'Brown'), ('blue', 'Blue'), ('green', 'Green'), ('violet', 'Violet'), ('gold', 'Gold'))):
            c.append([f"axo.look.setEyeStyle('round'); axo.look.setIris('{k}')", None, 10, [0.15, 0.05, 1.1, 'HC', 0, 0.02, 0], f'{st}: iris {nm}'])
    c.append(["axo.look.setIris('violet'); axo.look.setEyeStyle('round')", None, 1, [0.15, 0.05, 1.1, 'HC', 0, 0.02, 0], 'reset'])
    cells_run('face_eyes', c[:-1], 300, 290, 9, 'eye styles and iris colours (the game\'s), stand row then crawl row')
    stack([OUT + 'v7_face_pair.jpg', OUT + 'v7_face_expr.jpg', OUT + 'v7_face_eyes.jpg'], OUT + 'v7_face.jpg')
TEAM = [('pink', '0xff6b8a'), ('red', '0xe3122f'), ('amber', '0xffb300'), ('green', '0x3bd16f'), ('blue', '0x2f8cff'), ('violet', '0x9b5cff'), ('cyan', '0x22d3e6'), ('orange', '0xff7a1a')]
@sheet
def colors():
    c = []
    for st in ('stand', 'crawl'):
        for i, (nm, hx) in enumerate(TEAM):
            c.append([(mesh_pre(st) if i == 0 else '') + f';axo.look.setColor({hx}); axo.look.setPaint(0)', st if i == 0 else None, 160 if i == 0 else 4, ([0.75, 0.2, 3.3, 'hips', 0, 0.15, 0] if st == 'stand' else [0.75, 0.25, 3.9, 'spine', 0, 0.05, 0]), f'{st}: team {nm}'])
    cells_run('colors_team', c, 300, 280, 8, 'team colour drives the hue (base, gills, fin), the spots, belly and face stay in character; stand row then crawl row')
    c = []
    for st in ('stand', 'crawl'):
        for i, lv in enumerate((0, 0.35, 0.7, 1.0)):
            c.append([(mesh_pre(st) if i == 0 else '') + f';axo.look.setColor(0x2f8cff); axo.look.setPaint({lv})', st if i == 0 else None, 160 if i == 0 else 4, ([0.75, 0.2, 3.3, 'hips', 0, 0.15, 0] if st == 'stand' else [0.75, 0.25, 3.9, 'spine', 0, 0.05, 0]), f'{st}: paint coat {lv}'])
    c.append(['axo.look.setColor(0xff6b8a); axo.look.setPaint(0)', None, 1, [0, 0, 3, 'hips', 0, 0, 0], 'reset'])
    cells_run('colors_paint', c[:-1], 300, 280, 8, 'the paint coat (team blue) at 0, 0.35, 0.7, 1: stand row then crawl row')
    stack([OUT + 'v7_colors_team.jpg', OUT + 'v7_colors_paint.jpg'], OUT + 'v7_colors.jpg')
@sheet
def materials():
    c = []
    # both bodies at the same distance, same lighting: side, back 3/4 (dorsal speckles), belly from below-front, close skin
    for st in ('stand', 'crawl'):
        jt = 'hips' if st == 'stand' else 'spine'; ty = 0.15 if st == 'stand' else 0.0
        d1, d2 = (3.4, 2.8) if st == 'stand' else (4.6, 3.9)
        c.append([mesh_pre(st), st, 160, [1.57, 0.12, d1, jt, 0, ty, 0], f'{st}: side, {d1} m'])
        c.append(['', None, 0, [2.5, 0.5, d2, jt, 0, ty, 0], f'{st}: back 3/4 above (dorsal speckles, mottling)'])
        c.append(['', None, 0, [0.4, -0.25, 1.6, 'chest', 0, 0, 0], f'{st}: belly from below-front (pale belly, sheen)'])
        c.append(['', None, 0, [1.2, 0.3, 0.55, 'spine1', 0.12, 0.05, 0], f'{st}: skin close (speckles, pores, relief)'])
    cells_run('mat_pair', c, 380, 340, 4, 'both bodies, same distance and light: stand row then crawl row')
    c = []
    for st in ('stand', 'crawl'):
        # backlit tail: the camera on the far side of the key light (key from front-right-above), the fin between them
        c.append([mesh_pre(st), st, 160, [-1.57, 0.1, 2.0, 'tail3', 0, 0, 0], f'{st}: tail, the side away from the light (light through the fin)'])
        c.append(['', None, 0, [1.57, 0.1, 2.0, 'tail3', 0, 0, 0], f'{st}: tail, the lit side (core band, lit edge)'])
        c.append(['', None, 0, [-2.6, -0.25, 1.5, 'tail4', 0, 0.1, 0], f'{st}: tail from below-behind, toward the light'])
        c.append(['', None, 0, [-0.9, 0.25, 0.9, 'gill1.R.1', -0.1, 0.05, 0], f'{st}: gills backlit (feathery, saturated)'])
        c.append(['', None, 0, [0.9, 0.2, 0.75, 'gill1.L.1', 0.1, 0.05, 0], f'{st}: gills front-lit'])
        c.append(['', None, 0, [0.6, 0.0, 0.5, 'hand.L', 0, 0.03, 0], f'{st}: wrist and fingers (wrinkle bands)'])
    cells_run('mat_detail', c, 340, 320, 6, 'tail translucency, gills, wrinkles: stand row then crawl row')
    stack([OUT + 'v7_mat_pair.jpg', OUT + 'v7_mat_detail.jpg'], OUT + 'v7_materials.jpg')
if __name__ == '__main__':
    for n in (args or list(SHEETS)): print('==', n); SHEETS[n]()
