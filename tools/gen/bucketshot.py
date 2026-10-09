# the paint bucket up close: at rest, just after a blob lands in it (slosh, handle swing), while it drains (bubbles), and from the game camera
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'bk'
GFX = sys.argv[2] if len(sys.argv) > 2 else 'hi'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 600, 'height': 600}, device_scale_factor=2)
        await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};')
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: '" + GFX + "', mode: 'duo', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text[:300]))
        await pg.goto(SP + 'pc_t.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
        await pg.add_style_tag(content='.hud,.corner,#banner,#hint,.pop,#vig,#threat,#threatArrow{display:none !important}')
        await pg.evaluate("""() => { const T = __T, P = T.P; window.__noLoop = true; T.genWorld(5151, { themes: ['island'] }); T.mapUsed = false; T.start(); T.setWx('clear', 99); for (let i = 0; i < 200; i++) { T.step(0.016); T.visuals(0.016, 0.016); }
          const pot = T.pots.find(q => q.g.visible && q.y < 0.2) || T.pots[0]; window.__pot = pot; let best = null, bs = -1; for (let k = 0; k < 400; k++) { const x = (Math.random() - 0.5) * 40, z = (Math.random() - 0.5) * 40; if (T.surfaceUnder(x, z, 1, true) !== 0) continue; let m = 99; for (const b of T.BOXES) { const dx = Math.max(b[0] - x, 0, x - b[1]), dz = Math.max(b[2] - z, 0, z - b[3]); m = Math.min(m, Math.hypot(dx, dz)); } for (const it of T.swayItems) m = Math.min(m, Math.hypot(it.x - x, it.z - z) - 0.6); if (m > bs) { bs = m; best = [x, z]; } } pot.x = best[0]; pot.z = best[1]; pot.y = 0; pot.g.position.set(pot.x, 0, pot.z); P.x = pot.x + 9; P.z = pot.z; }""")
        cam = """(k) => { const T = __T, c = T.camera, pot = window.__pot; T.visuals(0.016, 0.016); const d = 2.1, a = 0.6; c.position.set(pot.x + Math.sin(a) * d, pot.y + 1.15, pot.z + Math.cos(a) * d); c.lookAt(pot.x, pot.y + 0.28, pot.z); c.fov = 45; c.updateProjectionMatrix(); c.updateMatrixWorld(); T.renderFrame(); c.fov = 60; c.updateProjectionMatrix(); }"""
        await pg.evaluate(cam, 0); await pg.screenshot(path=f'st/{TAG}_rest.png')
        await pg.evaluate("""() => { const T = __T, P = T.P, pot = window.__pot; T.enterPot2(P, pot); for (let i = 0; i < 6; i++) { T.step(0.016); T.visuals(0.016, 0.016); } }""")
        await pg.evaluate(cam, 1); await pg.screenshot(path=f'st/{TAG}_land.png')
        await pg.evaluate("""() => { const T = __T; for (let i = 0; i < 70; i++) { T.step(0.016); T.visuals(0.016, 0.016); } }""")
        await pg.evaluate(cam, 2); await pg.screenshot(path=f'st/{TAG}_drain.png')
        r = await pg.evaluate("() => { const p = window.__pot; return { ink: +p.ink.toFixed(2), slosh: +p.slosh.toFixed(2), bA: +p.bA.toFixed(2), bubs: p.bubs ? p.bubs.filter(b => b.m.visible).length : -1 }; }")
        print(json.dumps(r), errs[:3])
        await b.close()
asyncio.run(main())
