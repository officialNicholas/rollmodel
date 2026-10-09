# the accessories on the slime in Customize: a look per set, the screen as the player sees it, plus close-ups from the front and both sides
import asyncio, sys, json
from playwright.async_api import async_playwright
U = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
TAG = sys.argv[1]; GFX = sys.argv[2] if len(sys.argv) > 2 else 'hi'
LOOKS = json.loads(sys.argv[3]) if len(sys.argv) > 3 else [['red', {'head': 'pirate', 'eye': 'patch'}], ['purple', {'head': 'tophat', 'neck': 'bowtie'}], ['pink', {'side': 'flower', 'neck': 'bowtie'}], ['green', {'head': 'hat'}], ['gold', {'head': 'tophat', 'side': 'flower'}]]
async def settle(pg, n): await pg.evaluate(f"(()=>{{ for (let i=0;i<{n};i++) __T.visuals(0.016, 0.05); }})()")
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: '" + GFX + "', stage: 'island', owned: ['pirate','patch','flower','tophat','bowtie','tiara','lashes','glasses','hat','halo','fangs'], seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('console', lambda m: m.type == 'error' and 'ERR_' not in m.text and errs.append(m.text[:300]))
        await pg.goto(U, timeout=240000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=100, timeout=240000); await pg.wait_for_timeout(600)
        await pg.evaluate("window.__noLoop = true"); await settle(pg, 30)
        for col, look in LOOKS:
            name = col + '-' + '-'.join(v for v in look.values())
            await pg.evaluate("""([col, look]) => { const T = __T; T.setColor(col); Object.assign(T.myLook, { head: null, back: null, mouth: null, eye: null, side: null, neck: null, lash: null, iris: 'brown' }, look); if (!T.lookOpen) T.openLook(); T.renderLook(); }""", [col, look])
            await settle(pg, 140)
            await pg.evaluate("(() => { const T = __T; T.clock = 10.176; for (let i = 0; i < 4; i++) T.visuals(0.0005, 0.0005); T.renderFrame(); })()")
            await pg.screenshot(path=SP + f'acc/{TAG}_{name}_look.png')
            for k, (side, lift, dist) in enumerate([(0.25, 0.6, 6.2), (-1.25, 0.65, 6.2), (1.3, 0.65, 6.2), (3.0, 1.6, 6.4)]):
                await pg.evaluate("""([side, lift, dist]) => { const T = __T, P = T.P, c = T.camera, b = T.body, p = new THREE.Vector3(); b.getWorldPosition(p); const s = b.scale.y, gy = p.y - s * 0.82;
                  const a = P.yaw + side, cy = gy + 0.62; c.position.set(p.x + Math.sin(a) * dist, cy + lift, p.z + Math.cos(a) * dist); c.lookAt(p.x, cy, p.z); c.fov = 30; c.updateProjectionMatrix(); T.renderFrame(); c.fov = 40; c.updateProjectionMatrix(); }""", [side, lift, dist])
                await pg.screenshot(path=SP + f'acc/{TAG}_{name}_c{k}.png', clip={'x': 20, 'y': 60, 'width': 350, 'height': 600})
        print('errors', errs[:6]); await b.close()
asyncio.run(main())
