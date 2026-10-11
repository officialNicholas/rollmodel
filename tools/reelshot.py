"""The vote reel on its own: the fight card's vote panel opened over the menu, shots while it spins and once it lands."""
import asyncio, sys
from playwright.async_api import async_playwright
OUT = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axoshots'
W, H, T = (390, 844, 'p') if (len(sys.argv) < 2 or sys.argv[1] == 'p') else (844, 390, 'l')
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': W, 'height': H}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'" + ('land' if W > H else 'port') + "', name:'Dusk', runs: 9, mode: 'trio', stage: 'crypt', tut: { ph: 'done' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && !!__T.VP && !!__T.VP.slime', timeout=300000, polling=1000); await pg.wait_for_timeout(1500)
        # (the 3D stops drawing so the shots are quick; the vote panel opens over a plain fight card)
        await pg.evaluate("(() => { __T.renderer.render = () => {}; document.getElementById('menu').hidden = true; const v = document.getElementById('vsx'); v.hidden = false; __T.openVote(__T.runId, () => { window.__voted = true; }); })()")
        for k, w in enumerate([450, 900]):
            await pg.wait_for_timeout(w); await pg.screenshot(path=f'{OUT}/reel_{T}_spin{k}.png', timeout=120000)
        await pg.wait_for_function("!!document.querySelector('.vcard.win') && document.getElementById('vtally').classList.contains('on')", timeout=30000, polling=50); await pg.wait_for_timeout(500)
        await pg.screenshot(path=f'{OUT}/reel_{T}_land.png', timeout=120000)
        print(T, await pg.evaluate("[document.getElementById('vvLbl').textContent, document.getElementById('vvWin').textContent, document.getElementById('vtally').textContent]"), 'errors', errs[:4])
        await b.close()
asyncio.run(main())
