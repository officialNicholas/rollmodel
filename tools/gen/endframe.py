import asyncio, json, sys
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
SIZES=[(1366,800,'d'),(1024,768,'t'),(1920,1080,'f'),(390,844,'m')]
if len(sys.argv)>1: SIZES=[s for s in SIZES if s[2] in sys.argv[1]]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        for W,H,tag in SIZES:
            mobile = W < 600
            ctx = await b.new_context(viewport={'width':W,'height':H}, device_scale_factor=1, has_touch=mobile, is_mobile=mobile)
            await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', mode: '" + ('trio' if tag=='f' else 'duel') + "', seen: {steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
            pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=60000); await pg.wait_for_timeout(600)
            await pg.evaluate("document.getElementById('mWorld').hidden && document.getElementById('homePlay').click()"); await pg.wait_for_timeout(350); await pg.click('#startBtn'); await pg.wait_for_function("__T.state === 'play'", polling=100, timeout=20000); await pg.wait_for_timeout(600)
            await pg.evaluate("(()=>{ const T=__T, P=T.P; for (let i = 0; i < 16; i++) { const x = P.x + (i % 4 - 1.5) * 3.2, z = P.z + (i / 4 | 0) * 3.2 - 4.8; T.addSplat(x, Math.max(0, T.surfaceUnder(x, z, P.y + 3, true)), z, 0, 3, T.clock, false, true, 0); } T.flushTrail(); T.matchLeft = 0.05; })()")
            await pg.wait_for_function("!!__T.vic", polling=200, timeout=150000); await pg.wait_for_timeout(1200)
            await pg.click('#victory'); await pg.wait_for_function("!document.getElementById('end').hidden", polling=200, timeout=60000)
            # jump the camera to its settled framing at a few orbit angles
            for k, yaw in enumerate([0.0, 0.8, 1.6, 2.4]):
                await pg.evaluate(f"(()=>{{ window.__noLoop = true; const T = __T; T.camYaw = {yaw}; for (let i = 0; i < 90; i++) T.visuals(0.0001, 0.05); T.camYaw = {yaw}; for (let i = 0; i < 4; i++) T.visuals(0.0001, 0.05); T.renderFrame(); }})()")
                await pg.screenshot(path=f'ui/endf_{tag}{k}.png')
            print(tag, await pg.evaluate("[__T.outK.toFixed(2), __T.outroSc.toFixed(3), document.getElementById('end').offsetLeft, document.getElementById('end').offsetTop]"), errs[:3])
            await ctx.close()
        await b.close()
asyncio.run(main())
