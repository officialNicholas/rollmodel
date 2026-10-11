"""v216: the locker's dabs counter over the view and the big Shop button above the panel; portrait (with a phone's notch) and landscape;
the counter's number, the button opening the shop, and the onboarding pointing at it."""
import asyncio, json
from playwright.async_api import async_playwright
OUT = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/lab'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for w, h, it, ib, tag, ph in [(430, 790, 59, 34, 'p', 'done'), (844, 390, 0, 21, 'l', 'done'), (430, 790, 59, 34, 'pt', 'shop')]:
            ctx = await b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2, has_touch=True, is_mobile=True)
            await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'" + ('land' if w > h else 'port') + "', name:'Glossy', color: 'pink', seen:{look:1}, runs: 9, xp: 300, drops: 245, owned: ['flower', 'fangs'], bought: ['flower', 'fangs'], look: { mouth: 'fangs', side: 'flower' }, tut: { ph: '" + ph + "' } })); } catch (e) {}")
            pg = await ctx.new_page(); cdp = await ctx.new_cdp_session(pg); await cdp.send('Emulation.setSafeAreaInsetsOverride', {'insets': {'top': it, 'bottom': ib, 'left': 0, 'right': 0}})
            errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
            await pg.goto('http://localhost:8765/pc_h.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && !!__T.VP && !!__T.VP.slime', timeout=300000, polling=1000); await pg.wait_for_timeout(2000)
            await pg.evaluate("document.getElementById('lookBtn').click()"); await pg.wait_for_timeout(3500)
            r = await pg.evaluate("""(() => { const R = id => { const e = document.getElementById(id); if (!e || e.hidden) return null; const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)]; };
              return { dabs: R('lkDabs'), num: (document.getElementById('lkDabsN') || {}).textContent, shop: R('lkShop'), sheet: R('look'), lkBal: getComputedStyle(document.getElementById('lkBal')).display, coach: (document.querySelector('#tut') || {}).textContent }; })()""")
            print(tag, json.dumps(r)[:400])
            await pg.screenshot(path=f'{OUT}/lk_{tag}.png')
            if tag != 'pt':
                await pg.evaluate("document.getElementById('lkShop').click()"); await pg.wait_for_timeout(1200)
                print(tag, 'shop open', await pg.evaluate("[!document.getElementById('shop').hidden, document.getElementById('lkShop').hidden, document.getElementById('lkDabs').hidden]"))
            print(tag, 'errors', errs[:3]); await ctx.close()
        await b.close()
asyncio.run(main())
