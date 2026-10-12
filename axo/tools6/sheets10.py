# The comparison sheets for the v10 pass (the slime's head and ears): the head beside the slime's recording and the present axolotl,
# the ears in every pose, the faces, the hats, the two material variants, the paint coat. Pages are lab copies under fable3 served on
# port 8767: A (fable3/lab, variant A), B (fable3/labB), cur (fable3/lab_cur, the present axolotl from ws/lab).
#   python3 -I sheets10.py <head|poses|faces|hats|mats|coat|all> [--pages A,B,cur]
import json, subprocess, sys, os
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
WORK = S + '/fable3'; HERE = os.path.dirname(os.path.abspath(__file__))
U = 'http://localhost:8767/fable3/'
DIRS = {'6': 'lab6', '5': 'lab5', 'A': 'lab', 'B': 'labB', 'cur': 'lab_cur', 'v239': 'lab_v239'}
LAB = lambda d, dark=False: {'url': U + d + '/index.html', 'ready': 'window.LAB && LAB.ready', 'shot': 'screenshot', 'init': "LAB.set('idle'); LAB.step(120)" + ("; scene.background = new THREE.Color(0x1a1a1e); floor.visible = false" if dark else '')}
def cam(page, label, pos, at, pre='', steps=2): return [page, pre + f"LAB.cam='fixed'; LAB.camPos={json.dumps(pos)}; LAB.camAt={json.dumps(at)}; LAB.step({steps}); LAB.render()", label]
# a camera placed relative to the character's head (off and at as [side, up, forward] in its own frame, from the head joint's world
# place), for the scenarios that move it about
def rcam(page, label, off, at, pre='', steps=2):
    js = (f"LAB.step({steps}); {{ const D = LAB.D, h = LAB.feet().head, sy = Math.sin(D.yaw), cy = Math.cos(D.yaw), o = {json.dumps(off)}, a = {json.dumps(at)}; "
          "LAB.cam = 'fixed'; LAB.camPos = [h[0] + o[0] * cy + o[2] * sy, h[1] + o[1], h[2] - o[0] * sy + o[2] * cy]; LAB.camAt = [h[0] + a[0] * cy + a[2] * sy, h[1] + a[1], h[2] - a[0] * sy + a[2] * cy]; } LAB.render()")
    return [page, pre + js, label]
def img(path, label, crop=None): return [None, json.dumps({'img': path, 'crop': crop}), label]
def run(name, pages, cells, W, H, ncol, title):
    spec = {'out': f'{WORK}/shots/{name}.jpg', 'W': W, 'H': H, 'ncol': ncol, 'title': title, 'pages': pages, 'cells': cells}
    os.makedirs(f'{WORK}/shots', exist_ok=True); json.dump(spec, open(f'{WORK}/shots/{name}.json', 'w')); subprocess.run(['python3', '-I', HERE + '/shoot.py', f'{WORK}/shots/{name}.json'], check=True)
PG = ['A', 'B', 'cur']
RESET = "if (LAB.basin) { scene.remove(LAB.basin); LAB.basin = null; } LAB.D.x = 0; LAB.D.z = 0; LAB.D.y = 0; LAB.D.yaw = 0; LAB.D.spd = 0; LAB.D.turn = 0; LAB.D.air = false; LAB.D.rocket = false; LAB.D.dry = true; "
NEUTRAL = "LAB.I.setEyeStyle(0); LAB.I.setFangs(false); LAB.I.setLashes(0,0); LAB.I.setPatch(0); LAB.I.setExpression('neutral'); LAB.I.ax.look.exprK = 1; LAB.I.ax.look.expr = 'neutral'; LAB.step(8); LAB.I.ax.look.blinkK = 0; "
def tag(p): return {'A': 'v10 A', 'B': 'v10 B', 'cur': 'current', '5': 'v10d', '6': 'v10e'}[p]
REF = S + '/ref_slime_rec'
def head():
    pages = {p: LAB(DIRS[p]) for p in PG}; cells = []
    # the slime's recording: a front-ish frame, a 3/4 and a side-ish one (the sheet's frames, cropped round the character)
    cells.append(img(REF + '/f03.png', 'slime recording', [60, 40, 300, 300])); cells.append(img(REF + '/f08.png', 'slime recording', [60, 40, 300, 300])); cells.append(img(REF + '/f12.png', 'slime recording', [60, 40, 300, 300]))
    shots = [('lobby distance, front', [0.0, 0.55, 1.75], [0, 0.44, 0.33]), ('lobby distance, 3/4', [1.05, 0.7, 1.4], [0, 0.44, 0.33]), ('lobby distance, side', [1.75, 0.5, 0.33], [0, 0.44, 0.33]),
             ('head front', [0.0, 0.55, 1.6], [0, 0.47, 0.33]), ('head 3/4', [1.0, 0.75, 1.25], [0, 0.47, 0.33]), ('head side', [1.5, 0.52, 0.33], [0, 0.49, 0.33]),
             ('head from above', [0.05, 1.9, 0.5], [0, 0.45, 0.33]), ('head low 3/4', [1.0, 0.25, 1.2], [0, 0.45, 0.33]), ('from behind', [0.3, 0.9, -1.5], [0, 0.42, 0.33]),
             ('whole, game 3/4', [2.2, 1.4, 2.6], [0, 0.3, 0.0]), ('neck and shoulders, side', [1.6, 0.45, 0.1], [0, 0.38, 0.15])]
    for lab, pos, at in shots:
        for p in PG: cells.append(cam(p, f'{tag(p)}: {lab}', pos, at, pre=NEUTRAL if lab.startswith('lobby distance, front') else ''))
    for p in PG: cells.append(cam(p, f'{tag(p)}: portrait, dark ground', [0.0, 0.55, 1.35], [0, 0.47, 0.33], pre="scene.background = new THREE.Color(0x1a1a1e); floor.visible = false; LAB.I.setExpression('happy'); LAB.step(12); LAB.I.ax.look.blinkK = 0; "))
    for p in PG: cells.append(cam(p, f'{tag(p)}: portrait 3/4, dark ground', [0.7, 0.6, 1.2], [0, 0.47, 0.33], pre="LAB.I.setExpression('neutral'); LAB.step(12); LAB.I.ax.look.blinkK = 0; "))
    for p in PG: cells.append(cam(p, f'{tag(p)}: stand, side (amber)', [1.6, 1.2, 0.3], [0, 1.1, 0.1], pre="scene.background = new THREE.Color(0xd9d2c3); floor.visible = true; LAB.I.setColor(new THREE.Color(0xffb300)); LAB.I.ax.A.set('stand'); LAB.step(150); "))
    for p in PG: cells.append(cam(p, f'{tag(p)}: stand, front (amber)', [0.0, 1.2, 1.9], [0, 1.0, 0.0], pre=""))
    run('head_cmp', pages, cells, 420, 400, 3, 'the head: slime recording / v10 A / v10 B / current (lab, 8767)')
