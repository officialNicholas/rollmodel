"""Which stage-builder shapes a stage's props are made of, by triangles: every SG helper counted as the stage builds.
usage: sgcount.py page stage"""
import asyncio, sys, functools
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
PAGE, SID = sys.argv[1], sys.argv[2]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__noVote = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{ jump: 1, hold: 1, steer: 1, item: 1, orb: 1 }, drops: 0, runs: 5, stage: '" + SID + "', mode: 'duel', tut: { ph: 'done', strokes: 1, comms: 1 } })); } catch (e) {}")
        pg = await ctx.new_page(); ev = pg.evaluate
        await pg.goto('http://localhost:8765/' + PAGE, timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000, polling=100); await pg.wait_for_timeout(1000)
        await ev("""__T.ev(`(() => { window.__sgc = {}; const tri = g => (g.index ? g.index.count : g.attributes.position.count) / 3;
          for (const k of ['box', 'rbox', 'cyl', 'ball', 'torus', 'tube', 'cone', 'curve', 'sag']) { const f = SG[k]; SG[k] = (...a) => { const g = f(...a), c = __sgc[k] || (__sgc[k] = [0, 0]); c[0] += tri(g); c[1]++; return g; }; }
          const f2 = vcBag; })()`)""")
        await ev("__T.ev(`genWorld(12345, { themes: ['" + SID + "'] })`)")
        r = await ev("window.__sgc"); tot = sum(v[0] for v in r.values())
        for k, v in sorted(r.items(), key=lambda kv: -kv[1][0]): print(f'{k:6s} tris {int(v[0]):7d}  calls {v[1]:5d}  avg {v[0] / max(1, v[1]):.0f}')
        print('total', int(tot)); await b.close()
asyncio.run(main())
