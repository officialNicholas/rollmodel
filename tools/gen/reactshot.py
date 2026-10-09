# the slime's reactions, frame by frame from the side: a jump (push-off, leap, brace, the planted landing, the rock), a shove (the
# tumble, the landing, the shake), running into a wall (the brace, the knock back), a dodge roll (the tuck), a stop and a start.
# Each scenario becomes one contact sheet (rx/<tag>_<name>.png)
import asyncio, sys, json
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'v66'
ONLY = sys.argv[2].split(',') if len(sys.argv) > 2 else None
GFX = sys.argv[3] if len(sys.argv) > 3 else 'hi'
SETUP = r"""(stage) => { const T = __T; window.__noLoop = true; T.mode = window.__mode || 'solo'; T.applyMode(); T.setStage(stage); T.genWorld(88, { themes: [stage] }); T.mapUsed = false; T.start(); T.setWx('clear', 999);
  T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
  for (let i = 0; i < 90; i++) { T.step(1 / 60); T.visuals(1 / 60, 1 / 60); }
  const P = T.P, nodes = T.NAVo.nodes.filter(n => n.h === 0 && n.edge === 0), n0 = nodes.sort((a, b) => Math.hypot(a.x, a.z) - Math.hypot(b.x, b.z))[0]; window.__n0 = n0;
  window.__adv = (dt, f) => { let n = Math.round(dt * 60); while (n-- > 0) { if (f) f(); T.step(1 / 60); T.visuals(1 / 60, 1 / 60); } };
  document.querySelectorAll('#stage > *:not(#cv)').forEach(e => e.style.visibility = 'hidden');
  window.__side = (D, dist, yawOff) => { const c = T.camera; let a = D.yaw + (yawOff === undefined ? Math.PI / 2 : yawOff);
    if (window.__camA === undefined) { const ok = q => T.losClear(D.x, D.y + 0.6, D.z, D.x + Math.sin(q) * dist, D.y + 0.9, D.z + Math.cos(q) * dist); window.__camA = ok(a) ? a : ok(a + Math.PI) ? a + Math.PI : a; }
    a = window.__camA; c.position.set(D.x + Math.sin(a) * dist, D.y + 0.9, D.z + Math.cos(a) * dist); c.lookAt(D.x, D.y + 0.55, D.z); c.fov = 34; c.updateProjectionMatrix(); T.renderFrame(); c.fov = 40; c.updateProjectionMatrix(); };
  window.__info = D => { const V = D === T.P ? T.VP : D.look.V, I = V.slime, s = I.st; return { air: D.air, vy: +D.vy.toFixed(1), y: +D.y.toFixed(2), spd: +D.spd.toFixed(1), slam: D.slam, rx: +V.root.rotation.x.toFixed(2), ry: +(V.root.rotation.y - D.yaw).toFixed(2), brace: +s.brace.toFixed(2), wall: +s.wallK.toFixed(2), splat: +s.splat.toFixed(2), flail: +s.flail.toFixed(2), bp: +s.bp.toFixed(2), br: +s.br.toFixed(2), push: +s.pushK.toFixed(2), ball: +s.ball.toFixed(2), expr: s.exprB }; };
  return n0; }"""
