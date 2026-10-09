import asyncio, sys, time
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1)
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:400])); pg.on('console', lambda m: errs.append(m.type + ' ' + m.text[:300]))
        t0 = time.time(); await pg.goto('file://' + SP + 'pc_t.html', timeout=240000)
        r = await pg.evaluate("""async () => { const u = window.SLIME_PACK; const out = { has: !!u, len: u ? u.length : 0 }; try { const t = performance.now(); const r = await fetch(u); const b = await r.arrayBuffer(); out.fetch = [r.status, b.byteLength, Math.round(performance.now() - t)]; } catch (e) { out.err = String(e); } return out; }""")
        print('fetch test', r, round(time.time() - t0, 1))
        await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000); print('booted', round(time.time() - t0, 1))
        for i in range(10):
            s = await pg.evaluate("() => ({ ready: __T.SLIME && __T.SLIME.S.ready, failed: __T.SLIME && __T.SLIME.S.failed, geo: __T.SLIME && Object.keys(__T.SLIME.S.geo).length, tex: __T.SLIME && Object.keys(__T.SLIME.S.tex).length, att: !!__T.VP.slime })")
            print(round(time.time() - t0, 1), s)
            if s['ready']: break
            await pg.wait_for_timeout(2000)
        print('errors', [e for e in errs if 'GPU stall' not in e and 'swiftshader' not in e.lower()][:10]); await b.close()
asyncio.run(main())
