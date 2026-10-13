"""v252 animation probes: frame sheets of the character, stepped at a fixed rate (the page's own loop held).
usage: anim252.py PAGE SCENARIO TAG [extra]
  locker   the locker's crawl-out (front camera, then a side camera run)
  shake    a shake in the locker (front and side)
  home     the home screen idle acts, forced one by one (face crops)
  hop      hops on the home screen and in a match (ears)
  turn     turns in a match (ears, top camera)
  swim     crawl up to speed into the swim, in paint (side camera)"""
import asyncio, json, sys, os
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
OUT = S + '/a252'
PAGE, SCEN, TAG = sys.argv[1], sys.argv[2], sys.argv[3]
EXTRA = sys.argv[4:] 
ADV = """window.__adv = (dt, n, cb) => __T.ev(`(() => { for (let k = 0; k < ${n}; k++) { const dt = ${dt}; const m = Math.ceil(dt / 0.012); for (let i = 0; i < m; i++) step(dt / m); visuals(dt, dt); flushTrail(); pbarTick(dt); lockerTick(); dipTick(dt);
  if (window.__perFrame) window.__perFrame();
  if (window.__camRel) { const o = window.__camRel; camera.position.set(P.x + o[0][0], P.y + o[0][1], P.z + o[0][2]); camera.lookAt(P.x + o[1][0], P.y + o[1][1], P.z + o[1][2]); } } renderFrame(); })()`);
window.__scr = (y) => __T.ev(`(() => { const v = new THREE.Vector3(P.x, P.y + ${y}, P.z).project(camera); return [(v.x + 1) / 2 * innerWidth, (1 - v.y) / 2 * innerHeight]; })()`);"""
def sheet(frames, path, cols=8, label=True):
    if not frames: return
    w, h = frames[0][1].size; rows = (len(frames) + cols - 1) // cols
    im = Image.new('RGB', (cols * w, rows * h), (20, 20, 28)); d = ImageDraw.Draw(im)
    for i, (lab, f) in enumerate(frames):
        x, y = (i % cols) * w, (i // cols) * h; im.paste(f, (x, y))
        if label: d.rectangle([x, y, x + 64, y + 14], fill=(0, 0, 0)); d.text((x + 3, y + 1), lab, fill=(255, 255, 0))
    im.save(path); print('sheet', path, im.size)
async def grab(pg, cx, cy, W, H, name):
    p = f'{OUT}/_f.png'; await pg.screenshot(path=p, clip={'x': max(0, cx - W / 2), 'y': max(0, cy - H / 2), 'width': W, 'height': H}); return Image.open(p).convert('RGB').copy()
async def boot(b, save, vp=(390, 780), init=''):
    ctx = await b.new_context(viewport={'width': vp[0], 'height': vp[1]}, device_scale_factor=1, has_touch=True, is_mobile=True)
    await ctx.add_init_script("window.__tut = true; " + init + " try { localStorage.setItem('paint-world-red.v1', JSON.stringify(" + json.dumps(save) + ")); } catch (e) {}")
    pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('console', lambda m: errs.append(m.text[:300]) if m.type == 'error' and 'Failed to load' not in m.text and 'ERR_FAILED' not in m.text and 'CORS' not in m.text else None)
    await pg.goto('http://localhost:8765/' + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object" && !!__T.VP && !!__T.VP.slime', timeout=300000, polling=500); await pg.wait_for_timeout(1200)
    await pg.evaluate(ADV)
    return ctx, pg, errs
SAVE = { 'orient': 'port', 'name': 'Dusk', 'seen': {'steer':1,'jump':1,'hold':1,'roll':1,'missile':1,'pound':1,'burst':1,'orb':1,'look':1,'items':1}, 'runs': 9, 'xp': 140, 'drops': 168,
  'tut': { 'ph': 'done', 'strokes': 1, 'comms': 1, 'm3': 2 }, 'look': {'eyes': 'round', 'iris': 'violet'} }
CAMF = """window.__camAx = (eye, at) => { window.__perFrame = () => { const P = __T.P, f = [Math.sin(P.yaw), Math.cos(P.yaw)], r = [-f[1], f[0]];
  window.__camRel = [[r[0] * eye[0] + f[0] * eye[2], eye[1], r[1] * eye[0] + f[1] * eye[2]], [r[0] * at[0] + f[0] * at[2], at[1], r[1] * at[0] + f[1] * at[2]]]; }; window.__perFrame(); }; true"""
async def locker(b):
    for cam in ['front', 'side', 'side2']:
        ctx, pg, errs = await boot(b, SAVE)
        await pg.evaluate("document.getElementById('lookBtn').click()")
        await pg.wait_for_function("__T.ev('!!lookIntro')", timeout=30000, polling=20); await pg.evaluate("window.__tscale = 1e-9"); print("caught at", await pg.evaluate("__T.ev('lookIntro.t')"))
        await pg.evaluate("window.__tscale = 1e-9"); await pg.wait_for_timeout(200)
        if cam != 'front': await pg.evaluate(CAMF)
        if cam == 'side': await pg.evaluate("__camAx([3.6, 0.9, -0.5], [0, 0.25, -0.6])")
        if cam == 'side2': await pg.evaluate("__camAx([-2.3, 1.4, 2.2], [0, 0.25, -0.6])")
        frames = []; t = 0; dt = 1 / 30
        await pg.evaluate("__adv(1/30, 1)")
        cx, cy = await pg.evaluate("__scr(0.3)")
        while t < 3.3:
            await pg.evaluate("__adv(1/30, 3)"); t += 3 * dt
            info = await pg.evaluate("__T.ev('lookIntro ? +lookIntro.t.toFixed(2) : -1')")
            frames.append((f'{t:.2f}', await grab(pg, cx, cy, 300, 300, 'f')))
        sheet(frames, f'{OUT}/{TAG}_locker_{cam}.png', cols=8)
        print(cam, 'errors', errs[:4]); await ctx.close()
async def shake(b):
    for cam in ['front', 'side', 'top']:
        ctx, pg, errs = await boot(b, SAVE)
        await pg.evaluate("document.getElementById('lookBtn').click()")
        await pg.wait_for_function("__T.ev('!lookIntro && lookOpen')", timeout=30000, polling=100); await pg.wait_for_timeout(1500)
        await pg.evaluate("window.__tscale = 1e-9; window.__idleForce = 'still'"); await pg.wait_for_timeout(200)
        if cam == 'side': await pg.evaluate("window.__camRel = [[2.6, 0.7, 0.4], [0, 0.4, 0]]")
        if cam == 'top': await pg.evaluate("window.__camRel = [[0.3, 2.6, 1.6], [0, 0.3, 0]]")
        await pg.evaluate("__adv(1/30, 20)")
        cx, cy = await pg.evaluate("__scr(0.4)")
        await pg.evaluate("__T.ev('VP.slime.shake(1)')")
        frames = []; t = 0
        while t < 1.3:
            frames.append((f'{t:.2f}', await grab(pg, cx, cy, 280, 240, 'f')))
            await pg.evaluate("__adv(1/60, 3)"); t += 3 / 60
        sheet(frames, f'{OUT}/{TAG}_shake_{cam}.png', cols=9)
        print(cam, 'errors', errs[:4]); await ctx.close()
async def home(b):
    cam = 'front'; ex = list(EXTRA)
    if ex and ex[0] in ('side', 'front3'): cam = ex.pop(0)
    acts = ex or ['face', 'yawn', 'listen', 'look', 'bounce', 'wag', 'peek', 'hands', 'still']
    ctx, pg, errs = await boot(b, SAVE)
    await pg.wait_for_timeout(1500)
    if cam != 'front':
        # orbit the game's own camera round the character's middle (same distance, same height), and hide the page's UI
        ang = 80 if cam == 'side' else 35
        await pg.evaluate("""__T.ev(`(() => { const b = new THREE.Box3().setFromObject(VP.slime.root), c = b.getCenter(new THREE.Vector3()), o = camera.position.clone().sub(c), a = %d * Math.PI / 180;
          const r = new THREE.Vector3(o.x * Math.cos(a) + o.z * Math.sin(a), o.y, -o.x * Math.sin(a) + o.z * Math.cos(a)).add(c).sub(P), l = c.clone().sub(P); window.__camRel = [r.toArray(), l.toArray()];
          const cv = renderer.domElement; for (const el of document.querySelectorAll('body *')) if (!el.contains(cv) && el !== cv && !cv.contains(el)) el.style.visibility = 'hidden'; })()`)""" % ang)
        await pg.evaluate("window.__tscale = 1e-9"); await pg.evaluate("__adv(1/30, 2)"); await pg.evaluate("window.__tscale = 1")
    cx, cy = await pg.evaluate("__scr(0.45)")
    if cam != 'front': cx, cy = await pg.evaluate("__T.ev(`(() => { const b = new THREE.Box3().setFromObject(VP.slime.root), v = b.getCenter(new THREE.Vector3()).project(camera); return [(v.x + 1) / 2 * innerWidth, (1 - v.y) / 2 * innerHeight]; })()`)")
    for act in acts:
        await pg.evaluate(f"window.__tscale = 1e-9; window.__idleForce = '{act}'"); await pg.wait_for_timeout(100)
        for _ in range(400):
            if await pg.evaluate(f"__T.ev(\"idle.act === '{act}'\")"): break
            await pg.evaluate("__adv(1/30, 3)")
        frames = []; t = 0
        dur = await pg.evaluate("__T.ev('idle.dur')")
        while t < dur + 0.3:
            frames.append((f'{act[:5]} {t:.1f}', await grab(pg, cx, cy, 230 if cam == 'front' else 330, 210 if cam == 'front' else 300, 'f')))
            await pg.evaluate("__adv(1/30, 6)"); t += 0.2
        sheet(frames, f'{OUT}/{TAG}_home_{cam}_{act}.png', cols=9)
        await pg.evaluate("window.__idleForce = 'still'")
    print('errors', errs[:4]); await ctx.close()
async def basin(b):
    for cam in ['side', 'front']:
        ctx, pg, errs = await boot(b, SAVE, init="window.__skipIntro = false; window.__introKind = 'climb';")
        await pg.evaluate("__T.start()")
        await pg.wait_for_function("__T.ev('!!P.introCrawl')", timeout=120000, polling=20); await pg.evaluate("window.__tscale = 1e-9")
        print('caught at', await pg.evaluate("__T.ev('P.introCrawl.t')"))
        if cam == 'side': await pg.evaluate("window.__camRel = [[3.0, 1.1, 0.9], [0, 0.3, 0.6]]")
        else: await pg.evaluate("window.__camRel = [[Math.sin(__T.P.yaw) * 3.4 + 0.6, 1.3, Math.cos(__T.P.yaw) * 3.4], [0, 0.3, 0]]")
        await pg.evaluate("__adv(1/30, 1)")
        cx, cy = await pg.evaluate("__scr(0.3)")
        frames = []; t = 0
        while t < 3.2:
            frames.append((f'{t:.2f}', await grab(pg, cx, cy, 300, 300, 'f')))
            await pg.evaluate("__adv(1/30, 3)"); t += 0.1
        sheet(frames, f'{OUT}/{TAG}_basin_{cam}.png', cols=8)
        print(cam, 'errors', errs[:4]); await ctx.close()
MSAVE = dict(SAVE, mode='solo')
async def match(b, init=''):
    ctx, pg, errs = await boot(b, MSAVE, init=init)
    await pg.evaluate("__T.start()")
    await pg.wait_for_function("__T.state === 'play' && !__T.P.air", timeout=120000, polling=50)
    await pg.wait_for_timeout(400); await pg.evaluate("window.__tscale = 1e-9")
    return ctx, pg, errs
# a camera on P's own axes: side (its right), behind, front; o = [right, up, forward] for the eye, the look point the same
async def swim(b):
    for cam, eye, at in [('side', [3.2, 0.7, 0.3], [0, 0.3, 0.3]), ('front', [0.9, 1.0, 3.4], [0, 0.3, 0])]:
        ctx, pg, errs = await match(b)
        await pg.evaluate(CAMF); await pg.evaluate(f"__camAx({eye}, {at})")
        await pg.evaluate("__T.ev('P.spd = 0; P.paint = 1;')")
        await pg.evaluate("__adv(1/30, 1)"); cx, cy = await pg.evaluate("__scr(0.3)")
        frames = []; t = 0
        while t < 4.0:
            await pg.evaluate("__T.ev('P.paint = 1')")
            info = await pg.evaluate("__T.ev(`[+P.spd.toFixed(2), VP.slime.ax.A.loco ? +VP.slime.ax.A.loco.slK.toFixed(2) : -1, VP.slime.ax.A.loco && VP.slime.ax.A.loco.sl ? +VP.slime.ax.A.loco.sl.u.toFixed(2) : -1].join(' ')`)")
            frames.append((f'{t:.2f} {info}', await grab(pg, cx, cy, 280, 220, 'f')))
            await pg.evaluate("__adv(1/30, 2)"); t += 2 / 30
        sheet(frames, f'{OUT}/{TAG}_swim_{cam}.png', cols=10)
        print(cam, 'errors', errs[:4]); await ctx.close()
async def turn(b):
    for cam, eye, at in [('behind', [0, 1.5, -2.4], [0, 0.35, 0.4]), ('front', [0, 1.2, 2.6], [0, 0.35, 0])]:
        ctx, pg, errs = await match(b)
        await pg.evaluate(CAMF); await pg.evaluate(f"__camAx({eye}, {at})")
        await pg.evaluate("__T.ev('P.paint = 1')")
        await pg.evaluate("__adv(1/30, 30)"); cx, cy = await pg.evaluate("__scr(0.35)")
        frames = []; t = 0
        while t < 3.2:
            st = 1 if t < 1.0 else (-1 if t < 2.0 else 0)
            await pg.evaluate(f"__T.ev('steerIn = {st}; P.paint = 1')")
            frames.append((f'{t:.2f} s{st}', await grab(pg, cx, cy, 260, 220, 'f')))
            await pg.evaluate("__adv(1/30, 2)"); t += 2 / 30
        sheet(frames, f'{OUT}/{TAG}_turn_{cam}.png', cols=10)
        print(cam, 'errors', errs[:4]); await ctx.close()
async def hop(b):
    for cam, eye, at in [('side', [3.0, 0.9, 0.2], [0, 0.5, 0.2]), ('front', [0.5, 1.0, 3.0], [0, 0.5, 0])]:
        ctx, pg, errs = await match(b)
        await pg.evaluate(CAMF); await pg.evaluate(f"__camAx({eye}, {at})")
        await pg.evaluate("__T.ev('P.paint = 1; P.spd = 0')"); await pg.evaluate("__adv(1/30, 20)"); cx, cy = await pg.evaluate("__scr(0.4)")
        await pg.evaluate("__T.ev('jump(P)')")
        frames = []; t = 0
        while t < 1.6:
            frames.append((f'{t:.2f}', await grab(pg, cx, cy - 40, 260, 280, 'f')))
            await pg.evaluate("__adv(1/60, 3)"); t += 3 / 60
        sheet(frames, f'{OUT}/{TAG}_hop_{cam}.png', cols=11)
        print(cam, 'errors', errs[:4]); await ctx.close()
async def swimcam(b):
    # the game's own camera from rest up into the swim, then a close side run through a few strokes at 30 fps
    ctx, pg, errs = await match(b)
    await pg.evaluate("__T.ev('P.spd = 0; P.paint = 1;')"); await pg.evaluate("__adv(1/30, 1)")
    frames = []; t = 0 if 'side' not in EXTRA else 9
    if t > 3: await pg.evaluate("__adv(1/30, 30)")
    while t < 3.0:
        await pg.evaluate("__T.ev('P.paint = 1')")
        cx, cy = await pg.evaluate("__scr(0.3)")
        info = await pg.evaluate("__T.ev(`[+P.spd.toFixed(1), VP.slime.ax.A.loco ? +VP.slime.ax.A.loco.slK.toFixed(2) : -1, VP.slime.ax.A.loco && VP.slime.ax.A.loco.sl ? +VP.slime.ax.A.loco.sl.u.toFixed(2) : -1].join(' ')`)")
        frames.append((f'{t:.2f} {info}', await grab(pg, cx, cy, 240, 240, 'f')))
        await pg.evaluate("__adv(1/30, 2)"); t += 2 / 30
    if frames: sheet(frames, f'{OUT}/{TAG}_swimcam_game.png', cols=9)
    await pg.evaluate(CAMF); await pg.evaluate("__camAx([3.8, 0.9, -0.1], [0, 0.25, -0.15])")
    await pg.evaluate("__adv(1/30, 1)")
    frames = []; t = 0
    while t < 1.8:
        await pg.evaluate("__T.ev('P.paint = 1')")
        info = await pg.evaluate("__T.ev(`[+P.spd.toFixed(1), VP.slime.ax.A.loco && VP.slime.ax.A.loco.sl ? +VP.slime.ax.A.loco.sl.u.toFixed(2) : -1].join(' ')`)")
        cx, cy = await pg.evaluate("__scr(0.25)")
        frames.append((f'{t:.2f} {info}', await grab(pg, cx, cy, 330, 210, 'f')))
        await pg.evaluate("__adv(1/30, 1)"); t += 1 / 30
    sheet(frames, f'{OUT}/{TAG}_swimcam_side.png', cols=9)
    print('errors', errs[:4]); await ctx.close()
async def swimside(b):
    # from rest along the longest open run on the stage: the crawl up to speed, into the swim, two strokes; seen from the side
    ctx, pg, errs = await match(b)
    yaw = await pg.evaluate("""__T.ev(`(() => { let best = P.yaw, bd = -1; for (let i = 0; i < 36; i++) { const a = i / 36 * 6.2832; if (voidAhead(P, a, 14) > 0) continue; const r = clearRun(P, a, 14); if (r > bd) { bd = r; best = a; } } P.yaw = best; P.spd = 0; P.paint = 1; return [best, bd]; })()`)""")
    print('run', yaw)
    await pg.evaluate(CAMF); await pg.evaluate("__camAx([3.9, 0.85, -0.2], [0, 0.25, -0.25])")
    await pg.evaluate("__adv(1/30, 1)")
    frames = []; t = 0
    while t < 2.4:
        await pg.evaluate("__T.ev('P.paint = 1; steerIn = 0')")
        info = await pg.evaluate("__T.ev(`[+P.spd.toFixed(1), VP.slime.ax.A.loco ? +VP.slime.ax.A.loco.slK.toFixed(2) : -1, VP.slime.ax.A.loco && VP.slime.ax.A.loco.sl ? +VP.slime.ax.A.loco.sl.u.toFixed(2) : -1].join(' ')`)")
        cx, cy = await pg.evaluate("__scr(0.25)")
        frames.append((f'{t:.2f} {info}', await grab(pg, cx, cy, 330, 200, 'f')))
        await pg.evaluate("__adv(1/30, 1)"); t += 1 / 30
    sheet(frames, f'{OUT}/{TAG}_swimside.png', cols=8)
    print('errors', errs[:4]); await ctx.close()
SCN = { 'swimside': swimside, 'swimcam': swimcam, 'locker': locker, 'shake': shake, 'home': home, 'basin': basin, 'swim': swim, 'turn': turn, 'hop': hop }
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        await SCN[SCEN](b)
        await b.close()
asyncio.run(main())
