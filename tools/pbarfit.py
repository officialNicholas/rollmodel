"""The power bar against the logo: the home screen at a phone's game area (the Claude app's viewer leaves it shorter than the screen), on
the onboarding's home (rail and friends hidden) and the full one; where the bar, the logo and its season tag land, and a shot of each."""
import asyncio, json, sys
from playwright.async_api import async_playwright
OUT = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/lab'
SIZES = [(393, 722), (375, 640), (430, 800)]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for w, h in SIZES:
            for tut in (True, False):
                ctx = await b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2, has_touch=True, is_mobile=True)
                prof = "{ orient:'port', name:'Glossy', seen:{look:1}, runs: 2, xp: 80, drops: 0, owned: ['flower', 'fangs'], bought: ['flower', 'fangs'], look: { mouth: 'fangs', side: 'flower' }, tut: { ph: '" + ('vote' if tut else 'done') + "' } }"
                await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify(" + prof + ")); } catch (e) {}")
                pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
                await pg.goto('http://localhost:8765/pc_h.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && !!__T.VP && !!__T.VP.slime', timeout=300000, polling=1000)
                await pg.wait_for_timeout(4000)
                r = await pg.evaluate("""(() => { const R = id => { const e = document.querySelector(id); if (!e) return null; const r = e.getBoundingClientRect(); return [Math.round(r.top), Math.round(r.bottom), Math.round(r.left), Math.round(r.right)]; };
                  return { logo: R('#logo'), season: R('#logo .season'), card: R('#logo .tcard'), pbar: R('#pbar'), stage: R('#stage') }; })()""")
                ov = r['pbar'] and r['logo'] and r['pbar'][0] < r['logo'][1]
                print(f'{w}x{h} tut={tut}:', json.dumps(r), 'OVERLAP' if ov else 'ok')
                await pg.screenshot(path=f'{OUT}/pb_{w}x{h}_{"t" if tut else "n"}.png'); await ctx.close()
        await b.close()
asyncio.run(main())
