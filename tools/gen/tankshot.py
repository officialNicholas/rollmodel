# the paint tank riding beside the blob: normal, low, dried up (with the countdown), refilling in a basin
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
W = int(sys.argv[1]) if len(sys.argv) > 1 else 390; H = int(sys.argv[2]) if len(sys.argv) > 2 else 844; OUT = sys.argv[3] if len(sys.argv) > 3 else 'tank'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': W, 'height': H}, device_scale_factor=2, has_touch=True, is_mobile=W < 700)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'lo', mode: 'duel', look: { head: 'hat' }, seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300]))
        await pg.goto('file://' + SP + 'pc_t.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000)
        r = await pg.evaluate("""() => { const T = __T; window.__noLoop = true; T.mode = 'duel'; T.applyMode(); T.setStage('island'); T.freshMap(); T.mapUsed = false; T.setDiff('easy'); T.start();
          T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
          T.setWx('clear', 999); const dt = 1 / 60; T.aiReset(T.P); for (let i = 0; i < 60 * 3; i++) { T.aiStep(T.P, dt); T.steerIn = T.P.steer; T.step(dt); if (i % 10 === 0) { T.visuals(dt * 10, dt * 10); T.flushTrail(); } T.matchLeft = 99; }
          T.P.paint = 0.8; window.__noStep = true; window.__noLoop = false; return { st: T.P.st, paint: T.P.paint }; }""")
        print('ready', r)
        async def shot(name, js, wait=900):
            if js: await pg.evaluate(js)
            await pg.wait_for_timeout(wait)
            info = await pg.evaluate("(() => { const t = document.getElementById('bar'); const b = t.getBoundingClientRect(); return [t.className, Math.round(b.x), Math.round(b.y), Math.round(b.width), Math.round(b.height), getComputedStyle(t).opacity]; })()")
            print(name, info)
            await pg.screenshot(path=SP + OUT + '_' + name + '.png', timeout=120000)
        await shot('normal', None, 1500)
        await shot('low', "__T.P.paint = 0.18")
        await shot('dry', "__T.P.paint = 0; __T.P.dry = true; __T.P.dryT = 1.3")
        await shot('fill', "(() => { const T = __T, P = T.P; P.dry = false; P.dryT = 0; P.paint = 0.45; const pot = T.pots3.find(p => T.potUp(p) && !p.occ); if (pot) T.enterPot2(P, pot); })()", 1500)
        print('errors', errs[:5]); await b.close()
asyncio.run(main())
