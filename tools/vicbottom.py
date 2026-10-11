"""v198: the winner screen's bottom row before/after, on an iPhone-sized page with its 34pt home-bar band simulated (headless has no safe-area insets)"""
import asyncio
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 430, 'height': 932}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', mode:'duel', runs: 3, tut: { ph: 'done' }, seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1500)
        await pg.evaluate("(() => { const r = __T.renderer; window.__o = r.render.bind(r); r.render = () => {}; })(); 0")
        await pg.evaluate("document.getElementById('homePlay').click()"); await pg.wait_for_function("__T.state === 'play'", timeout=60000); await pg.wait_for_timeout(1500)
        await pg.evaluate("(() => { const P = __T.P; for (let i = 0; i < 16; i++) { const x = P.x + (i % 4 - 1.5) * 3.2, z = P.z + (i / 4 | 0) * 3.2 - 4.8; __T.addSplat(x, Math.max(0, __T.surfaceUnder(x, z, P.y + 3, true)), z, 0, 3, __T.clock, false, true, 0); } __T.flushTrail(); __T.matchLeft = 0.4; })()")
        await pg.wait_for_function("!!__T.vic", timeout=120000, polling=200)
        await pg.evaluate("(() => { const st = document.createElement('style'); st.textContent = ':root{padding-bottom:34px!important}'; document.head.appendChild(st); const b4 = document.createElement('style'); b4.id = 'b4'; b4.textContent = '.victory{padding-bottom:34px!important}'; document.head.appendChild(b4); __T.renderer.render = window.__o; })(); 0")
        await pg.wait_for_timeout(4000)
        m = "(() => { const r = id => { const q = document.getElementById(id).getBoundingClientRect(); return Math.round(q.bottom); }; return { stageBottom: Math.round(document.getElementById('stage').getBoundingClientRect().bottom), place: r('vPlace'), cards: r('vCards'), tap: r('vTap'), pad: getComputedStyle(document.getElementById('victory')).paddingBottom }; })()"
        print('before', await pg.evaluate(m)); await pg.screenshot(path=WS + '/ui/vicbottom_before.png')
        await pg.evaluate("document.getElementById('b4').remove(); 0"); await pg.wait_for_timeout(1500)
        print('after ', await pg.evaluate(m)); await pg.screenshot(path=WS + '/ui/vicbottom_after.png')
        print('errors', errs); await b.close()
asyncio.run(main())
