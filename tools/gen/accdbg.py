import asyncio, json
from playwright.async_api import async_playwright
U = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width': 390, 'height': 844}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('console', lambda m: errs.append(m.type + ' ' + m.text[:200]))
        await pg.goto(U, timeout=240000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=100, timeout=240000)
        r = await pg.evaluate("""() => { const T = __T; window.__noLoop = true; Object.assign(T.myLook, { head: 'pirate', eye: 'patch', neck: 'bowtie', side: 'flower' }); T.openLook(); for (let i = 0; i < 160; i++) T.visuals(0.016, 0.05);
          const found = []; T.scene.traverse(o => { if (o.isMesh && o.material && o.material.map && o.material.map.image && o.material.map.image.src && o.material.map.image.src.startsWith('data:image/jpeg')) { let vis = true, q = o; while (q) { if (!q.visible) { vis = false; break; } q = q.parent; } const p = new T.THREE.Vector3(); o.getWorldPosition(p); const s = new T.THREE.Vector3(); o.getWorldScale(s); const chain = []; { let q2 = o; while (q2) { chain.push((q2.type || '?')[0] + (q2.visible ? '1' : '0') + (q2 === T.body ? 'B' : '') + '[' + q2.children.length + (q2.userData.gin ? 'g' : '') + (q2.userData.lod ? 'L' : '') + ']'); q2 = q2.parent; } } found.push({ chain: chain.join('>'), vis, pos: [p.x, p.y, p.z].map(v => +v.toFixed(2)), ws: +s.x.toFixed(3), op: o.material.opacity, tr: o.material.transparent, parentIsBody: o.parent && o.parent.parent && o.parent.parent.parent === T.body }); } });
          const bp = new T.THREE.Vector3(); T.body.getWorldPosition(bp); return { found, bp: [bp.x, bp.y, bp.z].map(v => +v.toFixed(2)) };
          const out = {}; const b = T.body; for (const ch of b.children) { if (!ch.isGroup && !ch.isMesh) continue; }
          // find the groups by walking the body's children and reporting visible ones with their world position and scale
          const list = []; b.children.forEach((c, i) => { const p = new T.THREE.Vector3(); c.getWorldPosition(p); let n = 0; c.traverse(o => { if (o.isMesh) n++; }); list.push({ i, type: c.type, vis: c.visible, meshes: n, sc: [c.scale.x, c.scale.y, c.scale.z].map(v => +v.toFixed(3)), pos: [p.x, p.y, p.z].map(v => +v.toFixed(2)) }); });
          return { look: T.myLook, list: list.filter(x => x.meshes > 0) }; }""")
        print('body', r['bp']); [print(json.dumps(f)) for f in r['found']]; print(errs[:10]); await b.close()
asyncio.run(main())
