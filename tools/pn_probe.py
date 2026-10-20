"""pn: game smoothness probe on a phone-like setup. Builds nothing: point it at a --test build (q260.py ... --test).
Chromium at 390x844, device scale 3, iPhone user agent, touch, CPU throttled (default 4x) through the DevTools protocol.
Graphics run on SwiftShader (software), which would make every frame wait on it, so the drawing buffer is scaled down
(GPU, default 0.25 of the game's own pixel ratio) and the game's quality tuner is held where it starts (window.__fixedPR).
NODRAW (default 1) goes further: WebGL's draw calls do nothing, so frames come as fast as the page's own work allows
(everything up to the draw call still runs: the game, three.js, uniforms, buffers, the post passes; the screen is black).
The numbers to compare are the main thread's own work per frame (frame body, script, style and layout), the hitches in
it, and the GPU's load in draw calls, triangles and the pixels the game asks for (px, at full scale).

Scenes: launch (boot to menu), lobby, locker, a versus match on each stage, Showdown with four, Time trial. The game's AI
drives you in matches. Prints one line per scene and writes JSON.

usage: pn_probe.py <page.html> <tag> [scenes]   env: SECS (per scene, 10), CPU (throttle, 4), DPR (3), OUT (json dir),
       PORT (8765), STAGES (comma list), PROF=1 (a CPU profile per scene), TEXLOG=1 (what a match uploads to textures),
       SPLIT=1 (frame time by game function), FLAGS (extra browser flags)
scenes: launch,lobby,locker,stages,showdown,trial (default all), repeat (REPEAT matches on one stage, memory after each)"""
import asyncio, json, os, sys, http.server, threading, functools, time
from playwright.async_api import async_playwright

PAGE = os.path.abspath(sys.argv[1]); TAG = sys.argv[2]
SCENES = (sys.argv[3] if len(sys.argv) > 3 else 'launch,lobby,locker,stages,showdown,trial').split(',')
SECS = float(os.environ.get('SECS', 10)); GPU = float(os.environ.get('GPU', 0.25)); CPU = float(os.environ.get('CPU', 4)); DPR = float(os.environ.get('DPR', 3))
OUT = os.environ.get('OUT', os.path.dirname(PAGE)); PORT = int(os.environ.get('PORT', 8765))
PROF = os.environ.get('PROF') == '1'; NODRAW = os.environ.get('NODRAW', '1') == '1'
STAGES = os.environ.get('STAGES', 'island,blank,sewer,raft,crypt,cathedral,manor').split(',')
GAME = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'game') # (the page loads three.js and the art from here)
UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1'

# measuring hooks, put inside the game's own scope (its functions are local there). The probe page is written into game/
# (it loads three.js and the art from there) and deleted at the end.
HOOK = r"""
window.__pf = { fb: [], on: false };
{ const fb0 = frameBody; frameBody = function (t) { if (!__pf.on) return fb0.apply(this, arguments); const t0 = performance.now(); try { return fb0.apply(this, arguments); } finally { __pf.fb.push(performance.now() - t0); if (window.__sp && __sp.on) { for (const k in __sp.cur) (__sp.st[k] || (__sp.st[k] = [])).push(__sp.cur[k]); __sp.cur = {}; } } }; }
if (window.__pnGpu !== 1) { const sp = renderer.setPixelRatio.bind(renderer); renderer.setPixelRatio = v => sp(v * window.__pnGpu); renderer.setPixelRatio(curPR); resize(); }
window.__pn = { aiMe: () => { P.cpu = true; aiReset(P); }, info: () => ({ state, mode, stageSel, qLvl, curPR, menuPage, building, irisBusy, w: renderer.domElement.width, h: renderer.domElement.height }), renderer };
"""
# SPLIT=1: time spent in these game functions per frame (each wrapped where it lives; nested time counts in both)
SPLIT = ['visuals', 'renderFrame', 'aiStep', 'aiThink', 'dijkstra', 'stepBlob', 'moveBlob', 'paintBlob', 'updateParts', 'updateTrail', 'flushTrail', 'updateFx', 'lodPass', 'blobVisual', 'slimeVisual', 'covTick', 'teamCov', 'stepRivals', 'detectThreat', 'placeFace', 'cpuLook', 'idleStep', 'updateWeather', 'itemTick', 'updateShots', 'checkHold', 'stampTrail', 'addSplat', 'mirrorPass', 'updatePuffs']
SPLIT_JS = "window.__sp = { on: false, cur: {}, st: {} };\n" + "".join("try { if (typeof %s === 'function') { const o = %s; %s = function () { if (!__sp.on) return o.apply(this, arguments); const t0 = performance.now(); try { return o.apply(this, arguments); } finally { __sp.cur['%s'] = (__sp.cur['%s'] || 0) + performance.now() - t0; } }; } } catch (e) {}\n" % (n, n, n, n, n) for n in SPLIT)
AIIN = "let input = D === P ? (keyL || keyR ? (keyR ? 1 : 0) - (keyL ? 1 : 0) : steerIn) : D.steer;"

