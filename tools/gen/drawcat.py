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
          for (let i=0;i<5;i++) T.visuals(0.016,0.016); T.renderer.info.autoReset=false; T.renderer.info.reset(); T.renderFrame(); const calls = T.renderer.info.render.calls; T.renderer.info.autoReset=true;
          // visible meshes by top-level child of scene, with frustum test
          const cam=T.camera; cam.updateMatrixWorld(); const fr=new THREE.Frustum(); fr.setFromProjectionMatrix(new THREE.Matrix4().multiplyMatrices(cam.projectionMatrix, cam.matrixWorldInverse));
          const groups={}; let shadowCasters=0;
          for (const top of T.scene.children) { let n=0, sc=0; top.traverseVisible(o => { if (o.isMesh || o.isInstancedMesh || o.isPoints || o.isSprite) { if (o.castShadow) sc++; if (!o.frustumCulled || (o.geometry && (o.geometry.boundingSphere || o.geometry.computeBoundingSphere(), true) && fr.intersectsObject(o))) n++; } }); shadowCasters+=sc; if (n) { const k=(top.type)+':'+(top.children.length); groups[k]=(groups[k]||0)+n; } }
          const sorted = Object.entries(groups).sort((a,b)=>b[1]-a[1]).slice(0,25);
          return { calls, shadowCasters, sorted }; })()"""))
        await b.close()
asyncio.run(main())
