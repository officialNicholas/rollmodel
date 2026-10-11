"""The home screen as the Claude app shows it: a phone's game area with the notch's safe-area insets (emulated), on the onboarding's
home and the full one; where the bar, the logo's card and its season tag land."""
import asyncio, json, sys
from playwright.async_api import async_playwright
OUT = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/lab'
CASES = [(430, 790, 0, 0), (430, 790, 36, 34), (430, 790, 59, 34), (393, 722, 47, 34)]
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_h.html'; TAG = sys.argv[2] if len(sys.argv) > 2 else 'sa'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for w, h, it, ib in CASES:
            for ph in ('shop', 'done'):
                ctx = await b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2, has_touch=True, is_mobile=True)
                prof = "{ orient:'port', name:'Glossy', seen:{look:1}, runs: 2, xp: 80, drops: 0, owned: ['flower', 'fangs'], bought: ['flower', 'fangs'], look: { mouth: 'fangs', side: 'flower' }, tut: { ph: '" + ph + "' } }"
                await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify(" + prof + ")); } catch (e) {}")
                pg = await ctx.new_page(); cdp = await ctx.new_cdp_session(pg); await cdp.send('Emulation.setSafeAreaInsetsOverride', {'insets': {'top': it, 'bottom': ib, 'left': 0, 'right': 0}})
                errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
                await pg.goto('http://localhost:8765/' + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object" && !!__T.VP && !!__T.VP.slime', timeout=300000, polling=1000)
                await pg.wait_for_timeout(4500)
                await pg.evaluate("(() => { for (const id of ['tut', 'tutGo', 'tutDim']) { const e = document.getElementById(id); if (e) e.style.visibility = 'hidden'; } document.querySelectorAll('.tutdim,.coach,.tuthand').forEach(e => e.style.visibility = 'hidden'); })()")
                r = await pg.evaluate("""(() => { const R = s => { const e = document.querySelector(s); if (!e || e.offsetParent === null) return null; const r = e.getBoundingClientRect(); return [Math.round(r.top), Math.round(r.bottom)]; };
                  return { top: R('#lobbyTop'), card: R('#logo .tcard'), season: R('#logo .season'), pbar: R('#pbar'), play: R('#lobbyBot'), stage: R('#stage'), tutoring: document.querySelector('.menu').classList.contains('tutoring') }; })()""")
                lb = max((r['card'] or [0, 0])[1], (r['season'] or [0, 0])[1]); ov = r['pbar'] and r['pbar'][0] < lb
                print(f'{w}x{h} inset {it}/{ib} ph={ph}:', json.dumps(r), 'OVERLAP by %d' % (lb - r['pbar'][0]) if ov else 'ok', errs[:2])
                await pg.screenshot(path=f'{OUT}/{TAG}_{w}x{h}_{it}_{ph}.png'); await ctx.close()
        await b.close()
asyncio.run(main())
