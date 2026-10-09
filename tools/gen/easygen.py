import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000); await pg.wait_for_timeout(300)
        r = await pg.evaluate("""(() => { const T = __T; window.__noLoop = true; const res = {};
          for (const easy of [false, true]) { const st = { holes: 0, holeMaps: 0, floating: 0, high: 0, boxes: 0, area: 0, fallback: 0, tries: 0, ms: 0, archs: {}, maps: 0 };
            for (let k = 0; k < 40; k++) { T.genWorld(9000 + k * 7919, { easy }); const G = T.GEN; st.maps++;
              st.holes += T.HOLES.length; if (T.HOLES.length) st.holeMaps++; st.floating += T.BOXES.filter(b => b[4] > 0.5).length; st.high += T.BOXES.filter(b => b[4] > 1.8).length; st.boxes += T.BOXES.length;
              st.fallback += G.fallback ? 1 : 0; st.tries += G.tries; st.ms += G.ms; st.archs[G.arch] = (st.archs[G.arch] || 0) + 1; if (G.easy !== easy) st.bad = (st.bad || 0) + 1; }
            for (const k of ['holes', 'floating', 'high', 'boxes', 'tries', 'ms']) st[k] = +(st[k] / st.maps).toFixed(2); res[easy ? 'easy' : 'normal'] = st; }
          return res; })()""")
        print(json.dumps(r, indent=1), errs[:3]); await b.close()
asyncio.run(main())
