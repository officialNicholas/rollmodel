# The comparison sheets for the new crawl body (fable4) beside v246, both on the game's own runtime (the AXO runtime and the AXOC adapter
# taken from the game as it is now), in lab pages served on 8767: fable4/lab_new (the new pack) and fable4/lab_old (axo-pack-246).
#   python3 -I sheets7.py <body|motion|face|wear|teams|all> [--pages new,old] [--name suffix]
import json, subprocess, sys, os
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
HERE = os.path.dirname(os.path.abspath(__file__)); OUTD = S + '/fable4/shots'
U = 'http://localhost:8767/fable4/'
DIRS = {'new': 'lab_new', 'old': 'lab_old'}
TAG = {'new': 'new', 'old': 'v246'}
# (variant packs for comparisons: page 'dNN' is fable4/lab_dNN)
for _v in ('d31', 'd29', 'd27', 'd25', 'r30', 'r28', 'v1', 'v2', 'v3'): DIRS[_v] = 'lab_' + _v; TAG[_v] = _v
SUFFIX = ''
LAB = lambda d: {'url': U + d + '/index.html', 'ready': 'window.LAB && LAB.ready && LAB.I.ax.C.mesh.material.map && LAB.I.ax.C.mesh.material.map.userData.ready', 'shot': 'screenshot', 'init': "LAB.set('idle'); LAB.step(120)"}
def cam(page, label, pos, at, pre='', steps=2): return [page, pre + f"LAB.cam='fixed'; LAB.camPos={json.dumps(pos)}; LAB.camAt={json.dumps(at)}; LAB.step({steps}); LAB.render()", label]
def run(name, pages, cells, W, H, ncol, title):
    out = f'{OUTD}/{name}{SUFFIX}.jpg'; spec = {'out': out, 'W': W, 'H': H, 'ncol': ncol, 'title': title, 'pages': pages, 'cells': cells}
    os.makedirs(OUTD, exist_ok=True); json.dump(spec, open(f'{OUTD}/{name}{SUFFIX}.json', 'w'))
    subprocess.run(['python3', '-I', HERE + '/shoot.py', f'{OUTD}/{name}{SUFFIX}.json'], check=True, env=dict(os.environ, PLAYWRIGHT_BROWSERS_PATH='/opt/pw-browsers'))
    # (the sheet in parts of three rows, for reading)
    from PIL import Image
    im = Image.open(out); Wt, Ht = im.size; nrow = (len(cells) + ncol - 1) // ncol; rh = (Ht - 22) / nrow
    for i in range(0, nrow, 3): im.crop((0, int(22 + i * rh), Wt, int(22 + min(nrow, i + 3) * rh))).save(out.replace('.jpg', f'_p{i // 3 + 1}.jpg'), quality=90)
PG = ['new', 'old']
RESET = "state = 'play'; if (LAB.basin) { scene.remove(LAB.basin); LAB.basin = null; } LAB.D.x = 0; LAB.D.z = 0; LAB.D.y = 0; LAB.D.yaw = 0; LAB.D.spd = 0; LAB.D.turn = 0; LAB.D.air = false; LAB.D.rocket = false; LAB.D.dry = true; LAB.D.vy = 0; LAB.I.ax.coat = 0; LAB.I.ax.wade = 0; LAB.I.ax.wet = 0; LAB.I.ax.A.look.yaw = 0; LAB.I.ax.A.look.pitch = 0; LAB.I.ax.spin = 0; LAB.I.ax.spinV = 0; LAB.I.ax.A.loco = null; LAB.I.setExpression('neutral'); "
NEUTRAL = "LAB.I.setEyeStyle(0); LAB.I.setFangs(false); LAB.I.setLashes(0,0); LAB.I.setPatch(0); LAB.I.setExpression('neutral'); LAB.I.ax.look.exprK = 1; LAB.I.ax.look.expr = 'neutral'; LAB.step(8); LAB.I.ax.look.blinkK = 0; LAB.I.ax.look.blinkT = 9; "
LIGHT = "scene.background = new THREE.Color(0xd9d2c3); floor.visible = true; "
CARPET = ("if (!window.__carpet) { const rc = new THREE.Mesh(new THREE.PlaneGeometry(8, 2.4), new THREE.MeshStandardMaterial({ color: 0xc81428, roughness: 0.35 })); rc.rotation.x = -Math.PI / 2; rc.position.set(0, 0.003, 0.3); rc.receiveShadow = true; scene.add(rc); window.__carpet = rc; } "
          "scene.background = new THREE.Color(0xd6cdc8); floor.visible = true; ")
