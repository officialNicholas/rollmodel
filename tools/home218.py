"""v218: the home screen (onboarding and full, portrait with a notch, a narrower phone, landscape): Abilities always there, greyed when
locked; Friends and the spots beside you there in the onboarding too; Friends low in portrait, clear of the logo and the power bar.
Then Choose Event's order with Matchmaking."""
import asyncio, json
from playwright.async_api import async_playwright
OUT = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/lab'
CASES = [(430, 790, 59, 34, 'shop', 80), (430, 790, 59, 34, 'done', 300), (375, 667, 20, 0, 'done', 80), (375, 560, 20, 0, 'shop', 80), (844, 390, 0, 21, 'done', 80)]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for w, h, it, ib, ph, xp in CASES:
            ctx = await b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2, has_touch=True, is_mobile=True)
            await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'" + ('land' if w > h else 'port') + "', name:'Glossy', seen:{look:1}, runs: 3, xp: " + str(xp) + ", drops: 0, owned: ['flower', 'fangs'], bought: ['flower', 'fangs'], look: { mouth: 'fangs', side: 'flower' }, tut: { ph: '" + ph + "' } })); } catch (e) {}")
            pg = await ctx.new_page(); cdp = await ctx.new_cdp_session(pg); await cdp.send('Emulation.setSafeAreaInsetsOverride', {'insets': {'top': it, 'bottom': ib, 'left': 0, 'right': 0}})
            errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
            await pg.goto('http://localhost:8765/pc_h.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && !!__T.VP && !!__T.VP.slime', timeout=300000, polling=1000); await pg.wait_for_timeout(4500)
            await pg.evaluate("document.querySelectorAll('#tut,#tutGo,.tuthand,.tutdim,.coach').forEach(e => e.style.visibility = 'hidden')")
            r = await pg.evaluate("""(() => { const R = s => { const e = document.querySelector(s); if (!e || e.offsetParent === null || e.hidden) return null; const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)]; };
              return { abil: R('#abilBtn'), locked: document.getElementById('abilBtn').classList.contains('locked'), friends: R('#friendsBtn'), slotL: R('#slotL'), slotR: R('#slotR'), pbar: R('#pbar'), season: R('#logo .season'), tutoring: document.querySelector('.menu').classList.contains('tutoring') }; })()""")
            ov = lambda a, c: a and c and a[0] < c[2] and c[0] < a[2] and a[1] < c[3] and c[1] < a[3]
            print(f'{w}x{h} {ph}:', json.dumps(r), 'friends/bar overlap' if ov(r['friends'], r['pbar']) else '', 'friends/logo overlap' if r['friends'] and r['season'] and r['friends'][1] - 30 < r['season'][3] else '', errs[:2])
            await pg.screenshot(path=f'{OUT}/h218_{w}x{h}_{ph}.png')
            if (w, ph) == (430, 'done'):
                await pg.evaluate("document.getElementById('homePlay').click()"); await pg.wait_for_timeout(1500)
                print('events order:', await pg.evaluate("[...document.querySelectorAll('#evGrid .evcard')].map(c => c.dataset.ev + (c.classList.contains('soon') ? '(soon)' : ''))"))
                await pg.screenshot(path=f'{OUT}/h218_events.png')
                await pg.evaluate("document.getElementById('evMatch').click()"); await pg.wait_for_timeout(300); print('match toast:', await pg.evaluate("(document.querySelector('#evGrid .evtoast') || {}).textContent"))
            await ctx.close()
        await b.close()
asyncio.run(main())
