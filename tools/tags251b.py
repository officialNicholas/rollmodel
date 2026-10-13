"""v251 name tags, the special cases: the '!' over a tag, a rival in a basin, knocked out, behind a wall, a giant, a 3-way.
usage: tags251b.py scen [scen ...]  (alert hide ko wall giant trio)  env: VW VH DSF TAG MODE"""
import asyncio, os, sys, functools, json
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
SC = sys.argv[1:]; TAG = os.environ.get('TAG', 'b'); MODE = 'trio' if 'trio' in SC else os.environ.get('MODE', 'duel')
LAND = int(os.environ.get('VW', 390)) > int(os.environ.get('VH', 844))
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': int(os.environ.get('VW', 390)), 'height': int(os.environ.get('VH', 844))}, device_scale_factor=float(os.environ.get('DSF', 2)), has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; window.__noReveal = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'%s', name:'Dusk', seen:{}, drops: 0, xp: 900, tut: { ph: 'done', strokes: 1, comms: 1, m3: 2 } })); } catch (e) {}" % ('land' if LAND else 'port'))
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('console', lambda m: m.type == 'error' and errs.append('console: ' + m.text[:200])); ev = pg.evaluate
        async def wait(js, t=400000): await pg.wait_for_function(js, timeout=t, polling=100)
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await wait('typeof __T === "object"'); await pg.wait_for_timeout(800)
        await ev(f"__T.mode = '{MODE}'; __T.applyMode(); __T.start()"); await wait("__T.state === 'play'"); await pg.wait_for_timeout(1200)
        await ev("window.__noStep = true")
        tags = """(() => { const out = {}; for (const [D, t] of __T.ev('ntags')) { const r = t.el.getBoundingClientRect(); out[__T.ev('nameOf')(D)] = { k: +t.k.toFixed(2), d: +t.d.toFixed(1), hid: t.el.hidden, see: t.see, top: Math.round(r.top), bot: Math.round(r.bottom), x: Math.round((r.left + r.right) / 2), z: t.el.style.zIndex }; } return out; })()"""
        spot = await ev("""(() => { const T = __T, A = T.ARENA - 3, ok = (x, z) => Math.abs(x) < A && Math.abs(z) < A && T.surfaceUnder(x, z, 0.3) === 0 && !T.blockedAt(x, z, 0) && !T.pots.some(p => Math.hypot(p.x - x, p.z - z) < 2.5);
          let best = null; for (let gx = -A; gx <= A; gx += 1.5) for (let gz = -A; gz <= A; gz += 1.5) { if (!ok(gx, gz)) continue; for (let k = 0; k < 16; k++) { const a = k * Math.PI / 8; let run = 0; for (let d = 0.5; d <= 20; d += 0.5) { let c = true; for (const s of [-2.5, 0, 2.5]) if (!ok(gx + Math.sin(a) * d + Math.cos(a) * s, gz + Math.cos(a) * d - Math.sin(a) * s)) c = false; if (!c) break; run = d; }
            if (!best || run > best[3]) best = [gx, gz, a, run]; } } return best; })()""")
        async def place(d, side, d2=None, side2=None):
            await ev(f"""(() => {{ const T = __T, P = T.P, H = T.H, H2 = T.H2, [gx, gz, a] = {json.dumps(spot[:3])};
              P.x = gx; P.z = gz; P.y = 0; P.yaw = a; P.air = false; P.vy = 0; P.st = 'play'; P.spd = 0; T.camYaw = a; T.camSnap = true;
              const put = (D, d, s, y) => {{ D.x = gx + Math.sin(a) * d + Math.cos(a) * s; D.z = gz + Math.cos(a) * d - Math.sin(a) * s; D.y = 0; D.yaw = a + y; D.st = 'play'; D.air = false; D.vy = 0; D.spd = 0; D.giantT = 0; if (D.ai) D.ai.alert = null; }};
              put(H, {d}, {side}, Math.PI - 0.5); {'' if d2 is None else f'put(H2, {d2}, {side2}, Math.PI + 0.7);'} }})()""")
        for sc in SC:
            if sc == 'alert':
                await place(5, 0.8); await pg.wait_for_timeout(2500); await ev("__T.H.ai.alert = { k: '!', t: 0.9 }"); await pg.wait_for_timeout(150)
                print('alert', await ev(tags), await ev("(() => { const m = __T.LH.mark, v = m.position.clone().project(__T.camera); return { vis: m.visible, y: +(m.position.y - __T.H.y).toFixed(2), px: Math.round((0.5 - v.y * 0.5) * innerHeight) }; })()"))
                await pg.screenshot(path=f'{WS}/ui/tag251{TAG}_alert.png')
            if sc == 'hide':
                await place(5, 0.8); await pg.wait_for_timeout(2500); k0 = await ev(tags); await ev("__T.H.st = 'hide'"); await pg.wait_for_timeout(4000); print('hide: before', k0, 'after', await ev(tags)); await ev("__T.H.st = 'play'")
            if sc == 'ko':
                await place(5, 0.8); await pg.wait_for_timeout(2500); await ev("__T.H.st = 'ko'"); await pg.wait_for_timeout(4000); print('ko', await ev(tags)); await ev("__T.H.st = 'play'")
            if sc == 'giant':
                await place(6, 0.8); await ev("__T.H.giantT = 6; __T.LH.V.gk = __T.ev('GIANT_K')"); await pg.wait_for_timeout(3000); print('giant', await ev(tags), await ev("+__T.LH.V.gk.toFixed(2)")); await pg.screenshot(path=f'{WS}/ui/tag251{TAG}_giant.png'); await ev("__T.H.giantT = 0")
            if sc == 'trio':
                await place(6, 1.6, 4, -1.8); await pg.wait_for_timeout(3000); print('trio', await ev(tags)); await pg.screenshot(path=f'{WS}/ui/tag251{TAG}_trio.png')
                await place(5, 0.3, 5.6, 0.9); await pg.wait_for_timeout(2500); print('trio overlap', await ev(tags)); await pg.screenshot(path=f'{WS}/ui/tag251{TAG}_trio2.png')
            if sc == 'wall':
                # a tall block between the camera and the rival: you on the near side, the rival tucked behind its far face
                w = await ev("""(() => { const T = __T, A = T.ARENA - 2; let best = null; for (const r of T.BOXES) { if (r[6] === 'c' || r[4] > 0.2 || r[5] - r[4] < 1.6) continue; const cx = (r[0] + r[1]) / 2, cz = (r[2] + r[3]) / 2, hx = (r[1] - r[0]) / 2, hz = (r[3] - r[2]) / 2;
                  for (let k = 0; k < 4; k++) { const a = k * Math.PI / 2, ext = k % 2 ? hx : hz, px = cx - Math.sin(a) * (ext + 5), pz = cz - Math.cos(a) * (ext + 5), rx = cx + Math.sin(a) * (ext + 0.7), rz = cz + Math.cos(a) * (ext + 0.7);
                    const ok = (x, z) => Math.abs(x) < A && Math.abs(z) < A && T.surfaceUnder(x, z, 0.3) === 0 && !T.blockedAt(x, z, 0);
                    if (ok(px, pz) && ok(rx, rz) && (k % 2 ? hz : hx) > 1.2) { best = [px, pz, a, rx, rz, r[5] - r[4]]; break; } } if (best) break; } return best; })()""")
                print('wall setup', w)
                if w:
                    await ev(f"""(() => {{ const T = __T, P = T.P, H = T.H, [px, pz, a, rx, rz] = {json.dumps(w)}; P.x = px; P.z = pz; P.y = 0; P.yaw = a; P.st = 'play'; P.air = false; T.camYaw = a; T.camSnap = true; H.x = rx; H.z = rz; H.y = 0; H.st = 'play'; H.air = false; }})()""")
                    await ev("for (const t of __T.ev('ntags').values()) t.seeAt = -9"); await pg.wait_for_timeout(3000); print('wall', await ev(tags), 'sight', await ev("(() => { const c = __T.camera.position, H = __T.H; return __T.losClear(c.x, c.y, c.z, H.x, H.y + 0.35, H.z); })()")); await pg.screenshot(path=f'{WS}/ui/tag251{TAG}_wall.png')
        print('errors', errs[:6]); await b.close()
asyncio.run(main())
