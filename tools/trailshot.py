"""The paint stream under the axolotl: a match a few seconds in, from the play camera and from overhead (following it). Two builds side by
side. usage: trailshot.py pageA pageB tag"""
import asyncio, sys
from playwright.async_api import async_playwright
from PIL import Image
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
A, B, TAG = sys.argv[1], sys.argv[2], sys.argv[3]
async def run(b, page, tag):
    ctx = await b.new_context(viewport={'width': 360, 'height': 640}, device_scale_factor=1, has_touch=True)
    await ctx.add_init_script("window.__noVote = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{}, drops: 0, runs: 5, mode: 'solo', tut: { ph: 'done' } })); } catch (e) {}")
    pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
    await pg.goto('http://localhost:8765/' + page, timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000, polling=100); await pg.wait_for_timeout(1500)
    await ev("__T.mode = 'solo'; __T.applyMode(); __T.start()"); await pg.wait_for_function("__T.state === 'play'", timeout=400000, polling=100)
    await pg.wait_for_function('__T.P.spd > 4 && !__T.P.air', timeout=120000, polling=100); await pg.wait_for_timeout(2600); out = [f'{WS}/ui/trl_{TAG}_{tag}_play.png']; await pg.screenshot(path=out[0])
    for k in range(2):
        await ev("window.__camRel = [[0.01, 3.4, 0.0], [0, 0, 0]]"); await pg.wait_for_timeout(700)
        fn = f'{WS}/ui/trl_{TAG}_{tag}_top{k}.png'; await pg.screenshot(path=fn); out.append(fn)
    print(page, 'errors', errs[:3]); await ctx.close(); return out
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        fa = await run(b, A, 'a'); fb = await run(b, B, 'b'); await b.close()
    ims = [Image.open(f) for f in fa + fb]; w, h = ims[0].size; sh = Image.new('RGB', (w * 3, h * 2), 'white')
    for i, im in enumerate(ims): sh.paste(im, ((i % 3) * w, (i // 3) * h))
    sh.save(f'{WS}/ui/trl_{TAG}.png')
asyncio.run(main())
