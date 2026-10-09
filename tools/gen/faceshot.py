# the faces: close-ups of the player's face in each reaction, and a CPU's
import asyncio, sys
from playwright.async_api import async_playwright
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'fc'; EYES = sys.argv[2] if len(sys.argv) > 2 else 'round'
CASES = [('normal', ''), ('ouch', "emote(P,'ouch',5)"), ('glee', "emote(P,'glee',5)"), ('smug', "emote(P,'smug',5)"), ('bonk', "emote(P,'bonk',5)"), ('dizzy', "P.stunT=5"), ('flat', "P.flatT=1.2"), ('teeth', "P.charging=true;P.charge=0.8"), ('yawn', "emote(P,'yawn',2); P.emoT=1.0")]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 320, 'height': 320}, device_scale_factor=1)
        await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};')
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'duo', look: { eyes: '" + EYES + "', head: 'hat', back: null, mouth: null }, seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text[:300]))
        await pg.goto(SP + 'pc_t.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
        await pg.add_style_tag(content='.hud,.corner,#banner,#hint,.pop,#vig,#threat,#threatArrow,.count{display:none !important}')
        await pg.evaluate("() => { const T = __T; window.__noLoop = true; T.genWorld(5151, { themes: ['blank'] }); T.mapUsed = false; T.start(); T.setWx('clear', 99); for (let i = 0; i < 120; i++) { T.step(0.016); T.visuals(0.016, 0.016); } }")
        for nm, code in CASES:
            js = "() => { const T = __T, P = T.P, emote = T.emote; P.emoT = 0; P.stunT = 0; P.flatT = 0; P.charging = false; P.charge = 0; P.spd = 0; P.x = 0; P.z = 0; P.y = 0; P.air = false; P.yaw = 0; " + code + "; for (let i = 0; i < 12; i++) { T.visuals(0.016, 0.016); } const c = T.camera; c.position.set(P.x + 0.15, P.y + 0.75, P.z + 1.75); c.lookAt(P.x, P.y + 0.36, P.z); c.fov = 32; c.updateProjectionMatrix(); c.updateMatrixWorld(); T.renderFrame(); c.fov = 60; c.updateProjectionMatrix(); }"
            await pg.evaluate(js); await pg.screenshot(path=f'st/{TAG}_{nm}.png', timeout=180000)
        print('errors', errs[:4]); await b.close()
asyncio.run(main())
