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
        print(await pg.evaluate("""(() => { const b = document.querySelector('#shopGrid .shitem'), g = b.parentElement; const out = {}; const H = () => b.offsetHeight;
          out.base = H(); g.style.gridAutoRows = 'max-content'; out.maxc = H(); g.style.gridAutoRows = ''; b.style.alignSelf = 'start'; out.selfStart = H(); b.style.alignSelf = '';
          g.style.alignItems = 'start'; out.itemsStart = H(); g.style.alignItems = ''; out.cv = getComputedStyle(b).contentVisibility; out.cis = getComputedStyle(b).containIntrinsicSize;
          out.ctx = getComputedStyle(b).contain; out.hw = getComputedStyle(b).height + '/' + b.style.height; const shin = b.querySelector('.shin'); out.shinH = shin.offsetHeight; out.kids = [...shin.children].map(k => k.className + ':' + k.offsetHeight + ':' + getComputedStyle(k).display);
          g.style.gridTemplateColumns = '1fr 1fr'; out.cols2 = H(); g.style.gridTemplateColumns = ''; g.style.overflow = 'visible'; out.ovis = H(); g.style.overflow = ''; g.style.webkitMask = 'none'; out.nomask = H(); g.style.webkitMask = '';
          g.style.alignContent = 'normal'; out.acn = H(); g.style.alignContent = ''; g.style.flex = 'none'; out.noflex = H(); g.style.flex = ''; g.style.minHeight = 'auto'; out.mh = H(); g.style.minHeight = '';
          return out; })()"""))
        await b.close()
asyncio.run(main())
