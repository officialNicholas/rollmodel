# how many layers of paint each pixel shades: the paint drawn alone into a float target with additive counting, edges discarded like the
# real shader does, against the scene's depth; also the share of the screen covered
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
STAGE = sys.argv[1] if len(sys.argv) > 1 else 'island'; SECS = float(sys.argv[2]) if len(sys.argv) > 2 else 70; PAGE = sys.argv[3] if len(sys.argv) > 3 else 'pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};')
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'trio', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto(SP + PAGE, timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
        r = await pg.evaluate("""([stage, secs]) => { const T = __T, R = T.renderer; window.__noLoop = true;
          Math.random = (() => { let s = 777; return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; })();
          T.mode = 'trio'; T.applyMode(); T.genWorld(4242, { themes: [stage] }); T.mapUsed = false; T.setDiff('hard'); T.start();
          T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
          T.aiReset(T.P); T.setWx('clear', 999); const dt = 1 / 60, n = Math.round(secs / dt); const out = [];
          const measure = () => { T.visuals(dt, dt); T.flushTrail(); T.renderFrame();
            const W = R.domElement.width, H = R.domElement.height, rt = new THREE.WebGLRenderTarget(W, H, { type: THREE.FloatType, depthBuffer: true });
            const pm = T.paintMesh, mat0 = pm.material, cnt = mat0.clone(); cnt.blending = THREE.AdditiveBlending; cnt.transparent = true; cnt.depthTest = true;
            cnt.fragmentShader = mat0.fragmentShader.replace(/void main\\(\\)\\{[\\s\\S]*$/, 'void main(){ float nz = vnoise(vW.xz * 1.6) * 0.62 + vnoise(vW.xz * 4.1 + 7.3) * 0.38; float lim = 0.78 + 0.18 * nz; if (vEdge > lim) discard; gl_FragColor = vec4(1.0 / 64.0, 0.0, 0.0, 1.0); }');
            cnt.defines = {}; cnt.lights = false; cnt.fog = false; cnt.needsUpdate = true;
            // the scene's depth first (everything but the paint), then the paint counted on top of it
            const vis = []; T.scene.traverse(o => { if (o.isMesh && o !== pm && o.visible) { vis.push(o); } });
            R.setRenderTarget(rt); R.setClearColor(0x000000, 0); R.clear(); const keep = T.scene.background; T.scene.background = null;
            const ac = R.autoClear; R.autoClear = false; pm.visible = false; R.render(T.scene, T.camera); pm.visible = true;
            R.setRenderTarget(rt); R.clearColor(); const hide = []; T.scene.traverse(o => { if ((o.isMesh || o.isLine || o.isPoints || o.isSprite) && o !== pm && o.visible) { hide.push(o); o.visible = false; } });
            pm.material = cnt; R.render(T.scene, T.camera); pm.material = mat0; for (const o of hide) o.visible = true; R.autoClear = ac; T.scene.background = keep;
            const px = new Float32Array(W * H * 4); R.readRenderTargetPixels(rt, 0, 0, W, H, px); rt.dispose(); R.setRenderTarget(null);
            let sum = 0, cov = 0, mx = 0; for (let i = 0; i < W * H; i++) { const v = px[i * 4] * 64; sum += v; if (v > 0.5) cov++; if (v > mx) mx = v; }
            return { paintV: T.chunkN, layersPerPaintedPx: +(sum / Math.max(1, cov)).toFixed(2), paintedScreen: +(cov / (W * H)).toFixed(3), shadedPerScreenPx: +(sum / (W * H)).toFixed(2), max: Math.round(mx) }; };
          for (let i = 0, s = 0; i < n && T.state === 'play'; i++) { T.aiStep(T.P, dt); T.steerIn = T.P.steer; T.step(dt); if (i % 20 === 0) { T.visuals(dt * 20, dt * 20); T.flushTrail(); } T.matchLeft = 99; if (i > 0 && i % 1200 === 0) out.push(measure()); }
          out.push(measure()); return out; }""", [STAGE, SECS])
        for row in r: print(json.dumps(row))
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
