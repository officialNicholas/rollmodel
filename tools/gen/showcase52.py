# V52 showcase panels (390x844 @2x, Graphics mode): the countdown, the roller, the rocket's target and landing, the turret, a dizzy CPU,
# the island's bamboo spout, and the customize screen pulling a face
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
ONLY = sys.argv[1].split(',') if len(sys.argv) > 1 else None
NOHUD = '.hud,.corner,#banner,#hint,.pop,#vig,#threat,#threatArrow,.count,.foeptr,.orbptr{visibility:hidden !important}'
STEP = "(n) => { const T = __T; for (let i = 0; i < n; i++) { T.step(0.016); T.visuals(0.016, 0.016); } }"
CAM = """([x, y, z, lx, ly, lz, fov]) => { const T = __T, c = T.camera; T.visuals(0.016, 0.016); c.position.set(x, y, z); c.lookAt(lx, ly, lz); c.fov = fov; c.updateProjectionMatrix(); c.updateMatrixWorld(); T.renderFrame(); c.fov = 60; c.updateProjectionMatrix(); }"""
async def page(p, theme, instant=True, look=None, hud=True):
    b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
    ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, has_touch=True, is_mobile=True)
    await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};' + ('' if instant else 'window.__instant = false; window.__skipIntro = false;'))
    lk = json.dumps(look or { 'eyes': 'round', 'head': 'hat', 'back': None, 'mouth': None })
    await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'duo', color: 'red', look: " + lk + ", seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1} })); } catch (e) {}")
    pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text[:300]))
    await pg.goto(SP + 'pc_t.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
    if not hud: await pg.add_style_tag(content=NOHUD)
    else: await pg.add_style_tag(content='#banner,#hint,.pop{visibility:hidden !important}')
    await pg.evaluate("(th) => { const T = __T; window.__noLoop = true; T.genWorld(5151, { themes: [th] }); T.mapUsed = false; }", theme)
    return b, pg, errs
async def shot(pg, name): await pg.wait_for_timeout(300); await pg.screenshot(path=f'fin/v52_{name}.png', timeout=180000); print('shot', name)
async def main():
    async with async_playwright() as p:
        if not ONLY or 'intro' in ONLY:
            b, pg, errs = await page(p, 'crypt', instant=False)
            await pg.evaluate("() => { __T.start(); }"); await pg.wait_for_function('!__T.irisBusy', polling=100, timeout=60000)
            await pg.evaluate("() => { const T = __T; while (T.introT < 1.5 && T.state === 'intro') { T.step(0.016); T.visuals(0.016, 0.016); } for (const an of document.getAnimations()) { const tg = an.effect && an.effect.target; if (tg && tg.id === 'countN') { an.pause(); an.currentTime = (T.introT - 1.1) * 1000; } } T.renderFrame(); }")
            await shot(pg, '1_intro'); print(errs[:3]); await b.close()
        if not ONLY or 'roller' in ONLY:
            b, pg, errs = await page(p, 'manor', hud=False)
            await pg.evaluate("() => { const T = __T; T.start(); T.setWx('clear', 999); for (let i = 0; i < 100; i++) { T.step(0.016); T.visuals(0.016, 0.016); } T.P.power = { type: 'roller', t: 30 }; }")
            await pg.evaluate(STEP, 70)
            await pg.evaluate("() => { const T = __T, P = T.P, a = P.yaw + 0.55; T.visuals(0.016, 0.016); const c = T.camera; c.position.set(P.x + Math.sin(a) * 2.5, P.y + 1.05, P.z + Math.cos(a) * 2.5); c.lookAt(P.x, P.y + 0.32, P.z); c.fov = 50; c.updateProjectionMatrix(); c.updateMatrixWorld(); T.renderFrame(); c.fov = 60; c.updateProjectionMatrix(); }")
            await shot(pg, '2_roller'); print(errs[:3]); await b.close()
        if not ONLY or 'rocket' in ONLY:
            b, pg, errs = await page(p, 'island')
            await pg.evaluate("() => { const T = __T; T.start(); T.setWx('clear', 999); for (let i = 0; i < 90; i++) { T.step(0.016); T.visuals(0.016, 0.016); } const P = T.P; P.yaw = Math.atan2(-P.x, -P.z); T.camYaw = P.yaw; T.startRocket(P); }")
            await pg.evaluate(STEP, 120); await pg.evaluate("() => __T.renderFrame()"); await shot(pg, '3_rocket')
            await pg.evaluate("() => __T.rocketDive(__T.P, false)")
            await pg.evaluate("() => { const T = __T; for (let i = 0; i < 200 && T.P.rocket; i++) { T.step(0.016); T.visuals(0.016, 0.016); } for (let i = 0; i < 5; i++) { T.step(0.016); T.visuals(0.016, 0.016); } T.renderFrame(); }")
            await shot(pg, '4_land'); print(errs[:3]); await b.close()
        if not ONLY or 'turret' in ONLY:
            b, pg, errs = await page(p, 'cathedral')
            await pg.evaluate("() => { const T = __T; T.start(); T.setWx('clear', 999); for (let i = 0; i < 90; i++) { T.step(0.016); T.visuals(0.016, 0.016); } const P = T.P, H = T.H; H.ai = null; H.steer = 0; const d = 8.5; H.x = P.x + Math.sin(P.yaw) * d; H.z = P.z + Math.cos(P.yaw) * d; H.y = Math.max(0, T.surfaceUnder(H.x, H.z, P.y + 2, true)); H.yaw = P.yaw + 1.2; H.immuneT = 0; window.__H0 = [H.x, H.z]; T.startTurret(P); }")
            await pg.evaluate("() => { const T = __T, H = T.H; for (let i = 0; i < 44; i++) { H.spd = 0.5; T.step(0.016); T.visuals(0.016, 0.016); } }")
            await pg.evaluate("() => { const T = __T, P = T.P, H = T.H, a = P.yaw + Math.PI + 0.55, c = T.camera; T.visuals(0.016, 0.016); c.position.set(P.x + Math.sin(a) * 3.4, P.y + 2.3, P.z + Math.cos(a) * 3.4); c.lookAt((P.x + H.x) / 2, P.y + 0.6, (P.z + H.z) / 2); c.fov = 55; c.updateProjectionMatrix(); c.updateMatrixWorld(); T.renderFrame(); c.fov = 60; c.updateProjectionMatrix(); }")
            await shot(pg, '5_turret')
            r = await pg.evaluate("() => { const T = __T, H = T.H; for (let i = 0; i < 200 && !(H.stunT > 0.75); i++) { H.spd = 0.5; T.step(0.016); T.visuals(0.016, 0.016); } return +(H.stunT || 0).toFixed(2); }")
            print('stun', r)
            await pg.add_style_tag(content=NOHUD)
            await pg.evaluate("() => { const T = __T, H = T.H, P = T.P; for (let i = 0; i < 8; i++) T.visuals(0.016, 0.016); const a = Math.atan2(P.x - H.x, P.z - H.z), c = T.camera; c.position.set(H.x + Math.sin(H.yaw) * 1.9 + 0.3, H.y + 0.8, H.z + Math.cos(H.yaw) * 1.9); c.lookAt(H.x, H.y + 0.42, H.z); c.fov = 42; c.updateProjectionMatrix(); c.updateMatrixWorld(); T.renderFrame(); c.fov = 60; c.updateProjectionMatrix(); }")
            await shot(pg, '6_dizzy'); print(errs[:3]); await b.close()
        if not ONLY or 'spout' in ONLY:
            b, pg, errs = await page(p, 'island', hud=False)
            await pg.evaluate("() => { const T = __T; T.start(); T.setWx('clear', 999); for (let i = 0; i < 90; i++) { T.step(0.016); T.visuals(0.016, 0.016); } const pot = T.pots.find(q => q.g.visible) || T.pots[0]; window.__pot = pot; const P = T.P; P.x = pot.x + Math.sin(pot.g.rotation.y) * 2.6; P.z = pot.z + Math.cos(pot.g.rotation.y) * 2.6; P.yaw = pot.g.rotation.y + Math.PI; P.y = pot.y; P.spd = 0; P.charging = true; P.charge = 0.2; T.H.x = pot.x + 20; }")
            await pg.evaluate(STEP, 30)
            await pg.evaluate("() => { const T = __T, pot = window.__pot, c = T.camera, yaw = pot.g.rotation.y + 0.75; T.visuals(0.016, 0.016); c.position.set(pot.x + Math.sin(yaw) * 3.5, pot.y + 1.7, pot.z + Math.cos(yaw) * 3.5); c.lookAt(pot.x, pot.y + 0.5, pot.z); c.fov = 52; c.updateProjectionMatrix(); c.updateMatrixWorld(); T.renderFrame(); c.fov = 60; c.updateProjectionMatrix(); }")
            await shot(pg, '7_spout'); print(errs[:3]); await b.close()
        if not ONLY or 'look' in ONLY:
            b, pg, errs = await page(p, 'crypt', look={ 'eyes': 'round', 'head': 'horns', 'back': 'wings', 'mouth': None })
            await pg.evaluate("() => { const T = __T; T.showMenu(); T.openLook(); for (let i = 0; i < 220; i++) T.visuals(0.016, 0.016); T.emote(T.P, 'smug', 9); for (let i = 0; i < 20; i++) T.visuals(0.016, 0.016); T.renderFrame(); }")
            await shot(pg, '8_look'); print(errs[:3]); await b.close()
asyncio.run(main())
