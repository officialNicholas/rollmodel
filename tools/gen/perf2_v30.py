import asyncio, sys, json
from playwright.async_api import async_playwright
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_v30.html'
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/' + PAGE
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000)
        await pg.evaluate("(()=>{ __T.genWorld(5131); __T.mapUsed=false; __T.setDiff('hard'); __T.showMenu(); window.__noLoop=true; __T.AU.init(); for (const k in __T.AU) if (typeof __T.AU[k] === 'function') __T.AU[k] = () => {}; })()")
        r = await pg.evaluate(r"""(() => { Math.random = (() => { let s = 777; return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; })();
          const T = __T, P = T.P, H = T.H, R = T.renderer, out = {}; T.start(); T.setAI('hard'); T.aiReset(P);
          const frame = () => { T.visuals(0.016, 0.016); const t0 = performance.now(); T.renderFrame(); return performance.now() - t0; };
          frame(); frame(); R.info.reset && R.info.reset();
          let t0 = performance.now(); for (let i = 0; i < 6; i++) frame(); out.ms_start = +((performance.now() - t0) / 6).toFixed(1); out.calls_start = R.info.render.calls; out.tris_start = R.info.render.triangles;
          for (let i = 0; i < 6000 && T.state === 'play'; i++) { T.setAI('medium'); T.aiStep(P, 0.012); T.steerIn = P.steer; T.setAI('hard'); T.step(0.012); }
          frame(); t0 = performance.now(); for (let i = 0; i < 6; i++) frame(); out.ms_late = +((performance.now() - t0) / 6).toFixed(1); out.calls_late = R.info.render.calls; out.tris_late = R.info.render.triangles;
          out.programs = R.info.programs ? R.info.programs.length : -1; out.geoms = R.info.memory.geometries;
          // giant slam spike
          P.st = 'play'; P.air = false; P.giantT = 4; P.slamCD = 0; P.paint = 1; P.ai = null; T.useSlam(P); let k = 0; while ((P.air || P.slam) && k < 200) { T.step(0.012); k++; }
          T.hold = 0; t0 = performance.now(); T.step(0.012); out.slam_step = +(performance.now() - t0).toFixed(1);
          const f1 = frame(), f2 = frame(); let f3 = 0; for (let i = 0; i < 4; i++) { T.step(0.012); f3 += frame(); }
          out.slam_frame1 = +f1.toFixed(1); out.slam_frame2 = +f2.toFixed(1); out.slam_next = +(f3 / 4).toFixed(1); out.calls_slam = R.info.render.calls;
          out.cov = [+T.teamCov(0).toFixed(1), +T.teamCov(1).toFixed(1)];
          return out; })()""")
        print(PAGE, json.dumps(r), errs[:2]); await b.close()
asyncio.run(main())
