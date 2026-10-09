import asyncio
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':800,'height':600})
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=60000); await pg.wait_for_timeout(600)
        for th in ['garden', 'crypt', 'cathedral', 'manor', 'studio']:
            r = await pg.evaluate("""(th) => { const T = __T; window.__noLoop = true; if (th === 'studio') T.loadStd(); else T.genWorld(4242, { themes: [th] });
              const d = T.aoU.uLitMap.value.image.data; let mx = 0, nz = 0; for (let i = 0; i < d.length; i += 4) { const v = Math.max(d[i], d[i+1], d[i+2]); if (v > mx) mx = v; if (v > 8) nz++; }
              return { lights: T.LIGHTS.length, ex: T.LIGHTS.slice(0, 3).map(l => [l.x.toFixed(1), l.y.toFixed(1), l.z.toFixed(1), l.r.toFixed(1), l.k.toFixed(2)]), max: mx, lit: nz }; }""", th)
            print(th, r)
        print(errs[:3]); await b.close()
asyncio.run(main())