NOCARPET = "if (window.__carpet) { scene.remove(window.__carpet); window.__carpet = null; } "
CRAWL = "LAB.set('idle'); LAB.I.ax.A.set('crawl'); LAB.I.ax.state = 'crawl'; LAB.step(120); "
# a camera on the head itself (the face centre from AXOC.headTop, world space): d head radii out along the face's forward, up radii above
FACE = lambda d, up, up2: ("{ const I = LAB.I, q = new THREE.Quaternion(), c = AXOC.headTop(I, new THREE.Vector3(), q, 0), wq = new THREE.Quaternion(); I.root.updateWorldMatrix(true, true); "
    "LAB.V.body.getWorldQuaternion(wq); q.premultiply(wq); c.applyMatrix4(LAB.V.body.matrixWorld); const r = AXOC.headSize(I) * LAB.V.body.scale.x, f = new THREE.Vector3(0, 0, 1).applyQuaternion(q), u = new THREE.Vector3(0, 1, 0).applyQuaternion(q); "
    f"LAB.cam = 'fixed'; LAB.camPos = c.clone().addScaledVector(f, {d} * r).addScaledVector(u, {up} * r).toArray(); LAB.camAt = c.clone().addScaledVector(u, {up2} * r).toArray(); }} LAB.render()")
FOLLOW = lambda off, at: ("{ const I = LAB.I, c = AXOC.headTop(I, new THREE.Vector3(), null, 0); I.root.updateWorldMatrix(true, true); c.applyMatrix4(LAB.V.body.matrixWorld); const y = LAB.D.yaw, sy = Math.sin(y), cy = Math.cos(y); "
    f"const o = {json.dumps(off)}, a = {json.dumps(at)}; LAB.cam = 'fixed'; LAB.camPos = [c.x + o[0] * cy + o[2] * sy, c.y + o[1], c.z - o[0] * sy + o[2] * cy]; LAB.camAt = [c.x + a[0] * cy + a[2] * sy, c.y + a[1], c.z - a[0] * sy + a[2] * cy]; }} LAB.render()")
