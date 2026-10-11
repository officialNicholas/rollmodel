"""Every audio node the page starts in the menu's first seconds (oscillators with their pitch, buffers with their length), to find a stray chime."""
import asyncio
from playwright.async_api import async_playwright
HOOK = """(() => { const t0 = performance.now(); window.__au = []; const rec = (k, d) => __au.push([Math.round(performance.now() - t0), k, d]);
  const os = OscillatorNode.prototype.start; OscillatorNode.prototype.start = function (when) { rec('osc', [this.type, Math.round(this.frequency.value), when && this.context ? +(when - this.context.currentTime).toFixed(2) : 0]); return os.apply(this, arguments); };
  const bs = AudioBufferSourceNode.prototype.start; AudioBufferSourceNode.prototype.start = function (when, off, dur) { rec('buf', [this.buffer ? +this.buffer.duration.toFixed(2) : 0, off ? +(+off).toFixed(2) : 0, dur ? +(+dur).toFixed(2) : null, +this.playbackRate.value.toFixed(2), this.loop, when && this.context ? +(when - this.context.currentTime).toFixed(2) : 0]); return bs.apply(this, arguments); };
})()"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{look:1}, drops: 50, runs: 3, tut: { ph: 'done' } })); } catch (e) {}")
        await ctx.add_init_script(HOOK)
        pg = await ctx.new_page()
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000)
        r0 = await pg.evaluate("Math.round(performance.now())"); await pg.tap('#menu', position={'x': 200, 'y': 300}) if False else await pg.mouse.click(30, 400)
        t1 = await pg.evaluate("Math.round(performance.now())"); await pg.wait_for_timeout(14000)
        log = await pg.evaluate("__au"); print('menu ready', r0, 'first tap', t1)
        for e in log: print(e)
        await b.close()
asyncio.run(main())
