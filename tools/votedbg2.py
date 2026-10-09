import asyncio
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__instant = false; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', mode:'duel', stage:'crypt', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1} })); } catch (e) {}")
        pg = await ctx.new_page()
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(2500)
        await pg.evaluate("document.getElementById('homePlay').click()")
        await pg.wait_for_function("!document.getElementById('vvote').hidden", timeout=60000); await pg.wait_for_timeout(300)
        print(await pg.evaluate("(() => { const el = document.getElementById('vvote'); const out = []; for (const ss of document.styleSheets) { let rs; try { rs = ss.cssRules; } catch (e) { continue; } for (const r of rs) { const walk = q => { if (q.selectorText) { try { if (el.matches(q.selectorText)) out.push(q.selectorText + ' => ' + q.style.cssText.slice(0, 80)); } catch (e) {} } if (q.cssRules) for (const x of q.cssRules) walk(x); }; walk(r); } } return out; })()"))
        print(await pg.evaluate("['vsx','vvote'].map(i => { const c = getComputedStyle(document.getElementById(i)); return i + ' disp=' + c.display + ' rows=' + c.gridTemplateRows + ' top=' + c.top + ' h=' + c.height + ' align=' + c.alignSelf; })"))
        print(await pg.evaluate("['vvote','vts'].map(i => { const r = document.getElementById(i).getBoundingClientRect(); return i + ' ' + Math.round(r.top) + '-' + Math.round(r.bottom); }).concat([...document.querySelectorAll('#vvote > *')].map(e => e.className + ' ' + Math.round(e.getBoundingClientRect().top) + '-' + Math.round(e.getBoundingClientRect().bottom) + ' disp=' + getComputedStyle(e).display + ' pos=' + getComputedStyle(e).position))"));
        print(await pg.evaluate("""(() => { const out = []; for (const e of document.querySelectorAll('body *')) { const c = getComputedStyle(e); if (c.position === 'absolute' || c.position === 'fixed') { const r = e.getBoundingClientRect(); if (r.width > 300 && r.height > 500 && c.display !== 'none' && c.visibility !== 'hidden' && +c.opacity > 0.05 && !e.closest('.vsx')) out.push(e.tagName + '.' + String(e.className).slice(0, 20) + '#' + e.id + ' z=' + c.zIndex + ' op=' + c.opacity + ' pe=' + c.pointerEvents + ' bg=' + c.backgroundColor + ' ' + c.backgroundImage.slice(0, 30)); } } return out; })()"""))
        await pg.evaluate("document.getElementById('vvote').style.cssText = 'display:block;top:auto;height:auto'"); await pg.wait_for_timeout(200); await pg.screenshot(path=f'{WS}/ui/votedbg_top.png')
        await b.close()
asyncio.run(main())
