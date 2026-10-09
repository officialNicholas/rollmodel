import asyncio, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 300, 'height': 300})
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'duel', seen: {look:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300]))
        await pg.goto('file://' + SP + 'pc_t.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000)
        r = await pg.evaluate("""() => { const T = __T; window.__noLoop = true; T.mode = 'duel'; T.applyMode(); T.setStage('island'); T.freshMap(); T.mapUsed = false; T.start();
          T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
          const P = T.P, dt = 1/60; let gm = null; T.scene.traverse(o => { if (o.material && o.material.uniforms && o.material.uniforms.uNow && o.material.uniforms.uL) gm = o; });
          const out = []; for (let i = 0; i < 120; i++) { P.paint = 0; P.dry = true; P.dryT = 0; T.steerIn = 0.5; T.step(dt); if (i % 10 === 0) { T.visuals(dt, dt); out.push([+P.spd.toFixed(2), P.air, P.st, P.dry, T.TH.sand, P.grv ? [P.grv.on, +P.grv.x.toFixed(2)] : null, gm ? gm.geometry.drawRange.count : -1]); } }
          return out; }""")
        for row in r: print(row)
        print('errors', errs[:5]); await b.close()
asyncio.run(main())
