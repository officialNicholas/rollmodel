import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("Math.random = (()=>{ let s=4321; return ()=>{ s=(s*1664525+1013904223)>>>0; return s/4294967296; }; })(); try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ mode: 'duel', seen: {steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000); await pg.wait_for_timeout(300)
        r = await pg.evaluate(r"""(()=>{ const T=__T, P=T.P, H=T.H; window.__noLoop = true; T.start(); for (let i=0;i<110;i++) T.step(0.012); T.showBlobs(); H.ai=null; H.x=P.x+30; T.setWx('clear', 99);
          const out = {}; const x=P.x, z=P.z;
          for (const pv of [0.3, 0.2, 0.13, 0.12, 0.06]) { let flashes = 0; for (let i=0;i<120;i++) { P.paint = pv; P.dry = false; P.spd = 0; P.x=x; P.z=z; T.step(0.012); T.visuals(0.016, 0.016); const c = T.scene.getObjectByProperty ? null : null; } out[pv] = 0; }
          return out; })()""")
        # read the blob color via the drop material at different paint levels
        res = await pg.evaluate(r"""(()=>{ const T=__T, P=T.P; const out={}; const x=P.x, z=P.z; let mat=null; T.scene.traverse(o=>{ if (!mat && o.isMesh && o.material && o.material.uniforms === undefined && o.parent && o.renderOrder===32 && o.material.color) mat=o.material; });
          for (const pv of [0.3, 0.2, 0.13, 0.12, 0.06]) { let white=0; for (let i=0;i<150;i++) { P.paint = pv; P.dry=false; P.spd=0; P.x=x; P.z=z; T.step(0.012); T.visuals(0.016, 0.016); if (mat && mat.color.r > 0.97 && mat.color.g > 0.97 && mat.color.b > 0.97) white++; } out[pv]=white; }
          return out; })()""")
        print(res)
        await pg.evaluate(r"""(()=>{ const T=__T, P=T.P; P.paint=0.08; for (let i=0;i<200;i++) { P.paint=0.08; P.dry=false; P.spd=0; T.step(0.012); T.visuals(0.016,0.016); let mat=null; T.scene.traverse(o=>{ if (!mat && o.isMesh && o.renderOrder===32 && o.material.color) mat=o.material; }); if (mat.color.r > 0.97 && mat.color.g > 0.97) break; } T.renderFrame(); })()""")
        await pg.wait_for_timeout(200); await pg.screenshot(path='ui/lowflash.png')
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
