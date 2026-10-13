"""Per-stage smoothness probe: a real match on a phone-shaped page (iPhone UA) on one stage, the game's AI driving you.
Per frame: frame body ms, the subsystem split, draw calls, triangles, texture uploads, shader programs, quality level.
Prints the distribution, the spikes (frames over 2x the median and over 25 ms) with what happened in them, programs compiled
during play, quality steps, and a CPU profile summary.
usage: stageperf.py <stage> <tag> [seconds] [page]"""
import asyncio, json, os, sys
from playwright.async_api import async_playwright
STAGE = sys.argv[1]; TAG = sys.argv[2]; SECS = int(sys.argv[3]) if len(sys.argv) > 3 else 20; PAGE = sys.argv[4] if len(sys.argv) > 4 else 'pc_perf.html'
OUT = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/perf248'
UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1'
W, H, DPR = int(os.environ.get('VW', 390)), int(os.environ.get('VH', 844)), float(os.environ.get('DPR', 1))
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'])
        ctx = await b.new_context(viewport={'width': W, 'height': H}, device_scale_factor=DPR, has_touch=True, is_mobile=True, user_agent=UA)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', stage:'%s', seen:{look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1}, drops: 50, runs: 9, flings: 50, tut: { ph: 'done' } })); } catch (e) {}" % STAGE)
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/' + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object"', timeout=300000)
        await pg.wait_for_timeout(1500)
        print('stage sel', await pg.evaluate("__T.stageSel"), 'theme', await pg.evaluate("__T.TH && __T.TH.id"))
        # per-frame recorder, hooked before the match starts so the intro and the first seconds are in it
        await pg.evaluate("""(() => { const r = __T.renderer, I = r.info; I.autoReset = false; let ups = 0, upB = 0; window.__rec = []; window.__recOn = false;
          const gl = r.getContext(); for (const f of ['texImage2D', 'texSubImage2D', 'compressedTexImage2D', 'texImage3D', 'texSubImage3D']) { const o = gl[f]; if (o) gl[f] = function () { ups++; return o.apply(this, arguments); }; }
          let bufs = 0; for (const f of ['bufferData', 'bufferSubData']) { const o = gl[f]; gl[f] = function (t, d) { bufs++; try { upB += (d && d.byteLength) || 0; } catch (e) {} return o.apply(this, arguments); }; }
          let comp = 0; { const o = gl.compileShader; gl.compileShader = function () { comp++; return o.apply(this, arguments); }; }
          let lt = 0; const loop = t => { if (__recOn) { const q = window.__q ? __q() : {}; __rec.push({ t: +(t / 1000).toFixed(3), dt: lt ? +(t - lt).toFixed(2) : 0, fb: __pf.fb.length ? +__pf.fb[__pf.fb.length - 1].toFixed(2) : 0, st: __T.state, calls: I.render.calls, tris: I.render.triangles, ups, bufs, upB, comp, prog: I.programs ? I.programs.length : 0, q: q.lvl, pr: q.pr, geo: I.memory.geometries, tex: I.memory.textures }); }
            lt = t; I.reset(); ups = 0; bufs = 0; upB = 0; comp = 0; requestAnimationFrame(loop); }; requestAnimationFrame(loop); })()""")
        # per-frame subsystem split: keep the last frame's split with its index
        await pg.evaluate("(() => { __pf.on = true; })()")
        await pg.evaluate("window.__recOn = true")
        if os.environ.get('SEED'): await pg.evaluate(f"__T.ev('genWorld({int(os.environ['SEED'])}, {{ themes: stageThemes() }}); mapUsed = false; warmRender();')")
        await pg.evaluate("__T.start()")
        await pg.wait_for_function("__T.state === 'play'", timeout=300000)
        print('theme in play', await pg.evaluate("__T.TH && __T.TH.id"), 'ARENA', await pg.evaluate("__T.ARENA"))
        await pg.evaluate("window.__perfAI()")
        if os.environ.get('LOGIC'): await pg.evaluate("(() => { __T.renderer.render = () => {}; })()")
        cdp = await ctx.new_cdp_session(pg)
        await cdp.send('Profiler.enable'); await cdp.send('Profiler.setSamplingInterval', {'interval': 250}); await cdp.send('Profiler.start')
        await pg.wait_for_timeout(SECS * 1000)
        prof = (await cdp.send('Profiler.stop'))['profile']
        print('shadow cache:', await pg.evaluate("JSON.stringify(__T.shadowCache)"))
        await pg.evaluate("window.__recOn = false; __pf.on = false")
        R = await pg.evaluate("__rec"); ST = await pg.evaluate("__pf.st"); FB = await pg.evaluate("__pf.fb")
        json.dump({'rec': R, 'st': ST, 'fb': FB}, open(f'{OUT}/{TAG}.json', 'w'))
        play = [r for r in R if r['st'] == 'play']; pre = [r for r in R if r['st'] != 'play']
        q = lambda a, f: a[min(len(a) - 1, int(f * len(a)))] if a else 0
        def dist(name, a):
            a = sorted(a); return '%s p50 %.1f p90 %.1f p99 %.1f max %.1f' % (name, q(a, .5), q(a, .9), q(a, .99), a[-1] if a else 0)
        print(f'== {TAG} ({STAGE}) {len(R)} frames recorded, {len(pre)} before play, {len(play)} in play')
        print(dist('play dt', [r['dt'] for r in play[1:]]), '|', dist('fb', [r['fb'] for r in play]))
        print(dist('calls', [r['calls'] for r in play]), '|', dist('tris k', [r['tris'] / 1000 for r in play]))
        print('programs: start of play %d, end %d; compiles during play %d (frames with compiles: %s)' % (play[0]['prog'] if play else -1, play[-1]['prog'] if play else -1, sum(r['comp'] for r in play), [round(r['t'] - play[0]['t'], 2) for r in play if r['comp']][:20]))
        print('texture uploads in play: %d over %d frames; buffer uploads mean %.0f/frame, MB/frame p50 %.2f max %.2f' % (sum(r['ups'] for r in play), sum(1 for r in play if r['ups']), sum(r['bufs'] for r in play) / max(1, len(play)), q(sorted(r['upB'] / 1e6 for r in play), .5), max([r['upB'] / 1e6 for r in play] or [0])))
        qs = []; [qs.append((round(r['t'] - play[0]['t'], 2), r['q'], r['pr'])) for i, r in enumerate(play) if i == 0 or r['q'] != play[i - 1]['q']]
        print('quality steps (t, level, pr):', qs[:20])
        med = q(sorted(r['dt'] for r in play[1:]), .5)
        sp = [r for r in play[1:] if r['dt'] > max(2 * med, 25)]
        print('spikes (dt > max(2x median %.1f, 25)): %d' % (med, len(sp)))
        t0 = play[0]['t'] if play else 0
        for r in sp[:25]: print('   t %6.2f dt %6.1f fb %6.1f calls %4d tris %5dk ups %d bufs %d MB %.2f comp %d q %s' % (r['t'] - t0, r['dt'], r['fb'], r['calls'], r['tris'] // 1000, r['ups'], r['bufs'], r['upB'] / 1e6, r['comp'], r['q']))
        # spikes before play (intro, build)
        sp0 = [r for r in pre[1:] if r['dt'] > 60]
        print('pre-play long frames (>60 ms):', [(r['st'], round(r['dt']), r['comp'], r['ups']) for r in sp0][:15])
        SL = await pg.evaluate("__pf.slow || []")
        print('slow frames (fb > 6 ms):', len(SL))
        for d, c in sorted(SL, key=lambda x: -x[0])[:14]: print('   %5.1f  %s' % (d, ', '.join('%s %.1f' % kv for kv in sorted(c.items(), key=lambda kv: -kv[1])[:7])))
        print('by subsystem (mean / p99 / max ms):')
        for k, v in sorted(ST.items(), key=lambda kv: -sum(kv[1]))[:16]:
            v2 = sorted(v); print('   %-14s mean %6.3f  p99 %6.2f  max %7.2f  n %d' % (k, sum(v) / len(v), q(v2, .99), v2[-1], len(v)))
        nodes = {nd['id']: nd for nd in prof['nodes']}; self_t = {}
        key = lambda nd: f"{nd['callFrame']['functionName'] or '(anon)'}:{nd['callFrame']['lineNumber'] + 1}"
        for sid, dt in zip(prof['samples'], prof['timeDeltas']): k = key(nodes[sid]); self_t[k] = self_t.get(k, 0) + dt
        tot = sum(prof['timeDeltas'])
        print('CPU: idle %.0f%% program %.0f%% GC %.1f%%' % (100 * self_t.get('(idle):0', 0) / tot, 100 * self_t.get('(program):0', 0) / tot, 100 * self_t.get('(garbage collector):0', 0) / tot))
        print('top self:', ', '.join('%s %.1f%%' % (k, 100 * v / tot) for k, v in sorted(self_t.items(), key=lambda x: -x[1])[:14] if k != '(idle):0'))
        print('errors', errs[:5])
        await b.close()
asyncio.run(main())
