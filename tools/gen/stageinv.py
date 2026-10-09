# the stage's meshes by triangles, each matched to the theme material it uses (by its map or color), split shadow-only vs drawn
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_t.html'
GFX = sys.argv[2] if len(sys.argv) > 2 else 'hi'
STAGE = sys.argv[3] if len(sys.argv) > 3 else 'island'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 300, 'height': 500}, device_scale_factor=1)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: '" + GFX + "', mode: 'trio', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300]))
        await pg.goto('file://' + SP + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(1000)
        r = await pg.evaluate("""(stage) => { const T = __T; window.__noLoop = true; T.setStage(stage === 'island' || stage === 'blank' ? stage : 'season'); T.genWorld(2468, { themes: [stage] }); T.mapUsed = false;
          const M = T.themeMats(T.TH), keyOf = m => { for (const k in M) { const v = M[k]; if (!v || !v.isMaterial) continue; if (v === m) return k; if (m.map && v.map === m.map) return k + '(clone)'; } return (m.name || m.type) + (m.color ? '#' + m.color.getHexString() : '') + (m.transparent ? ' T' : ''); };
          const rows = []; let tot = 0, totShadow = 0;
          T.stageGroup.traverse(o => { if (!o.isMesh) return; const g = o.geometry, tri = (g.index ? g.index.count : g.attributes.position.count) / 3 * (o.isInstancedMesh ? o.count : 1);
            const shadowOnly = o.material.colorWrite === false || (o.material.isMeshDepthMaterial) || (!o.visible); const k = keyOf(o.material);
            rows.push([Math.round(tri), k, o.castShadow ? 'cast' : '', o.receiveShadow ? 'recv' : '', o.visible ? '' : 'HIDDEN', o.material.colorWrite === false ? 'NOCOLOR' : '', o.layers.mask]); tot += tri; });
          rows.sort((a, b) => b[0] - a[0]); return { total: Math.round(tot), meshes: rows.length, top: rows.slice(0, 30) }; }""", STAGE)
        print(GFX, STAGE, 'total stage tris', r['total'], 'meshes', r['meshes'])
        for row in r['top']: print('  ', row)
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