def poses():
    pages = {p: LAB(DIRS[p]) for p in PG}; cells = []
    P = [('crawl gait', RESET + "LAB.set('walk', {v: 5.4}); LAB.step(90); ", [1.3, 0.5, 1.4], [0, 0.0, 0.1]),
         ('crawl gait, side', "LAB.step(7); ", [1.9, 0.3, 0.0], [0, -0.05, -0.1]),
         ('swim', RESET + "LAB.D.dry = false; LAB.set('walk', {v: 5.4}); LAB.step(110); ", [1.3, 0.5, 1.4], [0, 0.0, 0.1]),
         ('swim, side', "LAB.step(9); ", [1.9, 0.3, 0.0], [0, -0.05, -0.1]),
         ('turn (weave)', RESET + "LAB.set('weave', {v: 5.4, k: 0.9, T: 1.4}); LAB.step(75); ", [1.3, 0.6, 1.4], [0, 0.0, 0.0]),
         ('turn, from above', "LAB.step(10); ", [0.3, 2.0, 0.3], [0, 0.0, 0.0]),
         ('jump, rising', RESET + "LAB.set('jump', {v: 4, at: 0.3}); LAB.step(28); ", [1.5, 0.5, 1.5], [0, 0.0, 0.0]),
         ('jump, tuck (top)', "LAB.step(14); ", [1.5, 0.5, 1.5], [0, 0.0, 0.0]),
         ('ball (fling)', RESET + "LAB.set('fling', {at: 0.2, c: 1}); LAB.step(40); ", [1.5, 0.5, 1.5], [0, 0.0, 0.0]),
         ('ball, later', "LAB.step(12); ", [1.5, 0.5, 1.5], [0, 0.0, 0.0]),
         ('landing +6', RESET + "LAB.set('jump', {v: 4, at: 0.3}); LAB.step(28); while (LAB.D.air) LAB.step(1); LAB.step(6); ", [1.3, 0.5, 1.4], [0, 0.0, 0.1]),
         ('landing +14', "LAB.step(8); ", [1.3, 0.5, 1.4], [0, 0.0, 0.1]),
         ('stand idle', RESET + "LAB.set('idle'); LAB.step(20); LAB.I.ax.A.set('stand'); LAB.step(150); ", [1.6, 1.2, 1.7], [0, 1.0, 0.1]),
         ('stand idle, side', "LAB.step(2); ", [2.0, 1.2, 0.1], [0, 1.0, 0.1]),
         ('victory +150', RESET + "LAB.set('idle'); LAB.step(20); LAB.I.ax.A.set('victory'); LAB.step(150); ", [1.6, 1.2, 1.7], [0, 1.0, 0.1]),
         ('victory +190, side', "LAB.step(40); ", [2.0, 1.2, 0.1], [0, 1.0, 0.1]),
         ('victory, front', "LAB.step(20); ", [0.0, 1.2, 2.0], [0, 1.0, 0.1]),
         ('jetpack', RESET + "LAB.set('idle'); LAB.D.rocket = true; LAB.step(120); ", [1.6, 1.2, 1.7], [0, 1.0, 0.1]),
         ('jetpack, side', "LAB.step(2); ", [2.0, 1.2, 0.1], [0, 1.0, 0.1]),
         ('pound +40', RESET + "LAB.set('idle'); LAB.step(20); LAB.I.ax.A.set('pound'); LAB.step(40); ", [1.6, 1.0, 1.7], [0, 0.8, 0.1]),
         ('mid morph crawl->stand +18', RESET + "LAB.set('idle'); LAB.step(20); LAB.I.ax.A.set('stand'); LAB.step(18); ", [1.6, 1.0, 1.7], [0, 0.7, 0.2]),
         ('mid morph +30', "LAB.step(12); ", [1.6, 1.0, 1.7], [0, 0.7, 0.2]),
         ('mid morph stand->crawl +20', "LAB.step(100); LAB.I.ax.A.set('crawl'); LAB.step(20); ", [1.6, 1.0, 1.7], [0, 0.7, 0.2]),
         ('climb out', RESET + "LAB.set('climb', {T: 2.0}); LAB.step(95); ", [1.5, 0.6, 1.3], [0.0, -0.1, 0.1])]
    FIXED = {'stand idle', 'stand idle, side', 'victory +150', 'victory +190, side', 'victory, front', 'jetpack', 'jetpack, side', 'pound +40', 'mid morph crawl->stand +18', 'mid morph +30', 'mid morph stand->crawl +20'}
    pg = [p for p in PG if p != 'cur'] or PG
    for lab, pre, pos, at in P:
        for p in pg: cells.append((cam if lab in FIXED else rcam)(p, f'{tag(p)}: {lab}', pos, at, pre=pre))
    run('poses', {p: LAB(DIRS[p]) for p in pg}, cells, 420, 400, 2 * len(pg), 'the ears in every pose: ' + ' / '.join(tag(p) for p in pg))
