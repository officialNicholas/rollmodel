# the locked accessories: Customize with nothing found yet (and a tap on a locked one), the unlock code, then a match on the island with an
# item due: it turns up, you grab it, and after the winner screen the full-screen "new item" moment, then Try it on
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'ul'
GFX = sys.argv[2] if len(sys.argv) > 2 else 'hi'
STAGE = sys.argv[3] if len(sys.argv) > 3 else "island"
SEEN = "{look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1}"
async def boot(b, extra):
    ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, has_touch=True, is_mobile=True)
    await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify(Object.assign({ name: 'Nick', gfx: '" + GFX + "', mode: 'duel', seen: " + SEEN + " }, " + extra + "))); } catch (e) {}")
    pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300])); pg.on('console', lambda m: m.type == 'error' and 'ERR_' not in m.text and errs.append(m.text[:300]))
    await pg.goto('file://' + SP + 'pc_t.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(500)
    return ctx, pg, errs
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        # ---- A: Customize, nothing found yet ----
        ctx, pg, errs = await boot(b, '{}')
        r = await pg.evaluate("""() => { const T = __T; window.__noLoop = true; T.openLook(); for (let i = 0; i < 90; i++) T.visuals(1 / 60, 1 / 60); T.renderFrame();
          return { owned: [...T.OWNED], itemIn: T.store.itemIn, locked: document.querySelectorAll('.ltile.locked').length, open: document.querySelectorAll('.ltile[data-w]:not(.locked)').length, look: JSON.stringify(T.myLook) }; }""")
        print('A', json.dumps(r))
        await pg.evaluate("() => { const el = document.querySelector('#look .lpanel') || document.getElementById('look'); const s = [...document.querySelectorAll('#look *')].find(e => e.scrollHeight > e.clientHeight + 20 && getComputedStyle(e).overflowY !== 'visible'); if (s) s.scrollTop = s.scrollHeight; }")
        await pg.wait_for_timeout(300); await pg.screenshot(path=SP + 'st/%s_locked.png' % TAG)
        await pg.click('#lookRail .ltile[data-w="pirate"]', force=True); await pg.wait_for_timeout(450)
        r = await pg.evaluate("() => ({ note: document.getElementById('lookNote').textContent, on: document.getElementById('lookNote').classList.contains('on'), head: __T.myLook.head })")
        print('tap locked', json.dumps(r)); await pg.screenshot(path=SP + 'st/%s_tap.png' % TAG)
        await pg.click('#unlockLink'); await pg.wait_for_timeout(200); await pg.fill('#unlockCode', '9999'); await pg.click('#unlockForm .ugo'); await pg.wait_for_timeout(300)
        r = await pg.evaluate("() => ({ note: document.getElementById('lookNote').textContent, owned: __T.OWNED.size })"); print('bad code', json.dumps(r))
        await pg.fill('#unlockCode', '1234'); await pg.screenshot(path=SP + 'st/%s_code.png' % TAG); await pg.click('#unlockForm .ugo'); await pg.wait_for_timeout(400)
        r = await pg.evaluate("() => ({ note: document.getElementById('lookNote').textContent, owned: __T.OWNED.size, locked: document.querySelectorAll('.ltile.locked').length, saved: JSON.parse(localStorage.getItem('paint-world-red.v1')).owned })")
        print('code 1234', json.dumps(r)); await pg.screenshot(path=SP + 'st/%s_unlocked.png' % TAG)
        await pg.click('#lookRail .ltile[data-w="tiara"]'); await pg.wait_for_timeout(200)
        await pg.evaluate("() => { const T = __T; for (let i = 0; i < 140; i++) T.visuals(1 / 60, 1 / 60); T.renderFrame(); }")
        r = await pg.evaluate("() => JSON.stringify(__T.myLook)"); print('tiara on', r)
        await pg.evaluate("() => { const s = [...document.querySelectorAll('#look *')].find(e => e.scrollHeight > e.clientHeight + 20 && getComputedStyle(e).overflowY !== 'visible'); if (s) s.scrollTop = 0; }")
        await pg.wait_for_timeout(200); await pg.screenshot(path=SP + 'st/%s_tiara.png' % TAG)
        print('errors A', errs[:6]); await ctx.close()
        # ---- B: a match with an item due ----
        ctx, pg, errs = await boot(b, "{ itemIn: 0, stage: '" + STAGE + "' }")
        r = await pg.evaluate("""(stage) => { const T = __T; window.__noLoop = true; T.mode = 'duel'; T.applyMode(); T.setStage(stage); T.genWorld(41, { themes: [stage] }); T.mapUsed = false; T.setDiff('easy'); T.start(); T.setWx('clear', 999);
          T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
          const g = T.gift; return { state: T.state, id: g.id, at: +g.at.toFixed(1), itemIn: T.store.itemIn }; }""", STAGE)
        print('B plan', json.dumps(r))
        r = await pg.evaluate("""() => { const T = __T, g = T.gift; g.at = 1; let n = 0; while (!g.on && n < 600) { T.aiStep(T.P, 1 / 60); T.steerIn = T.P.steer; T.step(1 / 60); n++; } for (let i = 0; i < 40; i++) { T.aiStep(T.P, 1 / 60); T.steerIn = T.P.steer; T.step(1 / 60); T.visuals(1 / 60, 1 / 60); }
          T.renderFrame(); const gp = document.getElementById('giftPtr'); return { on: g.on, x: +g.x.toFixed(1), z: +g.z.toFixed(1), steps: n, ptr: gp.classList.contains('on'), edge: gp.classList.contains('edge'), banner: document.getElementById('bannerBig').textContent, pd: +Math.hypot(T.P.x - g.x, T.P.z - g.z).toFixed(1) }; }""")
        print('B spawned', json.dumps(r)); await pg.screenshot(path=SP + 'st/%s_game.png' % TAG)
        await pg.evaluate("""() => { const T = __T, g = T.gift, c = T.camera; c.position.set(g.x + 3.4, 2.6, g.z + 3.4); c.lookAt(g.x, 0.9, g.z); c.updateMatrixWorld(); T.renderFrame(); }""")
        await pg.screenshot(path=SP + 'st/%s_giftclose.png' % TAG)
        # grab it (a CPU sitting on it first: it shouldn't count)
        r = await pg.evaluate("""() => { const T = __T, g = T.gift, H = T.H; H.x = g.x; H.z = g.z; H.y = 0; H.spd = 0; for (let i = 0; i < 10; i++) T.step(1 / 60); const cpuGot = g.got;
          H.x = g.x + 6; const P = T.P; P.x = g.x - 0.5; P.z = g.z; P.y = 0; P.air = false; for (let i = 0; i < 6; i++) T.step(1 / 60); for (let i = 0; i < 10; i++) T.visuals(1 / 60, 1 / 60); T.renderFrame();
          return { cpuGot, got: g.got, newItem: T.newItem, owned: [...T.OWNED], itemIn: T.store.itemIn, banner: document.getElementById('bannerBig').textContent + ' / ' + document.getElementById('bannerSmall').textContent }; }""")
        print('B grab', json.dumps(r)); await pg.screenshot(path=SP + 'st/%s_grab.png' % TAG)
        # the end of the match, the winner screen, then the new item
        r = await pg.evaluate("() => { const T = __T; for (let k = 0; k < 4 && T.state === 'play'; k++) { T.matchLeft = 0.01; for (let i = 0; i < 3; i++) T.step(1 / 60); } return T.state; }"); print("ended", r)
        await pg.wait_for_timeout(1700)
        r = await pg.evaluate("() => { const T = __T; for (let i = 0; i < 80; i++) T.visuals(1 / 60, 1 / 60); return { state: T.state, vic: !!T.vic, vt: T.vic ? +T.vic.t.toFixed(2) : -1 }; }"); print('B vic', json.dumps(r))
        await pg.evaluate("() => { __T.renderFrame(); }"); await pg.screenshot(path=SP + 'st/%s_vic.png' % TAG)
        await pg.evaluate("() => __T.endVictory()"); await pg.wait_for_timeout(700)
        await pg.screenshot(path=SP + 'st/%s_ni0.png' % TAG); await pg.wait_for_timeout(2200)
        r = await pg.evaluate("() => ({ shown: !document.getElementById('newItem').hidden, name: document.getElementById('niName').textContent, where: document.getElementById('niWhere').textContent, end: !document.getElementById('end').hidden })")
        print('B newitem', json.dumps(r)); await pg.screenshot(path=SP + 'st/%s_newitem.png' % TAG)
        await pg.click('#niTry'); await pg.wait_for_timeout(700)
        r = await pg.evaluate("() => { const T = __T; for (let i = 0; i < 120; i++) T.visuals(1 / 60, 1 / 60); T.renderFrame(); return { state: T.state, lookOpen: T.lookOpen, look: JSON.stringify(T.myLook), ni: document.getElementById('newItem').hidden, menu: !document.getElementById('menu').hidden }; }")
        print('B try', json.dumps(r)); await pg.screenshot(path=SP + 'st/%s_try.png' % TAG)
        print('errors B', errs[:6]); await ctx.close()
        await b.close()
asyncio.run(main())
