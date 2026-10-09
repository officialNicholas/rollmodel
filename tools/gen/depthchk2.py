import asyncio, json
from playwright.async_api import async_playwright
U = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844})
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ gfx: 'hi', seen: {steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page()
        await pg.goto(U, timeout=240000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=100, timeout=240000)
        r = await pg.evaluate("""() => { const T = __T, R = T.renderer; window.__noLoop = true; const log = []; const orig = R.renderBufferDirect.bind(R);
          const cnt = {}; R.renderBufferDirect = (cam, sc, geo, mat, obj, grp) => { const k = window.__pass + ':' + mat.type; cnt[k] = (cnt[k] || 0) + 1; const res = orig(cam, sc, geo, mat, obj, grp); if (mat.type === 'MeshDepthMaterial') { const cp = R.properties.get(mat).currentProgram, t = cp ? String(cp.cacheKey).split(',') : []; const tag = window.__pass + ' ' + (geo.parameters && geo.parameters.width === 0.01 ? 'STAND' : 'other') + ' map=' + !!mat.map + ' L=' + t[34] + t[38] + t[41] + ' t5=' + t[5] + ' t51=' + t[51] + ' ck=' + String(t[54]).slice(0, 14) + ' n=' + t.length; cnt[tag] = (cnt[tag] || 0) + 1; } return res; };
          const hid = []; T.scene.traverse(o => { if (!o.visible) { hid.push(o); o.visible = true; } }); const so = T.shadowCache.on; T.shadowCache.on = false; window.__pass = 1; T.sun.shadow.needsUpdate = true; T.renderFrame(); window.__pass = 2; T.sun.shadow.needsUpdate = true; T.renderFrame(); window.__pass = 3; T.sun.shadow.needsUpdate = true; T.renderFrame(); T.shadowCache.on = so; const after = R.info.programs.map(p => p.cacheKey).filter(k => k.startsWith('depth')).map(k => { const t = k.split(','); return [t[5], t[34], t[38], t[41], t[51], t[54].slice(0, 12)].join('|'); }); window.__after = after; for (const o of hid) o.visible = false;
          R.renderBufferDirect = orig; return { after: window.__after, cnt, log, info: T.shadowCache ? JSON.stringify(T.shadowCache) : null }; }""")
        print(json.dumps(r, indent=0)[:2000]); await b.close()
asyncio.run(main())
