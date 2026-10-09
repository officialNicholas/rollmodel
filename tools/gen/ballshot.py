# the beach balls: where they start, then the AI driving you about for a while (they get knocked around), a pound right by one
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'bb'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'duel', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300])); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text[:300]))
        await pg.goto('file://' + SP + 'pc_t.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000)
        r = await pg.evaluate("""() => { const T = __T; window.__noLoop = true; T.mode = 'duel'; T.applyMode(); T.setStage('island'); T.genWorld(77, { themes: ['island'] }); T.mapUsed = false; T.setDiff('easy'); T.start(); T.setWx('clear', 999);
          T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
          for (let i = 0; i < 30; i++) { T.step(1 / 60); T.visuals(1 / 60, 1 / 60); }
          const bl = T.balls; window.__look = (i) => { const bb = bl[i], c = T.camera; c.position.set(bb.x + 3.2, bb.y + 2.4, bb.z + 3.2); c.lookAt(bb.x, bb.y, bb.z); c.updateMatrixWorld(); T.renderFrame(); };
          return bl.map(b => ({ on: b.on, x: +b.x.toFixed(2), y: +b.y.toFixed(2), z: +b.z.toFixed(2) })); }""")
        print('balls', json.dumps(r))
        await pg.evaluate("() => window.__look(0)"); await pg.screenshot(path=SP + 'st/%s_start.png' % TAG)
        # drive the player straight at ball 0 and look
        r = await pg.evaluate("""() => { const T = __T, P = T.P, b = T.balls[0]; P.x = b.x - 3; P.z = b.z; P.y = 0; P.yaw = Math.PI / 2; P.spd = 6; P.air = false;
          for (let i = 0; i < 40; i++) { T.steerIn = 0; P.spd = Math.max(P.spd, 6); T.step(1 / 60); T.visuals(1 / 60, 1 / 60); } return { b: [b.x, b.y, b.z, b.vx, b.vz].map(v => +v.toFixed(2)) }; }""")
        print('after push', json.dumps(r)); await pg.evaluate("() => window.__look(0)"); await pg.screenshot(path=SP + 'st/%s_push.png' % TAG)
        r = await pg.evaluate("""() => { const T = __T, b = T.balls[1]; T.shockwaveTest && 0; for (let i = 0; i < 1; i++) {} const before = [b.x, b.z]; T.H.x = b.x + 1.2; T.H.z = b.z; T.H.y = 0;
          T.ballBlast(b.x + 1.2, 0, b.z, 2.4); for (let i = 0; i < 20; i++) { T.step(1 / 60); T.visuals(1 / 60, 1 / 60); } return { moved: +Math.hypot(b.x - before[0], b.z - before[1]).toFixed(2), y: +b.y.toFixed(2) }; }""")
        print('after blast', json.dumps(r)); await pg.evaluate("() => window.__look(1)"); await pg.screenshot(path=SP + 'st/%s_blast.png' % TAG)
        r = await pg.evaluate("""() => { const T = __T; for (let i = 0; i < 600; i++) { T.aiStep(T.P, 1 / 60); T.steerIn = T.P.steer; T.step(1 / 60); if (i % 10 == 0) T.visuals(1 / 6, 1 / 6); T.matchLeft = 99; } return T.balls.map(b => ({ on: b.on, out: +b.out.toFixed(2), x: +b.x.toFixed(1), y: +b.y.toFixed(2), z: +b.z.toFixed(1) })); }""")
        print('after 10s', json.dumps(r)); await pg.evaluate("() => { const T = __T; T.visuals(1/60, 1/60); window.__look(0); }"); await pg.screenshot(path=SP + 'st/%s_later.png' % TAG)
        print('errors', errs[:5]); await b.close()
asyncio.run(main())
