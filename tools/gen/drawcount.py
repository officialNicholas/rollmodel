import asyncio, sys, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844})
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000)
        await pg.evaluate("(()=>{ __T.genWorld(5131); __T.mapUsed=false; __T.setDiff('hard'); __T.showMenu(); window.__noLoop=true; __T.AU.init(); for (const k in __T.AU) if (typeof __T.AU[k] === 'function') __T.AU[k] = () => {}; })()")
        r = await pg.evaluate(r"""(() => { const T = __T, P = T.P, H = T.H; T.start(); T.setAI('hard'); T.aiReset(P);
          const census = () => { const c = {}; let n = 0; T.scene.traverseVisible(o => { if (o.isMesh || o.isSprite || o.isLine || o.isPoints) { n++; const k = (o.isInstancedMesh ? 'inst:' : '') + o.material.type + (o.geometry && o.geometry.type ? ':' + o.geometry.type : ''); c[k] = (c[k] || 0) + 1; } }); return { n, top: Object.entries(c).sort((a, b) => b[1] - a[1]).slice(0, 10) }; };
          const a = census();
          for (let i = 0; i < 6000 && T.state === 'play'; i++) { T.setAI('medium'); T.aiStep(P, 0.012); T.steerIn = P.steer; T.setAI('hard'); T.step(0.012); }
          const b = census(); return { a, b }; })()""")
        print(json.dumps(r, indent=0)); await b.close()
asyncio.run(main())
