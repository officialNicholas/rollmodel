"""Where the axolotl's body sits over the paint trail: runs a match a moment, then prints the head, chest, front hands, hips and hind feet
as distances ahead of the blob's own position (along its heading), and where the trail's newest points are. usage: trailpos.py [page]"""
import asyncio, sys, json
from playwright.async_api import async_playwright
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_h.html'
Q = """(() => { const P = __T.P, I = __T.VP.slime, A = I.ax.A, fx = Math.sin(P.yaw), fz = Math.cos(P.yaw), v = new THREE.Vector3(), out = {};
  I.root.updateWorldMatrix(true, true); const sk = I.ax.mesh ? I.ax.mesh : null;
  let bones = null; I.root.traverse(o => { if (o.isSkinnedMesh && o.visible && !bones) bones = o.skeleton.bones; });
  const ahead = n => { const b = bones && bones.find(b => b.name === n); if (!b) return null; b.getWorldPosition(v); return +(((v.x - P.x) * fx + (v.z - P.z) * fz)).toFixed(3); };
  for (const n of ['head', 'neck', 'chest', 'spine', 'hips', 'hand.L', 'hand.R', 'foot.L', 'foot.R', 'tail3', 'tail6']) out[n] = ahead(n);
  out.spd = +P.spd.toFixed(2); out.state = A.state; return out; })()"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 700}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', mode:'solo', stage:'manor', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1,items:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/' + PAGE, timeout=240000); await pg.wait_for_function('typeof __T === "object" && !!__T.VP && !!__T.VP.slime', timeout=240000, polling=1000)
        await pg.evaluate("__T.start()"); await pg.wait_for_function("__T.state === 'play'", timeout=60000, polling=500); await pg.wait_for_timeout(3000)
        for k in range(3):
            print(json.dumps(await pg.evaluate(Q))); await pg.wait_for_timeout(700)
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
