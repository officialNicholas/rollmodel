import asyncio, json, sys
from playwright.async_api import async_playwright
PAGE, CPU, N = sys.argv[1], sys.argv[2], int(sys.argv[3])
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/' + PAGE
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000)
        res = {'cpu': 0, 'you': 0, 'none': 0, 't': []}
        for k in range(N):
            r = await pg.evaluate(f"""(() => {{ let s = {k} * 7919 + 13; Math.random = () => {{ s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }};
              window.__noLoop = true; const T = __T, P = T.P, H = T.H, o = T.orb; T.genWorld(1000 + {k}); T.mapUsed = false; T.showMenu(); T.start(); T.setAI('{CPU}'); T.aiReset(P); T.setWx('clear', 999);
              const tick = () => {{ T.setAI('medium'); T.aiStep(P, 0.012); T.steerIn = P.steer; T.setAI('{CPU}'); T.step(0.012); }};
              for (let i = 0; i < 1000; i++) tick();
              if (o.on) return 'already';
              T.orbSpawn(); let i = 0; const md = {{}}; for (; i < 1000 && o.on && T.state === 'play'; i++) {{ tick(); if (H.ai) md[H.ai.mode] = (md[H.ai.mode] || 0) + 1; }} window.__md = md;
              return [H.giantT > 0 ? 'cpu' : P.giantT > 0 ? 'you' : 'none', +(i * 0.012).toFixed(1), window.__md]; }})()""")
            if r == 'already': continue
            res[r[0]] += 1
            res['t'].append([r[0][0], r[1], {k: round(v*0.012,1) for k, v in sorted(r[2].items(), key=lambda kv: -kv[1])[:3]}])
        print(PAGE, CPU, res['cpu'], res['you'], res['none']); [print('  ', t) for t in res['t']]; print(errs[:2]); await b.close()
asyncio.run(main())
