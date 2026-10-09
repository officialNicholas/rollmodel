import asyncio, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 300, 'height': 500}, device_scale_factor=1)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', seen: {look:1} })); } catch (e) {}")
        pg = await ctx.new_page(); await pg.goto('file://' + SP + 'pc_t.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000)
        r = await pg.evaluate("""() => { const T = __T; window.__noLoop = true; T.setStage('island'); T.genWorld(2468, { themes: ['island'] }); const M = T.themeMats(T.TH), out = [];
          T.stageGroup.traverse(o => { if (!o.isMesh) return; const m = o.material; if (!(m === M.canopy || (m.map && M.canopy && m.map === M.canopy.map) || m === M.rock || m === M.trim || m === M.foot || m === M.rope)) return;
            const g = o.geometry; g.computeBoundingBox(); const bb = g.boundingBox; out.push({ k: m === M.canopy ? 'canopy' : m.map === M.canopy.map ? 'canopyS' : m === M.rock ? 'rock' : m === M.trim ? 'trim' : m === M.foot ? 'foot' : 'rope', tris: (g.index ? g.index.count : g.attributes.position.count) / 3, verts: g.attributes.position.count, min: [bb.min.x, bb.min.y, bb.min.z].map(v => +v.toFixed(1)), max: [bb.max.x, bb.max.y, bb.max.z].map(v => +v.toFixed(1)) }); });
          return { sway: T.swayItems.length, bushes: T.swayItems.filter(s => s.kind === 'bush').length, out }; }""")
        print(json.dumps(r, indent=0)[:3000]); await b.close()
asyncio.run(main())
