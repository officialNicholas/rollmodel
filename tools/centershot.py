"""The sewer's middle and its cones, close: the drain grate from a few angles, a cone up close, and cones knocked over (a pound's blast,
and the player rolled into one). Prints what the stage holds: the cones and their states, the steam sources and puffs alive.
usage: centershot.py page tag"""
import asyncio, sys, functools, os
from playwright.async_api import async_playwright
from PIL import Image
print = functools.partial(print, flush=True)
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
PAGE, TAG = sys.argv[1], sys.argv[2]; SID = os.environ.get('SID', 'sewer'); W, H = 390, 844
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': W, 'height': H}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__noVote = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{ jump: 1, hold: 1, steer: 1, item: 1, orb: 1 }, drops: 0, runs: 5, stage: '" + SID + "', mode: 'duel', tut: { ph: 'done', strokes: 1, comms: 1 } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
        await pg.goto('http://localhost:8765/' + PAGE, timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000, polling=100); await pg.wait_for_timeout(1500)
        await ev("__T.mode = 'duel'; __T.applyMode(); __T.start()"); await pg.wait_for_function("__T.state === 'play'", timeout=400000, polling=100)
        await pg.wait_for_timeout(int(os.environ.get('SETTLE', 25000)))
        info = await ev("__T.ev(`[TH.id, CONES.length, CONES.map(c => [+c.x.toFixed(1), +c.y.toFixed(2), +c.z.toFixed(1), c.st]).slice(0, 14), STEAM_SRC.length, STEAM_P.filter(q => q.on).length, stmIM.visible, KN.cone.im && KN.cone.im.count, KN.barrel.n, KN.crate.n]`)")
        print('info', info)
        shots = []
        async def shot(name, pos, look):
            await ev(f"__T.dPos.set({pos[0]}, {pos[1]}, {pos[2]}); __T.dLook.set({look[0]}, {look[1]}, {look[2]}); __T.camSnap = true")
            await pg.wait_for_timeout(1500); f = f'{WS}/ui/cs_{TAG}_{name}.png'; await pg.screenshot(path=f); shots.append(f)
        await ev("__T.state = 'paused'; document.getElementById('hud').classList.add('off')")
        await shot('drain', (7.5, 6.0, 7.5), (0, 1.0, 0)); await shot('drainTop', (0.5, 9.5, 3.5), (0, 1.2, 0))
        c0 = await ev("__T.ev(`(() => { const c = CONES.find(q => q.y < 0.1) || CONES[0]; return c ? [c.x, c.y, c.z] : null; })()`)")
        print('cone0', c0)
        if c0:
            x, y, z = c0
            await shot('cone', (x + 0.9, y + 2.6, z + 2.1), (x, y + 0.2, z))
            # a pound right beside it, then let time run and look again as they fly and land
            await ev(f"__T.ev(`coneBlast({x - 1.2}, {y}, {z - 0.6}, 2.2)`); __T.state = 'play'")
            await pg.wait_for_timeout(500); await ev("__T.state = 'paused'"); await shot('blast1', (x + 1.2, y + 4.2, z + 3.6), (x, y + 0.4, z))
            await ev("__T.state = 'play'"); await pg.wait_for_timeout(5000); await ev("__T.state = 'paused'")
            st = await ev("__T.ev(`CONES.map(c => [+c.x.toFixed(2), +c.y.toFixed(2), +c.z.toFixed(2), c.st, +c.th.toFixed(2), c.live])`)"); print('after blast', st)
            await shot('blast2', (x + 1.2, y + 5.0, z + 4.4), (x, y + 0.2, z))
        print('errors', errs[:4]); await b.close()
    ims = [Image.open(f).convert('RGB') for f in shots]; w, h = ims[0].size; k = 0.5; n = len(ims)
    sh = Image.new('RGB', (int(w * k) * 3, int(h * k) * ((n + 2) // 3)), 'white')
    for i, im in enumerate(ims): sh.paste(im.resize((int(w * k), int(h * k))), ((i % 3) * int(w * k), (i // 3) * int(h * k)))
    sh.save(f'{WS}/ui/cs_{TAG}_sheet.jpg', quality=88); print('sheet', sh.size)
asyncio.run(main())
