"""v254 probe harness: boot a test page with a save, step the game at a fixed rate with the page's own loop held, and grab frames."""
import asyncio, json, os
from PIL import Image, ImageDraw
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
OUT = S + '/a254'
ADV = """window.__adv = (dt, n) => __T.ev(`(() => { for (let k = 0; k < ${n}; k++) { const dt = ${dt}; const m = Math.ceil(dt / 0.012); for (let i = 0; i < m; i++) step(dt / m); visuals(dt, dt); flushTrail(); pbarTick(dt); lockerTick(); dipTick(dt);
  if (window.__perFrame) window.__perFrame();
  if (window.__camRel) { const o = window.__camRel; camera.position.set(P.x + o[0][0], P.y + o[0][1], P.z + o[0][2]); camera.lookAt(P.x + o[1][0], P.y + o[1][1], P.z + o[1][2]); } } renderFrame(); })()`);
window.__scr = (y) => __T.ev(`(() => { const v = new THREE.Vector3(P.x, P.y + ${y}, P.z).project(camera); return [(v.x + 1) / 2 * innerWidth, (1 - v.y) / 2 * innerHeight]; })()`); true"""
CAMF = """window.__camAx = (eye, at) => { window.__perFrame = () => { const P = __T.P, f = [Math.sin(P.yaw), Math.cos(P.yaw)], r = [-f[1], f[0]];
  window.__camRel = [[r[0] * eye[0] + f[0] * eye[2], eye[1], r[1] * eye[0] + f[1] * eye[2]], [r[0] * at[0] + f[0] * at[2], at[1], r[1] * at[0] + f[1] * at[2]]]; }; window.__perFrame(); }; true"""
SAVE = { 'orient': 'port', 'name': 'Dusk', 'seen': {'steer':1,'jump':1,'hold':1,'roll':1,'missile':1,'pound':1,'burst':1,'orb':1,'look':1,'items':1,'airdash':1}, 'runs': 9, 'xp': 140, 'drops': 168,
  'tut': { 'ph': 'done', 'strokes': 1, 'comms': 1, 'm3': 2 }, 'look': {'eyes': 'round', 'iris': 'violet'} }
def sheet(frames, path, cols=8, label=True):
    if not frames: return
    w, h = frames[0][1].size; rows = (len(frames) + cols - 1) // cols
    im = Image.new('RGB', (cols * w, rows * h), (20, 20, 28)); d = ImageDraw.Draw(im)
    for i, (lab, f) in enumerate(frames):
        x, y = (i % cols) * w, (i // cols) * h; im.paste(f, (x, y))
        if label: d.rectangle([x, y, x + 6 * len(lab) + 6, y + 14], fill=(0, 0, 0)); d.text((x + 3, y + 1), lab, fill=(255, 255, 0))
    im.save(path); print('sheet', path, im.size)
async def grab(pg, cx, cy, W, H):
    p = f'{OUT}/_f{os.getpid()}.png'; await pg.screenshot(path=p, clip={'x': max(0, cx - W / 2), 'y': max(0, cy - H / 2), 'width': W, 'height': H}); return Image.open(p).convert('RGB').copy()
async def boot(b, page, save, vp=(390, 780), init='', dpr=1):
    ctx = await b.new_context(viewport={'width': vp[0], 'height': vp[1]}, device_scale_factor=dpr, has_touch=True, is_mobile=True)
    await ctx.add_init_script("window.__tut = true; " + init + " try { localStorage.setItem('paint-world-red.v1', JSON.stringify(" + json.dumps(save) + ")); } catch (e) {}")
    pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('console', lambda m: errs.append(m.text[:300]) if m.type == 'error' and 'Failed to load' not in m.text and 'ERR_FAILED' not in m.text and 'CORS' not in m.text else None)
    await pg.goto('http://localhost:8765/' + page, timeout=300000); await pg.wait_for_function('typeof __T === "object" && !!__T.VP && !!__T.VP.slime', timeout=300000, polling=500); await pg.wait_for_timeout(1200)
    await pg.evaluate(ADV)
    return ctx, pg, errs
async def match(b, page, mode='solo', init='', save=None, vp=(390, 780), dpr=1):
    ctx, pg, errs = await boot(b, page, dict(save or SAVE, mode=mode), init=init, vp=vp, dpr=dpr)
    await pg.evaluate("__T.start()")
    await pg.wait_for_function("__T.state === 'play' && !__T.P.air", timeout=120000, polling=50)
    await pg.wait_for_timeout(400); await pg.evaluate("window.__tscale = 1e-9")
    return ctx, pg, errs
def launch(p):
    return p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
