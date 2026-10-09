import asyncio
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844})
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', seen: {look:1} })); } catch (e) {}")
        pg = await ctx.new_page(); msgs = []
        pg.on('console', lambda m: msgs.append(m.type + ' ' + m.text[:300]))
        await pg.goto('file://' + SP + 'pc_t.html'); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000)
        r = await pg.evaluate("""() => { const m = __T.splIM.material, t = __T.SPLAT.map; const d = t.image.data; let a1 = 0, n = 0; for (let i = 3; i < d.length; i += 4) { if (d[i] > 127) a1++; n++; }
          return { type: m.type, transparent: m.transparent, alphaTest: m.alphaTest, blending: m.blending, depthWrite: m.depthWrite, side: m.side, a2c: m.alphaToCoverage, mapType: t.type, fmt: t.format, cs: t.colorSpace, w: t.image.width, frac: a1 / n, ver: t.version, mips: t.generateMipmaps, minF: t.minFilter, flipY: t.flipY, unpack: t.unpackAlignment, premul: t.premultiplyAlpha }; }""")
        print(r)
        print([m for m in msgs if 'error' in m.lower() or 'warn' in m.lower()][:10])
        await b.close()
asyncio.run(main())
