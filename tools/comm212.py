"""v212: the coverage commissions. A set saved today with the retired jobs (Half the canvas, Solo show at 40%) opens without breaking and
deals fresh jobs in their place; jobs count the whole number shown; the board with the new jobs, in portrait."""
import asyncio, json
from playwright.async_api import async_playwright
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, device_scale_factor=2)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{look:1}, drops: 40, runs: 12, tut: { ph: 'done' }, comm: { day: new Date().toDateString(), active: ['cov50', 'solo40', 'play3'], prog: { play3: 1 }, done: [] } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(2500)
        await pg.evaluate("document.getElementById('commBtn').click()"); await pg.wait_for_timeout(1200)
        print('stale set ->', await pg.evaluate("JSON.stringify(__T.store.comm.active)"), '| cards', await pg.evaluate("[...document.querySelectorAll('#commList .comm b:not(.cr)')].map(c => c.textContent)"))
        # the whole number shown decides
        r = await pg.evaluate("""(() => { const c = __T.store.comm, out = [];
          const t = (act, info) => { c.active = act.slice(); c.done = []; c.prog = {}; const f = __T.commProgress(info).map(k => k.id); out.push(JSON.stringify(info) + ' -> ' + JSON.stringify(f)); };
          t(['cov25', 'cov35', 'solo30'], { you: 24.6, mode: 'duel', win: 0 });
          t(['cov25', 'cov35', 'solo30'], { you: 24.4, mode: 'duel', win: 0 });
          t(['cov25', 'cov35', 'solo30'], { you: 29.5, mode: 'solo', win: 1 });
          t(['cov25', 'cov35', 'solo30'], { you: 34.4, mode: 'trio', win: 1 });
          t(['cov25', 'cov35', 'solo30'], { you: 34.5, mode: 'trio', win: 1 });
          return out; })()""")
        print('\n'.join(r))
        await pg.evaluate("(() => { const c = __T.store.comm; c.active = ['cov25', 'solo30', 'cov35']; c.done = []; c.prog = {}; __T.renderComms(); })()"); await pg.wait_for_timeout(600)
        await pg.screenshot(path=S + '/ws/ui/comm212.png'); print('errors', errs); await b.close()
asyncio.run(main())
