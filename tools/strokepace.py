"""The swim's pace in a match: logs, each frame, the stroke phase u, the swim weight, the pace factor the game moves the blob by, and the
blob's real ground speed against its set speed; prints the profile through a stroke and the ratio of distance covered to D.spd over
whole strokes (should be ~1). usage: strokepace.py [page]"""
import asyncio, sys, functools
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_h.html'
LOG = """(() => { window.__sp = []; let px = null, pz = null, pt = null; const f = () => { const P = __T.P, A = __T.VP.slime.ax.A, L = A.loco, t = __T.runT;
  if (__T.state === 'play' && L && L.sl && pt !== null && t > pt) { const v = Math.hypot(P.x - px, P.z - pz) / (t - pt); __sp.push([+t.toFixed(3), +L.sl.u.toFixed(3), +(L.slK || 0).toFixed(2), +(P.strokeK || 1).toFixed(3), +v.toFixed(3), +P.spd.toFixed(3), P.air ? 1 : 0, +(t - pt).toFixed(4)]); }
  px = P.x; pz = P.z; pt = t; if (__sp.length < 6000) requestAnimationFrame(f); }; requestAnimationFrame(f); })()"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 360, 'height': 640}, device_scale_factor=1, has_touch=True)
        await ctx.add_init_script("window.__noVote = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{}, drops: 0, runs: 5, mode: 'solo', tut: { ph: 'done' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
        await pg.goto('http://localhost:8765/' + PAGE, timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000, polling=100); await pg.wait_for_timeout(1500)
        await ev("(() => { const r = __T.renderer; r.render = () => {}; })(); 0")
        await ev("__T.mode = 'solo'; __T.applyMode(); __T.start()"); await pg.wait_for_function("__T.state === 'play'", timeout=400000, polling=100)
        await ev(LOG); await pg.wait_for_function("window.__sp.length > 1500 || __T.state !== 'play'", timeout=600000, polling=500)
        sp = await ev("window.__sp")
        sw = [r for r in sp if r[2] > 0.95 and not r[6]]
        print('frames', len(sp), 'fully swimming', len(sw))
        # the profile by phase bucket: mean pace factor and mean real speed / set speed
        bk = {}
        for r in sw: k = int(r[1] * 10); bk.setdefault(k, []).append((r[3], r[4] / r[5] if r[5] > 0 else 0))
        print('u bucket: factor | real speed / set speed')
        for k in sorted(bk): v = bk[k]; print('  %.1f-%.1f  %.2f | %.2f  (n %d)' % (k / 10, k / 10 + 0.1, sum(a for a, _ in v) / len(v), sum(b for _, b in v) / len(v), len(v)))
        # whole strokes: from one wrap of u to the next, distance covered vs set speed x time
        segs = []; cur = []
        for a, b2 in zip(sw, sw[1:]):
            cur.append(b2)
            if b2[1] < a[1] - 0.5: segs.append(cur); cur = []
        rat = []
        for s2 in segs[1:]:
            if len(s2) < 20: continue
            d = sum(r[4] * r[7] for r in s2); e = sum(r[5] * r[7] for r in s2); rat.append(d / e if e else 0)
        print('whole strokes:', len(rat), 'distance / (set speed x time):', [round(x, 3) for x in rat])
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