def faces():
    pages = {p: LAB(DIRS[p]) for p in PG}; cells = []
    EX = ['neutral', 'happy', 'angry', 'hurt', 'glee', 'scared', 'yawn', 'dizzy']; ST = [('round', 0), ('edgy', 1), ('dot', 2), ('zombie', 3), ('sly', 4)]
    face = ([0.0, 0.55, 1.35], [0, 0.47, 0.33])
    for e in EX:
        for p in PG: cells.append(cam(p, f'{tag(p)}: {e}', *face, pre=f"LAB.I.setEyeStyle(0); LAB.I.setFangs(false); LAB.I.setLashes(0,0); LAB.I.setPatch(0); LAB.I.setExpression('{e}'); LAB.I.ax.look.exprK = 1; LAB.I.ax.look.expr = '{e}'; LAB.I.ax.look.blinkK = 0; LAB.step(10); LAB.I.ax.look.blinkK = 0; "))
    for nm, k in ST:
        for p in PG: cells.append(cam(p, f'{tag(p)}: eyes {nm} + fangs', *face, pre=f"LAB.I.setEyeStyle({k}); LAB.I.setFangs(true); LAB.I.setExpression('happy'); LAB.I.ax.look.exprK = 1; LAB.I.ax.look.expr = 'happy'; LAB.I.ax.look.blinkK = 0; LAB.step(10); LAB.I.ax.look.blinkK = 0; "))
    for p in PG: cells.append(cam(p, f'{tag(p)}: lashes + patch', *face, pre="LAB.I.setEyeStyle(0); LAB.I.setFangs(false); LAB.I.setLashes(1,1); LAB.I.setPatch(1); LAB.I.setExpression('neutral'); LAB.I.ax.look.exprK = 1; LAB.I.ax.look.expr = 'neutral'; LAB.I.ax.look.blinkK = 0; LAB.step(10); LAB.I.ax.look.blinkK = 0; "))
    for p in PG: cells.append(cam(p, f'{tag(p)}: blink', *face, pre="LAB.I.setLashes(0,0); LAB.I.setPatch(0); LAB.step(2); LAB.I.ax.look.blinkK = 0.1; LAB.I.ax.look.U.fMix.value.y = 1; "))
    for p in PG: cells.append(cam(p, f'{tag(p)}: eye close-up', [0.3, 0.6, 1.0], [0.1, 0.52, 0.33], pre="LAB.I.ax.look.blinkK = 0; LAB.step(10); LAB.I.ax.look.blinkK = 0; "))
    run('faces', pages, cells, 400, 400, len(PG) * 2, 'the face: ' + ' / '.join(tag(p) for p in PG))
# the hat anchor (green) with a brim at the head's size, and the game's own hat fits as plain stand-ins (a brim ring at the hat's own y and
# tilt, its scale from HAT_FIT), so the fit of each can be read against the crown
HAT = """{ const I = LAB.I; I.root.updateWorldMatrix(true, true); const W = I.root.parent.matrixWorld, q0 = I.root.parent.getWorldQuaternion(new THREE.Quaternion());
  const t = AXOC.headTop(I, new THREE.Vector3()).applyMatrix4(W), hq = new THREE.Quaternion(); AXOC.headTop(I, new THREE.Vector3(), hq); hq.premultiply(q0);
  const hs = AXOC.headSize(I) * 1.3 * I.root.parent.scale.x;
  const G = window.__hatG || (window.__hatG = new THREE.Group()); scene.add(G); G.clear();
  const dot = new THREE.Mesh(new THREE.SphereGeometry(0.025, 12, 8), new THREE.MeshBasicMaterial({ color: 0x20c020 })); dot.position.copy(t); G.add(dot);
  const FIT = { skull: { s: 0.58, y: -0.34, rx: 0.12, rz: 0.55, c: 0xeeeeee }, bunny: { s: 0.92, y: -0.42, rx: -0.06, rz: 0.03, c: 0xff80c0 }, witch: { s: 1.3, y: -0.27, rx: -0.14, rz: -0.16, c: 0x303030 }, pirate: { s: 0.92, y: -0.2, rx: -0.1, rz: 0.06, c: 0x804020 }, top: { s: 0.86, y: -0.13, rx: -0.12, rz: -0.24, c: 0x202060 }, tiara: { s: 0.6, y: -0.13, rx: -0.22, rz: 0.05, c: 0xe0c040 } };
  const F = FIT[window.__hatName || 'top'];
  const ring = new THREE.Mesh(new THREE.TorusGeometry(0.5 * F.s, 0.012, 8, 48), new THREE.MeshBasicMaterial({ color: F.c })); ring.rotateX(Math.PI / 2);
  const hat = new THREE.Group(); hat.add(ring); if (window.__hatName === 'top') { const cyl = new THREE.Mesh(new THREE.CylinderGeometry(0.33 * F.s, 0.33 * F.s, 0.6 * F.s, 24, 1, true), new THREE.MeshBasicMaterial({ color: F.c, wireframe: true })); cyl.position.y = 0.3 * F.s; hat.add(cyl); }
  hat.position.copy(t).add(new THREE.Vector3(0, F.y * hs, 0).applyQuaternion(hq)); hat.quaternion.copy(hq).multiply(new THREE.Quaternion().setFromEuler(new THREE.Euler(F.rx, 0, F.rz))); hat.scale.setScalar(hs); G.add(hat); } """
def hats():
    pages = {p: LAB(DIRS[p]) for p in PG}; cells = []
    for nm in ['top', 'witch', 'pirate', 'tiara', 'bunny', 'skull']:
        for p in PG: cells.append(cam(p, f'{tag(p)}: {nm} fit (ring at its brim), front 3/4', [1.1, 0.8, 1.3], [0, 0.5, 0.33], pre=f"window.__hatName = '{nm}'; " + HAT))
        for p in PG: cells.append(cam(p, f'{tag(p)}: {nm} fit, side', [1.7, 0.6, 0.33], [0, 0.52, 0.33], pre=HAT))
    for p in PG: cells.append(cam(p, f'{tag(p)}: anchor, stand', [1.3, 1.5, 1.3], [0, 1.2, 0.1], pre="window.__hatName = 'top'; LAB.I.ax.A.set('stand'); LAB.step(150); " + HAT))
    for p in PG: cells.append(cam(p, f'{tag(p)}: anchor, jetpack', [1.3, 1.5, 1.3], [0, 1.2, 0.1], pre="LAB.D.rocket = true; LAB.step(120); " + HAT))
    run('hats', pages, cells, 420, 400, len(PG) * 2, 'the hat anchor and the fits (stand-in rings at each hat\'s brim): ' + ' / '.join(tag(p) for p in PG))
