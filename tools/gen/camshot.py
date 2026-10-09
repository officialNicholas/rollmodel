# the play camera, old and new, on the same canvas and the same spot
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def shot(b, page, out):
    ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
    await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'duel', color: 'red', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
    pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300]))
    await pg.goto('file://' + SP + page, timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(1500)
    r = await pg.evaluate("""() => { const T = __T; window.__noLoop = true; T.mode = 'duel'; T.applyMode(); T.setStage('island'); T.genWorld(4242, { themes: ['island'] }); T.mapUsed = false; T.start(); T.setWx('clear', 999);
      T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
      const P = T.P; for (let i = 0; i < 200; i++) { T.steerIn = 0; T.step(1 / 60); T.visuals(1 / 60, 1 / 60); }
      const nodes = T.NAVo.nodes.filter(n => n.h === 0 && n.edge === 0), n0 = nodes.sort((a, b) => Math.hypot(a.x, a.z + 8) - Math.hypot(b.x, b.z + 8))[0], yw = Math.atan2(-n0.x, -n0.z);
      const H = T.H; H.ai = null; H.x = 30; H.z = 30;
      P.x = n0.x; P.z = n0.z; P.yaw = yw; P.y = 0; P.air = false; T.camYaw = yw; for (let i = 0; i < 150; i++) { T.steerIn = 0; P.x = n0.x; P.z = n0.z; P.yaw = yw; P.spd = 0.01; T.step(1 / 60); P.x = n0.x; P.z = n0.z; P.spd = 0.01; T.visuals(1 / 60, 1 / 60); } T.renderFrame();
      const c = T.camera; return { cam: [c.position.x, c.position.y, c.position.z].map(v => +v.toFixed(2)), dist: +Math.hypot(c.position.x - P.x, c.position.y - P.y, c.position.z - P.z).toFixed(2) }; }""")
    await pg.screenshot(path=SP + out); print(page, json.dumps(r), errs[:2]); await ctx.close()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        await shot(b, 'pc_v64.html', 'st/cam_old.png'); await shot(b, 'pc_t.html', 'st/cam_new.png'); await b.close()
asyncio.run(main())
