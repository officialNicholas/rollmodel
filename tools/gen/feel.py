import asyncio, json, sys
from playwright.async_api import async_playwright
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_t.html'
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/' + PAGE
src = open('gen/v20test.py').read(); HELP = src.split('HELP = r"""')[1].split('"""')[0]
JS = r"""(() => { const T = __T, P = T.P, H = T.H, out = {}, dt = 0.012, cruise = T.cfg.speed;
  T.start(); __flat(); T.setWx('clear', 999); __freezeAI(); H.st = 'ko'; H.koT = 1e9; H.x = 99;
  const fresh = (yaw) => { __place(P, 0, 0, 0, yaw || 0); P.spd = cruise; P.turn = 0; T.steerIn = 0; for (let i = 0; i < 30; i++) T.step(dt); };
  // steering: how fast does a full-lock input turn into turning?
  fresh(0); const y0 = P.yaw; T.steerIn = 1; let t90 = null, maxTurn = 0, h100 = 0, h200 = 0, u180 = null;
  for (let i = 1; i <= 200; i++) { T.step(dt); const t = i * dt; maxTurn = Math.max(maxTurn, Math.abs(P.turn)); if (t90 === null && Math.abs(P.turn) > 0.9 * 3.2) t90 = t; const turned = Math.abs(P.yaw - y0); if (Math.abs(t - 0.1) < dt / 2) h100 = turned; if (Math.abs(t - 0.2) < dt / 2) h200 = turned; if (u180 === null && turned >= Math.PI) u180 = t; }
  out.steer = { t90: t90 && +t90.toFixed(3), deg100ms: +(h100 * 57.3).toFixed(0), deg200ms: +(h200 * 57.3).toFixed(0), uTurn: u180 && +u180.toFixed(2), maxTurn: +maxTurn.toFixed(2), radius: +(P.spd / Math.max(0.01, Math.abs(P.turn))).toFixed(2) };
  // reversal: full left to full right
  T.steerIn = -1; for (let i = 0; i < 40; i++) T.step(dt); T.steerIn = 1; let rev = null; for (let i = 1; i < 100; i++) { T.step(dt); if (rev === null && P.turn > 0.5 * 3.2) rev = i * dt; } out.reverse50 = rev && +rev.toFixed(3); T.steerIn = 0;
  // acceleration from a stop
  fresh(0); P.spd = 0; let a63 = null, a90 = null; for (let i = 1; i < 300; i++) { T.step(dt); if (a63 === null && P.spd > 0.63 * cruise) a63 = i * dt; if (a90 === null && P.spd > 0.9 * cruise) a90 = i * dt; } out.accel = { t63: a63 && +a63.toFixed(2), t90: a90 && +a90.toFixed(2) };
  // braking (hold)
  fresh(0); T.startCharge(P); let b30 = null; for (let i = 1; i < 100; i++) { T.step(dt); if (b30 === null && P.spd < 0.3 * cruise) b30 = i * dt; } out.brake30 = b30 && +b30.toFixed(3); T.flingIt(P, 0); P.charging = false;
  // jump arc
  fresh(0); T.jump(P); let air = 0, apex = 0; for (let i = 1; i < 200 && P.air; i++) { T.step(dt); air = i * dt; apex = Math.max(apex, P.y); } out.jump = { air: +air.toFixed(2), apex: +apex.toFixed(2) };
  // pound: press to impact
  fresh(0); P.slamCD = 0; P.paint = 1; T.useSlam(P); let imp = null; for (let i = 1; i < 200; i++) { T.step(dt); if (imp === null && !P.slam) imp = i * dt; } out.poundImpact = imp && +imp.toFixed(2);
  // full fling: distance and time
  fresh(0); P.paint = 1; T.startCharge(P); for (let i = 0; i < 10; i++) T.step(dt); const x0 = P.x, z0 = P.z; T.flingIt(P, 1); let ft = 0; for (let i = 1; i < 300 && (P.air || i < 3); i++) { T.step(dt); ft = i * dt; } out.fling = { dist: +Math.hypot(P.x - x0, P.z - z0).toFixed(2), time: +ft.toFixed(2), landSpd: +P.spd.toFixed(2) };
  out.cruise = cruise; return out; })()"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U, timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=240000)
        await pg.evaluate("window.__noLoop = true"); await pg.evaluate(HELP)
        r = await pg.evaluate(JS)
        print(PAGE, json.dumps(r, indent=1)); print(errs[:3]); await b.close()
asyncio.run(main())
