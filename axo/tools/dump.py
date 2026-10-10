import asyncio, json, sys
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width': 300, 'height': 300}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/axo/preview.html?manual', timeout=300000); await pg.wait_for_function('window.ready', timeout=300000)
        r = await pg.evaluate('''async () => { const THREE = await import('/node_modules/three/build/three.module.js'); const P = axo.P, A = axo.A;
          const out = {}; const Y = new THREE.Vector3(), pos = new THREE.Vector3(), e = new THREE.Vector3();
          const poses = [['LS', P.LS], ['proneStand', A.proneStand(new (P.LS.constructor)(P.nb))], ['crouch', A.crouch(new (P.LS.constructor)(P.nb))]];
          for (const [nm, pose] of poses) {
            for (const w of ['stand']) { P.apply(w, pose); P.m[w].mesh.updateMatrixWorld(true); const o = {};
              for (const bn of ['hips', 'tail1', 'tail2', 'tail3', 'tail6']) { const B = P.m[w].byName[bn]; B.getWorldPosition(pos); e.copy(P.m[w].end[P.idx[bn]]).sub(P.m[w].rest[P.idx[bn]]).applyQuaternion(B.getWorldQuaternion(new THREE.Quaternion())); o[bn] = { pos: pos.toArray().map(x => +x.toFixed(2)), dir: e.normalize().toArray().map(x => +x.toFixed(2)) }; }
              out[nm + '/' + w] = o; } }
          return out; }''')
        for k, v in r.items(): print(k); [print('   ', b, x) for b, x in v.items()]
        print(errs); await b.close()
asyncio.run(main())
