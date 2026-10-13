"""Weather and orb phases, one after another in a real match with the game's AI driving everyone: clear, sun, sun with the orb, rain,
rain with the orb. Per phase: frame body JS (and its subsystems), the page's own work outside the canvas (style, layout, paint, raster,
compositing, from a trace), and, with RENDER=1, the canvas's draw calls and triangles.
usage: wxprobe.py <stage> <tag> [secs per phase]   env: RENDER=1 (draw the canvas, small), PAGE"""
import asyncio, json, os, sys, collections
from playwright.async_api import async_playwright
STAGE = sys.argv[1]; TAG = sys.argv[2]; SEC = float(sys.argv[3]) if len(sys.argv) > 3 else 6
PAGE = os.environ.get('PAGE', 'pc_perf.html'); RENDER = os.environ.get('RENDER') == '1'
OUT = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/perf248'
UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1'
PH = os.environ.get('PHASES', 'clear,sun,sun+orb,rain,rain+orb').split(',')
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=float(os.environ.get('DPR', 2)), has_touch=True, is_mobile=True, user_agent=UA)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', stage:'%s', seen:{look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1}, drops: 50, runs: 9, flings: 50, tut: { ph: 'done' } })); } catch (e) {}" % STAGE)
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/' + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object"', timeout=300000)
        await pg.evaluate("__T.start()"); await pg.wait_for_function("__T.state === 'play'", timeout=300000)
        await pg.evaluate("(() => { window.__perfAI(); __pf.on = true; })()")
        if not RENDER: await pg.evaluate("(() => { __T.renderer.render = () => {}; })()")
        else:
            await pg.evaluate("(() => { const r = __T.renderer, I = r.info; I.autoReset = false; window.__rc = []; let lt = 0; const loop = t => { __rc.push([I.render.calls, I.render.triangles, lt ? t - lt : 0]); lt = t; I.reset(); requestAnimationFrame(loop); }; requestAnimationFrame(loop); })()")
        # keep the phase going (the weather would move on), and the orb up (respawned whenever it's taken) while a phase wants it
        await pg.evaluate("""(() => { window.__ph = 'clear'; setInterval(() => { const ph = __ph; const T = __T;
            if (ph.startsWith('sun') && T.wxPhase === 'sun') T.wxLeft = 1000; if (ph.startsWith('rain') && T.wxPhase === 'rain') T.wxLeft = 1000; if (ph === 'clear') { T.wxLeft = 1000; }
            if (ph.endsWith('orb') && !T.ev('orb.on')) T.ev('orbSpawn()'); if (!ph.endsWith('orb') && T.ev('orb.on')) T.ev('orbReset()');
            if (ph.includes('giant')) { T.P.giantT = 8; } else if (T.P.giantT > 0.5) T.P.giantT = 0.3;
            T.matchLeft = 80; }, 250); })()""")
        await pg.evaluate("__T.ev(\"setWx('clear', 1000)\")")
        cdp = await ctx.new_cdp_session(pg); await cdp.send('Performance.enable')
        events = []; done = asyncio.Event()
        cdp.on('Tracing.dataCollected', lambda e: events.extend(e['value'])); cdp.on('Tracing.tracingComplete', lambda e: done.set())
        await cdp.send('Tracing.start', {'categories': 'devtools.timeline,disabled-by-default-devtools.timeline,cc,disabled-by-default-cc.debug', 'transferMode': 'ReportEvents'})
        stats = {}
        for ph in PH:
            if ph == 'sun': await pg.evaluate("__T.ev(\"setWx('warn', 0.02)\")")
            if ph == 'rain': await pg.evaluate("__T.ev(\"setWx('dusk', 0.02); orbReset();\")")
            if ph.startswith('giant'): await pg.evaluate("(() => { window.__orbKind = 'giant'; if (!__T.ev('orb.on')) __T.ev('orbSpawn()'); __T.ev('takeOrb(P)'); })()")
            if ph == 'clear2': await pg.evaluate("__T.ev(\"setWx('clear', 1000)\")")
            await pg.evaluate(f"window.__ph = '{ph}'")
            await pg.wait_for_timeout(1500)  # (settle into it)
            await pg.evaluate(f"(() => {{ console.timeStamp('PH:{ph}'); __pf.fb.length = 0; __pf.st = {{}}; __pf.slow = []; if (window.__rc) __rc.length = 0; }})()")
            m0 = {x['name']: x['value'] for x in (await cdp.send('Performance.getMetrics'))['metrics']}
            await pg.wait_for_timeout(int(SEC * 1000))
            m1 = {x['name']: x['value'] for x in (await cdp.send('Performance.getMetrics'))['metrics']}
            await pg.evaluate(f"console.timeStamp('END:{ph}')")
            W = await pg.evaluate("({ fb: __pf.fb.slice(), st: __pf.st, wx: __T.wxPhase, orb: __T.ev('orb.on'), giant: __T.ACTIVE.map(D => +D.giantT.toFixed(1)), exposed: __T.P.exposed, vig: document.getElementById('vig').className, rc: window.__rc ? __rc.slice() : [] })")
            fb = sorted(W['fb']); n = len(fb); q = lambda f: fb[min(n - 1, int(f * n))] if n else 0
            d = {k: m1.get(k, 0) - m0.get(k, 0) for k in ('TaskDuration', 'ScriptDuration', 'LayoutDuration', 'RecalcStyleDuration', 'LayoutCount', 'RecalcStyleCount')}
            top = sorted(((k, sum(v) / max(1, n)) for k, v in W['st'].items()), key=lambda kv: -kv[1])[:8]
            rc = W['rc']; calls = sorted(x[0] for x in rc) if rc else []; tris = sorted(x[1] for x in rc) if rc else []; dts = sorted(x[2] for x in rc[1:]) if len(rc) > 1 else [0]
            stats[ph] = dict(n=n, p50=q(.5), p95=q(.95), p99=q(.99), mx=fb[-1] if fb else 0, mean=sum(fb) / max(1, n), task_ms_per_frame=1000 * d['TaskDuration'] / max(1, n), script=1000 * d['ScriptDuration'] / max(1, n), layout=1000 * d['LayoutDuration'] / max(1, n), style=1000 * d['RecalcStyleDuration'] / max(1, n), layouts=d['LayoutCount'] / max(1, n), styles=d['RecalcStyleCount'] / max(1, n), wx=W['wx'], orb=W['orb'], giant=W['giant'], vig=W['vig'], top=top, calls=calls[len(calls) // 2] if calls else 0, tris=tris[len(tris) // 2] if tris else 0, raf=dts[len(dts) // 2], rafn=len(dts))
        await cdp.send('Tracing.end'); await asyncio.wait_for(done.wait(), 120)
        # trace: per phase, page work by event name (main thread and the compositor/raster threads)
        marks = sorted([(e['ts'], e['args']['data']['message']) for e in events if e.get('name') == 'TimeStamp' and 'data' in e.get('args', {}) and 'message' in e['args']['data']])
        spans = {}; cur = None
        for ts, msg in marks:
            if msg.startswith('PH:'): cur = (msg[3:], ts)
            elif msg.startswith('END:') and cur: spans[cur[0]] = (cur[1], ts); cur = None
        WANT = ('Paint', 'RasterTask', 'UpdateLayerTree', 'Layout', 'UpdateLayoutTree', 'CompositeLayers', 'PrePaint', 'Layerize', 'ImageDecodeTask', 'Decode Image', 'GPUTask', 'PaintImage', 'ParseHTML', 'HitTest', 'Commit', 'Draw Frame', 'DrawFrame', 'BeginMainThreadFrame')
        for ph, (t0, t1) in spans.items():
            acc = collections.Counter(); cnt = collections.Counter()
            for e in events:
                if e.get('ph') != 'X' or not (t0 <= e.get('ts', 0) <= t1): continue
                nm = e.get('name'); 
                if nm in WANT: acc[nm] += e.get('dur', 0) / 1000; cnt[nm] += 1
            stats[ph]['trace'] = {k: (round(v, 1), cnt[k]) for k, v in acc.most_common(8)}
        print(f'== {TAG} ({STAGE}) render={RENDER}')
        for ph in PH:
            s = stats[ph]
            print('%-9s wx %-5s orb %-5s giant %s vig "%s" | fb p50 %.1f p95 %.1f p99 %.1f max %.1f mean %.2f | task/frame %.1f ms (script %.1f, style %.2f x%.1f, layout %.2f x%.2f)%s' % (ph, s['wx'], s['orb'], s['giant'], s['vig'], s['p50'], s['p95'], s['p99'], s['mx'], s['mean'], s['task_ms_per_frame'], s['script'], s['style'], s['styles'], s['layout'], s['layouts'], (' | calls %d tris %dk rAF p50 %.0f ms (%d frames)' % (s['calls'], s['tris'] // 1000, s['raf'], s['rafn'])) if RENDER else ''))
            print('          top JS:', ', '.join('%s %.2f' % kv for kv in s['top']))
            print('          trace ms (count):', s.get('trace'))
        print('errors', errs[:3])
        json.dump(stats, open(f'{OUT}/wx_{TAG}.json', 'w'))
        await b.close()
asyncio.run(main())
