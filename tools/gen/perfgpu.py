import asyncio, json, sys
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/' + (sys.argv[2] if len(sys.argv) > 2 else 'pc_t.html')
DPR = float(sys.argv[1]) if len(sys.argv) > 1 else 2
JS = r"""(m)=>{ const T=__T; window.__noLoop=true; window.__fixedPR=true; Math.random = (()=>{ let s=99; return ()=>{ s=(s*1664525+1013904223)>>>0; return s/4294967296; }; })(); T.mode=m; T.applyMode(); T.mapUsed=true; T.freshMap(); T.showMenu(); T.start(); T.aiReset(T.P); const P=T.P;
  for (let i=0;i<1500;i++){ T.aiStep(P,0.012); T.steerIn=P.steer; T.step(0.012); }
  for (let f=0; f<10; f++){ T.aiStep(P,0.008); T.step(0.008); T.visuals(0.016,0.016); }
  const gl = T.renderer.getContext(), px = new Uint8Array(4); const sync = () => gl.readPixels(0,0,1,1,gl.RGBA,gl.UNSIGNED_BYTE,px);
  const time = (fn, N=12) => { fn(); sync(); const a=performance.now(); for (let i=0;i<N;i++){ fn(); sync(); } return +((performance.now()-a)/N).toFixed(1); };
  const R = T.renderer, out = { mode: m };
  out.full = time(() => T.renderFrame());
  R.shadowMap.autoUpdate=false; out.noShadowPass = time(() => T.renderFrame()); R.shadowMap.autoUpdate=true;
  out.full2 = time(() => T.renderFrame());
  const pm = T.paintMesh; pm.visible=false; out.noPaint = time(() => T.renderFrame()); pm.visible=true;
  T.stageGroup.visible=false; out.noStage = time(() => T.renderFrame()); T.stageGroup.visible=true;
  out.calls = R.info.render.calls; out.tris = R.info.render.triangles;
  return out; }"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=DPR)
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000); await pg.wait_for_timeout(300)
        for m in ['trio']:
            print(json.dumps(await pg.evaluate(JS, m)))
        print(errs[:3]); await b.close()
asyncio.run(main())
