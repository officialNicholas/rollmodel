"""Measures the game's output level: taps whatever connects to the speakers with an analyser, then logs the peak and the share of samples
near full scale over the lobby and a match. usage: audiopeak.py [page] [tag]"""
import asyncio, sys, json
from playwright.async_api import async_playwright
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_h.html'
TAP = """(() => { const c0 = AudioNode.prototype.connect; window.__pk = { max: 0, hot: 0, n: 0, rms: 0 };
  AudioNode.prototype.connect = function (d, ...r) { if (d instanceof AudioDestinationNode && !d.__tap) { const ctx = d.context, an = ctx.createAnalyser(); an.fftSize = 2048; d.__an = an; d.__tap = 1;
      const buf = new Float32Array(2048); setInterval(() => { an.getFloatTimeDomainData(buf); let m = 0, s = 0; for (const v of buf) { const a = Math.abs(v); if (a > m) m = a; s += v * v; if (a > 0.89) __pk.hot++; } __pk.n += buf.length; __pk.max = Math.max(__pk.max, m); __pk.rms = Math.max(__pk.rms, Math.sqrt(s / buf.length)); }, 40); }
    if (d instanceof AudioDestinationNode && this !== d.__an) { c0.call(this, d.__an); } return c0.call(this, d, ...r); }; })()"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 700}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', mode:'duel', stage:'manor', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1,items:1} })); } catch (e) {}")
        await ctx.add_init_script(TAP)
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/' + PAGE, timeout=240000); await pg.wait_for_function('typeof __T === "object" && !!__T.VP', timeout=240000, polling=1000)
        await pg.mouse.click(195, 350); await pg.wait_for_timeout(4000)
        rd = lambda: pg.evaluate("(() => { const r = { max: +__pk.max.toFixed(3), rms: +__pk.rms.toFixed(3), hot: +(__pk.hot / Math.max(1, __pk.n) * 1000).toFixed(2) }; __pk.max = 0; __pk.rms = 0; __pk.hot = 0; __pk.n = 0; return r; })()")
        print('lobby', await rd())
        await pg.evaluate("__T.start()"); await pg.wait_for_function("__T.state === 'play'", timeout=60000, polling=500)
        for k in range(4):
            await pg.wait_for_timeout(5000); print('match', k, await rd())
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
