# the turret: a close look at it, its shots in the game view, a hit stunning a CPU
import asyncio, sys
from playwright.async_api import async_playwright
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'tu'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};')
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'duo', look: { eyes: 'round', head: 'hat', back: null, mouth: null }, seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text[:300]))
        await pg.goto(SP + 'pc_t.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
        await pg.evaluate("() => { const T = __T; window.__noLoop = true; T.genWorld(5151, { themes: ['blank'] }); T.mapUsed = false; T.start(); T.setWx('clear', 999); for (let i = 0; i < 120; i++) { T.step(0.016); T.visuals(0.016, 0.016); } const P = T.P, H = T.H; H.ai = null; H.x = P.x + Math.sin(P.yaw) * 9; H.z = P.z + Math.cos(P.yaw) * 9; H.y = T.surfaceUnder(H.x, H.z, 5, true); H.spd = 0; H.steer = 0; H.immuneT = 0; T.startTurret(P); }")
        # close look from the front-side
        r = await pg.evaluate("""() => { const T = __T, P = T.P; for (let i = 0; i < 20; i++) { T.step(0.016); T.visuals(0.016, 0.016); } const c = T.camera, yaw = P.yaw + 0.7; c.position.set(P.x + Math.sin(yaw) * 2.6, P.y + 1.2, P.z + Math.cos(yaw) * 2.6); c.lookAt(P.x, P.y + 0.45, P.z); c.fov = 45; c.updateProjectionMatrix(); c.updateMatrixWorld(); T.renderFrame(); c.fov = 60; c.updateProjectionMatrix(); return { tur: !!P.turret, shots: T.shots.length }; }""")
        await pg.screenshot(path=f'st/{TAG}_close.png', timeout=180000); print('close', r)
        for n, nm in [(36, 'fire'), (9, 'hit'), (40, 'after')]:
            r = await pg.evaluate("(n) => { const T = __T, P = T.P, H = T.H; H.spd = 0; for (let i = 0; i < n; i++) { T.step(0.016); T.visuals(0.016, 0.016); } T.renderFrame(); return { shots: T.shots.length, Hstun: +(H.stunT || 0).toFixed(2), Hx: +H.x.toFixed(2), Hz: +H.z.toFixed(2), d: +Math.hypot(H.x - P.x, H.z - P.z).toFixed(2), t: +(P.turret ? P.turret.t : 0).toFixed(2), pw: document.getElementById('pwText').textContent, cov: +T.teamCov(0).toFixed(2) }; }", n)
            await pg.screenshot(path=f'st/{TAG}_{nm}.png', timeout=180000); print(nm, r)
        r = await pg.evaluate("() => { const T = __T, P = T.P; for (let i = 0; i < 400 && P.turret; i++) T.step(0.016); T.visuals(0.016, 0.016); return { tur: !!P.turret, shots: T.shots.length, cov: +T.teamCov(0).toFixed(2), spd: +P.spd.toFixed(2) }; }")
        print('end', r, 'errors', errs[:5]); await b.close()
asyncio.run(main())
