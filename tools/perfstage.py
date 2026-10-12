"""What each stage costs to draw: a few seconds into a match on each stage given, the renderer's draw calls and triangles for one
frame, and the stage's own counts (meshes, props, steam). usage: perfstage.py page stage1,stage2,..."""
import asyncio, sys, functools
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
PAGE, STAGES = sys.argv[1], sys.argv[2].split(',')
async def one(p, sid):
    b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
    ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
    await ctx.add_init_script("window.__noVote = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{ jump: 1, hold: 1, steer: 1, item: 1, orb: 1 }, drops: 0, runs: 5, stage: '" + sid + "', mode: 'duel', tut: { ph: 'done', strokes: 1, comms: 1 } })); } catch (e) {}")
    pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); ev = pg.evaluate
    await pg.goto('http://localhost:8765/' + PAGE, timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000, polling=100); await pg.wait_for_timeout(1000)
    await ev("__T.mode = 'duel'; __T.applyMode(); __T.start()"); await pg.wait_for_function("__T.state === 'play'", timeout=400000, polling=100); await pg.wait_for_timeout(5000)
    r = await ev("""__T.ev(`(() => { const ri = renderer.info; ri.autoReset = false; ri.reset(); return new Promise(res => requestAnimationFrame(() => requestAnimationFrame(() => { const o = { calls: ri.render.calls, tris: ri.render.triangles, geos: ri.memory.geometries, tex: ri.memory.textures, progs: ri.programs.length, stageMeshes: stageGroup.children.length, props: CONES.length, steamSrc: STEAM_SRC.length }; ri.autoReset = true; res(o); }))); })()`)""")
    print(sid, r, 'errors', errs[:2]); await b.close()
async def main():
    async with async_playwright() as p:
        for sid in STAGES: await one(p, sid)
asyncio.run(main())
