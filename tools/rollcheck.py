"""v203: a match with the player rolling about: every looping sound that starts (by its spot in the sound sheet), and errors"""
import asyncio, json
from playwright.async_api import async_playwright
HOOK = """(() => { window.__lp = [];
  const bs = AudioBufferSourceNode.prototype.start; AudioBufferSourceNode.prototype.start = function (when, off) { if (this.loop) __lp.push([+(this.buffer ? this.buffer.duration : 0).toFixed(2), +(+(off || 0)).toFixed(2), +(+this.loopStart).toFixed(2), +(+this.loopEnd).toFixed(2)]); return bs.apply(this, arguments); };
})()"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'])
        ctx = await b.new_context(viewport={'width': 844, 'height': 390}, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'land', name:'Dusk', seen:{look:1}, drops: 50, runs: 3, tut: { ph: 'done' } })); } catch (e) {}")
        await ctx.add_init_script(HOOK)
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000)
        await pg.evaluate("(() => { __T.renderer.render = () => {}; })(); 0")
        await pg.mouse.click(400, 200); await pg.wait_for_timeout(3000)
        await pg.evaluate("document.getElementById('homePlay').click()")
        await pg.wait_for_function("__T.state === 'play'", timeout=300000); await pg.wait_for_timeout(4000)
        await pg.keyboard.down('ArrowUp'); await pg.keyboard.down('ArrowLeft'); await pg.wait_for_timeout(8000); await pg.keyboard.up('ArrowLeft'); await pg.keyboard.up('ArrowUp')
        sheet = {93.03: 'm', 38.79: 's'}; idx = None
        src = open('/home/claude/paint-the-canvas.html').read(); a0 = src.index('/*SFXI*/') + 8; idx = json.loads(src[a0:src.index('/*SFXI_END*/')])['snd']
        def name(ch, ls):
            for k, (c, tk, g) in idx.items():
                if c == ch and any(abs(ls - t0) < 0.1 for t0, d in tk): return k
            return '?'
        for d, off, ls, le in await pg.evaluate("__lp"):
            ch = sheet.get(d); print('loop', d, 'loopStart', ls, '->', name(ch, ls) if ch else 'music/other')
        print('state', await pg.evaluate("__T.state"), 'P.spd', await pg.evaluate("+__T.P.spd.toFixed(2)"), 'errors', errs)
        await b.close()
asyncio.run(main())