def mats():
    pg = ['A', 'B']; pages = {p: LAB(DIRS[p]) for p in pg}; cells = []
    TEAM = [('red', '0xe3122f'), ('blue', '0x2f8cff'), ('amber', '0xffb300'), ('green', '0x3cc43c'), ('violet', '0x9b4de0')]
    for nm, hx in TEAM:
        for p in pg: cells.append(cam(p, f'{tag(p)}: {nm}, lobby front', [0.0, 0.55, 1.75], [0, 0.44, 0.33], pre=RESET + f"LAB.set('idle'); LAB.I.setColor(new THREE.Color({hx})); LAB.step(20); "))
        for p in pg: cells.append(cam(p, f'{tag(p)}: {nm}, 3/4', [1.05, 0.7, 1.4], [0, 0.44, 0.33]))
    for p in pg: cells.append(cam(p, f'{tag(p)}: red, head close 3/4', [0.7, 0.6, 1.0], [0, 0.47, 0.33], pre="LAB.I.setColor(new THREE.Color(0xe3122f)); LAB.step(5); "))
    for p in pg: cells.append(cam(p, f'{tag(p)}: red, ears close side', [1.2, 0.5, 0.3], [0, 0.42, 0.33]))
    for p in pg: cells.append(cam(p, f'{tag(p)}: red, dark ground portrait', [0.0, 0.55, 1.35], [0, 0.47, 0.33], pre="scene.background = new THREE.Color(0x1a1a1e); floor.visible = false; LAB.I.setExpression('happy'); LAB.step(12); LAB.I.ax.look.blinkK = 0; "))
    run('mats', pages, cells, 420, 400, 4, 'the two material variants: A (skin) / B (jelly)')
def coat():
    pg = ['A', 'B']; pages = {p: LAB(DIRS[p]) for p in pg}; cells = []
    for nm, hx in [('red', '0xe3122f'), ('blue', '0x2f8cff')]:
        for lv in (0.5, 0.8, 1.0):
            for p in pg: cells.append(cam(p, f'{tag(p)}: {nm} crawl coat {lv}', [1.4, 0.8, 1.6], [0, 0.35, 0.2], pre=RESET + f"LAB.set('idle'); LAB.I.setColor(new THREE.Color({hx})); LAB.step(20); LAB.I.ax.coat = {lv}; LAB.I.ax.wet = 1; LAB.I.ax.rise = 0; LAB.I.ax.burstT = -1; LAB.I.ax.fadeT = 0; "))
    for p in pg: cells.append(cam(p, f'{tag(p)}: blue, head coat edge close', [0.8, 0.6, 1.1], [0, 0.45, 0.33], pre="LAB.I.ax.coat = 0.85; LAB.step(3); "))
    for p in pg: cells.append(cam(p, f'{tag(p)}: blue, wading', [1.4, 0.8, 1.6], [0, 0.35, 0.2], pre="LAB.I.ax.coat = 0; LAB.I.setWade(1); LAB.step(5); "))
    for p in pg: cells.append(cam(p, f'{tag(p)}: blue, drying (wet 0.6)', [1.4, 0.8, 1.6], [0, 0.35, 0.2], pre="LAB.I.setWade(0); LAB.I.ax.coat = 0; LAB.step(3); LAB.I.ax.wet = 0.6; LAB.step(2); "))
    run('coat', pages, cells, 420, 400, 4, 'the paint coat: A / B')
# the lobby defect check: the stand and the crawl from the front at lobby distance on a light and a dark ground, the crawl 3/4, the
# game's lobby view (the crawl looking up at the camera) and a close-up of the left ear's top
def fix():
    pg = ['A', 'B']; pages = {p: LAB(DIRS[p]) for p in pg}; cells = []
    LIGHT = "scene.background = new THREE.Color(0xd9d2c3); floor.visible = true; "; DARK = "scene.background = new THREE.Color(0x1a1a1e); floor.visible = false; "
    LOOKUP = "LAB.I.ax.A.look.pitch = 28; LAB.I.ax.A.look.yaw = 0; "
    for p in pg: cells.append(cam(p, f'{tag(p)}: crawl, lobby front, light', [0.0, 0.75, 2.0], [0, 0.4, 0.2], pre=RESET + LIGHT + NEUTRAL + "LAB.set('idle'); " + LOOKUP + "LAB.step(60); "))
    for p in pg: cells.append(cam(p, f'{tag(p)}: crawl, lobby front, dark', [0.0, 0.75, 2.0], [0, 0.4, 0.2], pre=DARK + "LAB.step(2); "))
    for p in pg: cells.append(cam(p, f'{tag(p)}: crawl 3/4, light', [1.4, 0.9, 1.6], [0, 0.4, 0.2], pre=LIGHT + "LAB.I.ax.A.look.pitch = 0; LAB.step(20); "))
    for p in pg: cells.append(cam(p, f'{tag(p)}: left ear top, close', [0.55, 1.1, 0.9], [0.3, 0.75, 0.33], pre="LAB.step(2); "))
    for p in pg: cells.append(cam(p, f'{tag(p)}: stand, lobby front, light', [0.0, 1.2, 2.6], [0, 0.95, 0.0], pre=RESET + LIGHT + "LAB.set('idle'); LAB.step(20); LAB.I.ax.A.set('stand'); LAB.step(150); "))
    for p in pg: cells.append(cam(p, f'{tag(p)}: stand, lobby front, dark', [0.0, 1.2, 2.6], [0, 0.95, 0.0], pre=DARK + "LAB.step(2); "))
    for p in pg: cells.append(cam(p, f'{tag(p)}: stand, chest close, dark', [0.3, 1.2, 1.5], [0, 1.0, 0.0], pre="LAB.step(2); "))
    for p in pg: cells.append(cam(p, f'{tag(p)}: stand 3/4, light', [1.5, 1.3, 1.9], [0, 0.95, 0.0], pre=LIGHT + "LAB.step(2); "))
    run('fix_seams', pages, cells, 420, 460, 4, 'the lobby defect check: A / B')
