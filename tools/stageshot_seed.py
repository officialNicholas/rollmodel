"""(fixed layout: env SEED builds that one before the match) A stage, looked at: the play view a few seconds into a match, then frozen and shot from set angles (high overview, low across the
floor, out at the edge looking back, the reveal's angle). usage: stageshot.py page stageId tag [mode]"""
import asyncio, sys, functools, os
from playwright.async_api import async_playwright
from PIL import Image
print = functools.partial(print, flush=True)
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
PAGE, SID, TAG = sys.argv[1], sys.argv[2], sys.argv[3]; MODE = sys.argv[4] if len(sys.argv) > 4 else 'duel'
W, H = (int(os.environ.get('W', 390)), int(os.environ.get('H', 844)))
VIEWS = {  # name: camera position and look-at, in units of ARENA (A) where marked
  'over': "[0.0, A * 1.15, A * 1.25], [0, 0, -A * 0.1]",
  'low': "[A * 0.55, 3.2, A * 0.75], [-A * 0.1, 0.5, -A * 0.2]",
  'edge': "[A * 1.1, 4.5, A * 0.2], [A * 0.3, 1.0, -A * 0.25]",
  'back': "[-A * 0.2, 6.0, -A * 0.45], [A * 0.3, 2.0, A * 1.4]",
  'reveal': "[Math.sin(0.9) * A * 1.4, A * 0.85, Math.cos(0.9) * A * 1.4], [0, 1.5, 0]",
}
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': W, 'height': H}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__noVote = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'" + ('land' if W > H else 'port') + "', name:'Dusk', seen:{ jump: 1, hold: 1, steer: 1, item: 1, orb: 1 }, drops: 0, runs: 5, stage: '" + SID + "', mode: '" + MODE + "', tut: { ph: 'done', strokes: 1, comms: 1 } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
        await pg.goto('http://localhost:8765/' + PAGE, timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000, polling=100); await pg.wait_for_timeout(1500)
        print('stage', await ev("[__T.stageSelV, __T.TH && __T.TH.id]"))
        await ev(f"__T.mode = '{MODE}'; __T.applyMode()")
        if os.environ.get('SEED'): await ev(f"__T.ev('genWorld({int(os.environ['SEED'])}, {{ themes: stageThemes() }}); mapUsed = false; warmRender();')")
        await ev("__T.start()"); await pg.wait_for_function("__T.state === 'play'", timeout=400000, polling=100)
        print('theme', await ev("[__T.TH.id, __T.GENv.arch, __T.GENv.sym, __T.ARENA]"))
        await pg.wait_for_timeout(int(os.environ.get('PLAYMS', 6000))); await pg.screenshot(path=f'{WS}/ui/st_{TAG}_play.png')
        await ev("__T.state = 'paused'; document.getElementById('hud').classList.add('off')")
        for name, cam in VIEWS.items():
            await ev(f"(() => {{ const A = __T.ARENA, c = [{cam}]; __T.dPos.set(...c[0]); __T.dLook.set(...c[1]); __T.camSnap = true; }})()")
            await pg.wait_for_timeout(1400); await pg.screenshot(path=f'{WS}/ui/st_{TAG}_{name}.png')
        print('errors', errs[:3]); await b.close()
    names = ['play'] + list(VIEWS)
    ims = [Image.open(f'{WS}/ui/st_{TAG}_{n}.png').convert('RGB') for n in names]; w, h = ims[0].size; k = 0.5
    sh = Image.new('RGB', (int(w * k) * 3, int(h * k) * 2), 'white')
    for i, im in enumerate(ims): sh.paste(im.resize((int(w * k), int(h * k))), ((i % 3) * int(w * k), (i // 3) * int(h * k)))
    sh.save(f'{WS}/ui/st_{TAG}_sheet.jpg', quality=88); print('sheet', sh.size)
asyncio.run(main())
