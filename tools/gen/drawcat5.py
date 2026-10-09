import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':390,'height':844})
        await ctx.add_init_script("Math.random = (()=>{ let s=33; return ()=>{ s=(s*1664525+1013904223)>>>0; return s/4294967296; }; })();")
        pg = await ctx.new_page()
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000)
        print(await pg.evaluate("""(()=>{ const T=__T; window.__noLoop=true; T.mode='trio'; T.applyMode(); T.mapUsed=true; T.freshMap(); T.showMenu(); T.start(); T.aiReset(T.P); const P=T.P;
          for (let i=0;i<1200;i++){ T.aiStep(P,0.012); T.steerIn=P.steer; T.step(0.012); if (P.st==='ko') { P.st='play'; P.koT=0; } }
          for (let i=0;i<5;i++) T.visuals(0.016,0.016);
          const blobRoots = [T.P, T.H, T.H2]; // find root groups by walking up from objects: label by top ancestor
          const R=T.renderer, orig=R.renderBufferDirect.bind(R); const cnt={};
          const label = o => { let a=o, chain=[]; while (a.parent && a.parent.type!=='Scene') { a=a.parent; } return (a===T.stageGroup?"stage":a.type+"#"+a.id+"|"+(a.isMesh?(a.geometry.type+"/"+a.material.type+"/ro"+a.renderOrder):"")) ; };
          R.renderBufferDirect = function(camera, scene, geometry, material, object, group) { if (camera !== T.sun.shadow.camera && object.geometry.drawRange.count !== 0) { const k = label(object); cnt[k]=(cnt[k]||0)+1; } return orig(camera, scene, geometry, material, object, group); };
          T.renderFrame(); R.renderBufferDirect = orig;
          const tops = {}; for (const c of T.scene.children) { let n=0; c.traverse(o=>{ if(o.isMesh) n++; }); tops[c.type+'#'+c.id] = n; }
          return Object.entries(cnt).sort((a,b)=>b[1]-a[1]).slice(0,60); const tot=Object.values(cnt).reduce((a,b)=>a+b,0); return {tot, list: Object.entries(cnt).sort((a,b)=>b[1]-a[1]).slice(0,60)}; })()"""))
        await b.close()
asyncio.run(main())
