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
          // hook gl draw calls by object: wrap renderBufferDirect
          const R=T.renderer, orig=R.renderBufferDirect.bind(R); const cnt={};
          R.renderBufferDirect = function(camera, scene, geometry, material, object, group) { if (object.geometry.drawRange.count === 0) return orig(camera, scene, geometry, material, object, group); let k = object.isInstancedMesh ? 'Inst:'+object.count : object.isSkinnedMesh ? 'skin' : (object.geometry.type + '/' + material.type + (object.parent && object.parent.type !== 'Scene' ? ' <' + object.parent.type : '')); if (camera.isOrthographicCamera) k = 'SHADOW ' + k; cnt[k]=(cnt[k]||0)+1; return orig(camera, scene, geometry, material, object, group); };
          T.renderFrame(); R.renderBufferDirect = orig;
          return Object.entries(cnt).sort((a,b)=>b[1]-a[1]).slice(0,40); })()"""))
        await b.close()
asyncio.run(main())
