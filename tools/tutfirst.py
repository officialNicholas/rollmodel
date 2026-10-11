"""The onboarding's first word: a new player's lobby. Logs, against real time from the moment the lobby stands clear, when the tip
appears, how the dim panes' opacity and blur come in, and how the plate slides up; shoots the clean lobby, the fade and the plate.
usage: tutfirst.py [tag]"""
import asyncio, sys, functools, time
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'a'
Q = """(() => { const d = document.getElementById('tutDim'), b = d.children[0], t = document.getElementById('tut'), p = t.querySelector('.tplate'), cs = getComputedStyle(b), ps = getComputedStyle(p);
  return { tip: __T.tutTip && __T.tutTip.key, dim: d.className, pane: +(+cs.opacity).toFixed(2), blur: cs.backdropFilter || cs.webkitBackdropFilter, tut: t.className, hidden: t.hidden, plate: [+(+ps.opacity).toFixed(2), ps.translate], menu: __T.state + '/' + (typeof menuPage !== 'undefined' ? menuPage : '?') }; })()"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 800}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{}, drops: 0, runs: 0, tut: { ph: 'match' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000, polling=50)
        await pg.wait_for_function("__T.state === 'menu' && !document.getElementById('mHome').hidden && document.getElementById('boot').classList.contains('gone')", timeout=240000, polling=30)
        # (sampled inside the page every 40 ms: a round trip to the page is far too slow here to time a one second wait)
        await ev("""window.__fl = []; window.__f0 = performance.now(); window.__fi = setInterval(() => { const d = document.getElementById('tutDim'), b = d.children[0], t = document.getElementById('tut'), p = t.querySelector('.tplate'), cs = getComputedStyle(b), ps = getComputedStyle(p);
          window.__fl.push({ t: +((performance.now() - window.__f0) / 1000).toFixed(2), tip: __T.tutTip && __T.tutTip.key, pane: +(+cs.opacity).toFixed(2), blur: (cs.backdropFilter || cs.webkitBackdropFilter || 'none').replace('blur(', '').replace(')', ''), on: d.classList.contains('on'), plate: [+(+ps.opacity).toFixed(2), ps.translate] });
          if (window.__fl.length > 120) clearInterval(window.__fi); }, 40);""")
        t0 = time.time(); shots = {0.3: 'clean', 1.4: 'fade', 2.0: 'slide', 3.0: 'set'}; done = set()
        while time.time() - t0 < 5.2:
            t = time.time() - t0
            for k, nm in shots.items():
                if k not in done and t >= k: done.add(k); await pg.screenshot(path=f'{WS}/ui/tutfirst_{TAG}_{nm}.png')
            await pg.wait_for_timeout(60)
        lg = await ev("window.__fl"); last = None
        for r in lg:
            key = (r['tip'], r['on'], r['pane'] >= 0.99, r['plate'][0] >= 0.99, r['plate'][1])
            if key != last or r['t'] in (0.0,): print(r); last = key
        print('n', len(lg))
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
