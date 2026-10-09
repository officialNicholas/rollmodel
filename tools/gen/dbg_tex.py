import asyncio, base64, sys
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844})
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', seen: {look:1} })); } catch (e) {}")
        pg = await ctx.new_page()
        await pg.goto('file://' + SP + 'pc_t.html'); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000)
        urls = await pg.evaluate("""() => { const S = __T.SPLAT, out = {};
          const dt = S.map.image, c = document.createElement('canvas'); c.width = dt.width; c.height = dt.height; const g = c.getContext('2d'), im = g.createImageData(dt.width, dt.height); im.data.set(dt.data); g.putImageData(im, 0, 0); out.map = c.toDataURL();
          const c2 = document.createElement('canvas'); c2.width = dt.width; c2.height = dt.height; const g2 = c2.getContext('2d'), im2 = g2.createImageData(dt.width, dt.height); for (let i = 0; i < dt.data.length; i += 4) { im2.data[i] = im2.data[i+1] = im2.data[i+2] = dt.data[i+3]; im2.data[i+3] = 255; } g2.putImageData(im2, 0, 0); out.alpha = c2.toDataURL();
          out.nrm = S.nrm.image.toDataURL(); out.aux = S.aux.image.toDataURL(); return out; }""")
        for k, u in urls.items(): open(SP + 'st/tex_' + k + '.png', 'wb').write(base64.b64decode(u.split(',')[1]))
        await b.close()
asyncio.run(main())
