import asyncio, sys
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for w, h, t, mode in [(390, 780, 'p', 'duel')]:
            ctx = await b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2, has_touch=True, is_mobile=True)
            await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'" + ('land' if w > h else 'port') + "', name:'Dusk', mode:'" + mode + "', stage:'manor', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1}, owned:['hat','lashes'], bought:['hat','lashes'], look:{head:'hat',lash:'lashes',iris:'violet'} })); } catch (e) {}")
            pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); logs = []; pg.on('console', lambda m: logs.append(m.text[:200]) if m.type == 'error' and 'CORS' not in m.text and 'ERR_FAILED' not in m.text else None)
            await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1500)
            await pg.evaluate("document.getElementById('homePlay').click()"); await pg.wait_for_function("__T.state === 'play'", timeout=30000); await pg.wait_for_timeout(1500)
            await pg.evaluate("(() => { const P = __T.P; for (let i = 0; i < 16; i++) { const x = P.x + (i % 4 - 1.5) * 3.2, z = P.z + (i / 4 | 0) * 3.2 - 4.8; __T.addSplat(x, Math.max(0, __T.surfaceUnder(x, z, P.y + 3, true)), z, 0, 3, __T.clock, false, true, 0); } __T.flushTrail(); __T.matchLeft = 0.4; })()")
            await pg.wait_for_function("!!__T.vic", timeout=40000, polling=200); await pg.wait_for_timeout(1600); await pg.screenshot(path=f'{WS}/ui/vic_{t}_0.png'); print(await pg.evaluate("(() => { const v = __T.vic, P = __T.P, I = __T.VP.slime; return { room: v.room, cy: v.cy, t: +v.t.toFixed(1), giant: P.giantT, form: I && I.st && I.st.form, formNext: I && I.st && I.st.formNext, rad: P.rad, bodyScale: +__T.VP.body.scale.x.toFixed(2), feat: v.feat.length }; })()"))
            await pg.wait_for_timeout(2500); await pg.screenshot(path=f'{WS}/ui/vic_{t}_1.png'); print(await pg.evaluate("(() => { const v = __T.vic, P = __T.P; return { t: +v.t.toFixed(1), giant: P.giantT, rad: P.rad, bodyScale: +__T.VP.body.scale.x.toFixed(2), camZ: +__T.vicCam.position.distanceTo(new __T.THREE.Vector3(P.x, P.y, P.z)).toFixed(2) }; })()")); await pg.wait_for_timeout(2500); await pg.screenshot(path=f'{WS}/ui/vic_{t}_2.png')
            print(t, 'errors', errs[:3], logs[:3]); await ctx.close()
        await b.close()
asyncio.run(main())