# markers: the hat anchor (green), the neck anchor (blue, AXOC.bodyPoint) and the face centre (yellow), with a brim ring at the hat's size
MARKS = """{ const I = LAB.I; I.root.updateWorldMatrix(true, true); const Wm = LAB.V.body.matrixWorld, q0 = LAB.V.body.getWorldQuaternion(new THREE.Quaternion());
  const t = AXOC.headTop(I, new THREE.Vector3()).applyMatrix4(Wm), hq = new THREE.Quaternion(); AXOC.headTop(I, new THREE.Vector3(), hq); hq.premultiply(q0);
  const c = AXOC.headTop(I, new THREE.Vector3(), null, 0).applyMatrix4(Wm), nk = AXOC.bodyPoint(I, 0, 0, 0, new THREE.Vector3()).applyMatrix4(Wm), hs = AXOC.headSize(I) * 1.3 * LAB.V.body.scale.x;
  const G = window.__mk || (window.__mk = new THREE.Group()); scene.add(G); G.clear();
  const dot = (p, col, r) => { const m = new THREE.Mesh(new THREE.SphereGeometry(r || 0.02, 12, 8), new THREE.MeshBasicMaterial({ color: col, depthTest: false })); m.renderOrder = 99; m.position.copy(p); G.add(m); };
  dot(t, 0x20c020, 0.025); dot(nk, 0x2050ff, 0.025); dot(c, 0xffe000, 0.018);
  const FIT = { top: { s: 0.86, y: -0.13, rx: -0.12, rz: -0.24, c: 0x202060 }, witch: { s: 1.3, y: -0.27, rx: -0.14, rz: -0.16, c: 0x303030 }, pirate: { s: 0.92, y: -0.2, rx: -0.1, rz: 0.06, c: 0x804020 }, tiara: { s: 0.6, y: -0.13, rx: -0.22, rz: 0.05, c: 0xe0c040 }, bunny: { s: 0.92, y: -0.42, rx: -0.06, rz: 0.03, c: 0xff80c0 }, skull: { s: 0.58, y: -0.34, rx: 0.12, rz: 0.55, c: 0xeeeeee } };
  const F = FIT[window.__hatName || 'top'];
  if (window.__hatName) { const ring = new THREE.Mesh(new THREE.TorusGeometry(0.5 * F.s, 0.012, 8, 48), new THREE.MeshBasicMaterial({ color: F.c })); ring.rotateX(Math.PI / 2);
    const hat = new THREE.Group(); hat.add(ring); if (window.__hatName === 'top') { const cyl = new THREE.Mesh(new THREE.CylinderGeometry(0.33 * F.s, 0.33 * F.s, 0.6 * F.s, 24, 1, true), new THREE.MeshBasicMaterial({ color: F.c, wireframe: true })); cyl.position.y = 0.3 * F.s; hat.add(cyl); }
    hat.position.copy(t).add(new THREE.Vector3(0, F.y * hs, 0).applyQuaternion(hq)); hat.quaternion.copy(hq).multiply(new THREE.Quaternion().setFromEuler(new THREE.Euler(F.rx, 0, F.rz))); hat.scale.setScalar(hs); G.add(hat); } } """
CLEARMK = "if (window.__mk) window.__mk.clear(); window.__hatName = null; "
def pages(pg): return {p: LAB(DIRS[p]) for p in pg}
def body():
    pg = PG; cells = []
    CR = RESET + NOCARPET + CLEARMK + LIGHT + NEUTRAL + CRAWL + "LAB.I.ax.look.blinkK = 0; LAB.I.ax.look.blinkT = 9; "
    V = [('lobby front', [0.0, 0.85, 2.1], [0, 0.4, 0.2]), ('lobby 3/4', [1.5, 0.9, 1.5], [0, 0.4, 0.0]), ('lobby side', [2.9, 0.55, -0.5], [0, 0.4, -0.5]),
         ('straight from above', [0.0, 4.6, -0.55], [0, 0.3, -0.55]), ('from behind, above', [0.0, 1.6, -2.6], [0, 0.35, -0.3]), ('3/4 from behind', [1.8, 1.2, -1.8], [0, 0.35, -0.2])]
    for i, (lab, pos, at) in enumerate(V):
        for p in pg: cells.append(cam(p, f'{TAG[p]}: {lab}', pos, at, pre=CR if i == 0 else 'LAB.step(2); '))
    WIN = RESET + NOCARPET + CLEARMK + LIGHT + CRAWL + "LAB.I.setExpression('glee'); LAB.step(12); LAB.I.ax.look.blinkK = 0; LAB.I.ax.look.blinkT = 9; "
    for p in pg: cells.append(cam(p, f'{TAG[p]}: win screen, low front (glee)', [0.0, 0.22, 2.0], [0, 0.42, 0.2], pre=WIN))
    for p in pg: cells.append([p, "LAB.step(2); " + FACE(4.4, -0.8, -0.3), f'{TAG[p]}: win screen close, a little below the face'])
    for p in pg: cells.append([p, "LAB.step(2); scene.background = new THREE.Color(0x1a1a1e); floor.visible = false; " + FACE(3.4, -1.7, -0.6) + "; scene.background = new THREE.Color(0xd9d2c3); floor.visible = true;", f'{TAG[p]}: under the chin (dark)'])
    UP = "LAB.I.ax.A.look.pitch = 25; LAB.step(40); LAB.I.ax.look.blinkK = 0; LAB.I.ax.look.blinkT = 9; "
    for p in pg: cells.append(cam(p, f'{TAG[p]}: win screen, low front, head up 25', [0.0, 0.22, 2.0], [0, 0.45, 0.2], pre=UP))
    for p in pg: cells.append(cam(p, f'{TAG[p]}: low 3/4 close, head up', [0.9, 0.2, 1.2], [0, 0.42, 0.15], pre="LAB.step(2); "))
    LK = RESET + CARPET + CLEARMK + NEUTRAL + CRAWL + "LAB.I.ax.A.look.pitch = 28; LAB.step(60); LAB.I.ax.look.blinkK = 0; LAB.I.ax.look.blinkT = 9; "
    for p in pg: cells.append(cam(p, f'{TAG[p]}: locker camera, red carpet', [0.0, 1.0, 2.7], [0, 0.4, 0.25], pre=LK))
    for p in pg: cells.append(cam(p, f'{TAG[p]}: locker 3/4', [1.6, 1.0, 2.2], [0, 0.4, 0.25], pre="LAB.step(2); "))
    run('body', pages(pg), cells, 520, 440, 2, 'the crawl body: ' + ' / '.join(TAG[p] for p in pg))