# the neck check (v10b): the stand from the front, 3/4, side and from under the chin; the crawl side and 3/4 looking up (the lobby
# pose); a dark-ground close of the chin and of the nape; A and B
def neck():
    pg = ['A', 'B']; pages = {p: LAB(DIRS[p]) for p in pg + ['v239']}; cells = []
    LIGHT = "scene.background = new THREE.Color(0xd9d2c3); floor.visible = true; "; DARK = "scene.background = new THREE.Color(0x1a1a1e); floor.visible = false; "
    ST = RESET + LIGHT + NEUTRAL + "LAB.set('idle'); LAB.step(20); LAB.I.ax.A.set('stand'); LAB.step(150); "
    for p in pg + ['v239']: cells.append(cam(p, f'{"v239 (shipped)" if p == "v239" else tag(p)}: stand front, lobby distance', [0.0, 1.2, 2.6], [0, 0.95, 0.0], pre=ST))
    cells.append(cam('v239', 'v239 (shipped): stand 3/4', [1.5, 1.3, 1.7], [0, 1.0, 0.0], pre="LAB.step(2); "))
    for p in pg: cells.append(cam(p, f'{tag(p)}: stand front', [0.0, 1.2, 2.2], [0, 1.0, 0.0], pre="LAB.step(2); "))
    for p in pg: cells.append(cam(p, f'{tag(p)}: stand 3/4', [1.5, 1.3, 1.7], [0, 1.0, 0.0], pre="LAB.step(2); "))
    for p in pg: cells.append(cam(p, f'{tag(p)}: stand side', [2.2, 1.2, 0.0], [0, 1.0, 0.0], pre="LAB.step(2); "))
    for p in pg: cells.append(cam(p, f'{tag(p)}: stand, from under the chin', [0.3, 0.45, 1.6], [0, 1.05, 0.0], pre="LAB.step(2); "))
    for p in pg: cells.append(cam(p, f'{tag(p)}: stand, chin and throat close, dark', [0.5, 0.8, 1.3], [0, 1.05, 0.0], pre=DARK + "LAB.step(2); "))
    for p in pg: cells.append(cam(p, f'{tag(p)}: stand, nape close, dark', [0.8, 1.35, -1.3], [0, 1.05, 0.0], pre="LAB.step(2); "))
    CR = RESET + LIGHT + "LAB.set('idle'); LAB.I.ax.A.set('crawl'); LAB.I.ax.state = 'crawl'; LAB.step(120); LAB.I.ax.A.look.pitch = 28; LAB.step(60); "
    for p in pg: cells.append(cam(p, f'{tag(p)}: crawl side, looking up', [2.0, 0.6, 0.3], [0, 0.42, 0.25], pre=CR))
    for p in pg: cells.append(cam(p, f'{tag(p)}: crawl 3/4, looking up', [1.4, 0.8, 1.5], [0, 0.42, 0.25], pre="LAB.step(2); "))
    for p in pg: cells.append(cam(p, f'{tag(p)}: crawl, throat close, dark', [0.6, 0.35, 1.4], [0, 0.5, 0.33], pre=DARK + "LAB.step(2); "))
    for p in pg: cells.append(cam(p, f'{tag(p)}: crawl, nape close, dark', [0.8, 1.2, -0.9], [0, 0.55, 0.2], pre="LAB.step(2); "))
    run('neck', pages, cells, 420, 440, 4, 'the neck: A / B')
# the locker (v10b): the game's locker camera, about 1.3x the lobby distance, front, a little above, the crawl looking up at it, on a red
# carpet with a warm backdrop; v10 A and B, A with the toon look off, v239 as shipped, and the slime's recording frame beside them
CARPET = ("if (!window.__carpet) { const rc = new THREE.Mesh(new THREE.PlaneGeometry(8, 2.4), new THREE.MeshStandardMaterial({ color: 0xc81428, roughness: 0.35 })); rc.rotation.x = -Math.PI / 2; rc.position.set(0, 0.003, 0.3); rc.receiveShadow = true; scene.add(rc); window.__carpet = rc; } "
          "scene.background = new THREE.Color(0xd6cdc8); floor.visible = true; ")
def locker():
    pg = ['A', 'B']; pages = {p: LAB(DIRS[p]) for p in pg + ['v239']}; cells = []
    LK = RESET + CARPET + NEUTRAL + "LAB.set('idle'); LAB.I.ax.A.set('crawl'); LAB.I.ax.state = 'crawl'; LAB.step(120); LAB.I.ax.A.look.pitch = 24; LAB.step(60); "
    V = ([0.0, 1.0, 2.7], [0, 0.4, 0.25])
    cells.append(img(REF + '/f03.png', 'slime recording', [60, 40, 300, 300]))
    for p in pg: cells.append(cam(p, f'{tag(p)}: locker, toon 0.7', *V, pre=LK))
    cells.append(cam('v239', 'v239 (shipped): locker', *V, pre=LK))
    cells.append(cam('A', 'v10 A: locker, toon off (0)', *V, pre="LAB.I.ax.look.U.uToon.value = 0; LAB.step(2); "))
    cells.append(cam('A', 'v10 A: locker, toon 1.0', *V, pre="LAB.I.ax.look.U.uToon.value = 1; LAB.step(2); "))
    cells.append(cam('A', 'v10 A: locker close, toon 0.7', [0.0, 0.8, 1.6], [0, 0.45, 0.3], pre="LAB.I.ax.look.U.uToon.value = 0.7; LAB.step(2); "))
    cells.append(cam('B', 'v10 B: locker close, toon 0.7', [0.0, 0.8, 1.6], [0, 0.45, 0.3], pre="LAB.step(2); "))
    cells.append(cam('A', 'v10 A: locker 3/4, toon 0.7', [1.6, 1.0, 2.2], [0, 0.4, 0.25], pre="LAB.step(2); "))
    cells.append(cam('v239', 'v239 (shipped): locker 3/4', [1.6, 1.0, 2.2], [0, 0.4, 0.25], pre="LAB.step(2); "))
    cells.append(cam('A', 'v10 A: stand, locker camera', [0.0, 1.3, 3.0], [0, 0.9, 0.0], pre="LAB.I.ax.A.look.pitch = 0; LAB.I.ax.A.set('stand'); LAB.step(150); "))
    cells.append(cam('v239', 'v239 (shipped): stand, locker camera', [0.0, 1.3, 3.0], [0, 0.9, 0.0], pre="LAB.I.ax.A.look.pitch = 0; LAB.I.ax.A.set('stand'); LAB.step(150); "))
    run('locker', pages, cells, 420, 460, 4, 'the locker: slime recording / v10 A / v10 B / v239, toon 0 vs 0.7 vs 1')
