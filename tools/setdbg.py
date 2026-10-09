import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{steer:1,look:1} })); } catch (e) {}")
        pg = await ctx.new_page(); await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1200)
        await pg.evaluate("document.getElementById('setBtn').click()"); await pg.wait_for_timeout(500)
        print(await pg.evaluate("(() => { const c = document.querySelector('#setModal .card'); const out = []; for (const ps of ['::before', '::after']) { const s = getComputedStyle(c, ps); out.push(ps + ' content=' + s.content + ' disp=' + s.display + ' pos=' + s.position + ' box=' + s.left + ',' + s.top + ' ' + s.width + 'x' + s.height + ' clip=' + s.clipPath.slice(0, 60) + ' bg=' + s.backgroundColor + ' op=' + s.opacity + ' z=' + s.zIndex + ' tr=' + s.transform + ' vis=' + s.visibility); } const cs = getComputedStyle(c); out.push('card ' + cs.position + ' ' + cs.width + 'x' + cs.height + ' ov=' + cs.overflow + ' disp=' + cs.display); return out; })()"))
        await b.close()
asyncio.run(main())
