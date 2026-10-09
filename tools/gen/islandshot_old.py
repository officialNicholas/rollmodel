# Palette Island: gameplay view, close-ups of a bush, a palm and the sand; then bump a palm's column and roll through a bush
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'isl'
GFX = sys.argv[2] if len(sys.argv) > 2 else 'hi'
SEED = int(sys.argv[3]) if len(sys.argv) > 3 else 5151
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};')
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: '" + GFX + "', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text[:300]))
        await pg.goto(SP + 'pc_old.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
        info = await pg.evaluate("""(seed) => { const T = __T, P = T.P; window.__noLoop = true; T.genWorld(seed, { themes: ['island'] }); T.mapUsed = false; T.start(); T.setWx('clear', 99);
          for (let i = 0; i < 160; i++) { T.step(0.016); T.visuals(0.016, 0.016); } document.getElementById('banner').style.display = 'none'; T.renderFrame();
          return (T.swayItems || []).map(it => [it.kind, +it.x.toFixed(1), +it.z.toFixed(1), +it.r.toFixed(2), +it.y0.toFixed(2)]); }""", SEED)
        print('items', len(info), json.dumps(info)[:600], errs[:3])
        await pg.screenshot(path=f'st/{TAG}_play.png')
        for kind in ['bush', 'palm']:
            ok = await pg.evaluate("""(kind) => { const T = __T, c = T.camera, it = T.swayItems.find(q => q.kind === kind && Math.abs(q.x) < 24 && Math.abs(q.z) < 24); if (!it) return false;
              T.visuals(0.016, 0.016); const d = kind === 'palm' ? 7.5 : 3.0, hgt = kind === 'palm' ? it.y0 + 2.4 : 1.3; c.position.set(it.x + d * 0.7, hgt, it.z + d * 0.7); c.lookAt(it.x, kind === 'palm' ? it.y0 + 1.3 : 0.3, it.z); c.updateMatrixWorld(); T.renderFrame(); return true; }""", kind)
            if ok: await pg.screenshot(path=f'st/{TAG}_{kind}.png')
        await pg.evaluate("""() => { const T = __T, c = T.camera, P = T.P; T.visuals(0.016, 0.016); c.position.set(P.x + 1.2, 1.0, P.z + 1.4); c.lookAt(P.x + 2.4, 0, P.z + 3.0); c.updateMatrixWorld(); T.renderFrame(); }""")
        await pg.screenshot(path=f'st/{TAG}_sand.png')
        r = await pg.evaluate("""() => { const T = __T, P = T.P, out = {}; const pi = T.swayItems.findIndex(q => q.kind === 'palm' && q.r > 0.4), bi = T.swayItems.findIndex(q => q.kind === 'bush');
          const peak = (i, f) => { let m = 0; for (let k = 0; k < 40; k++) { f(k); T.step(0.016); T.visuals(0.016, 0.016); const it = T.swayItems[i]; m = Math.max(m, Math.hypot(it.bx, it.bz)); } return +m.toFixed(3); };
          if (pi >= 0) { const it = T.swayItems[pi]; out.palmBump = peak(pi, k => { if (k < 6) { P.x = it.x - (it.r + 0.5) + k * 0.06; P.z = it.z; P.y = 0; P.yaw = Math.PI / 2; P.spd = 5; P.air = false; } });
            for (let k = 0; k < 240; k++) { T.step(0.016); T.visuals(0.016, 0.016); } out.palmRest = +Math.hypot(it.bx, it.bz).toFixed(3); }
          if (bi >= 0) { const it = T.swayItems[bi]; out.bushRoll = peak(bi, k => { if (k < 8) { P.x = it.x - 0.6 + k * 0.15; P.z = it.z; P.y = it.y0; P.yaw = Math.PI / 2; P.spd = 5; P.air = false; } }); }
          return out; }""")
        print('shake', json.dumps(r), errs[:3])
        await b.close()
asyncio.run(main())
