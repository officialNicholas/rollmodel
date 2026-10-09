# what the player sees: the real game camera through a few moments (a jump, being rammed and sent tumbling, a hard turn, rolling into a
# wall), one contact sheet each (rx/<tag>_pc_<name>.png)
import asyncio, sys, json
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'v66'
ONLY = sys.argv[2].split(',') if len(sys.argv) > 2 else None
PAGE = sys.argv[3] if len(sys.argv) > 3 else 'pc_t.html'
SETUP = r"""(stage) => { const T = __T; window.__noLoop = true; T.mode = 'duel'; T.applyMode(); T.setStage(stage); T.genWorld(88, { themes: [stage] }); T.mapUsed = false; T.start(); T.setWx('clear', 999);
  T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
  const H = T.H; H.st = 'out'; H.x = 99; H.z = 99;
  for (let i = 0; i < 60; i++) { T.steerIn = 0; T.step(1 / 60); T.visuals(1 / 60, 1 / 60); }
  const P = T.P, nodes = T.NAVo.nodes.filter(n => n.h === 0 && n.edge === 0), n0 = nodes.sort((a, b) => Math.hypot(a.x, a.z) - Math.hypot(b.x, b.z))[0]; window.__n0 = n0;
  window.__adv = (dt, f) => { let n = Math.round(dt * 60); while (n-- > 0) { if (f) f(); T.step(1 / 60); T.visuals(1 / 60, 1 / 60); } };
  window.__place = (x, z, yaw, spd) => { for (let i = 0; i < 50; i++) { T.steerIn = 0; P.x = x; P.z = z; P.y = T.surfaceUnder(x, z, 3); P.yaw = yaw; P.air = false; P.spd = spd; P.vy = 0; T.camYaw = yaw; T.step(1 / 60); P.x = x; P.z = z; T.visuals(1 / 60, 1 / 60); } };
  return n0; }"""
SCEN = {
  'jump': ("blank", "() => { const T = __T, P = T.P, n = window.__n0; window.__place(n.x, n.z, 0, T.cfg.speed); T.jump(P); }", [0.05, 0.1, 0.1, 0.1, 0.1, 0.1, 0.08, 0.06, 0.05, 0.06, 0.1, 0.15], "() => { __T.steerIn = 0; }"),
  'tumble': ("blank", "() => { const T = __T, P = T.P, H = T.H, n = window.__n0; window.__place(n.x, n.z, 0, T.cfg.speed * 0.6); H.st = 'play'; H.x = P.x + 0.75; H.z = P.z; H.y = P.y; H.yaw = -Math.PI / 2; H.spd = 11; H.flung = true; H.air = false; T.shove(H, P); }", [0.02, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08, 0.1, 0.1, 0.12, 0.15, 0.2], "() => { __T.steerIn = 0; }"),
  'ram': ("blank", "() => { const T = __T, P = T.P, H = T.H, n = window.__n0; window.__place(n.x, n.z, 0, T.cfg.speed); H.st = 'play'; H.x = P.x + 0.2; H.z = P.z + 3.2; H.y = P.y; H.yaw = 0.4; H.spd = 0; H.air = false; T.LH.drop.visible = true; P.flung = true; P.spd = 12; for (let i = 0; i < 30; i++) { if (H.knockT > 0) break; T.step(1 / 60); T.visuals(1 / 60, 1 / 60); } }", [0.04, 0.08, 0.08, 0.08, 0.08, 0.08, 0.1, 0.1, 0.1, 0.12, 0.15, 0.2], "() => { __T.steerIn = 0; }"),
  'turn': ("blank", "() => { const T = __T, P = T.P, n = window.__n0; window.__place(n.x, n.z, 0, T.cfg.speed); }", [0.1, 0.1, 0.1, 0.12, 0.12, 0.12, 0.12, 0.12, 0.12, 0.1, 0.1, 0.1], "() => { __T.steerIn = window.__tk = (window.__tk || 0) + 1, __T.steerIn = window.__tk < 70 ? 1 : -1; }"),
}
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 360, 'height': 640}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'duel', color: 'red', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300])); pg.on('console', lambda m: m.type == 'error' and 'ERR_' not in m.text and errs.append(m.text[:300]))
        await pg.goto('file://' + SP + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(1200)
        for name, (stage, setup, steps, per) in SCEN.items():
            if ONLY and name not in ONLY: continue
            await pg.evaluate(SETUP, stage); await pg.evaluate("() => { window.__tk = 0; }"); await pg.evaluate(setup)
            frames = []; t = 0
            for k, dt in enumerate(steps):
                await pg.evaluate("([dt, f]) => window.__adv(dt, f ? eval(f) : null)", [dt, per]); t += dt
                await pg.evaluate("() => __T.renderFrame()")
                fn = SP + 'rx/_p%d.png' % k; await pg.screenshot(path=fn); frames.append((fn, t))
            ims = [Image.open(f).crop((0, 140, 360, 560)) for f, _ in frames]; cols = 7; rws = (len(ims) + cols - 1) // cols; W, H = ims[0].size
            sheet = Image.new('RGB', (cols * W, rws * H), (20, 20, 20)); dr = ImageDraw.Draw(sheet)
            for i, im in enumerate(ims):
                x, y = (i % cols) * W, (i // cols) * H; sheet.paste(im, (x, y)); dr.text((x + 4, y + 4), '%.2fs' % frames[i][1], fill=(0, 0, 0))
            sheet.save(SP + 'rx/%s_pc_%s.png' % (TAG, name)); print(name, 'saved')
        print('errors', errs[:4]); await b.close()
asyncio.run(main())
