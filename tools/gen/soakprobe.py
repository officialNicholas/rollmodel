import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000)
        await pg.evaluate("(()=>{ __T.genWorld(5); __T.mapUsed=false; __T.showMenu(); __T.start(); window.__noStep = true; })()")
        r = await pg.evaluate(r"""(() => { const T = __T, P = T.P, H = T.H; H.ai = null; H.st = 'ko'; H.koT = 1e9; H.x = 99;
          let U = null; T.scene.traverse(o => { if (o.material && o.material.uniforms && o.material.uniforms.uRewet) U = o.material.uniforms; });
          for (let i = 0; i < 200; i++) T.step(0.012);
          T.forceSun(); let n = 0; for (; n < 4000 && !(T.wx === 'dusk' && T.wxLeft < 0.15); n++) T.step(0.012); for (; n < 6000 && T.wx !== 'rain'; n++) T.step(0.012);
          const out = [];
          for (let k = 0; k < 10; k++) { out.push([T.wx, U.uHardOn.value, +U.uRewet.value.toFixed(2), +T.dryClock.toFixed(2)]); for (let i = 0; i < 9; i++) { T.step(0.012); } T.visuals(0.108, 0.108); }
          return out; })()""")
        print(json.dumps(r), errs[:2]); await b.close()
asyncio.run(main())
