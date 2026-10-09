# Palette Island's palms up close from the angles play sees them: behind and above (the play camera), level with the crown, from under
# it, from the far side; plus the play view near one
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'pm'
GFX = sys.argv[2] if len(sys.argv) > 2 else 'hi'
PAGE = sys.argv[3] if len(sys.argv) > 3 else 'pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: '" + GFX + "', mode: 'duel', stage: 'island', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300])); pg.on('console', lambda m: m.type in ('error', 'warning') and 'GPU stall' not in m.text and errs.append(m.text[:300]))
        await pg.goto('file://' + SP + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(1500)
        r = await pg.evaluate("""() => { const T = __T; window.__noLoop = true; T.mode = 'duel'; T.applyMode(); T.setStage('island'); T.genWorld(4242, { themes: ['island'] }); T.mapUsed = false; T.start(); T.setWx('clear', 999);
          T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
          for (let i = 0; i < 60; i++) { T.step(1 / 60); T.visuals(1 / 60, 1 / 60); }
          const it = T.swayItems; const palms = []; const S = T.stageGroup; let n = 0; S.traverse(o => { if (o.isMesh && o.material && o.material.alphaTest > 0) n++; });
          return { sway: it.length, sample: it.slice(0, 3).map(s => Object.keys(s).join(',')), alphaMeshes: n }; }""")
        print(json.dumps(r))
        r = await pg.evaluate("() => { const it = __T.swayItems; return it.map(s => [s.kind, +s.x.toFixed(1), +s.z.toFixed(1), +(s.h || 0).toFixed(1), +(s.y0 || 0).toFixed(1)]); }"); print('items', json.dumps(r))
        palms = [x for x in r if 'palm' in str(x[0])] or r
        # shake one hard (as a blob slamming into its column would) and watch it ring down
        pl = palms[4]
        for k, wait in enumerate([0.05, 0.12, 0.2, 0.35, 0.6]):
            await pg.evaluate('''([x, z, h, y0, w, first]) => { const T = __T, c = T.camera, it = T.swayItems.reduce((a, s) => Math.hypot(s.x - x, s.z - z) < Math.hypot(a.x - x, a.z - z) ? s : a);
              if (first) { it.vx += 2.6; it.vz += 1.2; } for (let i = 0; i < Math.round(w * 60); i++) { T.step(1 / 60); T.visuals(1 / 60, 1 / 60); }
              c.position.set(x + 1.5, y0 + 8.5, z - 6.5); c.lookAt(x, y0 + h * 0.6, z); c.updateMatrixWorld(); T.renderFrame(); }''', [pl[1], pl[2], pl[3], pl[4], wait, k == 0])
            await pg.screenshot(path=SP + 'st/%s_shake%d.png' % (TAG, k))
        views = [('play', 'pv'), ('level', 'lv'), ('under', 'un'), ('far', 'fa'), ('top', 'tp')]
        for i, pl in enumerate(palms[:2]):
            for name, short in views:
                await pg.evaluate('''([x, z, h, name]) => { const T = __T, c = T.camera, H = Math.max(h, 4);
                  const V = { play: [[x - 1.2, 7.75, z - 5.65 - 2], [x, 0, z + 1.5]], level: [[x + 5.5, H * 0.95, z + 1.5], [x, H * 0.92, z]], under: [[x + 1.6, 1.2, z + 1.2], [x, H, z]], far: [[x - 5, H * 1.1, z + 5], [x, H * 0.85, z]], top: [[x + 0.5, H + 6, z - 3], [x, H * 0.8, z]] }[name];
                  c.position.set(...V[0]); c.lookAt(...V[1]); c.updateMatrixWorld(); T.sun.shadow.needsUpdate = true; T.renderFrame(); }''', [pl[1], pl[2], pl[3], name])
                await pg.screenshot(path=SP + 'st/%s_%d_%s.png' % (TAG, i, short))
        print('errors', errs[:6]); await b.close()
asyncio.run(main())
