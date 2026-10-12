# fragment cost in the lab: 4 characters filling a phone-sized view, each frame forced to finish (gl.finish + a 1x1 readPixels) so the
# rasterizer's work is inside the timing; SwiftShader runs it on the CPU, so the ms are not a phone's, but old vs new compare.
# usage: perf2.py <lab url> [frames] [coat level]
import asyncio, sys, statistics
from playwright.async_api import async_playwright
URL = sys.argv[1]; N = int(sys.argv[2]) if len(sys.argv) > 2 else 40; COAT = float(sys.argv[3]) if len(sys.argv) > 3 else 0
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width': 430, 'height': 754}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto(URL, timeout=120000); await pg.wait_for_function('window.LAB && LAB.ready', timeout=120000)
        await pg.evaluate("""(() => { window.__X = []; for (let i = 0; i < 3; i++) { const I = AXOC.make({ color: [0x2f8cff, 0x3bd16f, 0xffb300][i] }); const r = new THREE.Group(); r.add(I.root); r.position.set(-0.9 + i * 0.9, 0.34 * 0.82, -0.9); r.scale.setScalar(0.34); scene.add(r); I.noGhost = true; __X.push(I); }
          LAB.set('walk', { v: 4 }); LAB.cam = 'fixed'; LAB.camPos = [1.6, 1.3, 2.2]; LAB.camAt = [0, 0.3, -0.3]; LAB.step(30); for (const I of [LAB.I, ...__X]) { I.ax.coat = COAT; I.ax.wet = 1; } })()""".replace('COAT', str(COAT)))
        await pg.wait_for_timeout(2500)
        r = await pg.evaluate("""(() => { const gl = renderer.getContext(), px = new Uint8Array(4), t = []; const o0 = () => ({ dt: 1 / 60, spd: 0.6, lean: 0, inAir: false, vy: 0, height: 0, grav: 15, pos: [0, 0, 0], yaw: 0, speed: 4, rad: 0.34, squash: 0, rise: 0, glance: 0, watch: null, blob: 0, blobSt: 0, curl: 0, brace: 0, D: { st: 'play', spd: 4 }, climb: null });
          for (let i = 0; i < NNN; i++) { LAB.step(1); for (const I of __X) AXOC.update(I, o0()); const a = performance.now(); LAB.render(); gl.finish(); gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px); t.push(performance.now() - a); }
          let cov = 0; const W = gl.drawingBufferWidth, H = gl.drawingBufferHeight, buf = new Uint8Array(W * H * 4); gl.readPixels(0, 0, W, H, gl.RGBA, gl.UNSIGNED_BYTE, buf);
          return { t, calls: renderer.info.render.calls, tris: renderer.info.render.triangles, W, H }; })()""".replace('NNN', str(N)))
        v = sorted(r['t'][5:]); q = lambda f: v[min(len(v) - 1, int(f * len(v)))]
        print(f'  render+finish ms: p50 {q(.5):7.1f}  p90 {q(.9):7.1f}  mean {statistics.mean(v):7.1f}   (draw calls {r["calls"]}, tris {r["tris"]}, {r["W"]}x{r["H"]}) errors {errs[:2]}')
        await pg.screenshot(path=URL.split('/')[-2] + '_perf.png'); await b.close()
asyncio.run(main())