SCEN = {
  # a jump from a roll: frames from take-off to after the landing
  'jump': ("blank", r"""() => { const T = __T, P = T.P, n0 = window.__n0; for (let i = 0; i < 40; i++) { T.steerIn = 0; P.x = n0.x; P.z = n0.z; P.yaw = 0; P.y = 0; P.air = false; P.spd = T.cfg.speed; T.step(1 / 60); P.x = n0.x; P.z = n0.z; T.visuals(1 / 60, 1 / 60); } T.jump(P); window.__t = 0; }""",
           [0.03, 0.05, 0.1, 0.12, 0.12, 0.1, 0.06, 0.04, 0.03, 0.05, 0.08, 0.1, 0.15], "() => { const T = __T, P = T.P; window.__side(P, window.__camD || 4.2); return window.__info(P); }", "() => { __T.steerIn = 0; __T.P.yaw = 0; }"),
  # rammed by a flung rival: sent flying, a flip, the landing, the shake
  'tumble': ("blank", r"""() => { const T = __T, P = T.P, H = T.H, n0 = window.__n0; for (let i = 0; i < 20; i++) { T.steerIn = 0; P.x = n0.x; P.z = n0.z; P.yaw = 0; P.y = 0; P.air = false; P.spd = 0; T.step(1 / 60); T.visuals(1 / 60, 1 / 60); }
            H.st = 'play'; H.x = P.x; H.z = P.z - 0.8; H.y = 0; H.yaw = 0; H.spd = 11; H.flung = true; H.air = false; T.shove(H, P); P.yaw = 0; window.__yaw0 = P.yaw; }""",
           [0.02, 0.06, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08, 0.06, 0.06, 0.08, 0.1, 0.12, 0.15], "() => { const T = __T, P = T.P; window.__side(P, window.__camD || 4.6); return window.__info(P); }", "() => { __T.steerIn = 0; }"),
  'pound': ("blank", r"""() => { const T = __T, P = T.P, n0 = window.__n0; for (let i = 0; i < 40; i++) { T.steerIn = 0; P.x = n0.x; P.z = n0.z; P.yaw = 0; P.y = 0; P.air = false; P.spd = T.cfg.speed * 0.5; T.step(1 / 60); P.x = n0.x; P.z = n0.z; T.visuals(1 / 60, 1 / 60); } P.slamCD = 0; P.paint = 1; T.useSlam(P); }""",
           [0.04, 0.08, 0.08, 0.08, 0.08, 0.06, 0.05, 0.04, 0.04, 0.06, 0.08, 0.12], "() => { const T = __T, P = T.P; window.__side(P, window.__camD || 4.2); return window.__info(P); }", "() => { __T.steerIn = 0; }"),
  'slamhit': ("blank", r"""() => { const T = __T, P = T.P, H = T.H, n0 = window.__n0; for (let i = 0; i < 20; i++) { T.steerIn = 0; P.x = n0.x; P.z = n0.z; P.yaw = 0; P.y = 0; P.air = false; P.spd = 0; H.x = P.x + 10.5; H.z = P.z; H.spd = 0; T.step(1 / 60); T.visuals(1 / 60, 1 / 60); }
            H.st = 'play'; H.x = P.x + 10.5; H.z = P.z; H.y = 1.2; H.yaw = 0; H.spd = 0; H.air = true; H.slam = true; H.slamHang = 0; H.vy = -20; H.slamT = 0.5; H.giantT = 3; H.paint = 1; H.immuneT = 0; P.immuneT = 0; P.spd = 0; window.__holdP = true; }""",
           [0.03, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.08, 0.08, 0.1, 0.12], "() => { const T = __T, P = T.P; window.__side(P, window.__camD || 5.0, 0); return window.__info(P); }", "() => { __T.steerIn = 0; if (!__T.P.air && __T.P.spd > 0 && window.__k2 === undefined) {} }"),
  # a dodge roll from a full roll
  'roll': ("blank", r"""() => { const T = __T, P = T.P, n0 = window.__n0; for (let i = 0; i < 40; i++) { T.steerIn = 0; P.x = n0.x; P.z = n0.z; P.yaw = 0; P.y = 0; P.air = false; P.spd = T.cfg.speed; T.step(1 / 60); P.x = n0.x; P.z = n0.z; T.visuals(1 / 60, 1 / 60); } P.rollCD = 0; T.dodgeRoll(P); }""",
           [0.02, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.06, 0.08, 0.1, 0.15], "() => { const T = __T, P = T.P; window.__side(P, window.__camD || 4.2); return window.__info(P); }", "() => { __T.steerIn = 0; __T.P.yaw = 0; }"),
  # stop (hold to brake) then set off again
  'stopgo': ("blank", r"""() => { const T = __T, P = T.P, n0 = window.__n0; for (let i = 0; i < 40; i++) { T.steerIn = 0; P.x = n0.x; P.z = n0.z; P.yaw = 0; P.y = 0; P.air = false; P.spd = T.cfg.speed; T.step(1 / 60); P.x = n0.x; P.z = n0.z; T.visuals(1 / 60, 1 / 60); } T.startCharge(P); window.__k = 0; }""",
           [0.05, 0.08, 0.08, 0.1, 0.12, 0.2, 0.05, 0.06, 0.08, 0.1, 0.12], "() => { const T = __T, P = T.P; if (++window.__k === 6) { T.P.charging = false; T.P.charge = 0; } window.__side(P, window.__camD || 4.2); return window.__info(P); }", "() => { __T.steerIn = 0; __T.P.yaw = 0; }"),
}
WALL = ("blank", r"""() => { const T = __T, P = T.P; let best = null;
  for (const b of T.BOXES) { if (b[5] < 0.8 || b[4] > 0.05) continue; const w = b[1] - b[0], d = b[3] - b[2]; if (w < 1.5 || d < 0.6) continue; const cx = (b[0] + b[1]) / 2, z = b[2] - 2.6; if (T.surfaceUnder(cx, z, 0.5) !== 0 || T.blockedAt(cx, z, 0) || T.surfaceUnder(cx, z - 2, 0.5) !== 0) continue; best = [cx, z, b]; break; }
  if (!best) return 'nobox'; window.__wall = best;
  for (let i = 0; i < 30; i++) { T.steerIn = 0; P.x = best[0]; P.z = best[1] - 1.5; P.yaw = 0; P.y = 0; P.air = false; P.spd = T.cfg.speed; T.step(1 / 60); P.x = best[0]; P.z = best[1] - 1.5; T.visuals(1 / 60, 1 / 60); } return 'ok'; }""",
  [0.1, 0.06, 0.05, 0.04, 0.03, 0.03, 0.04, 0.06, 0.08, 0.1, 0.12], "() => { const T = __T, P = T.P; window.__side(P, window.__camD || 4.2, Math.PI / 2); return window.__info(P); }", "() => { __T.steerIn = 0; }")
