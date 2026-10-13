import asyncio, json, sys
PAGE = sys.argv[1]
sys.argv = ['x', PAGE, 'none', 'dbg']
exec(open('tools/anim252.py').read().split("SCN = {")[0])
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx, pg, errs = await boot(b, SAVE)
        await pg.evaluate("document.getElementById('lookBtn').click()")
        await pg.wait_for_function("__T.ev('!!lookIntro')", timeout=30000, polling=20); await pg.evaluate("window.__tscale = 1e-9")
        await pg.evaluate("__adv(1/30, 18)")
        print(await pg.evaluate("""__T.ev(`(() => { const L = lookIntro, I = VP.slime, X = I.ax, v = new THREE.Vector3(), out = {};
          for (const n of ['head', 'hips', 'tail6']) { X.P.jointWorld('crawl', n, v); out[n] = v.toArray().map(x => +x.toFixed(2)); const q = v.clone().applyMatrix4(L.cl.inv); out[n + '_pool'] = q.toArray().map(x => +x.toFixed(2)); out[n + '_fn'] = +L.cl.fn(q.x, q.z).toFixed(3); }
          const par = I.root.parent; par.updateWorldMatrix(true, false); const wq = new THREE.Quaternion(); par.getWorldQuaternion(wq); const e = new THREE.Euler().setFromQuaternion(wq, 'YXZ');
          return JSON.stringify({ t: L.t, P: [P.x, P.z], yawDraw: VP.yawDraw, parYaw: e.y, back: L.back, rootPos: I.root.position.toArray(), out, poolPos: dipPool.position.toArray() }); })()`)"""))
        for i in range(0):
            print(await pg.evaluate("""__T.ev(`(() => { const L = lookIntro; if (!L) return 'done'; const I = VP.slime, A = I.ax.A, lo = A.loco, tb = lo && lo.tb, M = A.motion;
              const tr = M.terrain ? [M.terrain(0, -0.777), M.terrain(0, 0.33)].map(v => +v.toFixed(3)) : null;
              return JSON.stringify({ t: +L.t.toFixed(2), back: L.back && +L.back.toFixed(2), D: L.cl && +L.cl.D.toFixed(2), vis: I.root.visible, rootPos: I.root.position.toArray().map(v => +v.toFixed(2)), climb: !!I.ax.A.motion.terrain, tr, tbh: tb && +tb.h.toFixed(3), a1: tb && +tb.a1.toFixed(2), sink: VP.sink && +VP.sink.toFixed(2), coat: VP.coatSt }); })()`)"""))
            await pg.evaluate("__adv(1/30, 6)")
        print(errs[:3]); await b.close()
asyncio.run(main())
