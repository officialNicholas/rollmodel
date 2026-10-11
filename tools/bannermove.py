"""v196: the lesson opens on the move tip (no Paint it banner first); the Paint it banner shows after Let's do it."""
import asyncio
from playwright.async_api import async_playwright
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; window.__skipIntro = false; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{}, drops: 0 })); } catch (e) {}")
        await ctx.add_init_script("window.__bans = []; new MutationObserver(() => {}).observe(document, {}); setInterval(() => { const b = document.getElementById('banner'); if (b && b.classList.contains('on')) { const t = document.getElementById('bannerBig').textContent; if (__bans[__bans.length - 1] !== t) __bans.push(t); } }, 30);")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        async def wait(js, t=300000): await pg.wait_for_function(js, timeout=t, polling=50)
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await wait('typeof __T === "object"'); await pg.wait_for_timeout(1500)
        await pg.evaluate("(() => { const r = __T.renderer; window.__o = r.render.bind(r); r.render = () => {}; })(); 0")
        await pg.tap('#homePlay'); await wait("__T.state === 'play'"); t0 = await pg.evaluate("performance.now()")
        await wait("__T.tut && __T.tut.step === 0"); t1 = await pg.evaluate("performance.now()")
        print('move tip after play (ms)', round(t1 - t0), await pg.evaluate("[__T.tutTip && __T.tutTip.key, JSON.stringify(__bans)]"))
        await pg.evaluate("(() => { let n = 0; while (__T.TUT_STEPS[__T.tut.step].id !== 'rest' && n++ < 20) __T.tutNext(); })(); 0")
        await wait("!document.getElementById('tutGo').hidden", 60000); await pg.evaluate("document.getElementById('tgGo').click()"); await pg.wait_for_timeout(250)
        print('after lets do it', await pg.evaluate("[document.getElementById('banner').className, document.getElementById('bannerBig').textContent, document.getElementById('bannerSmall').textContent, JSON.stringify(__bans)]"))
        await pg.wait_for_timeout(400); await pg.evaluate("document.querySelector('#banner .plate').style.animationPlayState = 'paused'; __T.renderer.render = window.__o; 0"); await pg.wait_for_timeout(150); print("at shot", await pg.evaluate("(() => { const b = document.getElementById('banner'), p = b.querySelector('.plate'); const out = [b.className, JSON.stringify(p && p.getBoundingClientRect()), p && getComputedStyle(p).opacity]; let e = b; while (e) { const c = getComputedStyle(e); if (c.display === 'none' || c.visibility === 'hidden' || +c.opacity < 1) out.push((e.id || e.className) + ':' + c.display + '/' + c.visibility + '/' + c.opacity); e = e.parentElement; } return out; })()")); await pg.screenshot(path=S + '/ws/ui/banner_after_go.png')
        print('errors', errs); await b.close()
asyncio.run(main())
