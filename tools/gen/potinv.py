import asyncio, sys, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
STAGE = sys.argv[1] if len(sys.argv) > 1 else 'island'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 300, 'height': 500}, device_scale_factor=1)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'trio', seen: {look:1} })); } catch (e) {}")
        pg = await ctx.new_page(); await pg.goto('file://' + SP + 'pc_t.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000)
        r = await pg.evaluate("""(stage) => { const T = __T; window.__noLoop = true; T.setStage(stage === 'island' || stage === 'blank' ? stage : 'season'); T.genWorld(2468, { themes: [stage] }); T.mapUsed = false; T.start();
          const p = T.pots3[0], rows = []; p.g.traverse(m => { if (!m.isMesh) return; const g = m.geometry, n = (g.index ? g.index.count : g.attributes.position.count) / 3; let path = []; let q = m; while (q && q !== p.g) { path.push(q.name || q.type); q = q.parent; }
            const key = (m.material.customProgramCacheKey ? String(m.material.customProgramCacheKey()).slice(0, 14) : m.material.type) + (m.material.color ? '#' + m.material.color.getHexString() : '');
            rows.push([Math.round(n), key, m.visible ? '' : 'hidden', m.castShadow ? 'cast' : '', path.length, Object.keys(g.attributes).join(',')]); });
          rows.sort((a, b) => b[0] - a[0]); for (const k of Object.keys(p)) {} return { kind: p.kind, keys: Object.keys(p).filter(k => p[k] && p[k].isMesh).join(','), rows: rows.slice(0, 16) }; }""", STAGE)
        print(STAGE, r['kind'], r['keys']); [print('  ', x) for x in r['rows']]; await b.close()
asyncio.run(main())
