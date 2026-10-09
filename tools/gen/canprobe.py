import asyncio, sys, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 360, 'height': 640})
        await ctx.add_init_script("window.__skipIntro = false; window.__introKind = 'cannon'; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'duel', color: 'red', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('file://' + SP + 'pc_t.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(800)
        r = await pg.evaluate("""() => { const T = __T; window.__noLoop = true; T.mode = 'duel'; T.applyMode(); T.setStage('island'); T.genWorld(88, { themes: ['island'] }); T.mapUsed = false;
          T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
          document.getElementById('menu').hidden = true; T.beginMatch(); const out = [];
          for (let i = 0; i < 120; i++) { T.step(1 / 60); T.visuals(1 / 60, 1 / 60); const P = T.P, I = T.VP.slime, U = I.U;
            if (i % 6 === 0 && T.introT > 1.5) out.push([+T.introT.toFixed(2), P.st, P.introAct ? P.introAct.launched : null, P.ip ? P.ip.coat : null, T.VP.coatSt, +I.coat.c.toFixed(2), +I.coat.b.toFixed(2), I.coat.melt, +U.sCoat.value.x.toFixed(2), +U.sWade.value.x.toFixed(2), +(T.VP.sink||0).toFixed(2), +I.root.position.y.toFixed(2)]); }
          return out; }""")
        for x in r: print(x)
        print(errs[:3]); await b.close()
asyncio.run(main())
