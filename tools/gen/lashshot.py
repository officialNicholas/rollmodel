# lashes: found (a dot on the button), put on in Customize (it turns to you and flutters them), close-ups through the flutter, the
# scoreboard face; then a CPU wearing them in a match
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'ls'
GFX = sys.argv[2] if len(sys.argv) > 2 else 'hi'
SEEN = "{look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1}"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: '" + GFX + "', mode: 'duel', color: 'pink', stage: 'blank', owned: ['lashes', 'tiara', 'bowtie'], fresh: ['lashes'], seen: " + SEEN + " })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300])); pg.on('console', lambda m: m.type == 'error' and 'ERR_' not in m.text and errs.append(m.text[:300]))
        await pg.goto('file://' + SP + 'pc_t.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(1800)
        r = await pg.evaluate("""() => { const T = __T; window.__noLoop = true; T.openLook(); for (let i = 0; i < 150; i++) T.visuals(1 / 60, 1 / 60); T.renderFrame();
          return { fresh: [...document.querySelectorAll('.lopt.fresh')].map(b => b.dataset.w), look: JSON.stringify(T.myLook) }; }""")
        print('fresh', json.dumps(r)); await pg.screenshot(path=SP + 'st/%s_fresh.png' % TAG)
        await pg.click('#wearBlk .lopt[data-w="lashes"]'); await pg.wait_for_timeout(50)
        r = await pg.evaluate("() => ({ fresh: [...document.querySelectorAll('.lopt.fresh')].map(b => b.dataset.w), storeFresh: __T.store.fresh, look: __T.myLook.lash })"); print('after pick', json.dumps(r))
        # step the scene on through the turn and the flutter (the flutter starts ~0.38 s after the pick, on a timer)
        await pg.evaluate("() => { const T = __T; for (let i = 0; i < 20; i++) T.visuals(1 / 60, 1 / 60); document.getElementById('look').style.visibility = 'hidden'; }"); await pg.wait_for_timeout(420)
        frames = []
        for k in range(8):
            r = await pg.evaluate("""() => { const T = __T, P = T.P, c = T.camera, bd = T.body, p = new T.THREE.Vector3(); for (let i = 0; i < 3; i++) T.visuals(1 / 60, 1 / 60); bd.getWorldPosition(p);
              const s = bd.scale.y, gy = p.y - s * 0.82, a = P.yaw + 0.05, cy = gy + 0.95; c.position.set(p.x + Math.sin(a) * 3.0, cy + 0.2, p.z + Math.cos(a) * 3.0); c.lookAt(p.x, cy, p.z); c.fov = 24; c.updateProjectionMatrix(); T.renderFrame(); c.fov = 40; c.updateProjectionMatrix();
              const U = T.VP.slime.U; return [+U.fMix.value.y.toFixed(2), +U.fLash.value.x.toFixed(2), +U.fLash.value.y.toFixed(2)]; }""")
            frames.append(r); await pg.screenshot(path=SP + 'st/%s_fl%d.png' % (TAG, k), clip={'x': 95, 'y': 322, 'width': 200, 'height': 200})
        print('flutter frames [blink, lashL, lashR]', frames)
        r = await pg.evaluate("() => document.querySelector('.sface') ? 1 : 0"); print('sface', r)
        print('errors', errs[:6]); await ctx.close(); await b.close()
asyncio.run(main())
