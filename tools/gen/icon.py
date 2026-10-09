import asyncio, json, sys
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
# background burst colors (night purple) and how close the camera sits
A, B, C, ZOOM, T = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]), float(sys.argv[5])
OUT = sys.argv[6]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':1024,'height':1024}, device_scale_factor=1)
        await ctx.add_init_script("Math.random = (()=>{ let s=2468; return ()=>{ s=(s*1664525+1013904223)>>>0; return s/4294967296; }; })(); try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', color: 'red', stage: 'season', look: { eyes: 'round', head: 'hat', mouth: 'fangs' }, seen: {steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000); await pg.wait_for_timeout(400)
        await pg.add_style_tag(content="#stage > :not(canvas){visibility:hidden !important}")
        r = await pg.evaluate("""([A, B, C, ZOOM, TT]) => { const T=__T, P=T.P; window.__noLoop = true; T.start(); T.setWx('clear', 999);
          for (let i=0;i<200;i++) T.step(0.012);
          for (const n of T.NAVo.nodes) if (n.h === 0 && Math.random() < 0.08) T.addSplat(n.x, 0, n.z, 0, 1.2, T.dryClock, false, true, 0);
          for (let k=0;k<3 && T.state==='play';k++) { T.matchLeft = 0.01; for (let i=0;i<60 && T.state==='play';i++) T.step(0.012); }
          T.startVictory(); const v = T.vic; v.cy = 0.5; v.room = 1;
          let t = 0; while (t < TT) { T.visuals(0.016, 0.016); t += 0.016; }
          return [T.state, !!T.vic, +T.vic.t.toFixed(2)]; }""", [A, B, C, ZOOM, T])
        # recolor the burst, pull the camera in, render one clean frame
        await pg.evaluate("""([A, B, C, ZOOM]) => { const T = __T; const s = T.scene; window.__vicTweak = { A, B, C, ZOOM }; }""", [A, B, C, ZOOM])
        await pg.evaluate("""([A, B, C, ZOOM]) => {
          const T = __T, cam = T.vicCam;
          T.vicU.uA.value.set(A); T.vicU.uB.value.set(B); T.vicU.uC.value.set(C); T.vicU.uK.value = 1;
          T.visuals(0.016, 0.016);
          const D = T.vic.feat[0], tgt = new D.constructor === Object ? null : null; const L = { x: D.x, y: D.y + 0.7, z: D.z }; cam.position.set(L.x + (cam.position.x - L.x) * ZOOM, L.y + (cam.position.y - L.y) * ZOOM, L.z + (cam.position.z - L.z) * ZOOM); cam.lookAt(L.x, L.y, L.z); cam.updateMatrixWorld();
          T.renderFrame(); }""", [A, B, C, ZOOM])
        await pg.screenshot(path=OUT)
        print(r, errs[:3]); await b.close()
asyncio.run(main())
