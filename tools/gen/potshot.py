# mid-match refill: diving in, just the eyes on the paint (play camera and close), then leaping out
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'po'
STAGE = sys.argv[2] if len(sys.argv) > 2 else 'island'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 700}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'duel', color: 'green', owned: ['glasses','tiara'], look: { iris: 'blue', eye: 'glasses', head: 'tiara' }, seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300])); pg.on('console', lambda m: m.type == 'error' and 'ERR_' not in m.text and errs.append(m.text[:300]))
        await pg.goto('file://' + SP + 'pc_t.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(1500)
        await pg.evaluate("""(stage) => { const T = __T; window.__noLoop = true; T.mode = 'duel'; T.applyMode(); T.setStage(stage); T.genWorld(3131, { themes: [stage] }); T.mapUsed = false; T.start(); T.setWx('clear', 999);
          T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
          for (let i = 0; i < 90; i++) { T.step(1 / 60); T.visuals(1 / 60, 1 / 60); }
          const P = T.P, pot = T.pots3.find(p => T.potUp(p) && !p.occ) || T.pots3[0]; window.__pot = pot; P.paint = 0.2; T.enterPot2(P, pot); window.__t = 0;
          window.__run = (dt, cam) => { const P = T.P; let n = Math.round(dt * 60); while (n-- > 0) { T.step(1 / 60); T.visuals(1 / 60, 1 / 60); window.__t += 1 / 60; }
            if (cam) { const c = T.camera, p = window.__pot, put = () => { c.position.set(p.x + 1.6, p.y + 1.9, p.z + 1.9); c.lookAt(p.x, p.y + 0.45, p.z); c.updateMatrixWorld(); }; put(); T.visuals(1e-4, 1e-4); put(); T.renderFrame(); } else T.renderFrame();
            const E = P.potEyes; return { t: +window.__t.toFixed(2), tiara: T.VP && 0, wearHid: !!P.wearHid, wearPop: P.wearPop === undefined ? null : +P.wearPop.toFixed(2), st: P.st, eyes: E ? +E.k.toFixed(2) : -1, vis: E ? E.g.visible : false, sink: +(T.VP.sink || 0).toFixed(2), slime: T.VP.slime.root.visible }; }; }""", STAGE)
        rows = []
        for k, (dt, cam) in enumerate([(0.1, True), (0.35, True), (0.6, True), (0.5, False), (0.6, True)]):
            r = await pg.evaluate("([dt, cam]) => window.__run(dt, cam)", [dt, cam]); rows.append(r); await pg.screenshot(path=SP + 'st/%s_%d.png' % (TAG, k))
        r = await pg.evaluate("() => { const T = __T; T.jump(T.P); return window.__run(0.15, true); }"); rows.append(r); await pg.screenshot(path=SP + 'st/%s_5.png' % TAG)
        r = await pg.evaluate("() => window.__run(0.25, true)"); rows.append(r); await pg.screenshot(path=SP + 'st/%s_6.png' % TAG)
        for r in rows: print(json.dumps(r))
        print('errors', errs[:4]); await b.close()
asyncio.run(main())
