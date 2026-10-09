# the results screen after a short 3-way match (stepped by hand to the end, then the real UI)
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
OUT = sys.argv[1] if len(sys.argv) > 1 else 'endscr'; MODE = sys.argv[2] if len(sys.argv) > 2 else 'trio'; W = int(sys.argv[3]) if len(sys.argv) > 3 else 390; H = int(sys.argv[4]) if len(sys.argv) > 4 else 844
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': W, 'height': H}, device_scale_factor=float(__import__("os").environ.get("DPR", "2")), has_touch=True, is_mobile=W < 700)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'lo', mode: '" + MODE + "', look: { head: 'hat' }, seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1} })); } catch (e) {}")
        pg = await ctx.new_page(); KOS = sys.argv[7] if len(sys.argv) > 7 else '3,1,0'; await ctx.add_init_script('window.__kos = [' + KOS + '];' + (('window.__paintFor = ' + sys.argv[8] + ';') if len(sys.argv) > 8 else '')); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300]))
        await pg.goto('file://' + SP + 'pc_t.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000)
        r = await pg.evaluate("""(mode) => { const T = __T; window.__noLoop = true; T.mode = mode; T.applyMode(); T.genWorld(4242, { themes: ['island'] }); T.mapUsed = false; T.setDiff('easy'); T.start();
          T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
          const dt = 1 / 60; T.aiReset(T.P); for (let i = 0; i < 60 * 25 && T.state === 'play'; i++) { T.aiStep(T.P, dt); T.steerIn = T.P.steer; T.step(dt); if (i % 10 === 0) { T.visuals(dt * 10, dt * 10); T.flushTrail(); } T.matchLeft = Math.max(T.matchLeft, 5); }
          if (window.__kills) window.__kills();
          if (window.__paintFor !== undefined) { const D = [T.P, T.H, T.H2][window.__paintFor]; for (let i = 0; i < 16; i++) { const x = D.x + (i % 4 - 1.5) * 3.2, z = D.z + (i / 4 | 0) * 3.2 - 4.8; T.addSplat(x, Math.max(0, T.surfaceUnder(x, z, D.y + 3, true)), z, 0, 3, T.clock, false, true, window.__paintFor); } T.flushTrail(); }
          if (window.__kos) { T.P.kos = window.__kos[0]; T.H.kos = window.__kos[1]; T.H2.kos = window.__kos[2]; } T.matchLeft = 0.01; let n = 0; while (T.state === 'play' && n++ < 2000) { T.step(dt); T.visuals(dt, dt); }
          window.__noLoop = false; return { vic: !!T.vic, state: T.state }; }""", MODE)
        print('to results', r)
        try: await pg.wait_for_function("!document.getElementById('victory').hidden", timeout=60000, polling=200)
        except Exception as e: print('no victory', errs[:5], await pg.evaluate("[__T.state, !!__T.vic, document.getElementById('victory').hidden]")); raise
        await pg.wait_for_timeout(int(sys.argv[5]) if len(sys.argv) > 5 else 2500)
        if len(sys.argv) > 6: await pg.screenshot(path=SP + OUT + '_vic.png', timeout=120000)
        await pg.evaluate("__T.vic && (__T.vic.t = Math.max(__T.vic.t, 1))")
        await pg.tap('#victory')
        await pg.wait_for_function("!document.getElementById('end').hidden", timeout=60000, polling=300)
        await pg.wait_for_timeout(3500)
        await pg.screenshot(path=SP + OUT + '.png', timeout=120000)
        print(await pg.evaluate('''(() => { const r = e => { const b = e.getBoundingClientRect(); return [e.className || e.tagName, Math.round(b.x), Math.round(b.y), Math.round(b.width), Math.round(b.height)]; }; const row = document.querySelector('#board .brow'); const end = document.getElementById('end'); const kos = Array.from(document.querySelectorAll('#board .bko')).map(k => [r(k), Array.from(k.children).map(r), getComputedStyle(k).fontSize, k.outerHTML.slice(0, 300)]); return { kos, end: r(end), scrollH: end.scrollHeight, clientH: end.clientHeight, row: r(row), kids: Array.from(row.children).map(r), cols: getComputedStyle(row).gridTemplateColumns }; })()'''))
        print('errors', errs[:5]); await b.close()
asyncio.run(main())
