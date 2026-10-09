# re-shoots: a CPU seeing stars after a turret hit, and the customize screen pulling a face (no idle bit mid-way)
import asyncio, sys, json
from playwright.async_api import async_playwright
sys.path.insert(0, 'gen')
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
NOHUD = '.hud,.corner,#banner,#hint,.pop,#vig,#threat,#threatArrow,.count,.foeptr,.orbptr{visibility:hidden !important}'
async def page(p, theme, look=None):
    b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
    ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, has_touch=True, is_mobile=True)
    await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};')
    lk = json.dumps(look or { 'eyes': 'round', 'head': 'hat', 'back': None, 'mouth': None })
    await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'duo', color: 'red', look: " + lk + ", seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1} })); } catch (e) {}")
    pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
    await pg.goto(SP + 'pc_t.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
    await pg.evaluate("(th) => { const T = __T; window.__noLoop = true; T.genWorld(5151, { themes: [th] }); T.mapUsed = false; }", theme)
    return b, pg, errs
async def main():
    async with async_playwright() as p:
        b, pg, errs = await page(p, 'cathedral'); await pg.add_style_tag(content=NOHUD)
        await pg.evaluate("""() => { const T = __T; T.start(); T.setWx('clear', 999); for (let i = 0; i < 90; i++) { T.step(0.016); T.visuals(0.016, 0.016); }
          const H = T.H, P = T.P; H.ai = null; H.steer = 0; H.x = P.x + Math.sin(P.yaw) * 4; H.z = P.z + Math.cos(P.yaw) * 4; H.y = Math.max(0, T.surfaceUnder(H.x, H.z, P.y + 2, true)); H.yaw = P.yaw + Math.PI; H.spd = 0; H.air = false; H.stunT = 1.6; P.x += 30;
          for (let i = 0; i < 30; i++) { H.spd = 0; H.stunT = Math.max(H.stunT, 1.2); T.step(0.016); T.visuals(0.016, 0.016); }
          const c = T.camera; c.position.set(H.x + Math.sin(H.yaw) * 2.1 + 0.35, H.y + 0.95, H.z + Math.cos(H.yaw) * 2.1); c.lookAt(H.x, H.y + 0.45, H.z); c.fov = 40; c.updateProjectionMatrix(); c.updateMatrixWorld(); T.renderFrame(); c.fov = 60; c.updateProjectionMatrix(); }""")
        await pg.wait_for_timeout(300); await pg.screenshot(path='fin/v52_6_dizzy.png', timeout=180000); print('dizzy', errs[:3]); await b.close()
        b, pg, errs = await page(p, 'crypt', look={ 'eyes': 'round', 'head': 'horns', 'back': 'wings', 'mouth': None })
        await pg.evaluate("() => { const T = __T; T.showMenu(); T.openLook(); for (let i = 0; i < 220; i++) { T.idle.t = 99; T.idle.act = null; T.visuals(0.016, 0.016); } T.emote(T.P, 'smug', 9); for (let i = 0; i < 24; i++) { T.idle.t = 99; T.visuals(0.016, 0.016); } T.renderFrame(); }")
        await pg.wait_for_timeout(300); await pg.screenshot(path='fin/v52_8_look.png', timeout=180000); print('look', errs[:3]); await b.close()
asyncio.run(main())
