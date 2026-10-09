import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000)
        r = await pg.evaluate("""(()=>{ const T=__T; window.__noLoop=true; let bad=0, n=0; const ex=[];
          const inR = (x, z, r, m) => (m = m || 0, r[6] === 'c' ? (x - (r[0] + r[1]) * 0.5) ** 2 + (z - (r[2] + r[3]) * 0.5) ** 2 < Math.max(0, (r[1] - r[0]) * 0.5 + m) ** 2 : x > r[0] - m && x < r[1] + m && z > r[2] - m && z < r[3] + m);
          const rampH = (r, x, z) => { const t = r[4] === 'x' ? (x - r[0]) / (r[1] - r[0]) : (z - r[2]) / (r[3] - r[2]); return r[5] + (r[6] - r[5]) * Math.min(1, Math.max(0, t)); };
          for (const m of ['duel','trio','duel','trio']) { T.mode=m; T.applyMode(); T.mapUsed=true; T.freshMap(); const A=T.ARENA;
            const floorAt = (x, z) => { if (Math.abs(x) > A || Math.abs(z) > A) return -Infinity; for (const h of T.HOLES) if (inR(x, z, h)) return -Infinity; return 0; };
            const su = (x, z, maxY) => { let best = -Infinity; const f = floorAt(x, z); if (f <= maxY) best = f; for (const b of T.BOXES) if (b[5] <= maxY && b[5] > best && inR(x, z, b)) best = b[5]; for (const r of T.RAMPS) if (inR(x, z, r)) { const h = rampH(r, x, z); if (h <= maxY && h > best) best = h; } return best; };
            const ba = (x, z, y) => { const mm = 0.34 * 0.9; for (const b of T.BOXES) if (y < b[5] - 0.32 && y + 0.8 > b[4] && inR(x, z, b, mm)) return true; for (const r of T.RAMPS) if (inR(x, z, r, mm * 0.3)) { const h = rampH(r, Math.min(r[1], Math.max(r[0], x)), Math.min(r[3], Math.max(r[2], z))); if (y < h - 0.32) return true; } return false; };
            for (let i=0;i<40000;i++) { const x=(Math.random()-0.5)*2*(A+3), z=(Math.random()-0.5)*2*(A+3), y=Math.random()*4-0.5; n++;
              const a1=T.surfaceUnder(x,z,y), b1=su(x,z,y); const a2=T.blockedAt(x,z,y), b2=ba(x,z,y); if (a1!==b1 || a2!==b2) { bad++; if (ex.length<5) ex.push([m,x.toFixed(2),z.toFixed(2),y.toFixed(2),a1,b1,a2,b2]); } } }
          return {n, bad, ex}; })()""")
        print(r, errs[:3]); await b.close()
asyncio.run(main())
