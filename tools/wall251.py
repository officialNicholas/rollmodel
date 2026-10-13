import asyncio, json, functools
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; window.__noReveal = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{}, drops: 0, xp: 900, tut: { ph: 'done', strokes: 1, comms: 1, m3: 2 } })); } catch (e) {}")
        pg = await ctx.new_page(); ev = pg.evaluate
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=400000); await pg.wait_for_timeout(800)
        await ev("__T.mode = 'duel'; __T.applyMode(); __T.start()"); await pg.wait_for_function("__T.state === 'play'", timeout=400000); await pg.wait_for_timeout(1200); await ev("window.__noStep = true")
        r = await ev("""(() => { const T = __T, A = T.ARENA - 2, out = []; for (const r of T.BOXES) { if (r[6] === 'c' || r[4] > 0.2 || r[5] - r[4] < 1.6) continue; out.push(r.slice(0, 7).map(v => typeof v === 'number' ? +v.toFixed(2) : v)); } return out.slice(0, 8); })()""")
        print('tall boxes', r)
        # a tall box: you 5 m from its near face, the rival 0.7 m behind its far face; the camera snapped; sight lines at heights
        res = await ev("""(() => { const T = __T, P = T.P, H = T.H, A = T.ARENA - 2; for (const r of T.BOXES) { if (r[6] === 'c' || r[4] > 0.2 || r[5] - r[4] < 1.6) continue; const cx = (r[0] + r[1]) / 2, cz = (r[2] + r[3]) / 2, hx = (r[1] - r[0]) / 2, hz = (r[3] - r[2]) / 2;
            for (let k = 0; k < 4; k++) { const a = k * Math.PI / 2, ext = k % 2 ? hx : hz, px = cx - Math.sin(a) * (ext + 5), pz = cz - Math.cos(a) * (ext + 5), rx = cx + Math.sin(a) * (ext + 0.7), rz = cz + Math.cos(a) * (ext + 0.7);
              const ok = (x, z) => Math.abs(x) < A && Math.abs(z) < A && T.surfaceUnder(x, z, 0.3) === 0 && !T.blockedAt(x, z, 0); if (!(ok(px, pz) && ok(rx, rz) && (k % 2 ? hz : hx) > 1.2)) continue;
              P.x = px; P.z = pz; P.y = 0; P.yaw = a; P.st = 'play'; P.air = false; T.camYaw = a; T.camSnap = true; H.x = rx; H.z = rz; H.y = 0; H.st = 'play'; H.air = false;
              return { box: r.slice(0, 6).map(v => +v.toFixed(2)), a, P: [px, pz], H: [rx, rz] }; } } return null; })()""")
        print('setup', res); await pg.wait_for_timeout(2500)
        print('cam', await ev("[__T.camera.position.x, __T.camera.position.y, __T.camera.position.z].map(v => +v.toFixed(2))"))
        print('sight', await ev("(() => { const c = __T.camera.position, H = __T.H; return [0, 0.35, 0.6, 1, 1.5].map(h => [h, __T.losClear(c.x, c.y, c.z, H.x, H.y + h, H.z)]); })()"))
        print('surface under rival', await ev("__T.surfaceUnder(__T.H.x, __T.H.z, 3)"), 'blocked at rival', await ev("__T.blockedAt(__T.H.x, __T.H.z, 0)"))
        await b.close()
asyncio.run(main())