SCEN['wall'] = WALL
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        VW = int(sys.argv[4]) if len(sys.argv) > 4 else 300
        ctx = await b.new_context(viewport={'width': VW, 'height': VW}, device_scale_factor=1)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: '" + GFX + "', mode: 'solo', color: 'red', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300])); pg.on('console', lambda m: m.type == 'error' and 'ERR_' not in m.text and errs.append(m.text[:300]))
        await pg.goto('file://' + SP + 'pc_t.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(1200)
        for name, (stage, setup, steps, shot, per) in SCEN.items():
            if ONLY and name not in ONLY: continue
            await pg.evaluate('(m) => { window.__mode = m; }', 'duel' if name == 'slamhit' else 'solo'); await pg.evaluate(SETUP, stage); await pg.evaluate('(d) => { window.__camA = undefined; window.__camD = d; }', float(sys.argv[5]) if len(sys.argv) > 5 else 0); r0 = await pg.evaluate(setup)
            if r0 == 'nobox': print(name, 'no box found'); continue
            frames, rows = [], []
            for k, dt in enumerate(steps):
                await pg.evaluate("([dt, f]) => window.__adv(dt, f ? eval(f) : null)", [dt, per])
                info = await pg.evaluate(shot); rows.append(info)
                fn = SP + 'rx/_f%d.png' % k; await pg.screenshot(path=fn); frames.append(fn)
            # contact sheet
            ims = [Image.open(f) for f in frames]; cols = 6; rws = (len(ims) + cols - 1) // cols; W, H = ims[0].size
            sheet = Image.new('RGB', (cols * W, rws * H), (20, 20, 20)); dr = ImageDraw.Draw(sheet); t = 0
            for i, im in enumerate(ims):
                t += steps[i]; x, y = (i % cols) * W, (i // cols) * H; sheet.paste(im, (x, y)); dr.text((x + 4, y + 4), '%.2fs %s' % (t, rows[i].get('expr', '')), fill=(255, 255, 255))
            sheet.save(SP + 'rx/%s_%s.png' % (TAG, name)); print(name, 'saved')
            for i, r in enumerate(rows): print(' ', i, json.dumps(r))
        print('errors', errs[:4]); await b.close()
asyncio.run(main())
