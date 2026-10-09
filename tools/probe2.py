import asyncio, sys
from playwright.async_api import async_playwright
LAND = '--land' in sys.argv
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        VP = {'width': 780, 'height': 360} if LAND else {'width': 390, 'height': 780}
        ctx = await b.new_context(viewport=VP, device_scale_factor=2, has_touch=True, is_mobile=True); await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'" + ('land' if LAND else 'port') + "', name:'Dusk', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(2000)
        await pg.evaluate("document.getElementById('stageBtn').click()"); await pg.wait_for_timeout(900)
        print('picker red probe', await pg.evaluate("(() => { const w = document.querySelector('.world[aria-pressed=\"true\"]'); const r = w.getBoundingClientRect(); const pts = [[r.right + 6, r.top + r.height/2], [r.left + r.width/2, r.bottom - 60]]; return pts.map(([x,y]) => document.elementsFromPoint(x, y).slice(0,3).map(e => e.tagName + '.' + e.className + '#' + e.id + ' bg=' + getComputedStyle(e).backgroundColor + ' sh=' + getComputedStyle(e).boxShadow.slice(0,60))); })()"))
        print('frame cs', await pg.evaluate("(() => { const f = document.querySelector('.world[aria-pressed=\"true\"] .frame'); const c = getComputedStyle(f), a = getComputedStyle(f, '::after'), b = getComputedStyle(f, '::before'); return [c.boxShadow, c.filter, c.transform, 'after:' + a.content + a.backgroundColor + a.display, 'before:' + b.display]; })()"))
        print('world after', await pg.evaluate("(() => { const f = document.querySelector('.world[aria-pressed=\"true\"]'); const a = getComputedStyle(f, '::after'), b = getComputedStyle(f, '::before'); return ['after:' + a.content + ' ' + a.backgroundColor + ' ' + a.backgroundImage.slice(0,80), 'before:' + b.content + ' ' + b.backgroundImage.slice(0,60)]; })()"))
        await pg.evaluate("document.getElementById('worldBack').click()"); await pg.wait_for_timeout(600)
        await pg.evaluate("document.getElementById('lookBtn').click()"); await pg.wait_for_timeout(3000)
        await pg.screenshot(path=f'{WS}/ui/probe_look_{"l" if LAND else "p"}.png')
        print('look boxes', await pg.evaluate("(() => { const out = []; const p = document.querySelector('.lookp'); const pr = p.getBoundingClientRect(); out.push('lookp ' + Math.round(pr.top) + '-' + Math.round(pr.bottom) + ' overflowY=' + getComputedStyle(p).overflowY + ' h=' + Math.round(pr.height) + ' sh=' + p.scrollHeight); for (const c of p.children) { const r = c.getBoundingClientRect(); out.push(c.tagName + '.' + c.className.slice(0,20) + '#' + c.id + ' ' + Math.round(r.top) + '-' + Math.round(r.bottom) + ' pos=' + getComputedStyle(c).position); } return out; })()"))
        await b.close()
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
asyncio.run(main())
