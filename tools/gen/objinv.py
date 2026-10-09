# triangles per top-level thing in the scene outside the stage (stations, rivals, balls, blobs...), mid-match
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_t.html'
STAGE = sys.argv[2] if len(sys.argv) > 2 else 'island'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 300, 'height': 500}, device_scale_factor=1)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'trio', seen: {look:1} })); } catch (e) {}")
        pg = await ctx.new_page(); await pg.goto('file://' + SP + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000)
        r = await pg.evaluate("""(stage) => { const T = __T; window.__noLoop = true; T.mode = 'trio'; T.applyMode(); T.setStage(stage === 'island' || stage === 'blank' ? stage : 'season'); T.genWorld(2468, { themes: [stage] }); T.mapUsed = false; T.start();
          for (let i = 0; i < 30; i++) { T.step(1 / 60); T.visuals(1 / 60, 1 / 60); }
          const tri = o => { let n = 0; o.traverse(m => { if (!m.isMesh || !m.visible) return; let v = true, q = m; while (q) { if (!q.visible) { v = false; break; } q = q.parent; } if (!v) return; const g = m.geometry; n += (g.index ? g.index.count : g.attributes.position.count) / 3 * (m.isInstancedMesh ? m.count : 1); }); return Math.round(n); };
          const rows = T.scene.children.filter(o => o !== T.stageGroup && o.visible).map(o => { let kind = o.type; const pot = T.pots3.find(p => p.g === o); if (pot) kind = 'pot:' + pot.kind; return [tri(o), kind, o.children.length]; }).filter(r => r[0] > 300).sort((a, b) => b[0] - a[0]);
          const sum = {}; for (const r of rows) sum[r[1]] = (sum[r[1]] || 0) + r[0];
          return { sum, top: rows.slice(0, 12) }; }""", STAGE)
        print(STAGE, json.dumps(r)); await b.close()
asyncio.run(main())