# the neck close (v10c): the throat and the nape at a larger size in the lab's light, to read the fillet's surface and the join's colour
def neckzoom():
    pg = ['A', 'B']; pages = {p: LAB(DIRS[p]) for p in pg}; cells = []
    LIGHT = "scene.background = new THREE.Color(0xd9d2c3); floor.visible = true; "
    ST = RESET + LIGHT + NEUTRAL + "LAB.set('idle'); LAB.step(20); LAB.I.ax.A.set('stand'); LAB.step(150); LAB.I.ax.look.blinkK = 0; "
    for p in pg: cells.append(cam(p, f'{tag(p)}: stand, throat from the side', [1.1, 0.95, 0.15], [0, 0.98, 0.0], pre=ST))
    for p in pg: cells.append(cam(p, f'{tag(p)}: stand, throat from the front', [0.0, 0.9, 1.15], [0, 0.98, 0.0], pre="LAB.step(2); "))
    for p in pg: cells.append(cam(p, f'{tag(p)}: stand, chest 3/4', [0.8, 0.95, 0.9], [0, 0.92, 0.05], pre="LAB.step(2); "))
    for p in pg: cells.append(cam(p, f'{tag(p)}: stand, nape 3/4 from behind', [0.8, 1.15, -0.95], [0, 1.0, 0.0], pre="LAB.step(2); "))
    CR = RESET + LIGHT + "LAB.set('idle'); LAB.I.ax.A.set('crawl'); LAB.I.ax.state = 'crawl'; LAB.step(120); LAB.I.ax.look.blinkK = 0; "
    for p in pg: cells.append(cam(p, f'{tag(p)}: crawl, nape from behind', [0.7, 0.95, -0.8], [0, 0.55, 0.15], pre=CR))
    for p in pg: cells.append(cam(p, f'{tag(p)}: crawl, side', [1.3, 0.5, 0.25], [0, 0.45, 0.2], pre="LAB.step(2); "))
    run('neckzoom', pages, cells, 640, 560, 2, 'the neck close: A / B')
# the lizard body (v10d): v10d beside v241 (the shipped v10) and the slime recording or a bearded dragon silhouette: stand and crawl,
# front, 3/4, side and top at lobby distance; the locker camera on the red carpet; the win screen close (victory, glee, from a little
# below the face, 1.5 head radii away); the animator's neck turn (weave) and a glance and a look (idle)
def lizard():
    pg = ['5', 'A']; pages = {p: LAB(DIRS[p]) for p in pg}; cells = []; REC = S + '/ref_slime_rec/'; SH = S + '/fable3/shots/'
    LIGHT = "scene.background = new THREE.Color(0xd9d2c3); floor.visible = true; "
    lab5 = lambda p: 'v10d' if p == '5' else 'v241'
    ST = RESET + LIGHT + NEUTRAL + "LAB.set('idle'); LAB.step(20); LAB.I.ax.A.set('stand'); LAB.step(150); LAB.I.ax.look.blinkK = 0; "
    for p in pg: cells.append(cam(p, f'{lab5(p)}: stand front, lobby distance', [0.0, 1.2, 2.6], [0, 0.95, 0.0], pre=ST))
    cells.append(img(REC + 'f01.png', 'the recording'))
    for p in pg: cells.append(cam(p, f'{lab5(p)}: stand 3/4', [1.5, 1.3, 1.9], [0, 1.0, 0.0], pre="LAB.step(2); "))
    cells.append(img(REC + 'f05.png', 'the recording'))
    for p in pg: cells.append(cam(p, f'{lab5(p)}: stand side', [2.6, 1.0, 0.0], [0, 0.95, 0.0], pre="LAB.step(2); "))
    cells.append(img(SH + 'dragon_side.png', 'bearded dragon, side'))
    for p in pg: cells.append(cam(p, f'{lab5(p)}: stand from above', [0.0, 3.4, 0.6], [0, 0.9, 0.0], pre="LAB.step(2); "))
    cells.append(img(SH + 'dragon_top.png', 'bearded dragon, top'))
    for p in pg: cells.append(cam(p, f'{lab5(p)}: stand from behind', [0.0, 1.3, -2.4], [0, 0.95, 0.0], pre="LAB.step(2); "))
    cells.append(cam('5', 'v10d: stand from behind, above', [0.0, 2.4, -1.8], [0, 0.95, 0.0], pre="LAB.step(2); "))
    CR = RESET + LIGHT + "LAB.set('idle'); LAB.I.ax.A.set('crawl'); LAB.I.ax.state = 'crawl'; LAB.step(120); LAB.I.ax.look.blinkK = 0; "
    for p in pg: cells.append(cam(p, f'{lab5(p)}: crawl front, lobby distance', [0.0, 0.85, 2.1], [0, 0.4, 0.2], pre=CR))
    cells.append(img(REC + 'f03.png', 'the recording'))
    for p in pg: cells.append(cam(p, f'{lab5(p)}: crawl 3/4', [1.5, 0.9, 1.5], [0, 0.4, 0.0], pre="LAB.step(2); "))
    cells.append(img(REC + 'f08.png', 'the recording'))
    for p in pg: cells.append(cam(p, f'{lab5(p)}: crawl side', [2.8, 0.6, -0.4], [0, 0.4, -0.4], pre="LAB.step(2); "))
    cells.append(img(SH + 'dragon_side.png', 'bearded dragon, side'))
    for p in pg: cells.append(cam(p, f'{lab5(p)}: crawl from above', [0.0, 3.2, -0.5], [0, 0.3, -0.5], pre="LAB.step(2); "))
    cells.append(img(SH + 'dragon_top.png', 'bearded dragon, top'))
    for p in pg: cells.append(cam(p, f'{lab5(p)}: crawl from behind, above', [0.0, 1.6, -2.6], [0, 0.35, -0.3], pre="LAB.step(2); "))
    cells.append(cam('5', 'v10d: crawl 3/4 from behind', [1.8, 1.2, -1.8], [0, 0.35, -0.2], pre="LAB.step(2); "))
    LK = RESET + CARPET + "LAB.set('idle'); LAB.I.ax.A.set('crawl'); LAB.I.ax.state = 'crawl'; LAB.step(120); LAB.I.ax.A.look.pitch = 28; LAB.step(60); LAB.I.ax.look.blinkK = 0; "
    for p in pg: cells.append(cam(p, f'{lab5(p)}: locker camera, red carpet', [0.0, 1.0, 2.7], [0, 0.4, 0.25], pre=LK))
    cells.append(img(REC + 'f01.png', 'the recording'))
    VI = RESET + LIGHT + "LAB.set('idle'); LAB.step(20); LAB.I.ax.A.set('victory'); LAB.step(150); LAB.I.setExpression('glee'); LAB.step(12); LAB.I.ax.look.blinkK = 0; "
    for p in pg: cells.append(rcam(p, f'{lab5(p)}: win screen close (victory, glee, from below, 1.5 r)', [0.0, -0.22, 0.56], [0, 0.02, 0.0], pre=VI))
    cells.append(img('/root/.claude/uploads/5c52352e-692f-5301-ac55-ec4d2c708f3e/6fede3e0-image.jpg', 'the win screen (v241, user)'))
    WV = RESET + LIGHT + "LAB.set('weave', {v: 5.4, k: 0.9, T: 1.4}); LAB.step(75); "
    for p in pg: cells.append(cam(p, f'{lab5(p)}: weave (the neck turn)', [1.3, 0.7, 1.4], [0, 0.1, 0.0], pre=WV))
    cells.append(cam('5', 'v10d: weave, from above', [0.3, 2.2, 0.3], [0, 0.0, 0.0], pre="LAB.step(10); "))
    GL = RESET + LIGHT + "LAB.set('idle'); LAB.step(20); LAB.I.ax.A.set('stand'); LAB.step(150); { const N = LAB.I.ax.A.neck; N.glance = [25, -4, 0]; N.holdT = 1; N.glanceT = 3; } LAB.step(30); LAB.I.ax.look.blinkK = 0; "
    for p in pg: cells.append(cam(p, f'{lab5(p)}: idle glance 25 deg', [0.0, 1.3, 1.7], [0, 1.05, 0.0], pre=GL))
    cells.append(cam('5', 'v10d: head look yaw 40 pitch 15', [0.0, 1.3, 1.7], [0, 1.05, 0.0], pre="LAB.I.ax.A.look.yaw = 40; LAB.I.ax.A.look.pitch = 15; LAB.step(40); "))
    run('lizard', pages, cells, 520, 440, 3, 'the lizard body: v10d / v241 / reference')
