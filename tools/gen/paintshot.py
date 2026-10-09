# the slime moving through its own paint: a few seconds of driving in a curve on the island, then the gameplay camera, a low close view
# beside it and a close view from behind; one sheet rx/<tag>_paint.png
import asyncio, sys
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'paint'
PAGE = sys.argv[2] if len(sys.argv) > 2 else 'pc_t.html'
COLOR = sys.argv[3] if len(sys.argv) > 3 else 'red'
STAGE = sys.argv[4] if len(sys.argv) > 4 else 'island'
SETUP = r"""(stage) => { const T = __T; window.__noLoop = true; T.mode = 'duel'; T.applyMode(); T.setStage(stage === 'island' || stage === 'blank' ? stage : 'season'); T.genWorld(stage === 'crypt' ? 4242 : 88, { themes: [stage] }); T.mapUsed = false; T.start(); T.setWx('clear', 999);
  T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
  document.querySelectorAll('#stage > *:not(#cv)').forEach(e => e.style.visibility = 'hidden');
  const H = T.H; H.st = 'out'; H.x = 99; H.z = 99; T.LH.drop.visible = false;
  for (let i = 0; i < 60; i++) { T.steerIn = 0; T.step(1 / 60); T.visuals(1 / 60, 1 / 60); }
  const P = T.P, open = n => { for (let a = 0; a < 12; a++) for (let r = 1; r <= 6; r += 1) { const x = n.x + Math.sin(a / 12 * 6.2832) * r, z = n.z + Math.cos(a / 12 * 6.2832) * r; if (T.surfaceUnder(x, z, 1) !== 0 || T.blockedAt(x, z, 0.3)) return false; } return true; }, nodes = T.NAVo.nodes.filter(n => n.h === 0 && n.edge === 0 && open(n));
  const n0 = nodes.sort((a, b) => Math.hypot(a.x, a.z) - Math.hypot(b.x, b.z))[0] || T.NAVo.nodes[0];
  // its own paint all round the spot: a few big round splats and a trail of smaller ones
  for (let i = 0; i < 7; i++) { const a = i / 7 * 6.2832, r = i ? 1.6 : 0; T.addSplat(n0.x + Math.sin(a) * r, 0, n0.z + Math.cos(a) * r, a, 1.5, T.clock, false, true, 0, 0); }
  for (let i = 0; i < 8; i++) T.addSplat(n0.x - 2.4 - i * 0.6, 0, n0.z + Math.sin(i) * 0.4, 0.3 * i, 0.55, T.clock, false, true, 0, 0);
  window.__place = (yaw, spd) => { for (let i = 0; i < 70; i++) { T.steerIn = 0; P.x = n0.x; P.z = n0.z; P.y = 0; P.yaw = yaw; P.air = false; P.spd = spd; P.vy = 0; T.camYaw = yaw; P.paint = 1; T.step(1 / 60); P.x = n0.x; P.z = n0.z; { const I = T.VP.slime; if (I) { I.st.blinkT = 9; I.st.blinkK = 0; } } T.visuals(1 / 60, 1 / 60); } };
  window.__place(0.6, T.cfg.speed * 0.9); T.flushTrail();
  window.__shot = (az, el, dist, look, fov) => { const c = T.camera, D = T.P, R = T.VP.root, a = D.yaw + az; c.position.set(R.position.x + Math.sin(a) * dist, R.position.y + el, R.position.z + Math.cos(a) * dist); c.lookAt(R.position.x, R.position.y + (look || 0), R.position.z); c.fov = fov || 30; c.updateProjectionMatrix(); T.renderFrame(); c.fov = 40; c.updateProjectionMatrix(); };
  const R = T.VP.root; return { x: P.x, z: P.z, wade: T.VP.wade, rootY: R.position.y, splats: T.splatN }; }"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 360, 'height': 640}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'duel', color: '" + COLOR + "', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300])); pg.on('console', lambda m: m.type == 'error' and 'ERR_' not in m.text and errs.append(m.text[:300]))
        await pg.goto('file://' + SP + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(1000)
        r = await pg.evaluate(SETUP, STAGE); print('setup', r)
        shots = []
        await pg.evaluate("() => { __T.renderFrame(); }"); fn = SP + 'rx/_p_play.png'; await pg.screenshot(path=fn); shots.append((fn, 'play', (0, 150, 360, 520)))
        await pg.evaluate("() => window.__shot(1.2, 0.45, 3.4, 0.1)"); fn = SP + 'rx/_p_side.png'; await pg.screenshot(path=fn); shots.append((fn, 'side close', (0, 120, 360, 520)))
        await pg.evaluate("() => window.__shot(3.0, 1.2, 4.2, 0.0)"); fn = SP + 'rx/_p_back.png'; await pg.screenshot(path=fn); shots.append((fn, 'back', (0, 120, 360, 520)))
        await pg.evaluate("() => window.__shot(0.5, 3.5, 8.5, 0.0, 34)"); fn = SP + 'rx/_p_far.png'; await pg.screenshot(path=fn); shots.append((fn, 'far', (0, 120, 360, 520)))
        ims = []
        for fn, label, box in shots:
            im = Image.open(fn).convert('RGB'); s = im.size[0] / 360; im = im.crop(tuple(int(v * s) for v in box)); im = im.resize((int(im.size[0] * 600 / im.size[1]), 600)); ims.append((im, label))
        W = sum(im.size[0] for im, _ in ims) + 8 * (len(ims) - 1); sheet = Image.new('RGB', (W, 600), (16, 12, 24)); x = 0; dr = ImageDraw.Draw(sheet)
        for im, label in ims: sheet.paste(im, (x, 0)); dr.text((x + 6, 6), label, fill=(255, 255, 255)); x += im.size[0] + 8
        sheet.save(SP + 'rx/%s_paint.png' % TAG); print('saved', sheet.size)
        print('errors', errs[:4]); await b.close()
asyncio.run(main())
