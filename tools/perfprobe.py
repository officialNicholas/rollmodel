"""Gameplay smoothness: a real match on a phone-sized screen (iPhone user agent, so the game picks its phone settings) with the game's
own AI driving both blobs. Reports:
  - frame body JS time per frame (game logic + visuals + render calls), p50/p95/p99/max, and frames over 8/12/16 ms
  - its split by stage (step, visuals, renderFrame) and the busiest subsystems
  - a sampling CPU profile: top functions by self and total time
  - garbage collection pauses (from a trace) and the JS heap's sawtooth (allocation rate)
  - renderer.info: draw calls, triangles, shader programs, textures
usage: perfprobe.py <tag> [seconds]"""
import asyncio, json, os, sys, statistics
from playwright.async_api import async_playwright
TAG = sys.argv[1] if len(sys.argv) > 1 else 'base'; SECS = int(sys.argv[2]) if len(sys.argv) > 2 else 20; MODE = sys.argv[3] if len(sys.argv) > 3 else 'full'  # full | logic (rendering stubbed) | small (a tiny canvas, for render-side counts)
UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1'
WRAP = "window.__pf.wrapped"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'])
        ctx = await b.new_context(viewport={'width': 430, 'height': 754} if MODE != 'small' else {'width': 215, 'height': 377}, device_scale_factor=3 if MODE != 'small' else 1, has_touch=True, is_mobile=True, user_agent=UA)
        if os.environ.get('SLIME'): await ctx.add_init_script("window.AXO_PACK = 'no-axo.txt'; Object.defineProperty(window, 'AXO_PACK_BUF', { set() {}, get() { return undefined; } });")
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{look:1}, drops: 50, runs: 5, flings: 50, tut: { ph: 'done' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/' + os.environ.get('PAGE', 'pc_perf.html'), timeout=300000); await pg.wait_for_function('typeof __T === "object"', timeout=300000)
        print('wrapped', await pg.evaluate(WRAP))
        await pg.evaluate("__T.start()")  # (Play opens the events page now: a match is started straight off)
        await pg.wait_for_function("__T.state === 'play'", timeout=300000); await pg.wait_for_timeout(1500)
        await pg.evaluate("window.__perfAI()")  # the game's own AI plays you
        if MODE == 'logic': await pg.evaluate("(() => { __T.renderer.render = () => {}; })()")
        # per-frame render counts: draw calls, triangles and texture uploads summed over every pass of a frame
        await pg.evaluate("""(() => { const r = __T.renderer, I = r.info; I.autoReset = false; window.__rc = { calls: [], tris: [], up: [] }; let ups = 0;
          const gl = r.getContext(); for (const f of ['texImage2D', 'texSubImage2D', 'compressedTexSubImage2D', 'texImage3D', 'texSubImage3D']) { const o = gl[f]; if (o) gl[f] = function () { ups++; return o.apply(this, arguments); }; }
          const loop = () => { if (__pf.on) { __rc.calls.push(I.render.calls); __rc.tris.push(I.render.triangles); __rc.up.push(ups); } I.reset(); ups = 0; requestAnimationFrame(loop); }; requestAnimationFrame(loop); })()""")
        await pg.wait_for_timeout(2000)
        cdp = await ctx.new_cdp_session(pg)
        await cdp.send('Profiler.enable'); await cdp.send('Profiler.setSamplingInterval', {'interval': 200}); await cdp.send('Profiler.start')
        await pg.evaluate("(() => { __pf.on = true; __pf.raf = []; let lt = 0; const loop = t => { if (!__pf.on) return; if (lt) __pf.raf.push(t - lt); lt = t; requestAnimationFrame(loop); }; requestAnimationFrame(loop); })()")
        heap = []
        for i in range(SECS * 2):
            await pg.wait_for_timeout(500)
            m = await cdp.send('Performance.getMetrics') if i else (await cdp.send('Performance.enable')) or await cdp.send('Performance.getMetrics')
            heap.append(next((x['value'] for x in m['metrics'] if x['name'] == 'JSHeapUsedSize'), 0) / 1e6)
        await pg.evaluate("__pf.on = false")
        prof = (await cdp.send('Profiler.stop'))['profile']
        W = await pg.evaluate("({ fb: __pf.fb, st: __pf.st, raf: __pf.raf || [], state: __T.state, info: (() => { const i = __T.renderer.info; return { calls: i.render.calls, tris: i.render.triangles, lines: i.render.lines, points: i.render.points, programs: i.programs ? i.programs.length : 0, geo: i.memory.geometries, tex: i.memory.textures }; })(), pr: __T.renderer.getPixelRatio(), size: [innerWidth, innerHeight] })")
        fb = sorted(W['fb']); n = len(fb)
        q = lambda a, f: a[min(len(a) - 1, int(f * len(a)))] if a else 0
        print(f"== {TAG}: {n} frames in {SECS}s (state at end: {W['state']}), pixel ratio {W['pr']}, view {W['size']}")
        print('frame body JS ms: p50 %.2f  p95 %.2f  p99 %.2f  max %.2f  mean %.2f | over 8ms %d, over 12ms %d, over 16ms %d' % (q(fb, .5), q(fb, .95), q(fb, .99), fb[-1] if fb else 0, sum(fb) / max(1, n), sum(x > 8 for x in fb), sum(x > 12 for x in fb), sum(x > 16 for x in fb)))
        raf = sorted(W['raf']); print('rAF interval ms (swiftshader, not a phone): p50 %.1f p95 %.1f max %.1f' % (q(raf, .5), q(raf, .95), raf[-1] if raf else 0))
        print('by stage (mean / p95 / max ms per frame, over frames where it ran):')
        for k, v in sorted(W['st'].items(), key=lambda kv: -sum(kv[1])):
            v2 = sorted(v); print('   %-14s mean %6.3f  p95 %6.3f  max %7.2f  (calls in %d frames)' % (k, sum(v) / len(v), q(v2, .95), v2[-1], len(v)))
        nodes = {nd['id']: nd for nd in prof['nodes']}; parent = {}
        for nd in prof['nodes']:
            for c in nd.get('children', []): parent[c] = nd['id']
        self_t, tot_t = {}, {}
        key = lambda nd: f"{nd['callFrame']['functionName'] or '(anon)'}:{nd['callFrame']['lineNumber'] + 1}"
        for sid, dt in zip(prof['samples'], prof['timeDeltas']):
            nd = nodes[sid]; self_t[key(nd)] = self_t.get(key(nd), 0) + dt; seen = set(); cur = sid
            while cur is not None:
                k = key(nodes[cur])
                if k not in seen: seen.add(k); tot_t[k] = tot_t.get(k, 0) + dt
                cur = parent.get(cur)
        tot = sum(prof['timeDeltas']); idle = self_t.get('(idle):0', 0)
        print('CPU profile: %.1f s sampled, idle %.0f%%, program %.0f%%, GC %.0f%%' % (tot / 1e6, 100 * idle / tot, 100 * self_t.get('(program):0', 0) / tot, 100 * self_t.get('(garbage collector):0', 0) / tot))
        print('top self time:'); [print('   %5.1f%%  %s' % (100 * v / tot, k)) for k, v in sorted(self_t.items(), key=lambda x: -x[1])[:28] if k not in ('(idle):0',)]
        print('top total time:'); [print('   %5.1f%%  %s' % (100 * v / tot, k)) for k, v in sorted(tot_t.items(), key=lambda x: -x[1])[:30] if k not in ('(idle):0', '(root):0')]
        hs = heap; drops = [hs[i] - hs[i + 1] for i in range(len(hs) - 1) if hs[i + 1] < hs[i]]
        rise = [hs[i + 1] - hs[i] for i in range(len(hs) - 1) if hs[i + 1] > hs[i]]
        print('JS heap MB: min %.1f max %.1f; rises per 0.5 s mean %.2f MB (allocation rate ~%.1f MB/s); drops %d' % (min(hs), max(hs), sum(rise) / max(1, len(rise)), 2 * sum(rise) / max(1, len(hs) - 1), len(drops)))
        print('renderer.info (last frame):', W['info'])
        rc = await pg.evaluate("__rc")
        if rc['calls']:
            cs, ts, us = sorted(rc['calls']), sorted(rc['tris']), sorted(rc['up'])
            print('per frame: draw calls p50 %d p95 %d max %d | triangles p50 %d max %d | texture uploads p50 %d p95 %d max %d (frames %d)' % (q(cs, .5), q(cs, .95), cs[-1], q(ts, .5), ts[-1], q(us, .5), q(us, .95), us[-1], len(cs)))
        print('errors', errs)
        json.dump({'fb': W['fb'], 'st': W['st'], 'self': self_t, 'tot': tot_t, 'heap': heap, 'info': W['info']}, open(f'/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/perf_{TAG}.json', 'w'))
        await b.close()
asyncio.run(main())
