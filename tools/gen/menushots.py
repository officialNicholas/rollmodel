# The title screen and the world picker at phone sizes (including the shorter view inside the Claude app's artifact viewer):
# python3 gen/menushots.py TAG
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'm'
SIZES = [(375, 600), (390, 664), (360, 560)]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for w, h in SIZES:
            ctx = await b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2, has_touch=True, is_mobile=True)
            await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ gfx: 'perf', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
            pg = await ctx.new_page(); await pg.goto(SP + 'pc_t.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
            await pg.wait_for_timeout(2500)
            r = await pg.evaluate("""() => { const q = id => { const e = document.getElementById(id); if (!e) return null; const r = e.getBoundingClientRect(); return [r.left | 0, r.top | 0, r.right | 0, r.bottom | 0]; };
              const t = document.querySelector('#logo .tcard'); const tr = t.getBoundingClientRect(); return { name: q('nameBtn'), logo: [tr.left | 0, tr.top | 0, tr.right | 0, tr.bottom | 0] }; }""")
            await pg.screenshot(path=f'st/{TAG}_home_{w}x{h}.png')
            await pg.evaluate("document.getElementById('homePlay').click()")
            await pg.wait_for_timeout(1200)
            r2 = await pg.evaluate("""() => { const g = document.getElementById('stagePick').getBoundingClientRect(), m = document.getElementById('modes').getBoundingClientRect(), rb = [...document.querySelectorAll('#stagePick .ribbon')].map(e => e.getBoundingClientRect()).filter(r => r.right > 0 && r.left < innerWidth).map(r => [r.left | 0, r.top | 0, r.bottom | 0]);
              return { gallery: [g.top | 0, g.bottom | 0], modesBottom: m.bottom | 0, ribbons: rb, worldH: document.querySelector('#stagePick .world').getBoundingClientRect().height | 0 }; }""")
            await pg.screenshot(path=f'st/{TAG}_world_{w}x{h}.png')
            print(w, h, json.dumps(r), json.dumps(r2))
            await ctx.close()
        await b.close()
asyncio.run(main())
