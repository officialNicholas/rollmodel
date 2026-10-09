import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844})
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000)
        print(await pg.evaluate("""(()=>{ const T=__T; window.__noLoop=true; T.mode='trio'; T.applyMode(); T.mapUsed=true; T.freshMap(); T.showMenu(); T.start(); T.aiReset(T.P); const P=T.P;
          for (let i=0;i<1200;i++){ T.aiStep(P,0.012); T.steerIn=P.steer; T.step(0.012); if (P.st==='ko') { P.st='play'; P.koT=0; } }
          for (let i=0;i<5;i++) T.visuals(0.016,0.016);
          const R=T.renderer, orig=R.renderBufferDirect.bind(R); const objs=new Map(); let total=0;
          R.renderBufferDirect = function(camera, scene, geometry, material, object, group) { if (camera === T.sun.shadow.camera) { total++; objs.set(object, (objs.get(object)||0)+1); } return orig(camera, scene, geometry, material, object, group); };
          T.renderFrame(); R.renderBufferDirect = orig;
          const rows=[]; for (const [o,n] of objs) rows.push([n, o.geometry.type, o.geometry.groups.length, Array.isArray(o.material)?o.material.length:1, o.uuid.slice(0,4)]);
          rows.sort((a,b)=>b[0]-a[0]); return { total, n: objs.size, rows: rows.slice(0,20) }; })()"""))
        await b.close()
asyncio.run(main())
