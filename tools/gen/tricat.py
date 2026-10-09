import asyncio, json, sys
from playwright.async_api import async_playwright
B='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        for f in sys.argv[1:]:
            ctx = await b.new_context(viewport={'width':390,'height':844})
            await ctx.add_init_script("Math.random = (()=>{ let s=33; return ()=>{ s=(s*1664525+1013904223)>>>0; return s/4294967296; }; })();")
            pg = await ctx.new_page()
            await pg.goto(B+f); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000)
            print(f, await pg.evaluate("""(()=>{ const T=__T; window.__noLoop=true; T.mode='trio'; T.applyMode(); T.mapUsed=true; T.freshMap(); T.showMenu(); T.start(); T.aiReset(T.P); const P=T.P;
              for (let i=0;i<1200;i++){ T.aiStep(P,0.012); T.steerIn=P.steer; T.step(0.012); if (P.st==='ko') { P.st='play'; P.koT=0; } }
              for (let i=0;i<5;i++) T.visuals(0.016,0.016);
              const R=T.renderer, orig=R.renderBufferDirect.bind(R); const cnt={};
              const label = o => { let a=o; while (a.parent && a.parent.type!=='Scene') a=a.parent; return (a===T.stageGroup?'stage':a.type) + (o.isInstancedMesh?'/inst':'') + '/' + o.geometry.type; };
              R.renderBufferDirect = function(camera, scene, geometry, material, object, group) { if (object.geometry.drawRange.count !== 0) { const sh = camera === T.sun.shadow.camera ? 'S:' : 'M:'; let n = group ? group.count : (geometry.index ? geometry.index.count : geometry.attributes.position.count); n = Math.min(n, geometry.drawRange.count) / 3; if (object.isInstancedMesh) n *= object.count; const k = sh + label(object); cnt[k]=(cnt[k]||0)+n; } return orig(camera, scene, geometry, material, object, group); };
              T.renderFrame(); R.renderBufferDirect = orig;
              return Object.entries(cnt).map(([k,v])=>[k,Math.round(v)]).sort((a,b)=>b[1]-a[1]).slice(0,14); })()"""))
            await ctx.close()
        await b.close()
asyncio.run(main())
