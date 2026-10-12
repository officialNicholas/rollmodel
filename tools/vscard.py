"""The versus card before a match (the fighters' portraits): a phone upright and sideways, 1v1 and 3-way. usage: vscard.py <tag> [modes]"""
import asyncio, os, sys, functools
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'; TAG = sys.argv[1]; MODES = (sys.argv[2] if len(sys.argv) > 2 else 'duel').split(',')
SIZES = ([] if os.environ.get('ONLYLAND') else [(430, 790)]) + ([(844, 390)] if os.environ.get('LAND') or os.environ.get('ONLYLAND') else [])
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for (w, h) in SIZES:
            for md in MODES:
                ctx = await b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=1, has_touch=True, is_mobile=True)
                await ctx.add_init_script("window.__instant = false; window.__noVote = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'" + ('land' if w > h else 'port') + "', name:'Dusk', seen:{}, drops: 0, runs: 3, " + os.environ.get('LOOK', '') + " tut: { ph: 'done' } })); } catch (e) {}")
                pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
                async def wait(js, t=300000): await pg.wait_for_function(js, timeout=t, polling=50)
                await pg.goto('http://localhost:8765/' + os.environ.get('PAGE', 'pc_h.html'), timeout=240000); await wait('typeof __T === "object"'); await pg.wait_for_timeout(1500)
                await ev("(() => { const st = window.setTimeout; window.setTimeout = (f, d, ...x) => d === 2100 ? 0 : st(f, d, ...x); })()")  # (the card stays up: its own timer to move on is dropped)
                await ev(f"__T.mode = '{md}'; __T.applyMode(); __T.start()")
                await wait("!document.getElementById('vsx').hidden && document.querySelectorAll('#vsRow .vbox canvas').length > 0")
                await pg.wait_for_timeout(1500); await ev("document.getElementById('vsx').getAnimations({ subtree: true }).forEach(a => { try { if (isFinite(a.effect.getTiming().iterations)) a.finish(); } catch (e) {} })"); await pg.wait_for_timeout(300)
                fn = f'{WS}/ui/vs_{TAG}_{md}_{w}x{h}.png'; await pg.screenshot(path=fn); print('shot', fn)
                # the portraits themselves, as rendered
                urls = await ev("[...document.querySelectorAll('#vsRow .vbox canvas')].map(c => [c.width, c.height, c.toDataURL('image/png')])")
                import base64
                for i, (cw, ch, u) in enumerate(urls): open(f'{WS}/ui/vs_{TAG}_{md}_{w}x{h}_p{i}.png', 'wb').write(base64.b64decode(u.split(',')[1]))
                print('portraits', [(cw, ch) for cw, ch, _ in urls], 'errors', errs[:3]); await ctx.close()
        await b.close()
asyncio.run(main())
