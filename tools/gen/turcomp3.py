import asyncio, json
from playwright.async_api import async_playwright
U = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844})
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ gfx: 'hi', seen: {steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page()
        await pg.add_init_script('window.__stage = "crypt"'); await pg.goto(U, timeout=240000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=100, timeout=240000)
        r = await pg.evaluate("""() => { const T = __T, R = T.renderer, P = T.P; window.__noLoop = true;
          const run = (k) => { for (let i = 0; i < k; i++) { T.step(0.016); T.visuals(0.016, 0.016); if (i % 4 === 0) T.renderFrame(); } T.renderFrame(); };
          T.setStage(window.__stage || 'island'); T.genWorld(9, { themes: [window.__stage || 'island'] }); T.mapUsed = false; T.start(); run(120); const k0 = new Set(R.info.programs.map(p => p.cacheKey)); T.startTurret(P); run(40); T.fireShot && T.fireShot(P); run(40);
          const nw = R.info.programs.filter(p => !k0.has(p.cacheKey)).map(p => p.cacheKey), depth = [...k0].filter(k => k.startsWith('depth'));
          return { nw, depth }; }""")
        def toks(k): return k.split(',')
        for n in r['nw']:
            for d in r['depth']:
                td = toks(d); tn = toks(n)
                if True: print('vs depth:', [(i, a[:40], b2[:40]) for i, (a, b2) in enumerate(zip(tn, td)) if a != b2], len(tn), len(td))
            best = min(r['depth'], key=lambda d: sum(1 for a, b2 in zip(toks(n), toks(d)) if a != b2) + abs(len(toks(n)) - len(toks(d))))
            tn, tb = toks(n), toks(best)
            print('NEW len', len(tn), 'closest len', len(tb))
            for i, (a, b2) in enumerate(zip(tn, tb)):
                if a != b2: print('  diff at', i, repr(a[:80]), 'vs', repr(b2[:80]))
        await b.close()
asyncio.run(main())
