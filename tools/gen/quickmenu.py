import asyncio, json, sys
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
W, H, TAG = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
STAGE = sys.argv[4] if len(sys.argv) > 4 else 'season'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        mobile = W < 700
        ctx = await b.new_context(viewport={'width':W,'height':H}, device_scale_factor=2 if mobile else 1, has_touch=mobile, is_mobile=mobile)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', stage: '" + STAGE + "', seen: {steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type=='error' and errs.append(m.text[:200]))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=60000); await pg.wait_for_timeout(900)
        await pg.evaluate("(()=>{ for (let i=0;i<160;i++) __T.visuals(0.0001, 0.05); __T.renderFrame(); })()")
        await pg.screenshot(path=f'ui/{TAG}_menu.png')
        info = await pg.evaluate("[document.title, __T.GEN.key, __T.GEN.std, document.getElementById('cvName').textContent, document.getElementById('shuffleBtn').hidden, __T.POTS.length]")
        await pg.click('#startBtn'); await pg.wait_for_function("__T.state === 'play'", polling=100, timeout=30000); await pg.wait_for_timeout(2500)
        await pg.screenshot(path=f'ui/{TAG}_play.png')
        print(TAG, info, errs[:4]); await b.close()
asyncio.run(main())
