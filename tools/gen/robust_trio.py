import asyncio, json, sys
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
N=int(sys.argv[1]) if len(sys.argv)>1 else 60
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844})
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_timeout(2000)
        r = await pg.evaluate("""(N)=>{ const T=__T; T.mode="trio"; T.applyMode(); const out={n:0, fb:0, ms:[], tries:[], sym:{}, arch:{}, bad:[], pots:[], riv:[], pw:[], cof:[], boxes:[], fair:[]};
          for (let i=0;i<N;i++){ const seed=(i*2654435761)>>>0; T.genWorld(seed); const G=T.GEN; out.n++; if(G.fallback) out.fb++; out.ms.push(G.ms); out.tries.push(G.tries); out.sym[G.sym]=(out.sym[G.sym]||0)+1; out.arch[G.arch]=(out.arch[G.arch]||0)+1;
            out.pots.push(T.POTS.length); out.riv.push(T.RIVALS.length); out.pw.push(T.POWER_SPOTS.length); out.cof.push(T.COF_SPOTS.length); out.boxes.push(T.BOXES.length);
            const chk=(lab,x,y,z)=>{ const s=T.surfaceUnder(x,z,y+0.3); if (Math.abs(s-y)>0.05) out.bad.push([seed,lab,'surface',x,y,z,s]); if (T.blockedAt(x,z,y)) out.bad.push([seed,lab,'blocked',x,y,z]); };
            T.POTS.forEach(p=>chk('pot',...p)); T.RIVALS.forEach(p=>chk('riv',...p)); T.POWER_SPOTS.forEach(p=>chk('pw',p[0],p[1],p[2]));
            for (const S of [T.START,T.CSTART]) { const s=T.surfaceUnder(S.x,S.z,10); if (s!==0) out.bad.push([seed,'spawn',S.x,S.z,s]); }
            // holes must not touch the rim, ramps must stay on the canvas
            T.HOLES.forEach(h=>{ if (Math.max(Math.abs(h[0]),Math.abs(h[1]),Math.abs(h[2]),Math.abs(h[3]))>33-1) out.bad.push([seed,'hole-rim',h]); });
            // fairness: path length from each spawn to its 3 nearest coffins
            T.nMultSet && 0;
          }
          return out; }""", N)
        import statistics as st
        print('maps', r['n'], 'fallbacks', r['fb'], 'ms avg', round(st.mean(r['ms'])), 'max', round(max(r['ms'])), 'tries avg', round(st.mean(r['tries']),2), 'max', max(r['tries']))
        print('sym', r['sym']); print('arch', r['arch'])
        for k in ['pots','riv','pw','cof','boxes']: print(k, 'min', min(r[k]), 'avg', round(st.mean(r[k]),1), 'max', max(r[k]))
        print('bad', len(r['bad']), r['bad'][:12])
        print('errors', errs)
        await b.close()
asyncio.run(main())