def motion():
    pg = PG; cells = []
    WV = RESET + NOCARPET + CLEARMK + LIGHT + "LAB.set('weave', {v: 5.4, k: 0.9, T: 1.4}); LAB.step(75); "
    for p in pg: cells.append([p, WV + FOLLOW([1.9, 0.8, 1.8], [0, -0.15, -0.3]), f'{TAG[p]}: weave (the neck turn)'])
    for p in pg: cells.append([p, "LAB.step(10); " + FOLLOW([0.2, 2.6, -0.2], [0, -0.2, -0.4]), f'{TAG[p]}: weave, from above'])
    for p in pg: cells.append([p, "LAB.step(21); " + FOLLOW([-1.9, 0.8, 1.8], [0, -0.15, -0.3]), f'{TAG[p]}: weave, the other way'])
    WK = RESET + NOCARPET + CLEARMK + LIGHT + "LAB.set('walk', {v: 5.4}); LAB.step(90); "
    for p in pg: cells.append([p, WK + FOLLOW([2.0, 0.6, 1.2], [0, -0.2, -0.5]), f'{TAG[p]}: crawl gait'])
    for p in pg: cells.append([p, "LAB.step(9); " + FOLLOW([0.0, 0.1, 2.0], [0, -0.1, 0.0]), f'{TAG[p]}: crawl gait, low front'])
    for p in pg: cells.append([p, "LAB.step(7); " + FOLLOW([2.6, 0.2, -0.4], [0, -0.2, -0.5]), f'{TAG[p]}: crawl gait, side'])
    SLOW = RESET + NOCARPET + CLEARMK + LIGHT + "LAB.set('walk', {v: 1.6}); LAB.step(120); "
    for p in pg: cells.append([p, SLOW + FOLLOW([1.8, 0.9, 1.2], [0, -0.3, -0.5]), f'{TAG[p]}: slow crawl (feet planted)'])
    CL = RESET + NOCARPET + CLEARMK + LIGHT + CRAWL + "LAB.I.ax.A.look.yaw = 45; LAB.I.ax.A.look.pitch = 25; LAB.step(60); LAB.I.ax.look.blinkK = 0; LAB.I.ax.look.blinkT = 9; "
    for p in pg: cells.append(cam(p, f'{TAG[p]}: head look yaw 45 pitch 25', [1.2, 0.8, 1.5], [0, 0.4, 0.0], pre=CL))
    for p in pg: cells.append(cam(p, f'{TAG[p]}: head look yaw -45 pitch -20, low', [-1.0, 0.25, 1.5], [0, 0.4, 0.0], pre="LAB.I.ax.A.look.yaw = -45; LAB.I.ax.A.look.pitch = -20; LAB.step(40); LAB.I.ax.look.blinkK = 0; LAB.I.ax.look.blinkT = 9; "))
    for p in pg: cells.append(cam(p, f'{TAG[p]}: head look yaw -45 pitch -20, from behind', [0.9, 1.2, -1.6], [0, 0.45, 0.0], pre="LAB.step(2); "))
    GL = RESET + NOCARPET + CLEARMK + LIGHT + CRAWL + "{ const N = LAB.I.ax.A.neck; N.glance = [30, -4, 0]; N.holdT = 1; N.glanceT = 3; } LAB.step(30); LAB.I.ax.look.blinkK = 0; LAB.I.ax.look.blinkT = 9; "
    for p in pg: cells.append(cam(p, f'{TAG[p]}: idle glance 30 deg', [0.3, 0.7, 1.9], [0, 0.4, 0.0], pre=GL))
    SW = RESET + NOCARPET + CLEARMK + LIGHT + "LAB.D.dry = false; LAB.set('walk', {v: 5.4}); LAB.step(90); "
    for p in pg: cells.append([p, SW + FOLLOW([2.0, 0.7, 1.2], [0, -0.2, -0.5]), f'{TAG[p]}: swimming (in paint)'])
    for p in pg: cells.append([p, "LAB.step(13); " + FOLLOW([0.3, 2.4, -0.3], [0, -0.2, -0.4]), f'{TAG[p]}: swimming, from above'])
    for p in pg: cells.append([p, "LAB.step(17); " + FOLLOW([-1.6, 0.4, 1.6], [0, -0.2, -0.4]), f'{TAG[p]}: swimming, glide'])
    BL = RESET + NOCARPET + CLEARMK + LIGHT + "LAB.set('fling', {c: 1, at: 0.3, every: 99}); LAB.step(30); "
    for p in pg: cells.append([p, BL + FOLLOW([1.6, 0.4, 1.4], [0, -0.1, 0.0]), f'{TAG[p]}: the ball (slingshot flight)'])
    for p in pg: cells.append([p, "LAB.step(5); " + FOLLOW([-1.4, 0.9, -1.4], [0, -0.1, 0.0]), f'{TAG[p]}: the ball, from behind'])
    JP = RESET + NOCARPET + CLEARMK + LIGHT + "LAB.set('jump', {v: 4, at: 0.3}); LAB.step(28); "
    for p in pg: cells.append([p, JP + FOLLOW([1.5, 0.3, 1.5], [0, -0.2, -0.2]), f'{TAG[p]}: jump, rising'])
    for p in pg: cells.append([p, "LAB.step(14); " + FOLLOW([1.5, 0.3, 1.5], [0, -0.2, -0.2]), f'{TAG[p]}: jump, top'])
    LD = RESET + NOCARPET + CLEARMK + LIGHT + "LAB.set('jump', {v: 4, at: 0.3}); LAB.step(28); while (LAB.D.air) LAB.step(1); LAB.step(6); "
    for p in pg: cells.append([p, LD + FOLLOW([1.4, 0.4, 1.4], [0, -0.25, -0.2]), f'{TAG[p]}: landing +6'])
    CB = RESET + NOCARPET + CLEARMK + LIGHT + "LAB.set('climb', {T: 2.0}); LAB.step(95); "
    for p in pg: cells.append([p, CB + FOLLOW([1.5, 0.6, 1.3], [0, -0.2, -0.3]), f'{TAG[p]}: climbing out of a basin'])
    for p in pg: cells.append([p, "LAB.step(15); " + FOLLOW([1.5, 0.6, 1.3], [0, -0.2, -0.3]), f'{TAG[p]}: climbing out, later'])
    HOP = RESET + NOCARPET + CLEARMK + LIGHT + CRAWL + "state = 'menu'; LAB.I.setExpression('glee'); LAB.set('jump', {v: 0, at: 0.2, every: 0.9}); LAB.step(40); "
    for p in pg: cells.append(cam(p, f'{TAG[p]}: win hops (menu), in the air', [0.0, 0.5, 2.3], [0, 0.55, 0.2], pre=HOP))
    for p in pg: cells.append(cam(p, f'{TAG[p]}: win hops, landing', [0.0, 0.5, 2.3], [0, 0.45, 0.2], pre="while (LAB.D.air) LAB.step(1); LAB.step(4); "))
    CT = RESET + NOCARPET + CLEARMK + LIGHT + CRAWL + "LAB.I.setPaint(new THREE.Color(0x2a7fff)); LAB.I.coatOn(); LAB.step(90); LAB.I.ax.look.blinkK = 0; LAB.I.ax.look.blinkT = 9; "
    for p in pg: cells.append(cam(p, f'{TAG[p]}: coated in paint, low front', [0.0, 0.25, 2.0], [0, 0.42, 0.2], pre=CT))
    for p in pg: cells.append(cam(p, f'{TAG[p]}: coated, 3/4 from behind', [1.4, 1.0, -1.4], [0, 0.4, -0.1], pre="LAB.step(2); "))
    WD = RESET + NOCARPET + CLEARMK + LIGHT + CRAWL + "LAB.I.setPaint(new THREE.Color(0x2a7fff)); LAB.I.setWade(1); LAB.I.ax.wet = 1; LAB.step(60); "
    for p in pg: cells.append(cam(p, f'{TAG[p]}: wading (paint up the legs and belly)', [1.5, 0.6, 1.5], [0, 0.3, 0.0], pre=WD))
    run('motion', pages(pg), cells, 520, 440, 2, 'the crawl in motion: ' + ' / '.join(TAG[p] for p in pg))