def probe_page():
    s = open(PAGE).read()
    a = '\nwindow.__T = { ev: s => eval(s) };'; assert s.count(a) == 1, 'not a --test build'
    s = s.replace(a, a + HOOK + (SPLIT_JS if os.environ.get('SPLIT') else ''))
    assert s.count(AIIN) == 1; s = s.replace(AIIN, AIIN.replace('D === P ?', 'D === P && !P.cpu ?'))
    out = os.path.join(GAME, '_pnprobe_' + os.path.basename(PAGE)); open(out, 'w').write(s); return os.path.basename(out)

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
http.server.ThreadingHTTPServer.allow_reuse_address = True
def serve(dirpath):
    h = functools.partial(Quiet, directory=dirpath)
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), h); threading.Thread(target=srv.serve_forever, daemon=True).start(); return srv

SAVE = "localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient: 'port', name: 'Dusk', introDone: 1, seen: { look: 1, steer: 1, jump: 1, hold: 1, roll: 1, missile: 1, pound: 1, burst: 1, orb: 1 }, drops: 50, runs: 30, flings: 50, xp: 99999, tut: { ph: 'done' }, gfx: 'hi' }))"

REC = r"""(() => { const r = __pn.renderer, I = r.info; I.autoReset = false; window.__rec = []; window.__recOn = false;
  const gl = r.getContext(); let comp = 0; { const o = gl.compileShader; gl.compileShader = function () { comp++; return o.apply(this, arguments); }; }
  let ups = 0; for (const f of ['texImage2D', 'texSubImage2D']) { const o = gl[f]; gl[f] = function () { ups++; return o.apply(this, arguments); }; }
  let lt = 0; const loop = t => { if (__recOn) { const n = __pf.fb.length; __rec.push([t - lt, n ? __pf.fb[n - 1] : 0, I.render.calls, I.render.triangles, comp, ups]); }
    lt = t; I.reset(); comp = 0; ups = 0; requestAnimationFrame(loop); }; requestAnimationFrame(loop); })()"""

pkey = lambda nd: '%s:%d' % (nd['callFrame']['functionName'] or '(anon)', nd['callFrame']['lineNumber'] + 1)
def top_self(prof, n):
    nodes = {nd['id']: nd for nd in prof['nodes']}; t = {}
    for sid, dt in zip(prof['samples'], prof['timeDeltas']): k = pkey(nodes[sid]); t[k] = t.get(k, 0) + dt
    tot = sum(prof['timeDeltas']) or 1
    return ', '.join('%s %.1f%%' % (k, 100 * v / tot) for k, v in sorted(t.items(), key=lambda x: -x[1])[:n])
