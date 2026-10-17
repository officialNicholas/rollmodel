"""pn: game smoothness probe on a phone-like setup. Builds nothing: point it at a --test build (q260.py ... --test).
Chromium at 390x844, device scale 3, iPhone user agent, touch, CPU throttled (default 4x) through the DevTools protocol.
Graphics run on SwiftShader (software), which would make every frame wait on it, so the drawing buffer is scaled down
(GPU, default 0.25 of the game's own pixel ratio) and the game's quality tuner is held where it starts (window.__fixedPR).
The numbers to compare are the main thread's own work per frame (frame body, script, style and layout), the hitches in
it, and the GPU's load in draw calls, triangles and the pixels the game asks for (px, at full scale).

Scenes: launch (boot to menu), lobby, locker, a versus match on each stage, Showdown with four, Time trial. The game's AI
drives you in matches. Prints one line per scene and writes JSON.

usage: pn_probe.py <page.html> <tag> [scenes]   env: SECS (per scene, 10), CPU (throttle, 4), DPR (3), OUT (json dir),
       PORT (8765), STAGES (comma list)
scenes: launch,lobby,locker,stages,showdown,trial (default all)"""
import asyncio, json, os, sys, http.server, threading, functools, time
from playwright.async_api import async_playwright

PAGE = os.path.abspath(sys.argv[1]); TAG = sys.argv[2]
SCENES = (sys.argv[3] if len(sys.argv) > 3 else 'launch,lobby,locker,stages,showdown,trial').split(',')
SECS = float(os.environ.get('SECS', 10)); GPU = float(os.environ.get('GPU', 0.25)); CPU = float(os.environ.get('CPU', 4)); DPR = float(os.environ.get('DPR', 3))
OUT = os.environ.get('OUT', os.path.dirname(PAGE)); PORT = int(os.environ.get('PORT', 8765))
STAGES = os.environ.get('STAGES', 'island,blank,sewer,raft,crypt,cathedral,manor').split(',')
GAME = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'game') # (the page loads three.js and the art from here)
UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1'

# measuring hooks, put inside the game's own scope (its functions are local there). The probe page is written into game/
# (it loads three.js and the art from there) and deleted at the end.
HOOK = r"""
window.__pf = { fb: [], on: false };
{ const fb0 = frameBody; frameBody = function (t) { if (!__pf.on) return fb0.apply(this, arguments); const t0 = performance.now(); try { return fb0.apply(this, arguments); } finally { __pf.fb.push(performance.now() - t0); } }; }
if (window.__pnGpu !== 1) { const sp = renderer.setPixelRatio.bind(renderer); renderer.setPixelRatio = v => sp(v * window.__pnGpu); renderer.setPixelRatio(curPR); resize(); }
window.__pn = { aiMe: () => { P.cpu = true; aiReset(P); }, info: () => ({ state, mode, stageSel, qLvl, curPR, menuPage, building, irisBusy, w: renderer.domElement.width, h: renderer.domElement.height }), renderer };
"""
AIIN = "let input = D === P ? (keyL || keyR ? (keyR ? 1 : 0) - (keyL ? 1 : 0) : steerIn) : D.steer;"

def probe_page():
    s = open(PAGE).read()
    a = '\nwindow.__T = { ev: s => eval(s) };'; assert s.count(a) == 1, 'not a --test build'
    s = s.replace(a, a + HOOK)
    assert s.count(AIIN) == 1; s = s.replace(AIIN, AIIN.replace('D === P ?', 'D === P && !P.cpu ?'))
    out = os.path.join(GAME, '_pnprobe_' + os.path.basename(PAGE)); open(out, 'w').write(s); return os.path.basename(out)

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
def serve(dirpath):
    h = functools.partial(Quiet, directory=dirpath)
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), h); threading.Thread(target=srv.serve_forever, daemon=True).start(); return srv

SAVE = "localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient: 'port', name: 'Dusk', introDone: 1, seen: { look: 1, steer: 1, jump: 1, hold: 1, roll: 1, missile: 1, pound: 1, burst: 1, orb: 1 }, drops: 50, runs: 30, flings: 50, xp: 99999, tut: { ph: 'done' }, gfx: 'hi' }))"

