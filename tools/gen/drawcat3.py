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
          const out={}; const potGs = new Set(T.pots.map(p=>p.g)); 
          T.scene.traverseVisible(o => { if (!o.isMesh || !o.castShadow) return; let a=o, depth=0, tag='?'; while (a.parent && a.parent.type !== 'Scene') { a=a.parent; depth++; if (potGs.has(a)) tag='pot'; }
            if (tag==='?') { if (a === T.stageGroup) tag='stage'; else if (T.pots2.some(p=>p.tele===a)) tag='tele'; }
            const k = tag + ':' + o.geometry.type + ':d' + depth + ':top' + a.children.length; out[k]=(out[k]||0)+1; });
          return Object.entries(out).sort((a,b)=>b[1]-a[1]); })()"""))
        await b.close()
asyncio.run(main())
