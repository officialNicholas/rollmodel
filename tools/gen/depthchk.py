import asyncio, json
from playwright.async_api import async_playwright
U = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844})
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ gfx: 'hi', seen: {steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page()
        await pg.goto(U, timeout=240000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=100, timeout=240000)
        r = await pg.evaluate("""() => { const T = __T, R = T.renderer; const ks = () => R.info.programs.map(p => p.cacheKey).filter(k => k.startsWith('depth')).map(k => { const t = k.split(','); return [t[5], t[34], t[38], t[41], t[51], t[54].slice(0, 12)].join('|'); });
          const a = ks(); let stand = 0; T.scene.traverse(o => { if (o.isMesh && o.geometry && o.geometry.parameters && o.geometry.parameters.width === 0.01) stand++; });
          return { depthAtBoot: a, stand, sm: { enabled: R.shadowMap.enabled, auto: R.shadowMap.autoUpdate, type: R.shadowMap.type }, sunAuto: T.sun.shadow.autoUpdate }; }""")
        print(json.dumps(r, indent=1)); await b.close()
asyncio.run(main())
