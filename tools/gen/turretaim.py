# the turret's range: the reticle near and far, shots per second, a shot landing at the far range, and the barrel tipping up
import asyncio
from playwright.async_api import async_playwright
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'duo', look: { eyes: 'round', head: 'hat', back: null, mouth: null }, seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto(SP + 'pc_t.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
        r = await pg.evaluate("""() => { const T = __T; window.__noLoop = true; T.genWorld(5151, { themes: ['blank'] }); T.mapUsed = false; T.start(); T.setWx('clear', 999); for (let i = 0; i < 100; i++) { T.step(0.016); T.visuals(0.016, 0.016); }
          const P = T.P, H = T.H; H.x = 40; H.z = 40; T.startTurret(P); const out = {};
          for (const aim of [0, 0.5, 1]) { P.turret.aim = aim; T.visuals(0.016, 0.016); const m = T.turretMark.g; out['reticle' + aim] = +Math.hypot(m.position.x - P.x, m.position.z - P.z).toFixed(1); }
          P.turret.aim = 1; let fired = 0, n0 = T.shots.length, far = 0; const seen = new Set();
          for (let i = 0; i < 125; i++) { T.step(0.008); for (const s of T.shots) if (!seen.has(s)) { seen.add(s); fired++; } }
          out.shotsPerSec = +(fired / 1.0).toFixed(1); out.visible = T.turretMark.g.visible;
          return out; }""")
        print(r)
        await pg.evaluate("() => { const T = __T, P = T.P; P.turret.aim = 1; for (let i = 0; i < 30; i++) { T.step(0.016); T.visuals(0.016, 0.016); } T.renderFrame(); }")
        await pg.screenshot(path='st/tu_far.png', timeout=180000)
        await pg.evaluate("() => { const T = __T, P = T.P; P.turret.aim = 0; for (let i = 0; i < 30; i++) { T.step(0.016); T.visuals(0.016, 0.016); } T.renderFrame(); }")
        await pg.screenshot(path='st/tu_near.png', timeout=180000)
        print('errors', errs[:4]); await b.close()
asyncio.run(main())
