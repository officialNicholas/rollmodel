import asyncio, sys, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    lvl = sys.argv[1]; ks = [int(x) for x in sys.argv[2:]]
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        for k in ks:
            pg = await b.new_page(viewport={'width':390,'height':844})
            await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000)
            await pg.evaluate(f"(()=>{{ __T.genWorld({5000 + k * 131}); __T.mapUsed=false; __T.setDiff('hard'); __T.showMenu(); }})()")
            await pg.evaluate('window.__noLoop=true; window.__fixedPR=true; __T.AU.init(); for (const k in __T.AU) if (typeof __T.AU[k] === "function") __T.AU[k] = () => {};')
            r = await pg.evaluate("""([lvl, sd])=>{ __T.clock=0; Math.random = (()=>{ let s = sd; return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; })(); __T.start(); const T=__T, P=T.P, H=T.H; T.setAI(lvl); P.st='ko'; P.koT=1e9; const ring=[], dumps=[]; let outs=0;
              for (let i=0;i<7600 && T.state==='play';i++){ T.step(0.012);
                if (i%10===0){ const a=H.ai, gp=a.goPot; ring.push([(90-T.matchLeft).toFixed(1), a.mode, H.st, 'p'+H.paint.toFixed(2), 'n'+(a.need||0).toFixed(2), 'v'+H.spd.toFixed(1), H.air?'AIR':'', H.slowed?'S':'', H.x.toFixed(1)+','+H.y.toFixed(1)+','+H.z.toFixed(1), gp?Math.hypot(gp.x-H.x,gp.z-H.z).toFixed(1)+gp.st:'-', a.poundAt, a.plan?a.plan.kind:'', H.charging?'CH':''].join(' ')); if (ring.length>120) ring.shift(); }
                if (H.outs>outs){ outs=H.outs; dumps.push({why:JSON.stringify(H.outWhy), log:ring.slice(-60)}); } }
              return {cov:T.teamCov(1), slams:H.slams, outs:H.outWhy, dumps}; }""", [lvl, 1234 + k * 977])
            print('k', k, 'cov', round(r['cov'],1), 'slams', r['slams'], 'outs', r['outs'])
            for d in r['dumps'][:2]:
                print('  --', d['why']); print('     ' + '\n     '.join(d['log']))
            await pg.close()
        await b.close()
asyncio.run(main())