def face():
    pg = PG; cells = []
    EX = ['neutral', 'happy', 'angry', 'hurt', 'glee', 'scared']
    F0 = RESET + NOCARPET + CLEARMK + LIGHT + CRAWL
    for i, e in enumerate(EX):
        for p in pg: cells.append([p, (F0 if i == 0 else '') + f"LAB.I.setEyeStyle(0); LAB.I.setFangs(false); LAB.I.setExpression('{e}'); LAB.I.ax.look.exprK = 1; LAB.I.ax.look.expr = '{e}'; LAB.I.ax.look.blinkK = 0; LAB.step(10); LAB.I.ax.look.blinkK = 0; " + FACE(4.0, 0.0, 0.0), f'{TAG[p]}: {e}'])
    for nm, k in [('round', 0), ('squid', 1), ('dot', 2), ('zombie', 3)]:
        for p in pg: cells.append([p, f"LAB.I.setEyeStyle({k}); LAB.I.setFangs(true); LAB.I.setExpression('happy'); LAB.I.ax.look.exprK = 1; LAB.I.ax.look.expr = 'happy'; LAB.I.ax.look.blinkK = 0; LAB.step(10); LAB.I.ax.look.blinkK = 0; " + FACE(4.0, 0.0, 0.0), f'{TAG[p]}: eyes {nm} + fangs'])
    for p in pg: cells.append([p, "LAB.I.setEyeStyle(0); LAB.I.setFangs(false); LAB.I.setLashes(1,1); LAB.I.setPatch(1); LAB.I.setExpression('neutral'); LAB.I.ax.look.exprK = 1; LAB.I.ax.look.expr = 'neutral'; LAB.step(10); LAB.I.ax.look.blinkK = 0; " + FACE(4.0, 0.0, 0.0), f'{TAG[p]}: lashes + patch'])
    for p in pg: cells.append([p, "LAB.I.setLashes(0,0); LAB.I.setPatch(0); LAB.step(2); " + FACE(2.6, 0.4, 0.1), f'{TAG[p]}: face close, from a little above'])
    for p in pg: cells.append([p, "LAB.step(2); " + FACE(2.6, -0.2, 0.0).replace('addScaledVector(f, 2.6 * r)', 'addScaledVector(f, 2.6 * r).addScaledVector(new THREE.Vector3(1, 0, 0).applyQuaternion(q), 1.6 * r)'), f'{TAG[p]}: face 3/4 close'])
    run('face', pages(pg), cells, 420, 400, 4, 'the drawn face: ' + ' / '.join(TAG[p] for p in pg))
