# the slime in the game: a match in play (and optionally the customize screen), as screenshots, with any errors
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
GFX = sys.argv[1] if len(sys.argv) > 1 else 'hi'; STAGE = sys.argv[2] if len(sys.argv) > 2 else 'island'; OUT = sys.argv[3] if len(sys.argv) > 3 else 'sl'; WHAT = sys.argv[4] if len(sys.argv) > 4 else 'play'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True, reduced_motion='reduce')
        await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};')
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: '" + GFX + "', mode: 'trio', look: { head: 'hat' }, seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:400])); pg.on('console', lambda m: errs.append(m.type + ' ' + m.text[:300]) if m.type in ('error', 'warning') and 'GPU stall' not in m.text and 'swiftshader' not in m.text.lower() else None)
        await pg.goto('file://' + SP + 'pc_t.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
        info = await pg.evaluate("() => ({ attached: !!(__T.VP && __T.VP.slime), ready: __T.SLIME && __T.SLIME.S.ready, failed: __T.SLIME && __T.SLIME.S.failed })")
        print('slime', info, 'errors so far', errs[:6])
        if WHAT == 'look':
            await pg.evaluate("() => { __T.openLook(); }"); await pg.wait_for_timeout(5000); await pg.screenshot(path=SP + OUT + '_look.png', timeout=120000)
            dbg = await pg.evaluate("() => { const V = __T.VP, I = V.slime, w = new __T.THREE.Vector3(); I.root.getWorldPosition(w); const r = V.root; const c = __T.camera.position; let vis = true; for (let o = I.root; o; o = o.parent) if (!o.visible) { vis = o.type + ':' + (o.name || '') ; break; } return { rootVis: I.root.visible, chainVis: vis, world: [w.x, w.y, w.z].map(v => +v.toFixed(2)), cam: [c.x, c.y, c.z].map(v => +v.toFixed(2)), drop: r.visible, form: I.form, scale: [V.body.scale.x, I.root.scale.x].map(v => +v.toFixed(3)), old: V.oldBlob.visible, lookIntro: __T.lookOpen }; }")
            print('look dbg', dbg)
        else:
            await pg.evaluate("""([stage]) => { const T = __T; T.mode = 'trio'; T.applyMode(); T.genWorld(4242, { themes: [stage] }); T.mapUsed = false; T.setDiff('hard'); T.start(); T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {}; T.aiReset(T.P); T.setWx('clear', 999); window.__aiP = setInterval(() => { if (T.state === 'play') { T.aiStep(T.P, 1/30); T.steerIn = T.P.steer; T.matchLeft = 99; } }, 33); }""", [STAGE])
            await pg.wait_for_timeout(9000); await pg.screenshot(path=SP + OUT + '_play1.png', timeout=120000)
            await pg.wait_for_timeout(5000); await pg.screenshot(path=SP + OUT + '_play2.png', timeout=120000)
            st = await pg.evaluate("() => { const V = __T.VP, I = V.slime; return { vis: I && I.root.visible, form: I && I.form, expr: I && I.st.exprB, old: V.oldBlob && V.oldBlob.visible, state: __T.state }; }")
            print('state', st)
        print('errors', errs[:8]); await b.close()
asyncio.run(main())
