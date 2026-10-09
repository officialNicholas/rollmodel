import asyncio
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist','--autoplay-policy=no-user-gesture-required'])
        pg = await b.new_page(viewport={'width':390,'height':844}); errs=[]; await pg.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', seen: {steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}"); pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type in ('error','warning') and 'ERR_' not in m.text and errs.append(m.type + ': ' + m.text))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000)
        await pg.mouse.click(200, 100); await pg.wait_for_timeout(1500)
        await pg.evaluate("document.getElementById('mWorld').hidden && document.getElementById('homePlay').click()"); await pg.wait_for_timeout(350); await pg.click('#shuffleBtn'); await pg.wait_for_timeout(400)
        await pg.evaluate("document.getElementById('mWorld').hidden && document.getElementById('homePlay').click()"); await pg.wait_for_timeout(350); await pg.click('#startBtn'); await pg.wait_for_timeout(3000)
        # fire every effect once, from near and far, while the music plays
        r = await pg.evaluate("""(async () => { const T = __T, A = T.AU, H = T.H, names = ['ui','nope','jump','land','splat','slam','quake','burst','fling','whoosh','swish','brake','notch','release','enter','glug','pop','power','orb','grow','shrink','die','fall','squish','bonk','spot','ready','lead','danger','low','count','tick','horn','fanfare','lose','draw','thunder','heatWarn','heatOn','dusk','splashWater','sprinkle','sink','rumble','rise','flip','flipBack','brushWarn','brushDrop'];
          let n = 0; for (const k of names) { if (typeof A[k] !== 'function') return 'missing ' + k; A.at(H.x, H.z); A[k](0.7); n++; await new Promise(r => setTimeout(r, 60)); }
          A.chargeStart(); A.chargeSet(0.6); await new Promise(r => setTimeout(r, 200)); A.chargeStop(); A.rain(1); A.sizzle(1); A.roll(5, 0.5); A.mood(true, true, true, false); await new Promise(r => setTimeout(r, 2500)); A.rain(0); A.sizzle(0); A.mood(false, false, false, false);
          return n; })()""")
        print('fired', r)
        await pg.click('#pauseBtn'); await pg.wait_for_timeout(800); await pg.click('#resumeBtn'); await pg.wait_for_timeout(500)
        await pg.evaluate("__T.matchLeft = 0.05; __T.teamNA[1] = 0;"); await pg.wait_for_timeout(5000)
        print('state', await pg.evaluate("__T.state"), 'errors', errs[:6]); await b.close()
asyncio.run(main())
