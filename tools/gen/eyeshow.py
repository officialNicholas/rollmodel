# picking an eye color: no hop; the camera moves in on the face and it pulls a funny face
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'es'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', color: 'orange', stage: 'blank', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300])); pg.on('console', lambda m: m.type == 'error' and 'ERR_' not in m.text and errs.append(m.text[:300]))
        await pg.goto('file://' + SP + 'pc_t.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(1500)
        await pg.evaluate("() => { window.__noLoop = true; __T.openLook(); for (let i = 0; i < 200; i++) __T.visuals(1 / 60, 1 / 60); __T.renderFrame(); }")
        await pg.screenshot(path=SP + 'st/%s_before.png' % TAG)
        for kind in range(2):
            await pg.click('#irises .eyec[data-i="%s"]' % ('green' if kind == 0 else 'violet')); rows = []
            for k, t in enumerate([0.3, 0.45, 0.45, 0.45, 0.6]):
                r = await pg.evaluate("(t) => { const T = __T, P = T.P; for (let i = 0; i < Math.round(t * 60); i++) T.visuals(1 / 60, 1 / 60); T.renderFrame(); const I = T.VP.slime; return { y: +P.y.toFixed(2), expr: I.st.exprB, look: I.st.look.map(v => +v.toFixed(2)), camY: +T.camera.position.y.toFixed(2) }; }", t)
                rows.append(r); await pg.screenshot(path=SP + 'st/%s_%d_%d.png' % (TAG, kind, k), clip={'x': 0, 'y': 0, 'width': 390, 'height': 520})
            print(kind, rows)
        print('errors', errs[:4]); await b.close()
asyncio.run(main())
