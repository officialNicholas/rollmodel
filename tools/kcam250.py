"""v250 kill cam: you pound the rival out a few metres from the edge of the canvas, rolling at it; while the slow-motion shot plays the
game steers you round the other way and never over the drop, and the view comes back in behind your new heading. Logs where you are
(distance to the drop ahead, heading) through it and after. usage: kcam250.py [stage]"""
import asyncio, os, sys, functools, json
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'; SID = sys.argv[1] if len(sys.argv) > 1 else 'island'; PAGE = os.environ.get('PAGE', 'pc_h.html')
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 300, 'height': 560}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__noVote = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{ jump: 1, hold: 1, steer: 1, item: 1, orb: 1, roll: 1, pound: 1, missile: 1, burst: 1 }, drops: 0, runs: 5, stage: '" + SID + "', mode: 'duel', tut: { ph: 'done', strokes: 1, comms: 1 } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
        await pg.goto('http://localhost:8765/' + PAGE, timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000, polling=100); await pg.wait_for_timeout(1000)
        if os.environ.get('FAST'): await ev("(() => { const r = __T.renderer; window.__rr = r.render.bind(r); r.render = () => {}; })(); 0")  # (logic only: 3D drawing off, so the game runs at full speed)
        await ev("__T.start()"); await pg.wait_for_function("__T.state === 'play'", timeout=400000, polling=100); await pg.wait_for_timeout(2500)
        # (a spot facing a drop off the canvas, about 4 m from it, the floor flat between; the rival just ahead of you)
        sp = await ev("""(() => { const T = __T, P = T.P, H = T.H, A = T.ARENA; let best = null;
          for (let k = 0; k < 32 && !best; k++) { const a = k / 32 * 6.2832, sx = Math.sin(a), sz = Math.cos(a);
            for (let r = 2; r < A + 6; r += 0.25) { const x = sx * r, z = sz * r; if (T.surfaceUnder(x, z, 0.4, true) === -Infinity) { // (the lip along this heading)
                const px = x - sx * 4.2, pz = z - sz * 4.2; let ok = true; for (let d = 0; d <= 3.8 && ok; d += 0.3) { const qx = px + sx * d, qz = pz + sz * d; if (T.blockedAt(qx, qz, 0) || Math.abs(T.surfaceUnder(qx, qz, 0.4, true)) > 0.05) ok = false; }
                if (ok) best = { a, px, pz, ex: x, ez: z }; break; } } }
          if (!best) return null; P.x = best.px; P.z = best.pz; P.y = 0; P.yaw = best.a; P.air = false; P.vy = 0; P.spd = T.cfg.speed; P.stroke++; T.camYaw = best.a;
          H.x = best.px + Math.sin(best.a) * 1.2; H.z = best.pz + Math.cos(best.a) * 1.2; H.y = 0; H.air = false; H.stroke++; H.immuneT = 0; return best; })()""")
        print('setup', sp)
        if not sp: print('no edge found'); await b.close(); return
        await ev("__T.steerIn = 0"); await pg.wait_for_timeout(100)
        await ev("__T.knockOut(__T.H, 'pound', __T.P)")
        print('kcam on', await ev("!!__T.kcam"), await ev("__T.kcam && [+__T.kcam.yaw.toFixed(2), __T.kcam.dir]"))
        rows = []; t0 = await ev("performance.now()"); shots = 0
        for i in range(400):
            r = await ev("""(() => { const T = __T, P = T.P, a0 = %f, ex = %f, ez = %f; let lip = 0; const sx = Math.sin(P.yaw), sz = Math.cos(P.yaw); for (let d = 0.2; d < 12; d += 0.2) { if (T.surfaceUnder(P.x + sx * d, P.z + sz * d, P.y + 0.4, true) === -Infinity) { lip = +d.toFixed(1); break; } }
              return [Math.round(performance.now()), !!T.kcam, P.st, +P.spd.toFixed(2), +(((P.yaw - a0) % 6.2832 + 9.4248) % 6.2832 - 3.1416).toFixed(2), lip, +Math.hypot(P.x - ex, P.z - ez).toFixed(2), +T.camYaw.toFixed(2), +P.yaw.toFixed(2), P.air]; })()""" % (sp['a'], sp['ex'], sp['ez']))
            rows.append(r)
            if shots < 4 and (i in (15, 45) or (not r[1] and rows[-2][1])): shots += 1; await pg.screenshot(path=f'{WS}/ui/kc250_{SID}_{i}.png')
            if r[2] != 'play' or (not r[1] and r[0] - t0 > 6500): break
            await pg.wait_for_timeout(60)
        for r in rows[::6]: print('  ', r)
        print('  last', rows[-1]); print('fell' if any(r[2] != 'play' for r in rows) else 'stayed on', 'min to lip', min(r[6] for r in rows))
        print('errors', errs[:4]); await b.close()
asyncio.run(main())
