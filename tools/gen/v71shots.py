# screenshots for the V71 preview: gameplay at the new zoom (portrait and landscape), a far fling as a ball with its hat floating on top
import asyncio, sys
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def shoot(b, w, h, tag):
    ctx = await b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2, has_touch=True, is_mobile=True)
    await ctx.add_init_script("Math.random = (()=>{ let s=777; return ()=>{ s=(s*1664525+1013904223)>>>0; return s/4294967296; }; })(); try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', unlockAll: 1, mode: 'duel', stage: 'island', look: { head: 'tiara' }, seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
    pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    await pg.goto('file://' + SP + 'pc_t.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000)
    await pg.wait_for_timeout(6000)
    await pg.evaluate("() => { const T = __T; T.myLook.head = 'tiara'; try { T.renderLook(); } catch (e) {} T.setStage('island'); document.getElementById('menu').hidden = true; T.beginMatch(); }")
    await pg.wait_for_function("__T.state === 'play'", timeout=60000)
    await pg.evaluate("() => { const T = __T, P = T.P; window.__noLoop = true; for (let i = 0; i < 60 * 1.5; i++) { T.step(1 / 60); T.visuals(1 / 60, 1 / 60); } T.renderFrame(); }")
    await pg.screenshot(path=SP + 'rx/v71_%s_play.png' % tag)
    # a far fling: the ball at the top of its arc
    await pg.evaluate("() => { const T = __T, P = T.P; for (let i = 0; i < 30; i++) { P.spd = 0; T.step(1 / 60); T.visuals(1 / 60, 1 / 60); } T.flingIt(P, 0.95); for (let i = 0; i < 13; i++) { T.step(1 / 60); T.visuals(1 / 60, 1 / 60); } T.renderFrame(); }")
    await pg.screenshot(path=SP + 'rx/v71_%s_ball.png' % tag)
    await ctx.close()
    return errs
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        e1 = await shoot(b, 390, 844, 'port')
        e2 = await shoot(b, 844, 390, 'land')
        print('errors', e1[:3], e2[:3])
        await b.close()
asyncio.run(main())
