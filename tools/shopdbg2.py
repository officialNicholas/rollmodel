import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{steer:1,look:1}, owned:['flower','hockey'], bought:[], drops:900, look:{head:null, eyes:'edgy', iris:'violet'} })); } catch (e) {}")
        pg = await ctx.new_page()
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1500)
        await pg.evaluate("document.getElementById('dabsBtn').click()"); await pg.wait_for_timeout(1500)
        print(await pg.evaluate("""(() => { const b = document.querySelector('#shopGrid .shitem'); const cs = getComputedStyle(b); const r = e => { const q = e.getBoundingClientRect(); return [Math.round(q.width), Math.round(q.height)]; };
          const par = b.parentElement, pcs = getComputedStyle(par); const shin = b.querySelector('.shin');
          const rules = []; const walk = (list, med) => { for (const ru of list) { if (ru.cssRules && ru.media) { if (matchMedia(ru.media.mediaText).matches) walk(ru.cssRules, ru.media.mediaText); continue; } if (ru.style && ru.selectorText) { let m = false; try { m = b.matches(ru.selectorText) || par.matches(ru.selectorText) || shin.matches(ru.selectorText); } catch (e) {} if (m) rules.push((med ? '@' : '') + ru.cssText.slice(0, 140)); } } }; for (const ss of document.styleSheets) { try { walk(ss.cssRules, ''); } catch (e) {} }
          const anon = b.firstElementChild.getBoundingClientRect(); const cont = cs.contain; const bh = b.offsetHeight, sh = b.scrollHeight;
          return { h: cs.height, maxH: cs.maxHeight, minH: cs.minHeight, box: cs.boxSizing, parent: par.className, pdisp: pcs.display, rows: pcs.gridAutoRows, prows: pcs.gridTemplateRows.slice(0, 80), shin: shin ? [r(shin), getComputedStyle(shin).display, getComputedStyle(shin).position] : null, rules, cont, bh, sh, inl: b.getAttribute('style') }; })()"""))
        await b.close()
asyncio.run(main())