def wear():
    pg = PG; cells = []
    W0 = RESET + NOCARPET + LIGHT + NEUTRAL + CRAWL
    for i, nm in enumerate(['top', 'witch', 'pirate', 'tiara', 'bunny', 'skull']):
        for p in pg: cells.append(cam(p, f'{TAG[p]}: {nm} fit (ring at its brim), 3/4', [1.1, 0.9, 1.5], [0, 0.55, 0.2], pre=(W0 if i == 0 else '') + f"window.__hatName = '{nm}'; LAB.step(2); " + MARKS))
        for p in pg: cells.append(cam(p, f'{TAG[p]}: {nm} fit, side', [1.8, 0.7, 0.2], [0, 0.6, 0.1], pre=MARKS))
    for p in pg: cells.append(cam(p, f'{TAG[p]}: anchors (green hat, blue neck, yellow face), front', [0.0, 0.7, 1.9], [0, 0.5, 0.2], pre="window.__hatName = null; LAB.step(2); " + MARKS))
    for p in pg: cells.append(cam(p, f'{TAG[p]}: anchors, side', [1.8, 0.6, 0.3], [0, 0.5, 0.1], pre=MARKS))
    for p in pg: cells.append(cam(p, f'{TAG[p]}: anchors, head look yaw 40 pitch 20', [0.8, 0.8, 1.7], [0, 0.55, 0.2], pre="LAB.I.ax.A.look.yaw = 40; LAB.I.ax.A.look.pitch = 20; LAB.step(40); " + MARKS))
    for p in pg: cells.append([p, "LAB.I.ax.A.look.yaw = 0; LAB.I.ax.A.look.pitch = 0; window.__hatName = 'top'; LAB.set('walk', {v: 5.4}); LAB.step(60); " + FOLLOW([1.5, 0.3, 1.0], [0, -0.25, -0.2]) + "; " + MARKS + "; LAB.render()", f'{TAG[p]}: anchors in the gait (top hat ring)'])
    for p in pg: cells.append([p, "LAB.step(9); " + FOLLOW([0.2, 0.1, 1.8], [0, -0.2, 0.0]) + "; " + MARKS + "; LAB.render()", f'{TAG[p]}: anchors in the gait, low front'])
    run('wear', pages(pg), cells, 420, 400, 4, 'the wearing anchors and hat fits: ' + ' / '.join(TAG[p] for p in pg))
def teams():
    pg = PG; cells = []
    TEAM = [('red', '0xe3122f'), ('blue', '0x2f8cff'), ('amber', '0xffb300'), ('green', '0x3cc43c'), ('violet', '0x9b4de0'), ('pink', '0xff5fa2')]
    for i, (nm, hx) in enumerate(TEAM):
        for p in pg: cells.append(cam(p, f'{TAG[p]}: {nm}', [1.3, 0.9, 1.6], [0, 0.42, 0.0], pre=(RESET + NOCARPET + CLEARMK + LIGHT + NEUTRAL + CRAWL if i == 0 else '') + f"LAB.I.setColor(new THREE.Color({hx})); LAB.step(4); "))
    run('teams', pages(pg), cells, 420, 360, 4, 'team colours: ' + ' / '.join(TAG[p] for p in pg))
if __name__ == '__main__':
    a = sys.argv[1:]
    if '--pages' in a: i = a.index('--pages'); PG = a[i + 1].split(','); del a[i:i + 2]
    if '--name' in a: i = a.index('--name'); SUFFIX = a[i + 1]; del a[i:i + 2]
    which = a or ['body']
    for w in which:
        if w == 'all': [f() for f in (body, motion, face, wear, teams)]
        else: globals()[w]()
