# character close-ups for comparing with the reference art: python3 gen/charlook.py TAG [stage]
# renders, per look: the Customize screen as a player sees it (desktop and phone), and a tight hero close-up
import asyncio, sys, json
from playwright.async_api import async_playwright
U = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t2.html'
TAG = sys.argv[1]; STAGE = sys.argv[2] if len(sys.argv) > 2 else 'standard'
LOOKS = [('red', 'round', None, None, None), ('red', 'round', None, 'wings', None), ('orange', 'round', None, None, None), ('purple', 'happy', 'hat', None, None)]
ONLY = [a[5:] for a in sys.argv[3:] if a.startswith('only=')]
if ONLY: LOOKS = [l for l in LOOKS if f'{l[0]}-{l[1]}-{l[2]}-{l[3]}' in ONLY[0].split(',')]
async def settle(pg, n):
    await pg.evaluate(f"(()=>{{ for (let i=0;i<{n};i++) __T.visuals(0.016, 0.05); }})()")
async def run(b, W, H, dsf, mobile, views):
    ctx = await b.new_context(viewport={'width': W, 'height': H}, device_scale_factor=dsf, has_touch=mobile, is_mobile=mobile)
    await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', stage: '" + STAGE + "', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
    pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type == 'error' and 'ERR_' not in m.text and errs.append(m.text[:300]))
    await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=60000); await pg.wait_for_timeout(900)
    await pg.evaluate("window.__noLoop = true"); await settle(pg, 60)
    for col, eyes, head, back, mouth in LOOKS:
        name = f'{col}-{eyes}-{head}-{back}'
        await pg.evaluate("""([col, eyes, head, back, mouth]) => { const T = __T; T.setColor(col); Object.assign(T.myLook, { eyes, head, back, mouth }); if (!T.lookOpen) T.openLook(); T.renderLook(); }""", [col, eyes, head, back, mouth])
        await settle(pg, 150)
        # hold the idle bounce at rest (it stretches and squashes about once a second), so the shape reads as it sits
        await pg.evaluate("(() => { const T = __T; T.clock = 10.176; for (let i = 0; i < 4; i++) T.visuals(0.0005, 0.0005); T.renderFrame(); })()")
        if 'look' in views: await pg.screenshot(path=f'char/{TAG}_{name}_look{W}.png')
        if 'hero' in views:
            # a tight three-quarter close-up, like the reference renders: low camera, long lens, face toward us
            for k, (side, lift, dist) in enumerate([(0.3, 0.3, 2.7), (-0.55, 0.6, 3.0)]):
                sc = await pg.evaluate("""([side, lift, dist]) => { const T = __T, P = T.P, c = T.camera, b = T.body, p = new THREE.Vector3(); b.getWorldPosition(p); const s = b.scale.y, gy = p.y - s * 0.82;
                  const a = P.yaw + side, cy = gy + 0.26; c.position.set(p.x + Math.sin(a) * dist, cy + lift, p.z + Math.cos(a) * dist); c.lookAt(p.x, cy, p.z); c.fov = 30; c.updateProjectionMatrix(); T.renderFrame(); c.fov = 40; c.updateProjectionMatrix(); return [s.toFixed(3), p.y.toFixed(3)]; }""", [side, lift, dist])
                if k == 0: print(name, 'scale', sc)
                await pg.screenshot(path=f'char/{TAG}_{name}_hero{k}.png')
    print(W, H, errs[:4]); await ctx.close()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        await run(b, 1000, 1000, 1, False, ['look', 'hero'])
        if '--phone' in sys.argv: await run(b, 390, 844, 2, True, ['look'])
        await b.close()
asyncio.run(main())
