import asyncio, json, sys
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def settle(pg, n=160):
    await pg.evaluate(f"(()=>{{ for (let i=0;i<{n};i++) __T.visuals(0.0001, 0.05); __T.renderFrame(); }})()")
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ seen: {steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type=='error' and 'ERR_' not in m.text and errs.append(m.text))
        pg.set_default_timeout(180000); await pg.goto(U, timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000); await pg.wait_for_timeout(500)
        for m in ['trio', 'solo']:
            await pg.evaluate("document.getElementById('mWorld').hidden && document.getElementById('homePlay').click()"); await pg.wait_for_timeout(350); await pg.click(f'#modes button[data-m="{m}"]'); await pg.wait_for_timeout(600); await settle(pg)
            print(m, 'menu', await pg.evaluate("({mode: __T.mode, arena: __T.ARENA, active: __T.ACTIVE.length, h2vis: __T.L2.drop.visible, hvis: __T.LH.drop.visible, stagesHidden: document.getElementById('stages').hidden, note: document.getElementById('soloNote').textContent, c2: __T.CSTART2})"))
            await pg.screenshot(path=f'ui/mode_{m}_menu.png')
            # play a fast simulated match: you are driven by the AI too
            r = await pg.evaluate("""(m)=>{ const T=__T; window.__noLoop = true; T.start(); T.aiReset(T.P); const P=T.P; let i=0; const t0=performance.now();
              for (; i<(m==='solo'?5200:7800) && T.state==='play'; i++) { T.aiStep(P, 0.012); T.steerIn = P.steer; T.step(0.012); }
              return { steps: i, state: T.state, you: T.teamCov(0).toFixed(1), cpu: T.teamCov(1).toFixed(1), cpu2: T.teamCov(2).toFixed(1), kos: [T.P.kos, T.H.kos, T.H2.kos], outs: [T.P.outs, T.H.outs, T.H2.outs], flats: [T.P.flats, T.H.flats, T.H2.flats], hst: T.H.st, h2st: T.H2.st, ms: Math.round(performance.now()-t0) }; }""", m)
            print(m, 'sim', json.dumps(r))
            await pg.evaluate("window.__noLoop = false;"); await pg.wait_for_timeout(400); await pg.screenshot(path=f'ui/mode_{m}_hud.png')
            await pg.evaluate("__T.matchLeft = 0.05")
            await pg.wait_for_function("!!__T.vic || !document.getElementById('end').hidden", polling=250, timeout=240000); await pg.wait_for_timeout(2500)
            if await pg.evaluate("!!__T.vic && !document.getElementById('victory').hidden"): await pg.tap('#victory')
            await pg.wait_for_function("!document.getElementById('end').hidden", polling=250, timeout=240000); await pg.wait_for_timeout(1200)
            print(m, 'end', await pg.evaluate("({title: document.getElementById('endTitle').textContent, chips: [...document.querySelectorAll('.pchip')].filter(c=>!c.hidden).map(c=>c.innerText.replace(/\\n/g,' ')), stats: document.getElementById('endStats').innerText.replace(/\\n/g,' | ')})"))
            await pg.screenshot(path=f'ui/mode_{m}_end.png')
            await pg.click('#menuBtn', no_wait_after=True, timeout=120000); await pg.wait_for_timeout(800)
        print('errors', errs[:5]); await b.close()
asyncio.run(main())
