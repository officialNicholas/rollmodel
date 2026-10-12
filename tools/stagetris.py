"""Where a stage's triangles go: its meshes by triangle count (with what they're drawn with), and the whole stage's total.
usage: stagetris.py page stage1,stage2"""
import asyncio, sys, functools
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
PAGE, STAGES = sys.argv[1], sys.argv[2].split(',')
Q = """__T.ev(`(() => { const out = []; let tot = 0; stageGroup.traverse(o => { if (!o.isMesh || !o.geometry) return; const g = o.geometry, n = (g.index ? g.index.count : g.attributes.position.count) / 3 * (o.isInstancedMesh ? o.count : 1);
  const m = Array.isArray(o.material) ? o.material[0] : o.material; tot += n; out.push([Math.round(n), (m && m.type || '').replace('Mesh', '').replace('Material', ''), m && m.map ? 'map' : '', m && m.vertexColors ? 'vc' : '', m && m.color ? '#' + m.color.getHexString() : '', o.castShadow ? 'cast' : '', o.visible ? '' : 'hidden']); });
  out.sort((a, b) => b[0] - a[0]); return [Math.round(tot), out.length, out.slice(0, 14)]; })()`)"""
async def one(p, sid):
    b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
    ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
    await ctx.add_init_script("window.__noVote = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{ jump: 1, hold: 1, steer: 1, item: 1, orb: 1 }, drops: 0, runs: 5, stage: '" + sid + "', mode: 'duel', tut: { ph: 'done', strokes: 1, comms: 1 } })); } catch (e) {}")
    pg = await ctx.new_page(); ev = pg.evaluate
    await pg.goto('http://localhost:8765/' + PAGE, timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000, polling=100); await pg.wait_for_timeout(1000)
    await ev("__T.mode = 'duel'; __T.applyMode(); __T.start()"); await pg.wait_for_function("__T.state === 'play'", timeout=400000, polling=100); await pg.wait_for_timeout(2000)
    tot, n, top = await ev(Q); print(sid, 'stage tris', tot, 'meshes', n)
    for r in top: print('   ', r)
    await b.close()
async def main():
    async with async_playwright() as p:
        for sid in STAGES: await one(p, sid)
asyncio.run(main())
