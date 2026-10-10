import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 844, 'height': 390}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'land', name:'Juliana', seen:{steer:1,look:1}, owned:['flower'], bought:[], drops:68, look:{head:null, eyes:'edgy', iris:'violet'}, colorId:'pink' })); } catch (e) {}")
        pg = await ctx.new_page()
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1500)
        await pg.evaluate("document.getElementById('lookBtn').click()"); await pg.wait_for_timeout(2000)
        print(await pg.evaluate("""(() => { const c = document.getElementById('lc-eyes'), cs = getComputedStyle(c), lk = document.getElementById('look'), lcs = getComputedStyle(lk), d = document.getElementById('lookDone'), dcs = getComputedStyle(d);
          const sw = document.getElementById('swatches'), scs = getComputedStyle(sw); const out = { mm: matchMedia('(max-height:520px) and (min-aspect-ratio:1/1)').matches, vw: innerWidth, vh: innerHeight, catMinH: cs.minHeight, catPad: cs.padding, catH: c.offsetHeight, gap: getComputedStyle(c.parentElement).gap, lookGap: lcs.gap, lookMaxH: lcs.maxHeight, lookH: lk.offsetHeight, lookScroll: lk.scrollHeight, overflow: lcs.overflowY, doneMinH: dcs.minHeight, doneH: d.offsetHeight, donePad: dcs.padding, doneMargin: dcs.marginTop, swPad: scs.padding, swH: sw.offsetHeight, swBtnH: sw.querySelector('.sw') && sw.querySelector('.sw').offsetHeight };
          const rules = []; const walk = (list, med) => { for (const ru of list) { if (ru.cssRules && ru.media) { if (matchMedia(ru.media.mediaText).matches) walk(ru.cssRules, ru.media.mediaText); continue; } if (ru.style && ru.selectorText && ru.style.minHeight) { let m = false; try { m = c.matches(ru.selectorText); } catch (e) {} if (m) rules.push((med ? '@ ' : '') + ru.selectorText.slice(0, 60) + ' => ' + ru.style.minHeight); } } }; for (const ss of document.styleSheets) { try { walk(ss.cssRules, ''); } catch (e) {} } out.rules = rules.slice(-3); out.kids = [...lk.children].map(k => { const q = getComputedStyle(k); return [k.id || k.className.slice(0, 18), k.offsetHeight, q.flex, q.height, q.minHeight, q.alignSelf, q.marginTop + '/' + q.marginBottom, q.display]; }); out.lookJ = lcs.justifyContent + ' ' + lcs.alignItems + ' ' + lcs.display + ' ' + lcs.flexDirection + ' pad ' + lcs.padding; const g = document.getElementById('lookCats'); out.catsRows = getComputedStyle(g).gridTemplateRows + ' / ' + getComputedStyle(g).alignItems + ' h ' + g.offsetHeight; return out; })()"""))
        await b.close()
asyncio.run(main())
