import asyncio, json
from playwright.async_api import async_playwright
U = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844})
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ gfx: 'hi', seen: {steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('console', lambda m: m.type in ('error', 'warning') and 'GPU stall' not in m.text and 'swiftshader' not in m.text and errs.append(m.type + ' ' + m.text[:300]))
        await pg.goto(U, timeout=240000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=100, timeout=240000)
        r = await pg.evaluate("""() => { const T = __T, R = T.renderer; window.__noLoop = true; const hid = []; T.scene.traverse(o => { if (!o.visible) { hid.push(o); o.visible = true; } });
          let err = null; T.sun.shadow.needsUpdate = true; try { T.renderFrame(); } catch (e) { err = String(e.stack || e).slice(0, 600); } for (const o of hid) o.visible = false; return { err, programs: R.info.programs.length }; }""")
        print(json.dumps(r, indent=1)); print(errs[:8]); await b.close()
asyncio.run(main())
