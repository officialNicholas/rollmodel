"""Shader programs and texture/buffer uploads at each weather and orb transition (sun, rain, orb, giant, rocket), rendering every frame
on a tiny canvas so each phase draws. usage: wxcompile.py <stage>"""
import asyncio, sys, os
from playwright.async_api import async_playwright
STAGE = sys.argv[1]; PAGE = os.environ.get('PAGE', 'pc_perf.html')
UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 90, 'height': 190}, device_scale_factor=1, has_touch=True, is_mobile=True, user_agent=UA)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', stage:'%s', gfx:'%s', seen:{look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1}, drops: 50, runs: 9, flings: 50, tut: { ph: 'done' } })); } catch (e) {}" % (STAGE, os.environ.get('GFX', 'hi')))
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/' + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object"', timeout=300000)
        await pg.evaluate(r"""(() => { const r = __T.renderer, I = r.info, gl = r.getContext(); window.__seen = new Set(); window.__log = []; let ups = 0, upB = 0;
          for (const f of ['texImage2D', 'texSubImage2D', 'texStorage2D']) { const o = gl[f]; if (o) gl[f] = function () { ups++; return o.apply(this, arguments); }; }
          for (const f of ['bufferData']) { const o = gl[f]; gl[f] = function (t, d) { try { upB += (d && d.byteLength) || (typeof d === 'number' ? d : 0); } catch (e) {} return o.apply(this, arguments); }; }
          window.__mark = tag => { const nw = []; for (const p of I.programs || []) if (!__seen.has(p.cacheKey)) { __seen.add(p.cacheKey); let uni = ''; try { const sh = gl.getAttachedShaders(p.program); const src = gl.getShaderSource(sh[1]) || ''; uni = [...new Set((src.match(/uniform\s+\w+\s+(\w+)/g) || []).map(x => x.split(/\s+/).pop()))].slice(0, 8).join(','); } catch (e) {} nw.push((p.name || '?') + ' [' + uni + ']'); } __log.push([tag, nw, ups, Math.round(upB / 1024)]); ups = 0; upB = 0; };
        })()""")
        await pg.evaluate("__T.start()"); await pg.wait_for_function("__T.state === 'play'", timeout=300000)
        await pg.evaluate("window.__perfAI(); __mark('start of play')")
        async def step(tag, js, wait=2500):
            await pg.evaluate(f"__mark('before {tag}')")
            if js: await pg.evaluate(js)
            await pg.wait_for_timeout(wait); await pg.evaluate(f"__mark('{tag}')")
        await step('clear 3s', None, 3000)
        await step('sun', "__T.ev(\"setWx('warn', 0.02)\")", 4000)
        await step('orb in sun', "__T.ev('orbSpawn()')", 3000)
        await step('giant (P takes orb)', "(() => { window.__orbKind = 'giant'; __T.ev('takeOrb(P)'); })()", 3000)
        await step('dusk', "__T.ev(\"setWx('sun', 0.02)\")", 3000)
        await step('rain', "__T.ev(\"setWx('dusk', 0.02)\")", 4000)
        await step('orb in rain', "__T.ev('orbSpawn()')", 3000)
        await step('rocket (P takes orb)', "(() => { window.__orbKind = 'rocket'; __T.ev('takeOrb(P)'); })()", 4000)
        await step('clear again', "__T.ev(\"setWx('rain', 0.02)\")", 3000)
        L = await pg.evaluate("__log")
        print('==', STAGE)
        for tag, nw, ups, kb in L:
            if tag.startswith('before'): 
                if nw or ups > 50: print('   (between steps)', tag, len(nw), nw[:6], 'tex uploads', ups, 'buffer KB', kb)
                continue
            print('%-22s new programs %d %s | texture uploads %d | buffer uploads %d KB' % (tag, len(nw), nw[:8], ups, kb))
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
