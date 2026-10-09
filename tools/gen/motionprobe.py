# how smooth and responsive moving feels, measured: a scripted run (straight, weaving, a hard turn, let go, a jump, a step up onto a
# deck) at 60 or 120 fps (or uneven frames), recording each frame the physics yaw, the drawn body's yaw and height, the camera's position
# and heading. Reports the input-to-turn delay, the camera's lag behind the turn, and jitter: frame-to-frame changes that jump about
# rather than flowing (the second differences)
import asyncio, sys, json, math
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_t.html'
FPS = sys.argv[2] if len(sys.argv) > 2 else '60'
JS = r"""(fps) => { const T = __T, P = T.P, out = []; window.__noLoop = true;
  T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
  T.mode = 'solo'; T.applyMode(); T.setStage('blank'); T.genWorld(88, { themes: ['blank'] }); T.mapUsed = false; T.start(); T.setWx('clear', 999);
  const nodes = T.NAVo.nodes.filter(n => n.h === 0 && n.edge === 0), n0 = nodes.sort((a, b) => Math.hypot(a.x, a.z) - Math.hypot(b.x, b.z))[0];
  for (let i = 0; i < 60; i++) { T.steerIn = 0; T.step(1 / 60); T.visuals(1 / 60, 1 / 60); }
  P.x = n0.x; P.z = n0.z; P.y = 0; P.yaw = Math.atan2(-n0.x, -n0.z); P.air = false; T.camYaw = P.yaw;
  const uneven = fps === 'uneven', base = uneven ? 60 : +fps; let t = 0, f = 0;
  // the script: steer as a function of time
  const steerAt = t => t < 0.6 ? 0 : t < 2.6 ? Math.sin((t - 0.6) * 3.2) * 0.75 : t < 3.2 ? 1 : t < 3.9 ? 0 : t < 4.4 ? -0.6 : 0;
  const R = T.VP.root || T.body.parent, cam = T.camera;
  let jumped = false;
  while (t < 5.2) { const dt = uneven ? (f % 7 === 3 ? 1 / 24 : f % 5 === 1 ? 1 / 40 : 1 / 60) : 1 / base; f++;
    T.steerIn = steerAt(t); if (!jumped && t >= 3.95) { T.jump(P); jumped = true; }
    const n = Math.ceil(dt / 0.012); for (let i = 0; i < n; i++) T.step(dt / n); T.visuals(dt, dt); t += dt;
    const fwd = new T.THREE.Vector3(); cam.getWorldDirection(fwd);
    out.push([+t.toFixed(4), T.steerIn, P.yaw, R.rotation.y, R.position.y, cam.position.x, cam.position.y, cam.position.z, Math.atan2(fwd.x, fwd.z), P.turn, P.spd, P.air ? 1 : 0]); }
  return out; }"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 200, 'height': 400}, device_scale_factor=1)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'lo', mode: 'solo', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300]))
        await pg.goto('file://' + SP + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(800)
        rows = await pg.evaluate(JS, FPS)
        json.dump(rows, open(SP + 'motion_%s_%s.json' % (PAGE.split('.')[0], FPS), 'w'))
        # metrics
        def wrap(a): return math.atan2(math.sin(a), math.cos(a))
        ts = [r[0] for r in rows]
        # delay: from the steer going to full right (t = 2.6) to the yaw rate reaching 63% of its eventual rate in the hard turn
        rates = [(wrap(rows[i][2] - rows[i - 1][2]) / (rows[i][0] - rows[i - 1][0]), rows[i][0]) for i in range(1, len(rows))]
        hard = [r for r in rates if 2.6 <= r[1] <= 3.2]; fin = sum(r[0] for r in hard[-5:]) / 5
        start = next((r[1] for r in hard if abs(r[0]) >= 0.63 * abs(fin)), None)
        # camera lag: the angle between the camera's heading and the blob's heading through the weave and the turn
        lag = [abs(wrap(r[8] - r[2])) for r in rows if 1.0 < r[0] < 3.3]
        # jitter: second differences of the drawn yaw, the drawn height and the camera's position, per frame (normalized to 60 fps steps)
        def jit(idx, scale=1):
            d2 = []
            for i in range(2, len(rows)):
                a, b2, c = rows[i - 2][idx], rows[i - 1][idx], rows[i][idx]; dt1 = rows[i - 1][0] - rows[i - 2][0]; dt2 = rows[i][0] - rows[i - 1][0]
                v1 = (wrap(b2 - a) if idx in (2, 3, 8) else b2 - a) / dt1; v2 = (wrap(c - b2) if idx in (2, 3, 8) else c - b2) / dt2; d2.append(abs(v2 - v1) / ((dt1 + dt2) / 2) * scale)
            d2.sort(); return round(d2[len(d2) // 2], 2), round(d2[int(len(d2) * 0.95)], 2), round(d2[-1], 2)
        camD = []
        for i in range(2, len(rows)):
            p = [rows[k][5:8] for k in (i - 2, i - 1, i)]; dt1 = rows[i - 1][0] - rows[i - 2][0]; dt2 = rows[i][0] - rows[i - 1][0]
            v1 = [(p[1][j] - p[0][j]) / dt1 for j in range(3)]; v2 = [(p[2][j] - p[1][j]) / dt2 for j in range(3)]
            camD.append(math.sqrt(sum((v2[j] - v1[j]) ** 2 for j in range(3))) / ((dt1 + dt2) / 2))
        camD.sort()
        print(json.dumps({ 'page': PAGE, 'fps': FPS, 'frames': len(rows), 'turnDelay_ms': round((start - 2.6) * 1000) if start else None, 'hardTurnRate': round(fin, 2),
          'camLag_deg': { 'mean': round(sum(lag) / len(lag) * 57.3, 1), 'max': round(max(lag) * 57.3, 1) },
          'jitter(med,p95,max)': { 'physYaw': jit(2), 'drawnYaw': jit(3), 'drawnY': jit(4), 'camYaw': jit(8), 'camPos': [round(camD[len(camD) // 2], 1), round(camD[int(len(camD) * 0.95)], 1), round(camD[-1], 1)] } }))
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