def top_total(prof, n): # (ms, each function counted once per sample however deep it recurses)
    nodes = {nd['id']: nd for nd in prof['nodes']}; par = {}
    for nd in prof['nodes']:
        for c in nd.get('children', []): par[c] = nd['id']
    t = {}
    for sid, dt in zip(prof['samples'], prof['timeDeltas']):
        seen = set(); i = sid
        while i is not None:
            k = pkey(nodes[i])
            if k not in seen: seen.add(k); t[k] = t.get(k, 0) + dt
            i = par.get(i)
    skip = ('(root):0', '(program):0', '(idle):0')
    return ', '.join('%s %d' % (k, v / 1000) for k, v in sorted(t.items(), key=lambda x: -x[1]) if k not in skip)[:2500]
def pct(a, f): a = sorted(a); return a[min(len(a) - 1, int(f * len(a)))] if a else 0

async def main():
    page = probe_page(); srv = serve(GAME); res = {'tag': TAG, 'cpu': CPU, 'dpr': DPR, 'scenes': {}}
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=os.environ.get('CHROME', '/opt/pw-browsers/chromium'), args=os.environ.get('FLAGS', '').split() + ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--enable-precise-memory-info', '--autoplay-policy=no-user-gesture-required'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=DPR, has_touch=True, is_mobile=True, user_agent=UA)
        await ctx.route('**/*supabase.co/**', lambda r: r.abort()); await ctx.route('**/*fly.dev/**', lambda r: r.abort())
        if NODRAW: await ctx.add_init_script("for (const C of [WebGL2RenderingContext, WebGLRenderingContext]) for (const f of ['drawElements', 'drawArrays', 'drawElementsInstanced', 'drawArraysInstanced', 'drawRangeElements', 'blitFramebuffer', 'clear']) if (C.prototype[f]) C.prototype[f] = function () {};")
        await ctx.add_init_script("window.__tapGate = false; window.__fixedPR = true; window.__pnGpu = %g; try { if (!sessionStorage.getItem('pn')) { sessionStorage.setItem('pn', 1); %s; } } catch (e) {}" % (GPU, SAVE))
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        cdp = await ctx.new_cdp_session(pg); await cdp.send('Performance.enable')
        await cdp.send('Emulation.setCPUThrottlingRate', {'rate': CPU})
        if PROF: await cdp.send('Profiler.enable'); await cdp.send('Profiler.setSamplingInterval', {'interval': 500}); await cdp.send('Profiler.start')
        t0 = time.time()
        await pg.goto(f'http://127.0.0.1:{PORT}/{page}', timeout=600000)
        t_load = time.time() - t0
        await cdp.send('Emulation.setCPUThrottlingRate', {'rate': 1}) if os.environ.get('BOOT1') else None
        for i in range(2400):
            if await pg.evaluate("!!(window.__pn && __pn.info().state === 'menu' && document.getElementById('boot').classList.contains('gone'))"): break
            if i % 40 == 0: print('  booting', round(time.time() - t0), 's', await pg.evaluate("(() => { const b = document.getElementById('boot'); return [b && b.className, window.__pn ? __pn.info().state : '-', window.__bootP]; })()"), errs[:2], flush=True)
            await pg.wait_for_timeout(250)
        await cdp.send('Emulation.setCPUThrottlingRate', {'rate': CPU})
        t_menu = time.time() - t0
        nav = await pg.evaluate("(() => { const n = performance.getEntriesByType('navigation')[0]; return { dcl: n.domContentLoadedEventEnd, load: n.loadEventEnd, now: performance.now() }; })()")
        await pg.evaluate(REC)
        async def metrics(): return {x['name']: x['value'] for x in (await cdp.send('Performance.getMetrics'))['metrics']}
        async def heap():
            await cdp.send('HeapProfiler.collectGarbage')
            return await pg.evaluate("(() => ({ js: performance.memory.usedJSHeapSize / 1048576, geo: __pn.renderer.info.memory.geometries, tex: __pn.renderer.info.memory.textures, prog: (__pn.renderer.info.programs || []).length, dom: document.getElementsByTagName('*').length }))()")
        mb = await metrics()
        if PROF: boot_prof = (await cdp.send('Profiler.stop'))['profile']; print('   launch profile:', top_self(boot_prof, 22), flush=True); print('   launch, by total time:', top_total(boot_prof, 22), flush=True)
        if 'launch' in SCENES:
            await pg.wait_for_timeout(1500)
            res['scenes']['launch'] = dict(dcl_ms=round(nav['dcl']), load_ms=round(nav['load']), menu_ms=round(t_menu * 1000), main_ms=round(mb['TaskDuration'] * 1000), script_ms=round(mb['ScriptDuration'] * 1000), heap=await heap())
            print('launch: DOMContentLoaded %d ms, load %d ms, menu ready %d ms wall (SwiftShader compiles included); main thread busy %d ms, script %d ms (%gx CPU)' % (nav['dcl'], nav['load'], t_menu * 1000, mb['TaskDuration'] * 1000, mb['ScriptDuration'] * 1000, CPU), res['scenes']['launch']['heap'])

        async def measure(name, secs=SECS, settle=2500):
            await pg.wait_for_timeout(settle)
            if PROF: await cdp.send('Profiler.enable'); await cdp.send('Profiler.setSamplingInterval', {'interval': 200}); await cdp.send('Profiler.start')
            m0 = await metrics(); await pg.evaluate("__pf.fb.length = 0; __rec.length = 0; __pf.on = true; __recOn = true; if (window.__sp) { __sp.st = {}; __sp.cur = {}; __sp.on = true; }")
            await pg.wait_for_timeout(int(secs * 1000))
            await pg.evaluate("__pf.on = false; __recOn = false"); m1 = await metrics()
            if PROF:
                print('   profile (self time):', top_self((await cdp.send('Profiler.stop'))['profile'], 16), flush=True)
            R = await pg.evaluate("__rec"); info = await pg.evaluate("__pn.info()")
            if os.environ.get('SPLIT'):
                ST = await pg.evaluate("(() => { __sp.on = false; return __sp.st; })()"); nf = max(1, len(R))
                print('   split (ms per frame, mean / p95):', ', '.join('%s %.2f/%.1f' % (k, sum(v) / nf, pct(v + [0] * (nf - len(v)), .95)) for k, v in sorted(ST.items(), key=lambda kv: -sum(kv[1]))[:14]), flush=True)
            n = max(1, len(R)); dts = [r[0] for r in R[1:]]; fb = [r[1] for r in R]
            d = {k: (m1.get(k, 0) - m0.get(k, 0)) * 1000 / n for k in ('TaskDuration', 'ScriptDuration', 'LayoutDuration', 'RecalcStyleDuration')}
            o = dict(frames=len(R), fps=len(R) / secs, dt50=pct(dts, .5), dt95=pct(dts, .95), fb50=pct(fb, .5), fb95=pct(fb, .95), fb99=pct(fb, .99), fbmax=max(fb or [0]),
                     fbmean=sum(fb) / n, hitch16=sum(1 for x in fb if x > 16.7), hitch33=sum(1 for x in fb if x > 33.3),
                     task=d['TaskDuration'], script=d['ScriptDuration'], layout=d['LayoutDuration'], style=d['RecalcStyleDuration'],
                     calls=pct([r[2] for r in R], .5), tris=pct([r[3] for r in R], .5), comp=sum(r[4] for r in R), ups=sum(r[5] for r in R),
                     px=info['w'] * info['h'] / (GPU * GPU), pr=info['curPR'], q=info['qLvl'], state=info['state'], mode=info['mode'], stage=info['stageSel'])
            res['scenes'][name] = o
            print('%-16s fb p50 %5.1f p95 %5.1f p99 %5.1f max %5.1f mean %5.1f | >16.7 %3d >33 %3d of %4d | task %5.1f script %5.1f style %4.1f layout %4.1f ms/frame | calls %4d tris %4dk px %4.2fM pr %.2f q %d | compiles %d tex %d | %s'
                  % (name, o['fb50'], o['fb95'], o['fb99'], o['fbmax'], o['fbmean'], o['hitch16'], o['hitch33'], o['frames'], o['task'], o['script'], o['style'], o['layout'], o['calls'], o['tris'] // 1000, o['px'] / 1e6, o['pr'], o['q'], o['comp'], o['ups'], o['state']), flush=True)
            return o

        async def to_menu():
            if await pg.evaluate("__pn.info().state") != 'menu': await pg.evaluate("__T.ev('showMenu(); irisBusy = false;')") # (the skipped intro leaves the wipe's flag up)
            for i in range(600):
                inf = await pg.evaluate("__pn.info()")
                if inf['state'] == 'menu' and not inf['irisBusy'] and not inf['building']: return
                if i % 60 == 59: print('  waiting for the menu', inf, flush=True)
                await pg.wait_for_timeout(500)
            raise RuntimeError('no menu')

        async def match(name, mode, stage):
            await to_menu()
            await pg.evaluate(f"__T.ev(\"if (lkOn()) closeLocker(true); stageSel = '{stage}'; setMode('{mode}');\")")
            await pg.evaluate("window.__skipIntro = true; __T.ev('start()')")
            await pg.wait_for_function("__pn.info().state === 'play'", timeout=600000, polling=100)
            await pg.evaluate("__pn.aiMe()")
            if os.environ.get('TEXLOG'):
                await pg.evaluate("""(() => { const gl = __pn.renderer.getContext(); window.__tl = {}; for (const f of ['texImage2D', 'texSubImage2D']) { const o = gl[f]; gl[f] = function () {
                  const a = [...arguments], src = a.find(x => x && typeof x === 'object' && 'width' in x), w = src ? src.width : a[3], h = src ? src.height : a[4];
                  const st = new Error().stack.split('\\n').slice(2, 9).map(l => l.trim().replace(/^at /, '').replace(/\\(.*:(\\d+):\\d+\\)/, ':$1')).join(' < ');
                  const k = f + ' ' + w + 'x' + h + ' ' + (src ? src.constructor.name : 'data') + ' | ' + st; __tl[k] = (__tl[k] || 0) + 1; return o.apply(this, arguments); }; } })()""")
                await pg.wait_for_timeout(8000)
                for k, v in sorted((await pg.evaluate('__tl')).items(), key=lambda kv: -kv[1])[:8]: print('  %4d  %s' % (v, k[:400]), flush=True)
            o = await measure(name); o['heap'] = await heap(); return o

        if 'lobby' in SCENES: await to_menu(); await measure('lobby')
        if 'locker' in SCENES:
            await to_menu(); await pg.evaluate("__T.ev(\"openLocker('mine')\")"); await measure('locker'); await pg.evaluate("__T.ev('closeLocker(true)')")
        if 'stages' in SCENES:
            for st in STAGES: await match('duel:' + st, 'duel', st)
        if 'showdown' in SCENES: await match('showdown4', 'ffa', 'island')
        if 'trial' in SCENES: await match('trial', 'solo', 'island')
        if 'repeat' in SCENES: # (the same match again and again: does anything pile up?)
            res['repeat'] = []
            for i in range(int(os.environ.get('REPEAT', 6))):
                await to_menu(); h = await heap(); res['repeat'].append(h); print('  menu before match %d:' % (i + 1), h, flush=True)
                await pg.evaluate("__T.ev(\"stageSel = 'island'; setMode('duel');\")"); await pg.evaluate("window.__skipIntro = true; __T.ev('start()')")
                await pg.wait_for_function("__pn.info().state === 'play'", timeout=600000, polling=100); await pg.wait_for_timeout(3000)
        await to_menu(); res['heap_end'] = await heap(); print('heap at the end, back in the menu:', res['heap_end'])
        print('errors:', errs[:5]); res['errors'] = errs
        await b.close()
    srv.shutdown(); os.remove(os.path.join(GAME, page))
    json.dump(res, open(os.path.join(OUT, 'pnprobe_%s.json' % TAG), 'w'), indent=1)
asyncio.run(main())
