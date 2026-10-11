"""v214 in a real match: the game's AI drives you (and the CPU); the feet's slip measured from the animator's own stance flags over a few
seconds of play, a jump and a full slingshot; frames from the game's camera."""
import asyncio, json, sys
from playwright.async_api import async_playwright
OUT = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/lab'
STEP = """(n => { const T = __T, dt = 1 / 60, rows = []; for (let k = 0; k < n; k++) { T.step(dt / 2); T.step(dt / 2); T.visuals(dt, dt); T.flushTrail();
  const D = T.P, I = T.VP.slime, A = I && I.ax && I.ax.A, L = A && A.loco;
  if (A && L && A.state === 'crawl') { const M = A.P.m[A.mesh]; I.root.updateWorldMatrix(true, true); const r = { t: T.runT, x: D.x, z: D.z, spd: D.spd, air: !!D.air, f: L.f, v: L.v, ball: +(L.ballK || 0).toFixed(2) };
    for (const l of L.limbs) { const w = new THREE.Vector3(); M.byName[l.en].getWorldPosition(w); r[l.en] = [w.x, w.y, w.z, l.st]; } rows.push(r); } } return rows; })"""
def slip(rows):
    out = {}
    for n in ['hand.L', 'hand.R', 'foot.L', 'foot.R']:
        sp, bs = [], []
        for a, c in zip(rows, rows[1:]):
            if a[n][3] == 'stance' and c[n][3] == 'stance' and c['t'] - a['t'] > 0.001:
                dt = c['t'] - a['t']; sp.append(((c[n][0] - a[n][0]) ** 2 + (c[n][2] - a[n][2]) ** 2) ** 0.5 / dt); bs.append(((c['x'] - a['x']) ** 2 + (c['z'] - a['z']) ** 2) ** 0.5 / dt)
        out[n] = (round(sum(sp) / max(1, len(sp)), 2), round(sum(bs) / max(1, len(bs)), 2), len(sp))
    return out
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 430, 'height': 754}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1,items:1}, runs: 9, flings: 99, tut: { ph: 'done' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:400])); pg.on('console', lambda m: errs.append(m.text[:300]) if m.type == 'error' and 'Failed to load' not in m.text and 'ERR_FAILED' not in m.text else None)
        await pg.goto('http://localhost:8765/pc_perf.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && !!__T.VP && !!__T.VP.slime && !!window.__perfAI', timeout=300000, polling=1000)
        await pg.evaluate("(() => { __T.mode = 'duel'; __T.applyMode(); __T.start(); })()")
        await pg.wait_for_function("__T.state === 'play'", timeout=240000, polling=500); await pg.evaluate("window.__noStep = true; window.__perfAI();")
        await pg.evaluate(STEP + "(150)"); rows = []
        for k in range(8): rows += await pg.evaluate(STEP + "(30)")
        print('play: frames', len(rows), 'slip', slip(rows), 'game speeds', [round(r['spd'], 1) for r in rows[::30]], 'gait f', [round(r['f'], 1) for r in rows[::30]])
        for i in range(6): await pg.evaluate(STEP + "(4)"); await pg.screenshot(path=f'{OUT}/g_run_{i}.png')
        # a jump, then a full slingshot from the ground
        for k in range(40):
            if not await pg.evaluate("__T.P.air"): break
            await pg.evaluate(STEP + "(3)")
        await pg.evaluate("__T.jump(__T.P)"); rows = await pg.evaluate(STEP + "(80)"); print('jump: frames', len(rows), 'air frames', sum(r['air'] for r in rows), 'slip', slip(rows))
        for k in range(40):
            if not await pg.evaluate("__T.P.air"): break
            await pg.evaluate(STEP + "(3)")
        await pg.evaluate("__T.flingIt(__T.P, 1)"); shots = []
        for i in range(8): await pg.evaluate(STEP + "(6)"); await pg.screenshot(path=f'{OUT}/g_fling_{i}.png'); shots.append(await pg.evaluate("[!!__T.P.air, +(__T.VP.slime.ax.A.loco.ballK || 0).toFixed(2), +(__T.VP.slime.ax.spin || 0).toFixed(2)]"))
        print('fling (air, ball, spin):', shots)
        print('cpu animator:', await pg.evaluate("(() => { const V = __T.ACTIVE.filter(D => D !== __T.P).map(D => D); return __T.ACTIVE.length; })()"))
        print('errors', errs[:6]); await b.close()
asyncio.run(main())