REC = r"""(() => { const r = __pn.renderer, I = r.info; I.autoReset = false; window.__rec = []; window.__recOn = false;
  const gl = r.getContext(); let comp = 0; { const o = gl.compileShader; gl.compileShader = function () { comp++; return o.apply(this, arguments); }; }
  let ups = 0; for (const f of ['texImage2D', 'texSubImage2D']) { const o = gl[f]; gl[f] = function () { ups++; return o.apply(this, arguments); }; }
  let lt = 0; const loop = t => { if (__recOn) { const n = __pf.fb.length; __rec.push([t - lt, n ? __pf.fb[n - 1] : 0, I.render.calls, I.render.triangles, comp, ups]); }
    lt = t; I.reset(); comp = 0; ups = 0; requestAnimationFrame(loop); }; requestAnimationFrame(loop); })()"""

def pct(a, f): a = sorted(a); return a[min(len(a) - 1, int(f * len(a)))] if a else 0

async def main():
    page = probe_page(); srv = serve(GAME); res = {'tag': TAG, 'cpu': CPU, 'dpr': DPR, 'scenes': {}}
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=os.environ.get('CHROME', '/opt/pw-browsers/chromium'), args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--enable-precise-memory-info', '--autoplay-policy=no-user-gesture-required'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=DPR, has_touch=True, is_mobile=True, user_agent=UA)
        await ctx.route('**/*supabase.co/**', lambda r: r.abort()); await ctx.route('**/*fly.dev/**', lambda r: r.abort())
        await ctx.add_init_script("window.__tapGate = false; window.__fixedPR = true; window.__pnGpu = %g; try { if (!sessionStorage.getItem('pn')) { sessionStorage.setItem('pn', 1); %s; } } catch (e) {}" % (GPU, SAVE))
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        cdp = await ctx.new_cdp_session(pg); await cdp.send('Performance.enable')
        await cdp.send('Emulation.setCPUThrottlingRate', {'rate': CPU})
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
        if 'launch' in SCENES:
            await pg.wait_for_timeout(1500)
            res['scenes']['launch'] = dict(dcl_ms=round(nav['dcl']), load_ms=round(nav['load']), menu_ms=round(t_menu * 1000), heap=await heap())
            print('launch: DOMContentLoaded %d ms, load %d ms, menu ready %d ms (wall, %gx CPU)' % (nav['dcl'], nav['load'], t_menu * 1000, CPU), res['scenes']['launch']['heap'])

        async def measure(name, secs=SECS, settle=2500):
            await pg.wait_for_timeout(settle)
            m0 = await metrics(); await pg.evaluate("__pf.fb.length = 0; __rec.length = 0; __pf.on = true; __recOn = true")
            await pg.wait_for_timeout(int(secs * 1000))
            await pg.evaluate("__pf.on = false; __recOn = false"); m1 = await metrics()
            R = await pg.evaluate("__rec"); info = await pg.evaluate("__pn.info()")
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
            if await pg.evaluate("__pn.info().state") != 'menu': await pg.evaluate("__T.ev('showMenu()')")
            await pg.wait_for_function("__pn.info().state === 'menu' && !__pn.info().irisBusy && !__pn.info().building", timeout=600000, polling=100)

        async def match(name, mode, stage):
            await to_menu()
            await pg.evaluate(f"__T.ev(\"if (lkOn()) closeLocker(true); stageSel = '{stage}'; setMode('{mode}');\")")
            await pg.evaluate("window.__skipIntro = true; __T.ev('start()')")
            await pg.wait_for_function("__pn.info().state === 'play'", timeout=600000, polling=100)
            await pg.evaluate("__pn.aiMe()")
            o = await measure(name); o['heap'] = await heap(); return o

        if 'lobby' in SCENES: await to_menu(); await measure('lobby')
        if 'locker' in SCENES:
            await to_menu(); await pg.evaluate("__T.ev(\"openLocker('mine')\")"); await measure('locker'); await pg.evaluate("__T.ev('closeLocker(true)')")
        if 'stages' in SCENES:
            for st in STAGES: await match('duel:' + st, 'duel', st)
        if 'showdown' in SCENES: await match('showdown4', 'ffa', 'island')
        if 'trial' in SCENES: await match('trial', 'solo', 'island')
        await to_menu(); res['heap_end'] = await heap(); print('heap at the end, back in the menu:', res['heap_end'])
        print('errors:', errs[:5]); res['errors'] = errs
        await b.close()
    srv.shutdown(); os.remove(os.path.join(GAME, page))
    json.dump(res, open(os.path.join(OUT, 'pnprobe_%s.json' % TAG), 'w'), indent=1)
asyncio.run(main())
