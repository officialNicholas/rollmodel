"""v189: the lesson's short callouts sit mid-screen, and slow motion calls the audio cue (muffled music + whoosh) going in and out."""
import asyncio
from playwright.async_api import async_playwright
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{}, drops: 0 })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); sheets = []
        pg.on('response', lambda r: sheets.append((r.url.split('/')[-1], r.status)) if r.url.endswith('.mp3') and '/sfx' in r.url else None)
        async def wait(js, t=300000): await pg.wait_for_function(js, timeout=t, polling=200)
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await wait('typeof __T === "object"'); await pg.wait_for_timeout(1500)
        await pg.evaluate("(() => { const r = __T.renderer; window.__o = r.render.bind(r); r.render = () => {}; const A = __T.AU, f = A.slow; window.__slow = []; A.slow = (...a) => { __slow.push(a); return f(...a); }; })(); 0")
        await pg.tap('#homePlay'); await wait("__T.tut && __T.tut.step === 0"); await pg.wait_for_timeout(800)
        print('move', await pg.evaluate("[JSON.stringify(__slow), __T.tut.slowK, document.getElementById('tutSlow').className]"))
        await pg.evaluate("(() => { let n = 0; while (__T.TUT_STEPS[__T.tut.step].id !== 'sling' && n++ < 20) __T.tutNext(); })()"); await pg.wait_for_timeout(1200)
        print('sling', await pg.evaluate("[JSON.stringify(__slow), __T.tutTip && __T.tutTip.call, __T.tutTip && __T.tutTip.text, Math.round(document.getElementById('tut').getBoundingClientRect().top), Math.round(document.getElementById('tut').getBoundingClientRect().bottom), innerHeight]"))
        await pg.evaluate("__T.renderer.render = window.__o; 0"); await pg.wait_for_timeout(1500); await pg.screenshot(path=S + '/ws/ui/call_center.png')
        print('sheets', sheets, await pg.evaluate("[1]")); print('errors', errs); await b.close()
asyncio.run(main())
