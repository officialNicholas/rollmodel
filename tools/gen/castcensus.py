# who draws into the shadow map in a paint-heavy match: each caster's triangles, where it hangs and whether it moved over a second
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
STAGE = sys.argv[1] if len(sys.argv) > 1 else 'island'; PAGE = sys.argv[2] if len(sys.argv) > 2 else 'pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};')
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'trio', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto(SP + PAGE, timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
        r = await pg.evaluate("""([stage]) => { const T = __T, R = T.renderer; window.__noLoop = true;
          Math.random = (() => { let s = 777; return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; })();
          T.mode = 'trio'; T.applyMode(); T.genWorld(4242, { themes: [stage] }); T.mapUsed = false; T.setDiff('hard'); T.start();
          T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
          T.aiReset(T.P); T.setWx('clear', 999); const dt = 1 / 60;
          for (let i = 0; i < 600 && T.state === 'play'; i++) { T.aiStep(T.P, dt); T.steerIn = T.P.steer; T.step(dt); T.visuals(dt, dt); T.matchLeft = 99; }
          T.scene.updateMatrixWorld(true);
          const list = []; const walk = (o, path) => { if (!o.visible) return; const p2 = path + '/' + (o.name || o.type); if (o.isMesh && o.castShadow) list.push({ o, path: p2, m: o.matrixWorld.elements.slice() }); for (const c of o.children) walk(c, p2); }; walk(T.scene, '');
          for (let i = 0; i < 60 && T.state === 'play'; i++) { T.aiStep(T.P, dt); T.steerIn = T.P.steer; T.step(dt); T.visuals(dt, dt); T.matchLeft = 99; }
          T.scene.updateMatrixWorld(true);
          return list.map(({ o, path, m }) => { const g = o.geometry, n = (g.index ? g.index.count : g.attributes.position.count) / 3; let mv = 0; const e = o.matrixWorld.elements; for (let i = 0; i < 16; i++) mv = Math.max(mv, Math.abs(e[i] - m[i])); return [path.slice(-70), Math.round(n), o.material.type, +mv.toFixed(4), o.parent && o.parent.visible]; }).sort((a, b) => b[1] - a[1]); }""", [STAGE])
        tot = 0
        for row in r: print(row); tot += row[1]
        print('total', tot, 'n', len(r)); print('errors', errs[:3]); await b.close()
asyncio.run(main())
