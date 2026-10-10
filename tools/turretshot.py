import asyncio, json, sys
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
# the turret on the player, from two angles, and the turret pick-up on the stage
async def run():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 844, 'height': 390}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'land', name:'Dusk', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1,items:1}, look:{head:null, eyes:'edgy', iris:'violet'} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('console', lambda m: m.type == 'error' and 'Failed to load' not in m.text and errs.append(m.text[:200]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1500)
        await pg.evaluate("document.getElementById('mWorld').hidden && document.getElementById('stageBtn').click()"); await pg.wait_for_timeout(350); await pg.tap('#startBtn'); await pg.wait_for_timeout(400)
        await pg.wait_for_function("__T.state === 'play'", timeout=40000); await pg.wait_for_function("!__T.P.air", timeout=90000, polling=300); await pg.wait_for_timeout(800)
        await pg.evaluate("__T.matchLeft = 400; for (const D of __T.ACTIVE) if (D !== __T.P) { D.ai && (D.ai.thinkT = 99); D.spd = 0; } __T.P.held = 'turret'; __T.useHeld(__T.P); if (__T.P.turret) __T.P.turret.t = 60;")
        for k in range(3):
            await pg.wait_for_timeout(2500); print('probe', await pg.evaluate("[__T.P.st, !!__T.P.turret, __T.P.held, +(__T.VP.turK || 0).toFixed(2), __T.VP.tur && __T.VP.tur.visible, __T.P.air, +__T.runT.toFixed(1)]"))
        for i, (off, name) in enumerate([([2.3, 1.5, 2.6], 'side'), ([0.4, 1.3, 3.4], 'front'), ([-2.6, 2.2, -1.4], 'back')]):
            await pg.evaluate("(o => { const P = __T.P; window.__cam = [[P.x + o[0], P.y + o[1], P.z + o[2]], [P.x, P.y + 0.55, P.z]]; })(%s)" % json.dumps(off)); await pg.wait_for_timeout(1200)
            await pg.screenshot(path=f'{WS}/ui/turret_{name}.png')
        print('turret', await pg.evaluate("[!!__T.P.turret, __T.VP.tur && __T.VP.tur.visible, __T.VP.tur && __T.VP.tur.children.length]"))
        # the pick-up: spawn until a turret turns up, then look at it
        got = await pg.evaluate("(() => { __T.P.turret = null; for (let k = 0; k < 8; k++) { __T.itemSpawn.last = 'roller'; __T.itemSpawn.t = 0; __T.spawnItem(); const pw = __T.powers.find(p => p.type === 'turret'); if (pw) return [pw.x, pw.y, pw.z]; for (const p of __T.powers) p.gone = 1; __T.powers.length = 0; } return null; })()")
        print('pickup at', got)
        if got:
            await pg.evaluate("(o => { window.__cam = [[o[0] + 1.6, o[1] + 1.4, o[2] + 2.0], [o[0], o[1] + 0.5, o[2]]]; })(%s)" % json.dumps(got)); await pg.wait_for_timeout(1500)
            await pg.screenshot(path=f'{WS}/ui/turret_pickup.png')
        print('errors', errs[:4]); await b.close()
asyncio.run(run())
