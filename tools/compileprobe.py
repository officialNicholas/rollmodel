"""A whole match at full speed (rendering only every Nth pass, so the game runs at 60 a second), the AI playing both sides; reports any
shader program built after the match started (a hitch on a phone), with when and which material, and the frame body spikes."""
import asyncio, sys
from playwright.async_api import async_playwright
UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1'
STAGE = sys.argv[1]; SECS = int(sys.argv[2]) if len(sys.argv) > 2 else 100; MODE = sys.argv[3] if len(sys.argv) > 3 else 'duel'; PAGE = sys.argv[4] if len(sys.argv) > 4 else 'pc_perf.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 120, 'height': 260}, device_scale_factor=1, has_touch=True, is_mobile=True, user_agent=UA)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', stage:'%s', seen:{look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1}, drops: 50, runs: 9, flings: 50, tut: { ph: 'done' } })); } catch (e) {}" % STAGE)
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/' + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object"', timeout=300000)
        await pg.evaluate(f"__T.mode = '{MODE}'; __T.applyMode()")
        await pg.evaluate(r"""(() => { const r = __T.renderer, I = r.info; window.__progs = new Set((I.programs || []).map(p => p.cacheKey)); window.__newProgs = []; window.__on = false;
          const r0 = r.render.bind(r); let k = 0; window.__sparse = false; r.render = (s, c) => { if (!__sparse || (++k % 23) === 0) r0(s, c); };
          const chk = () => { if (!__on) for (const p of I.programs || []) __progs.add(p.cacheKey); if (__on) for (const p of I.programs || []) if (!__progs.has(p.cacheKey)) { __progs.add(p.cacheKey); const gl = r.getContext(); let src = ''; try { const sh = gl.getAttachedShaders(p.program); src = gl.getShaderSource(sh[0]) + '\n----FRAG----\n' + gl.getShaderSource(sh[1]); } catch (e) {}
              const uni = [...new Set((src.match(/uniform\s+\w+\s+(\w+)/g) || []).map(x => x.split(/\s+/).pop()))].filter(n => !/^(modelMatrix|modelViewMatrix|projectionMatrix|viewMatrix|normalMatrix|cameraPosition|isOrthographic|toneMappingExposure)$/.test(n));
              const owners = []; __T.scene.traverse(o => { const ms = Array.isArray(o.material) ? o.material : o.material ? [o.material] : []; for (const m of ms) { const pp = r.properties.get(m); if (pp && pp.currentProgram === p) { const path = []; for (let q = o; q && q !== __T.scene; q = q.parent) path.push(q.name || q.type); owners.push(m.type + ' ' + (m.name || '') + ' <' + path.slice(0, 4).join('<') + '> vis ' + o.visible + ' rO ' + o.renderOrder); } } });
              __newProgs.push([+__T.runT.toFixed(2), __T.state, p.name, (p.cacheKey || '').slice(0, 60), uni.slice(0, 14).join(','), owners.slice(0, 3)]); } requestAnimationFrame(chk); }; requestAnimationFrame(chk); })()""")
        await pg.evaluate("__T.start()"); await pg.wait_for_function("__T.state === 'play'", timeout=300000)
        await pg.evaluate("(() => { window.__perfAI(); window.__sparse = true; window.__on = true; __pf.on = true; __pf.fb.length = 0; })()")
        t = 0
        while t < SECS:
            await pg.wait_for_timeout(5000); t += 5
            st = await pg.evaluate("[__T.state, +__T.runT.toFixed(1), __T.matchLeft]")
            if st[0] not in ('play', 'paused') and t > SECS * 0.5: break
        R = await pg.evaluate("({ np: __newProgs, fb: __pf.fb, slow: (__pf.slow || []).slice(-400) })")
        fb = sorted(R['fb']); q = lambda f: fb[min(len(fb) - 1, int(f * len(fb)))] if fb else 0
        print(f'== {STAGE} {MODE}: state {st}, {len(fb)} frames; fb p50 {q(.5):.1f} p99 {q(.99):.1f} p999 {q(.999):.1f} max {fb[-1] if fb else 0:.1f}; over 12 ms {sum(x > 12 for x in fb)}, over 20 ms {sum(x > 20 for x in fb)}')
        print('programs built during play:', len(R['np']))
        for x in R['np'][:30]: print('   ', x)
        sl = sorted(R['slow'], key=lambda x: -x[0])[:10]
        for d, c in sl: print('   %5.1f  %s' % (d, ', '.join('%s %.1f' % kv for kv in sorted(c.items(), key=lambda kv: -kv[1])[:7])))
        print('errors', errs[:3])
        await b.close()
asyncio.run(main())
