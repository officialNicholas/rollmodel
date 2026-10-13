"""v251 name tags: a 1v1 (or 3-way with MODE=trio), the rival set down at distances ahead; the tag's opacity, size and place, screenshots.
usage: tags251.py [dist ...]   env: VW VH (viewport), MODE, DSF, TAG (file tag)"""
import asyncio, os, sys, functools, json
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
DISTS = [float(a) for a in sys.argv[1:]] or [3, 6, 9, 12, 15, 18]
MODE = os.environ.get('MODE', 'duel'); TAG = os.environ.get('TAG', 'p')
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': int(os.environ.get('VW', 390)), 'height': int(os.environ.get('VH', 844))}, device_scale_factor=float(os.environ.get('DSF', 2)), has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; window.__noReveal = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'%s', name:'Dusk', seen:{}, drops: 0, xp: +(window.__xp || 900), tut: { ph: 'done', strokes: 1, comms: 1, m3: 2 } })); } catch (e) {}" % ('land' if int(os.environ.get('VW', 390)) > int(os.environ.get('VH', 844)) else 'port'))
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('console', lambda m: m.type == 'error' and errs.append('console: ' + m.text[:200])); ev = pg.evaluate
        async def wait(js, t=400000): await pg.wait_for_function(js, timeout=t, polling=100)
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await wait('typeof __T === "object"'); await pg.wait_for_timeout(800)
        await ev(f"__T.mode = '{MODE}'; __T.applyMode(); __T.start()"); await wait("__T.state === 'play'"); await pg.wait_for_timeout(1200)
        print('ranks: you', await ev("__T.ev('rankOf(P)')"), 'rivals', await ev("__T.ev('[rankOf(H), rankOf(H2), NAMES[1], NAMES[2], diff]')"))
        # an open run of floor: you at one end facing along it
        spot = await ev("""(() => { const T = __T, A = T.ARENA - 3, ok = (x, z) => Math.abs(x) < A && Math.abs(z) < A && T.surfaceUnder(x, z, 0.3) === 0 && !T.blockedAt(x, z, 0) && !T.pots.some(p => Math.hypot(p.x - x, p.z - z) < 2.5);
          let best = null; for (let gx = -A; gx <= A; gx += 1.5) for (let gz = -A; gz <= A; gz += 1.5) { if (!ok(gx, gz)) continue; for (let k = 0; k < 16; k++) { const a = k * Math.PI / 8; let run = 0; for (let d = 0.5; d <= 26; d += 0.5) { let c = true; for (const s of [-2, 0, 2]) if (!ok(gx + Math.sin(a) * d + Math.cos(a) * s, gz + Math.cos(a) * d - Math.sin(a) * s)) c = false; if (!c) break; run = d; }
            if (!best || run > best[3]) best = [gx, gz, a, run]; } } return best; })()""")
        print('run', spot)
        await ev("window.__noStep = true")
        rows = []
        for i, d in enumerate(DISTS):
            await ev(f"""(() => {{ const T = __T, P = T.P, H = T.H, [gx, gz, a] = {json.dumps(spot[:3])}, d = {d}, side = {0.9 if MODE == 'duel' else -1.4};
              P.x = gx; P.z = gz; P.y = 0; P.yaw = a; P.air = false; P.vy = 0; P.st = 'play'; P.spd = 0; T.camYaw = a; T.camSnap = true;
              H.x = gx + Math.sin(a) * d + Math.cos(a) * side; H.z = gz + Math.cos(a) * d - Math.sin(a) * side; H.y = 0; H.yaw = a + Math.PI; H.st = 'play'; H.air = false; H.vy = 0; H.spd = 0;
              if (T.mode === 'trio') {{ const H2 = T.H2, d2 = d * 0.6 + 2; H2.x = gx + Math.sin(a) * d2 - Math.cos(a) * 1.6; H2.z = gz + Math.cos(a) * d2 + Math.sin(a) * 1.6; H2.y = 0; H2.yaw = a + 2.4; H2.st = 'play'; H2.air = false; H2.vy = 0; }} }})()""")
            await pg.wait_for_timeout(int(os.environ.get('HOLD', 2500)))
            r = await ev("""(() => { const out = []; for (const [D, t] of __T.ev('ntags')) { const r = t.el.getBoundingClientRect(); out.push({ who: __T.ev('nameOf')(D), k: +t.k.toFixed(2), d: +t.d.toFixed(1), hid: t.el.hidden, box: [Math.round(r.left), Math.round(r.top), Math.round(r.width), Math.round(r.height)], see: t.see }); } return out; })()""")
            top = await ev("""(() => { const T = __T, H = T.H, L = H.look, b = new T.THREE.Box3().setFromObject(L.drop), v = new T.THREE.Vector3(H.x, b.max.y, H.z).project(T.camera), h = T.ev('charTall')(L.wearing); return { boxTop: +(b.max.y - H.y).toFixed(2), charTall: +h.toFixed(2), headPx: Math.round((0.5 - v.y * 0.5) * innerHeight), head: L.wearing.head }; })()""")
            print(f'd={d}', r, top); rows.append(r)
            await pg.screenshot(path=f'{WS}/ui/tag251_{TAG}_{i}_{d:g}.png')
        print('errors', errs[:6]); await b.close()
asyncio.run(main())
