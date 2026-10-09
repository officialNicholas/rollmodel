import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', mode: 'trio', stage: 'standard', seen: {steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type=='error' and errs.append(m.text[:200]))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=60000); await pg.wait_for_timeout(600)
        a = await pg.evaluate("[__T.GEN.key, __T.GEN.std, __T.ARENA, __T.POTS.length, __T.COF_SPOTS.length, document.getElementById('cvName').textContent]")
        await pg.evaluate("document.getElementById('mWorld').hidden && document.getElementById('homePlay').click()"); await pg.wait_for_timeout(350); await pg.click('#startBtn'); await pg.wait_for_function("__T.state === 'play'", polling=100, timeout=30000); await pg.wait_for_timeout(1500)
        bb = await pg.evaluate("[__T.state, __T.H2.st, +__T.H2.x.toFixed(1), +__T.H2.z.toFixed(1), __T.pots2.length, document.getElementById('bannerSmall').textContent]")
        await pg.evaluate("(()=>{ const T=__T, P=T.P; for (let i = 0; i < 16; i++) { const x = P.x + (i % 4 - 1.5) * 3.2, z = P.z + (i / 4 | 0) * 3.2 - 4.8; T.addSplat(x, Math.max(0, T.surfaceUnder(x, z, P.y + 3, true)), z, 0, 3, T.clock, false, true, 0); } T.flushTrail(); T.matchLeft = 0.05; })()")
        await pg.wait_for_function("!!__T.vic", polling=200, timeout=150000); await pg.wait_for_timeout(900)
        await pg.click('#victory'); await pg.wait_for_function("!document.getElementById('end').hidden", polling=200, timeout=60000); await pg.wait_for_timeout(600)
        c = await pg.evaluate("[document.getElementById('replayBtn').hidden, document.getElementById('endBtn').innerText.replace(/\\n/g,' / '), document.getElementById('pMeta').textContent, document.getElementById('chipCpuName').textContent, document.getElementById('chipCpu2Name').textContent]")
        await pg.screenshot(path='ui/stdtrio_end.png')
        await pg.click('#endBtn'); await pg.wait_for_function("__T.state === 'play'", polling=200, timeout=60000); await pg.wait_for_timeout(300)
        d = await pg.evaluate("[__T.GEN.std, __T.GEN.key, document.getElementById('bannerBig').textContent]")
        print(json.dumps([a, bb, c, d]), errs[:4]); await b.close()
asyncio.run(main())
