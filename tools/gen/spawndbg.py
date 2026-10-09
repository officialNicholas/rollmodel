# why the spawn guard didn't turn: blank 9074, the path the blob takes out of that basin, and what the guard sees each step
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 200, 'height': 300}, device_scale_factor=1)
        await ctx.add_init_script("window.__skipIntro = false; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'lo', mode: 'solo', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300]))
        await pg.goto('file://' + SP + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(800)
        r = await pg.evaluate("""() => { const T = __T, P = T.P; window.__noLoop = true; T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
          T.mode = 'solo'; T.applyMode(); T.setStage('blank'); T.genWorld(9074, { themes: ['blank'] }); T.mapUsed = false; T.start(); T.setWx('clear', 999);
          let n = 0; while (T.state === "intro" && n++ < 400) { T.steerIn = 0; T.step(1 / 60); T.visuals(1 / 60, 1 / 60); }
          // put it in the basin it used, facing the way it left
          const pot = T.pots.find(q => Math.hypot(q.x + 2.9, q.z - 9.1) < 0.3); if (!pot) return 'no pot';
          if (pot.occ) pot.occ = null; T.enterPot(P, pot); P.spawnImm = true; P.yaw = 6.48 - 6.2832; for (let i = 0; i < 20; i++) T.step(1 / 60); P.yaw = 6.48 - 6.2832; T.jump(P);
          const rows = []; const vA = (a, reach) => { const sx = Math.sin(a), sz = Math.cos(a); for (let d = 0.4; d <= reach + 1e-6; d += 0.4) if (T.surfaceUnder(P.x + sx * d, P.z + sz * d, P.y + 0.32, true) === -Infinity) return +(1 - (d - 0.4) / reach).toFixed(2); return 0; };
          for (let i = 0; i < 100 && P.st !== 'ko'; i++) { T.steerIn = 0; T.step(1 / 60); if (i % 3 === 0) rows.push([i, +P.x.toFixed(2), +P.z.toFixed(2), +P.y.toFixed(2), +P.yaw.toFixed(2), P.air ? 1 : 0, +P.spd.toFixed(2), +(P.spawnGuard || 0).toFixed(2), vA(P.yaw, 2.6 + P.spd * 0.45), +P.turn.toFixed(2)]); }
          // the ground along the heading from the landing
          const g = []; for (let d = 0; d < 6; d += 0.4) g.push(+(T.surfaceUnder(-2.2 + Math.sin(0.2) * d, 12.6 + Math.cos(0.2) * d, 0.32, true)).toFixed(2));
          return { rows, ground: g, st: P.st }; }""")
        print(json.dumps(r)[:3000]); print('errors', errs[:3]); await b.close()
asyncio.run(main())
