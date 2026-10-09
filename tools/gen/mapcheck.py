# do the three blobs (and their looks) share one shape (V8 hidden class)? After a stretch of a 3-way match: same-map checks, and the
# properties each has that the others don't (in the order they were added)
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist', '--js-flags=--allow-natives-syntax'])
        ctx = await b.new_context(viewport={'width': 200, 'height': 300}, device_scale_factor=1)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'trio', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300]))
        await pg.goto('file://' + SP + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(800)
        r = await pg.evaluate("""() => { const T = __T, P = T.P, H = T.H, H2 = T.H2; window.__noLoop = true;
          T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
          T.mode = 'trio'; T.applyMode(); T.setStage('island'); T.genWorld(77, { themes: ['island'] }); T.mapUsed = false; T.start(); T.setWx('clear', 999); T.aiReset(P);
          for (let i = 0; i < 1800; i++) { T.aiStep(P, 1 / 60); T.steerIn = P.steer; T.step(1 / 60); T.visuals(1 / 60, 1 / 60); }
          const keys = o => Object.keys(o), diff = (a, b) => keys(a).filter(k => !(k in b));
          const VC = T.VC, V2 = T.L2.V, VP = T.VP;
          return { sameMapPH: %HaveSameMap(P, H), sameMapHH2: %HaveSameMap(H, H2), fastP: %HasFastProperties(P), nP: keys(P).length, nH: keys(H).length, nH2: keys(H2).length,
            PnotH: diff(P, H), HnotP: diff(H, P), H2notH: diff(H2, H), HnotH2: diff(H, H2),
            sameVPVC: %HaveSameMap(VP, VC), sameVCV2: %HaveSameMap(VC, V2), fastVP: %HasFastProperties(VP), nVP: keys(VP).length, VPnotVC: diff(VP, VC), VCnotVP: diff(VC, VP), VCnotV2: diff(VC, V2), V2notVC: diff(V2, VC),
            orderP: keys(P).slice(-30), orderH: keys(H).slice(-30) }; }""")
        print(json.dumps(r, indent=0)[:6000]); print('errors', errs[:3]); await b.close()
asyncio.run(main())
