# after a turret, a rocket, a giant and a roller end in full sun: half a second unburnt and untouchable, then the burn starts
import asyncio, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 300, 'height': 300})
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'lo', mode: 'solo', seen: {look:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300]))
        await pg.goto('file://' + SP + 'pc_t.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
        r = await pg.evaluate("""() => { const T = __T; window.__noLoop = true; T.mode = 'solo'; T.applyMode(); T.genWorld(91, { themes: ['blank'] }); T.mapUsed = false; T.start(); T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
          const P = T.P, dt = 1 / 60, out = {};
          const run = (n) => { for (let i = 0; i < n; i++) { T.step(dt); T.matchLeft = 99; } };
          run(30);
          // an open sunny spot
          T.setWx('sun', 99); run(5); for (let i = 0; i < 400; i++) { const x = (Math.random() * 2 - 1) * 18, z = (Math.random() * 2 - 1) * 18; if (!T.inShadow(x, z, 0) && Math.abs(T.surfaceUnder(x, z, 3, true)) < 0.05) { P.x = x; P.z = z; P.y = 0; break; } }
          const watch = (label) => { const rows = []; for (let i = 0; i < 48; i++) { T.step(dt); T.matchLeft = 99; P.paint = Math.max(P.paint, 0.5); if (i % 6 === 0) rows.push([+(i * dt).toFixed(2), P.exposed, +(P.immuneT || 0).toFixed(2), +(P.sunGrace || 0).toFixed(2)]); } out[label] = rows; };
          out.wx = T.wx;
          T.startTurret(P); run(10); P.turret.t = 0.01; watch('turret');
          P.giantT = 0.05; run(1); watch('giant');
          P.power = { type: 'roller', t: 0.02 }; watch('roller');
          return out; }""")
        print(json.dumps(r)); print('errors', errs[:4]); await b.close()
asyncio.run(main())
