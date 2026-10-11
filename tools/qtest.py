"""v206: the smoothness tuning, fed made-up frame times: a clean run steps up, late frames step down (and a notch that didn't hold
waits), and a steady 30 a second from Low Power Mode is told apart from real overload"""
import asyncio, json
from playwright.async_api import async_playwright
UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 430, 'height': 754}, device_scale_factor=3, has_touch=True, is_mobile=True, user_agent=UA)
        await ctx.add_init_script("window.__tut = true; window.__noLoop = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{look:1}, runs: 5, tut: { ph: 'done' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/pc_perf.html', timeout=300000)
        for i in range(120):
            if await pg.evaluate("typeof __T === 'object' && typeof window.__tp === 'function'"): break
            await pg.wait_for_timeout(2500)
        q0 = await pg.evaluate("__q()"); print('ladder', len(q0['lad']), json.dumps(q0['lad'])); print('start: level', q0['lvl'], 'post', q0['post'], 'pr', q0['pr'])
        await pg.evaluate("window.__noLoop = true; window.__fixedPR = false; __setCpu(0.003)")
        async def feed(ms, n=60, late=0):
            return await pg.evaluate(f"(() => {{ for (let i = 0; i < {n}; i++) __tp(i < {late} ? 0.034 : {ms} / 1000); return __q(); }})()")
        await feed(16.7, 61)  # (the screen-change skip)
        for i in range(9):
            q = await feed(16.7)
        print('after 9 clean seconds: level', q['lvl'], 'post', q['post'])
        q = await feed(16.7, late=6); print('a second with 6 late frames: level', q['lvl'], 'ban', q['ban'])
        for i in range(10): q = await feed(16.7)
        print('10 clean seconds later (that notch is banned for a while): level', q['lvl'])
        for i in range(3): q = await feed(16.7, late=8)
        print('three bad seconds: level', q['lvl'], 'pr', q['pr'], 'post', q['post'])
        lv = q['lvl']
        for i in range(5): q = await feed(33.3); print('  steady 30 a second, second', i + 1, ': level', q['lvl'], 'capped', q['capped'])
        print('steady 30 held by the phone: back to', q['lvl'], '(was', lv, ')')
        for i in range(2): q = await feed(16.7)
        print('60 again: capped', q['capped'], 'level', q['lvl'])
        await pg.evaluate("__setCpu(0.012)")
        for i in range(12): q = await feed(16.7)
        print('12 clean seconds but the frame itself takes 12 ms (no headroom): level', q['lvl'], '(no step up)')
        print('errors', errs)
        await b.close()
asyncio.run(main())