# v10e: cameras on the head itself (the face centre, from AXOC.headTop, in world space): FACE puts the camera d head radii out along the
# face's own forward and up head radii above its centre, looking at up2 radii above it; FOLLOW keeps a camera at [side, up, forward]
# metres from the face centre in the character's own heading (for scenarios that move it about)
FACE = lambda d, up, up2: ("{ const I = LAB.I, q = new THREE.Quaternion(), c = AXOC.headTop(I, new THREE.Vector3(), q, 0), wq = new THREE.Quaternion(); I.root.updateWorldMatrix(true, true); "
    "LAB.V.body.getWorldQuaternion(wq); q.premultiply(wq); c.applyMatrix4(LAB.V.body.matrixWorld); const r = AXOC.headSize(I) * LAB.V.body.scale.x, f = new THREE.Vector3(0, 0, 1).applyQuaternion(q), u = new THREE.Vector3(0, 1, 0).applyQuaternion(q); "
    f"LAB.cam = 'fixed'; LAB.camPos = c.clone().addScaledVector(f, {d} * r).addScaledVector(u, {up} * r).toArray(); LAB.camAt = c.clone().addScaledVector(u, {up2} * r).toArray(); }} LAB.render()")
FOLLOW = lambda off, at: ("{ const I = LAB.I, c = AXOC.headTop(I, new THREE.Vector3(), null, 0); I.root.updateWorldMatrix(true, true); c.applyMatrix4(LAB.V.body.matrixWorld); const y = LAB.D.yaw, sy = Math.sin(y), cy = Math.cos(y); "
    f"const o = {json.dumps(off)}, a = {json.dumps(at)}; LAB.cam = 'fixed'; LAB.camPos = [c.x + o[0] * cy + o[2] * sy, c.y + o[1], c.z - o[0] * sy + o[2] * cy]; LAB.camAt = [c.x + a[0] * cy + a[2] * sy, c.y + a[1], c.z - a[0] * sy + a[2] * cy]; }} LAB.render()")
def liz6(new='6', old='A'):
    """v10e beside v241 and the references: stand and crawl front, 3/4, side, top and from behind at lobby distance; the locker camera;
    the win screen close (victory, glee, a little below the face)"""
    pg = [new, old]; pages = {p: LAB(DIRS[p]) for p in pg}; cells = []; REC = S + '/ref_slime_rec/'; SH = S + '/fable3/shots/'
    LIGHT = "scene.background = new THREE.Color(0xd9d2c3); floor.visible = true; "
    nm = lambda p: tag(p) if p == new else 'v241'
    ST = RESET + LIGHT + NEUTRAL + "LAB.set('idle'); LAB.step(20); LAB.I.ax.A.set('stand'); LAB.step(150); LAB.I.ax.look.blinkK = 0; "
    for p in pg: cells.append(cam(p, f'{nm(p)}: stand front, lobby distance', [0.0, 1.2, 2.6], [0, 0.95, 0.0], pre=ST))
    cells.append(img(REC + 'f01.png', 'the recording'))
    for p in pg: cells.append(cam(p, f'{nm(p)}: stand 3/4', [1.5, 1.3, 1.9], [0, 1.0, 0.0], pre="LAB.step(2); "))
    cells.append(img(REC + 'f05.png', 'the recording'))
    for p in pg: cells.append(cam(p, f'{nm(p)}: stand side', [2.6, 1.0, 0.0], [0, 0.95, 0.0], pre="LAB.step(2); "))
    cells.append(img(SH + 'dragon_side.png', 'bearded dragon, side'))
    for p in pg: cells.append(cam(p, f'{nm(p)}: stand from above', [0.0, 3.4, 0.6], [0, 0.9, 0.0], pre="LAB.step(2); "))
    cells.append(img(SH + 'dragon_top.png', 'bearded dragon, top'))
    for p in pg: cells.append(cam(p, f'{nm(p)}: stand from behind', [0.0, 1.3, -2.4], [0, 0.95, 0.0], pre="LAB.step(2); "))
    cells.append(cam(new, f'{tag(new)}: stand from behind, above', [0.0, 2.4, -1.8], [0, 0.95, 0.0], pre="LAB.step(2); "))
    CR = RESET + LIGHT + "LAB.set('idle'); LAB.I.ax.A.set('crawl'); LAB.I.ax.state = 'crawl'; LAB.step(120); LAB.I.ax.look.blinkK = 0; "
    for p in pg: cells.append(cam(p, f'{nm(p)}: crawl front, lobby distance', [0.0, 0.85, 2.1], [0, 0.4, 0.2], pre=CR))
    cells.append(img(REC + 'f03.png', 'the recording'))
    for p in pg: cells.append(cam(p, f'{nm(p)}: crawl 3/4', [1.5, 0.9, 1.5], [0, 0.4, 0.0], pre="LAB.step(2); "))
    cells.append(img(REC + 'f08.png', 'the recording'))
    for p in pg: cells.append(cam(p, f'{nm(p)}: crawl side', [2.8, 0.6, -0.4], [0, 0.4, -0.4], pre="LAB.step(2); "))
    cells.append(img(SH + 'dragon_side.png', 'bearded dragon, side'))
    for p in pg: cells.append(cam(p, f'{nm(p)}: crawl from above', [0.0, 3.2, -0.5], [0, 0.3, -0.5], pre="LAB.step(2); "))
    cells.append(img(SH + 'dragon_top.png', 'bearded dragon, top'))
    for p in pg: cells.append(cam(p, f'{nm(p)}: crawl from behind, above', [0.0, 1.6, -2.6], [0, 0.35, -0.3], pre="LAB.step(2); "))
    cells.append(cam(new, f'{tag(new)}: crawl 3/4 from behind', [1.8, 1.2, -1.8], [0, 0.35, -0.2], pre="LAB.step(2); "))
    LK = RESET + CARPET + "LAB.set('idle'); LAB.I.ax.A.set('crawl'); LAB.I.ax.state = 'crawl'; LAB.step(120); LAB.I.ax.A.look.pitch = 28; LAB.step(60); LAB.I.ax.look.blinkK = 0; "
    for p in pg: cells.append(cam(p, f'{nm(p)}: locker camera, red carpet', [0.0, 1.0, 2.7], [0, 0.4, 0.25], pre=LK))
    cells.append(img(REC + 'f01.png', 'the recording'))
    VI = RESET + LIGHT + "LAB.set('idle'); LAB.step(20); LAB.I.ax.A.set('victory'); LAB.step(150); LAB.I.setExpression('glee'); LAB.step(12); LAB.I.ax.look.blinkK = 0; "
    for p in pg: cells.append([p, VI + FACE(2.5, -0.7, -0.35), f'{nm(p)}: win close (victory, glee; 1.5 r out from the face, below it)'])
    cells.append(img('/root/.claude/uploads/5c52352e-692f-5301-ac55-ec4d2c708f3e/6fede3e0-image.jpg', 'the win screen (v241, the user)'))
    for p in pg: cells.append([p, "LAB.step(2); " + FACE(4.4, -0.5, -0.25), f'{nm(p)}: win close, the user\'s framing'])
    cells.append([new, "LAB.step(2); scene.background = new THREE.Color(0x1a1a1e); floor.visible = false; " + FACE(2.5, -1.4, -0.6), f'{tag(new)}: win close, from under the chin (dark)'])
    run('liz6', pages, cells, 520, 440, 3, 'the lizard body: v10e / v241 / reference')
