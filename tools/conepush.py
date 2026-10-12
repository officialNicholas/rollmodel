"""Roll into a traffic cone in the sewer: the player is set down a few metres from a cone in the open, facing it, and rolls on into it
(the blobs never stop rolling). Shots as it hits and after, from the play camera, with the cone's state printed each time.
usage: conepush.py page tag"""
import asyncio, sys, functools, os
from playwright.async_api import async_playwright
from PIL import Image
print = functools.partial(print, flush=True)
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
PAGE, TAG = sys.argv[1], sys.argv[2]; W, H = 390, 844
FIND = """(() => { const want = '""" + os.environ.get('KIND', '') + """';
  // a cone on the open floor with a clear run-up of 4 m from some side
  for (const c of CONES) { if (c.y > 0.05 || c.st !== 0 || (want && c.k.id !== want)) continue;
    for (let k = 0; k < 16; k++) { const a = k / 16 * 6.2832, fx = Math.sin(a), fz = Math.cos(a); let ok = true;
      for (let d = 0.6; d <= 4.2 && ok; d += 0.3) { const x = c.x - fx * d, z = c.z - fz * d; if (surfaceUnder(x, z, 0.3) !== 0 || solidThrough(x, z, 0.3) || Math.abs(x) > ARENA - 1 || Math.abs(z) > ARENA - 1 || CONES.some(o => o !== c && Math.hypot(o.x - x, o.z - z) < 0.8)) ok = false; }
      if (ok) return [CONES.indexOf(c), c.x, c.z, a]; } }
  return null; })()"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': W, 'height': H}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__noVote = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{ jump: 1, hold: 1, steer: 1, item: 1, orb: 1 }, drops: 0, runs: 5, stage: '" + os.environ.get('SID', 'sewer') + "', mode: 'solo', tut: { ph: 'done', strokes: 1, comms: 1 } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
        await pg.goto('http://localhost:8765/' + PAGE, timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000, polling=100); await pg.wait_for_timeout(1500)
        await ev("__T.mode = 'solo'; __T.applyMode(); __T.start()"); await pg.wait_for_function("__T.state === 'play'", timeout=400000, polling=100)
        await pg.wait_for_timeout(3000)
        f = await ev("__T.ev(`" + FIND + "`)"); print('target', f)
        if not f: print('no clear cone'); await b.close(); return
        i, cx, cz, a = f
        await ev(f"__T.ev(`(() => {{ const a = {a}; P.x = {cx} - Math.sin(a) * 3.2; P.z = {cz} - Math.cos(a) * 3.2; P.yaw = a; P.spd = cfg.speed; }})()`)")
        if os.environ.get('SIDE', '1') == '1':
            await ev(f"(() => {{ const a = {a}, fx = Math.sin(a), fz = Math.cos(a), sx = fz, sz = -fx; window.__cam = [[{cx} + sx * 4.2 - fx * 0.6, 1.9, {cz} + sz * 4.2 - fz * 0.6], [{cx} + fx * 0.9, 0.35, {cz} + fz * 0.9]]; }})()")
        shots = []; st = lambda: ev(f"__T.ev(`(c => [c.k.id, +c.x.toFixed(2), +c.y.toFixed(2), +c.z.toFixed(2), c.st, +c.th.toFixed(2), +c.dir.toFixed(2), c.air])(CONES[{i}])`)")
        for k, ms in enumerate([1200, 1200, 1500, 2500, 4000]):
            await pg.wait_for_timeout(ms); await ev("__T.state = 'paused'"); print(k, 'P', await ev("__T.ev(`[+P.x.toFixed(2), +P.z.toFixed(2), +P.spd.toFixed(2)]`)"), 'cone', await st())
            fn = f'{WS}/ui/cp_{TAG}_{k}.png'; await pg.screenshot(path=fn); shots.append(fn); await ev("__T.state = 'play'")
        print('errors', errs[:4]); await b.close()
    ims = [Image.open(f).convert('RGB') for f in shots]; w, h = ims[0].size; k = 0.5; n = len(ims)
    sh = Image.new('RGB', (int(w * k) * 3, int(h * k) * ((n + 2) // 3)), 'white')
    for j, im in enumerate(ims): sh.paste(im.resize((int(w * k), int(h * k))), ((j % 3) * int(w * k), (j // 3) * int(h * k)))
    sh.save(f'{WS}/ui/cp_{TAG}_sheet.jpg', quality=88); print('sheet', sh.size)
asyncio.run(main())
