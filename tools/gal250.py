"""v250 canvas vote page: swiping the paintings picks the one reaching the middle right away (no waiting for the scroll to settle), no
canvas is rebuilt while you browse (it's built when you leave; Play builds the pick anyway), the label follows the pick, no count under
the title, the title a little lower. Shots of the page before and after a swipe. usage: gal250.py"""
import asyncio, os, sys, functools, json
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'; PAGE = os.environ.get('PAGE', 'pc_h.html')
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__noVote = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{ jump: 1, hold: 1, steer: 1, item: 1, orb: 1 }, drops: 0, runs: 5, stage: 'island', mode: 'duel', tut: { ph: 'done', strokes: 1, comms: 1 } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
        await pg.goto('http://localhost:8765/' + PAGE, timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000, polling=100); await pg.wait_for_timeout(2500)
        await ev("__T.ev(`(() => { window.__fm = 0; const o = freshMap; freshMap = function () { window.__fm++; return o(); }; })()`)")
        await ev("__T.ev('openWorlds()')"); await pg.wait_for_timeout(1500); await pg.screenshot(path=f'{WS}/ui/gal250_open.png')
        print('header', await ev("(() => { const h = document.getElementById('worldTitle'), r = h.getBoundingClientRect(), a = getComputedStyle(h, '::after'); return [h.textContent, Math.round(r.top), Math.round(r.bottom), a.content, a.display, h.getAttribute('data-sub')]; })()"))
        print('start', await ev("[__T.stageSelV, document.getElementById('cvName').textContent]"))
        # a swipe: the gallery moved across a frame at a time, each step what one frame of a finger drag would do
        log = await ev("""new Promise(res => { const g = document.getElementById('stagePick'), out = [], t0 = performance.now(); let n = 0;
          const step = () => { g.scrollLeft += 26; n++; const sel = __T.stageSelV, mid = [...g.querySelectorAll('.world')].find(b => b.getAttribute('aria-pressed') === 'true');
            out.push([Math.round(performance.now() - t0), Math.round(g.scrollLeft), sel, mid && mid.dataset.s]); if (n < 40) requestAnimationFrame(step); else setTimeout(() => res(out), 400); };
          requestAnimationFrame(step); })""")
        prev = None
        for r in log:
            if r[2] != prev: print('  ', r); prev = r[2]
        print('picked', await ev("[__T.stageSelV, document.getElementById('cvName').textContent, window.__fm]"), '(freshMap calls while browsing)')
        await pg.wait_for_timeout(800); await pg.screenshot(path=f'{WS}/ui/gal250_swiped.png')
        await ev("document.getElementById('worldBack').click()"); await pg.wait_for_timeout(1500)
        print('after leaving', await ev("[__T.ev('menuPage'), window.__fm, __T.TH.id, __T.stageSelV]"))
        print('errors', errs[:4]); await b.close()
asyncio.run(main())