def liz6poses(new='6', old='A'):
    """the animator's neck turn and head look on v10e beside v241 (nothing tears, the head still turns): weave (from the side and from
    above), the crawl gait, the idle glance, a head look, the stand idle"""
    pg = [new, old]; pages = {p: LAB(DIRS[p]) for p in pg}; cells = []; LIGHT = "scene.background = new THREE.Color(0xd9d2c3); floor.visible = true; "
    nm = lambda p: tag(p) if p == new else 'v241'
    WV = RESET + LIGHT + "LAB.set('weave', {v: 5.4, k: 0.9, T: 1.4}); LAB.step(75); "
    for p in pg: cells.append([p, WV + FOLLOW([1.9, 0.8, 1.8], [0, -0.15, -0.3]), f'{nm(p)}: weave (the neck turn)'])
    for p in pg: cells.append([p, "LAB.step(10); " + FOLLOW([0.2, 2.6, -0.2], [0, -0.2, -0.4]), f'{nm(p)}: weave, from above'])
    for p in pg: cells.append([p, "LAB.step(21); " + FOLLOW([-1.9, 0.8, 1.8], [0, -0.15, -0.3]), f'{nm(p)}: weave, the other way'])
    WK = RESET + LIGHT + "LAB.set('walk', {v: 5.4}); LAB.step(90); "
    for p in pg: cells.append([p, WK + FOLLOW([2.0, 0.6, 1.2], [0, -0.2, -0.5]), f'{nm(p)}: crawl gait'])
    for p in pg: cells.append([p, "LAB.step(9); " + FOLLOW([2.6, 0.2, -0.4], [0, -0.2, -0.5]), f'{nm(p)}: crawl gait, side'])
    GL = RESET + LIGHT + "LAB.set('idle'); LAB.step(20); LAB.I.ax.A.set('stand'); LAB.step(150); { const N = LAB.I.ax.A.neck; N.glance = [25, -4, 0]; N.holdT = 1; N.glanceT = 3; } LAB.step(30); LAB.I.ax.look.blinkK = 0; "
    for p in pg: cells.append(cam(p, f'{nm(p)}: stand idle glance 25 deg', [0.0, 1.3, 1.9], [0, 1.05, 0.0], pre=GL))
    for p in pg: cells.append(cam(p, f'{nm(p)}: stand, head look yaw 40 pitch 15', [0.9, 1.3, 1.7], [0, 1.05, 0.0], pre="LAB.I.ax.A.look.yaw = 40; LAB.I.ax.A.look.pitch = 15; LAB.step(40); "))
    for p in pg: cells.append(cam(p, f'{nm(p)}: stand, head look yaw -40 pitch -20', [-0.9, 1.0, 1.7], [0, 1.05, 0.0], pre="LAB.I.ax.A.look.yaw = -40; LAB.I.ax.A.look.pitch = -20; LAB.step(40); "))
    CL = RESET + LIGHT + "LAB.set('idle'); LAB.I.ax.A.set('crawl'); LAB.I.ax.state = 'crawl'; LAB.step(120); LAB.I.ax.A.look.yaw = 45; LAB.I.ax.A.look.pitch = 25; LAB.step(60); "
    for p in pg: cells.append(cam(p, f'{nm(p)}: crawl, head look yaw 45 pitch 25', [1.2, 0.8, 1.5], [0, 0.4, 0.0], pre=CL))
    VI = RESET + LIGHT + "LAB.set('idle'); LAB.step(20); LAB.I.ax.A.set('victory'); LAB.step(150); "
    for p in pg: cells.append(cam(p, f'{nm(p)}: victory', [1.2, 1.3, 1.9], [0, 1.0, 0.0], pre=VI))
    run('liz6poses', pages, cells, 520, 440, 2, 'the neck turn and head look: v10e / v241')
if __name__ == '__main__':
    a = sys.argv[1:]
    if '--pages' in a: i = a.index('--pages'); PG = a[i + 1].split(','); del a[i:i + 2]
    which = a or ['head']
    for w in which:
        if w == 'all': [f() for f in (head, poses, faces, hats, mats, coat)]
        else: globals()[w]()
