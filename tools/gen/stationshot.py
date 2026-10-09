# a refill station up close: at rest, a moment after a blob dives in (the crown), mid-drain, and the blob leaping out; then from the game camera
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
TAG, THEME = sys.argv[1], sys.argv[2]; GFX = sys.argv[3] if len(sys.argv) > 3 else 'hi'; ANG = float(sys.argv[4]) if len(sys.argv) > 4 else 0.6; DIST = float(sys.argv[5]) if len(sys.argv) > 5 else 2.4
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 640, 'height': 640}, device_scale_factor=2)
        await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};')
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: '" + GFX + "', mode: 'duo', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text[:300]))
        await pg.goto(SP + 'pc_t.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
        await pg.add_style_tag(content='.hud,.corner,#banner,#hint,.pop,#vig,#threat,#threatArrow{display:none !important}')
        info = await pg.evaluate("""(theme) => { const T = __T, P = T.P; window.__noLoop = true; T.genWorld(5151, { themes: [theme] }); T.mapUsed = false; T.start(); T.setWx('clear', 99); for (let i = 0; i < 120; i++) { T.step(0.016); T.visuals(0.016, 0.016); }
          const pot = T.pots.find(q => q.g.visible && q.y < 0.2) || T.pots[0]; window.__pot = pot; P.x = pot.x + 9; P.z = pot.z; T.H.x = pot.x - 9; T.H.z = pot.z + 3;
          return { kind: pot.kind, n: T.pots.length, yaw: +pot.g.rotation.y.toFixed(2), x: +pot.x.toFixed(1), z: +pot.z.toFixed(1), meshes: (() => { let c = 0; pot.g.traverse(o => { if (o.isMesh) c++; }); return c; })() }; }""", THEME)
        print('station', json.dumps(info), errs[:3])
        cam = """([a, d, h]) => { const T = __T, c = T.camera, pot = window.__pot; T.visuals(0.016, 0.016); const yaw = pot.g.rotation.y + a; c.position.set(pot.x + Math.sin(yaw) * d, pot.y + h, pot.z + Math.cos(yaw) * d); c.lookAt(pot.x, pot.y + 0.45, pot.z); c.fov = 45; c.updateProjectionMatrix(); c.updateMatrixWorld(); T.renderFrame(); c.fov = 60; c.updateProjectionMatrix(); }"""
        await pg.evaluate(cam, [ANG, DIST, 1.35]); await pg.screenshot(path=f'st/{TAG}_rest.png', timeout=180000)
        await pg.evaluate(cam, [ANG + 2.2, DIST, 1.2]); await pg.screenshot(path=f'st/{TAG}_rest2.png')
        await pg.evaluate("""() => { const T = __T, P = T.P, pot = window.__pot; T.enterPot2(P, pot); for (let i = 0; i < 9; i++) { T.step(0.016); T.visuals(0.016, 0.016); } }""")
        await pg.evaluate(cam, [ANG, DIST, 1.35]); await pg.screenshot(path=f'st/{TAG}_dive.png')
        await pg.evaluate("""() => { const T = __T; for (let i = 0; i < 60; i++) { T.step(0.016); T.visuals(0.016, 0.016); } }""")
        await pg.evaluate("""() => { const T = __T, P = T.P; T.jump(P); for (let i = 0; i < 10; i++) { T.step(0.016); T.visuals(0.016, 0.016); } }""")
        await pg.evaluate(cam, [ANG, DIST + 0.6, 1.5]); await pg.screenshot(path=f'st/{TAG}_leap.png')
        r = await pg.evaluate("() => { const p = window.__pot, P = __T.P; return { ink: +p.ink.toFixed(2), st: P.st, batT: +(P.batT || 0).toFixed(2), crown: p.crown.visible, jet: p.jet.visible, flow: +p.flow.toFixed(2) }; }")
        # the game's own camera on it
        await pg.evaluate("""() => { const T = __T, P = T.P, pot = window.__pot; for (let i = 0; i < 120; i++) { T.step(0.016); T.visuals(0.016, 0.016); } P.x = pot.x + Math.sin(pot.g.rotation.y) * 3.2; P.z = pot.z + Math.cos(pot.g.rotation.y) * 3.2; P.yaw = pot.g.rotation.y + Math.PI; P.y = pot.y; for (let i = 0; i < 40; i++) { T.step(0.016); T.visuals(0.016, 0.016); } T.renderFrame(); }""")
        await pg.screenshot(path=f'st/{TAG}_game.png')
        print('after', json.dumps(r), errs[:3])
        await b.close()
asyncio.run(main())
