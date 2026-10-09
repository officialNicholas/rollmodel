# the rocket: lift-off, the high view of its target, the boost dive, the landing; then a CPU's rocket coming down on you
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'rk'
STEP = """(n) => { const T = __T; for (let i = 0; i < n; i++) { T.step(0.016); T.visuals(0.016, 0.016); } T.renderFrame(); const P = T.P, R = P.rocket, H = T.H;
  return { st: T.state, ph: R ? R.ph : null, slow: R ? !!R.slow : null, y: +P.y.toFixed(2), gy: R ? +(+R.gy).toFixed(2) : null, x: +P.x.toFixed(1), z: +P.z.toFixed(1), Hst: H.st, Hph: H.rocket ? H.rocket.ph : null, Hy: +H.y.toFixed(2), mark: T.rocketMark.m.visible, markS: +T.rocketMark.m.scale.x.toFixed(2), btn: document.getElementById('slamBtn').className, pw: document.getElementById('pwText').textContent }; }"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};')
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'duo', look: { eyes: 'round', head: 'hat', back: null, mouth: null }, seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text[:300]))
        await pg.goto(SP + 'pc_t.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
        await pg.evaluate("() => { const T = __T; window.__noLoop = true; T.genWorld(5151, { themes: ['blank'] }); T.mapUsed = false; T.start(); T.setWx('clear', 999); for (let i = 0; i < 150; i++) { T.step(0.016); T.visuals(0.016, 0.016); } T.startRocket(T.P); }")
        shots = [(20, 'a_lift'), (45, 'b_top'), (120, 'c_hover')]
        for n, nm in shots:
            r = await pg.evaluate(STEP, n); await pg.screenshot(path=f'st/{TAG}_{nm}.png', timeout=180000); print(nm, r)
        await pg.evaluate("() => __T.rocketDive(__T.P, false)")
        for n, nm in [(14, 'd_dive'), (40, 'e_land'), (30, 'f_after')]:
            r = await pg.evaluate(STEP, n); await pg.screenshot(path=f'st/{TAG}_{nm}.png', timeout=180000); print(nm, r)
        # a CPU's rocket: it should line up over you and come down; you see its target
        await pg.evaluate("() => { const T = __T; T.P.immuneT = 0; T.H.immuneT = 0; T.startRocket(T.H); }")
        for n, nm in [(80, 'g_cpu_up'), (90, 'h_cpu_aim')]:
            r = await pg.evaluate(STEP, n); await pg.screenshot(path=f'st/{TAG}_{nm}.png', timeout=180000); print(nm, r)
        r = await pg.evaluate("""() => { const T = __T; let out = null; for (let i = 0; i < 600 && T.H.rocket; i++) { T.aiStep(T.H, 0.016); T.step(0.016); } T.visuals(0.016, 0.016); T.renderFrame(); return { Hrocket: !!T.H.rocket, Pst: T.P.st, d: +Math.hypot(T.P.x - T.H.x, T.P.z - T.H.z).toFixed(2), Hst: T.H.st }; }""")
        await pg.screenshot(path=f'st/{TAG}_i_cpu_land.png', timeout=180000); print('cpu landed', r)
        print('errors', errs[:5]); await b.close()
asyncio.run(main())
