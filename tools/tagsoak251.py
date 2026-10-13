"""v251 name tags, live: a whole match with the AI playing (3D drawing off so it runs at speed), the tags sampled through it: how often
each shows, its opacity against distance, that it's never up while its rival hides, is out or the kill cam runs, and no errors.
usage: tagsoak251.py [duel|trio] [seconds]"""
import asyncio, os, sys, functools, json
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
MODE = sys.argv[1] if len(sys.argv) > 1 else 'duel'; SECS = float(sys.argv[2]) if len(sys.argv) > 2 else 60
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; window.__noReveal = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{ jump: 1, hold: 1, steer: 1, item: 1, orb: 1, roll: 1, pound: 1, missile: 1, burst: 1 }, drops: 0, runs: 5, xp: 400, tut: { ph: 'done', strokes: 1, comms: 1, m3: 2 } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('console', lambda m: m.type == 'error' and errs.append('console: ' + m.text[:200])); ev = pg.evaluate
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=400000); await pg.wait_for_timeout(800)
        await ev("(() => { const r = __T.renderer; r.render = () => {}; })(); 0")
        await ev(f"__T.mode = '{MODE}'; __T.applyMode(); __T.start()"); await pg.wait_for_function("__T.state === 'play'", timeout=400000)
        # you drive about: steering that wanders, so the rivals come and go
        await ev("""(() => { let a = 0; window.__drv = setInterval(() => { if (__T.state !== 'play') return; a += 0.25; __T.steerIn = Math.sin(a) * 0.8; }, 100); })()""")
        stats = {}; bad = []; t0 = await ev("__T.runT"); n = 0
        while True:
            r = await ev("""(() => { const out = []; for (const [D, t] of __T.ev('ntags')) out.push([__T.ev('nameOf')(D), +t.k.toFixed(2), +t.d.toFixed(1), D.st, t.see, !t.el.hidden, !!__T.kcam, __T.ev('rankOf')(D), __T.ev('foes(P)').includes(D)]); return [__T.state, __T.runT, out]; })()""")
            if r[0] != 'play': break
            for nm, k, d, st, see, shown, kc, rk, foe in r[2]:
                s = stats.setdefault(nm, { 'n': 0, 'shown': 0, 'kmax': 0, 'dmin': 99, 'dshown_max': 0, 'rank': rk, 'foe': foe, 'states': {} })
                s['n'] += 1; s['states'][st] = s['states'].get(st, 0) + 1
                if shown: s['shown'] += 1; s['kmax'] = max(s['kmax'], k); s['dshown_max'] = max(s['dshown_max'], d)
                if foe: s['dmin'] = min(s['dmin'], d)
                if shown and k > 0.2 and (st != 'play' and k > 0.6 or kc and k > 0.6 or see == 0 and k > 0.6): bad.append([round(r[1], 1), nm, k, d, st, see, kc])
                if shown and d > 25.5: bad.append(['far', round(r[1], 1), nm, k, d])
            n += 1
            if r[1] - t0 > SECS: break
            await pg.wait_for_timeout(120)
        print(MODE, 'samples', n, 'game secs', round(r[1] - t0, 1))
        for nm, s in stats.items(): print(' ', nm, s)
        print('suspicious', bad[:12]); print('errors', errs[:6]); await b.close()
asyncio.run(main())
