# does the shadow cache draw exactly what a full shadow pass draws? A match is played, the cache built, the match moved on, then the same
# frame is drawn with the cache and without it and the two pictures compared (pots' pulse tolerance off, then on)
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
GFX = sys.argv[1] if len(sys.argv) > 1 else 'hi'; STAGE = sys.argv[2] if len(sys.argv) > 2 else 'island'; PAGE = sys.argv[3] if len(sys.argv) > 3 else 'pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};')
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: '" + GFX + "', mode: 'trio', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('console', lambda m: errs.append('console: ' + m.text[:200]) if m.type == 'error' or m.type == 'warning' else None)
        await pg.goto(SP + PAGE, timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
        r = await pg.evaluate("""([stage]) => { const T = __T, R = T.renderer, SC = T.shadowCache; window.__noLoop = true;
          Math.random = (() => { let s = 777; return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; })();
          T.mode = 'trio'; T.applyMode(); T.genWorld(4242, { themes: [stage] }); T.mapUsed = false; T.setDiff('hard'); T.start();
          T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
          T.aiReset(T.P); T.setWx('clear', 999); const dt = 1 / 60; let fake = 0; const pn = performance.now.bind(performance); performance.now = () => pn() + fake;
          const run = (n, draw) => { for (let i = 0; i < n && T.state === 'play'; i++) { T.aiStep(T.P, dt); T.steerIn = T.P.steer; T.step(dt); if (draw || i % 20 === 0) { T.visuals(dt, dt); T.flushTrail(); } T.matchLeft = 99; fake += dt * 1000; if (draw && i % 10 === 9) T.renderFrame(); } };
          const gl = R.getContext(), W = R.domElement.width, H = R.domElement.height;
          const grab = () => { T.renderFrame(); R.setRenderTarget(null); const px = new Uint8Array(W * H * 4); gl.readPixels(0, 0, W, H, gl.RGBA, gl.UNSIGNED_BYTE, px); return px; };
          const diff = (a, b) => { let n = 0, mx = 0, sum = 0; for (let i = 0; i < a.length; i += 4) { const d = Math.max(Math.abs(a[i] - b[i]), Math.abs(a[i + 1] - b[i + 1]), Math.abs(a[i + 2] - b[i + 2])); if (d > 2) n++; if (d > mx) mx = d; sum += d; } return { px: n, max: mx, mean: +(sum / (a.length / 4)).toFixed(4) }; };
          const tolOff = () => { T.scene.traverse(o => { if (o.userData.shadowTol) { o.userData._tol = o.userData.shadowTol; delete o.userData.shadowTol; } }); };
          const tolOn = () => { T.scene.traverse(o => { if (o.userData._tol) o.userData.shadowTol = o.userData._tol; }); };
          const out = {};
          run(900, false);
          // exact: no tolerance
          tolOff(); SC.on = true; run(200, true); out.afterWarm = Object.assign({}, SC);
          run(40, true); // keep the cache, things move
          SC.on = true; const a = grab(); out.cacheState = Object.assign({}, SC); SC.on = false; const bb = grab(); SC.on = true; out.exact = diff(a, bb);
          // a cached thing moves: the stage's own shadow mesh nudged, then put back
          const sh = T.stageGroup.children.find(o => o.castShadow && o.userData.shadowStatic); out.hasStageShadow = !!sh;
          if (sh) { sh.position.x += 0.5; sh.updateMatrixWorld(); const c = grab(); SC.on = false; const d = grab(); SC.on = true; out.moved = diff(c, d); out.afterMove = Object.assign({}, SC); sh.position.x -= 0.5; }
          // hidden then shown
          if (sh) { sh.visible = false; const c = grab(); SC.on = false; const d = grab(); SC.on = true; out.hidden = diff(c, d); sh.visible = true; run(2, true); }
          // with the pots' tolerance back on, after a while
          tolOn(); run(200, true); const e = grab(); out.tolState = Object.assign({}, SC); SC.on = false; const f = grab(); SC.on = true; out.tol = diff(e, f);
          const sync = () => { R.setRenderTarget(null); gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, new Uint8Array(4)); };
          const time = () => { T.renderFrame(); sync(); const t0 = pn(); for (let k = 0; k < 4; k++) { T.renderFrame(); } sync(); return Math.round((pn() - t0) / 4); };
          SC.on = true; out.msCache = time(); SC.on = false; out.msFull = time(); SC.on = true; T.sun.castShadow = false; out.msNoShadow = time(); T.sun.castShadow = true;
          return out; }""", [STAGE])
        print(GFX, STAGE, json.dumps(r, indent=1)); print('errors', errs[:6]); await b.close()
asyncio.run(main())
