"""v225: the onboarding's locker and shop tips leave the scene clear (no dark, no blur), the control asked for ringed in gold."""
import asyncio, os, functools
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for ph in ['shop', 'locker']:
            ctx = await b.new_context(viewport={'width': 430, 'height': 790}, device_scale_factor=1, has_touch=True, is_mobile=True)
            owned = "['flower','fangs']" if ph == 'locker' else "[]"
            await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{}, drops: 40, runs: 1, owned: " + owned + ", tut: { ph: '" + ph + "', price: { flower: 10 } } })); } catch (e) {}")
            pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
            async def wait(js, t=240000): await pg.wait_for_function(js, timeout=t, polling=100)
            await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await wait('typeof __T === "object"'); await pg.wait_for_timeout(2500)
            if ph == 'shop': await ev("document.getElementById('dabsBtn').click()")
            else: await ev("__T.openLook()")
            await pg.wait_for_timeout(2500)
            if ph == 'locker':  # (the face first: the fangs on, then Headgear is what it asks for)
                for i in range(4):
                    k = await ev("__T.tutTip && __T.tutTip.key")
                    if k in ('headg', 'wearf'): break
                    await ev("(() => { const t = __T.tutTip, at = t && t.at; const el = typeof at === 'string' ? document.getElementById(at) : typeof at === 'function' ? at() : at; if (el) el.click(); })()"); await pg.wait_for_timeout(1500)
            info = await ev("(() => { const d = document.getElementById('tutDim'), b = d.children[0]; return { tip: __T.tutTip && __T.tutTip.key, text: __T.tutTip && __T.tutTip.text, cls: d.className, paneBg: getComputedStyle(b).backgroundColor, paneFilter: getComputedStyle(b).backdropFilter || getComputedStyle(b).webkitBackdropFilter, ring: getComputedStyle(d, '::after').opacity }; })()")
            print(ph, info); await pg.screenshot(path=f'{WS}/ui/nodim_{ph}.png'); print('errors', errs[:3]); await ctx.close()
        await b.close()
asyncio.run(main())
