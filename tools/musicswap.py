"""v203: lobby -> locker -> lobby in a real page: where each song starts, the cross-fade curves, and whether the locker's
Halloween cut comes in at exactly the spot the lobby song had reached (and back)"""
import asyncio, json
from playwright.async_api import async_playwright
HOOK = """(() => { window.__mx = [];
  const bs = AudioBufferSourceNode.prototype.start; AudioBufferSourceNode.prototype.start = function (when, off) { if (this.buffer && this.buffer.duration > 30 && this.buffer.duration < 50 && this.loop) __mx.push({ k: 'start', now: this.context.currentTime, when, off, dur: this.buffer.duration, ls: this.loopStart, le: this.loopEnd }); return bs.apply(this, arguments); };
  const sv = AudioParam.prototype.setValueCurveAtTime; AudioParam.prototype.setValueCurveAtTime = function (c, t, d) { __mx.push({ k: 'curve', t, d, a: c[0], b: c[c.length - 1], n: c.length }); return sv.apply(this, arguments); };
  window.addEventListener('error', e => __mx.push({ k: 'err', m: String(e.message) }));
})()"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'])
        ctx = await b.new_context(viewport={'width': 430, 'height': 932}, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{look:1}, drops: 50, runs: 3, tut: { ph: 'done' } })); } catch (e) {}")
        await ctx.add_init_script(HOOK)
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000)
        await pg.evaluate("(() => { __T.renderer.render = () => {}; })(); 0")
        await pg.mouse.click(215, 300)
        await pg.wait_for_function("__mx.some(e => e.k === 'start' && Math.abs(e.dur - 43.8) < 0.2)", timeout=300000)
        await pg.wait_for_timeout(7000)
        for step, sel in [('to locker', 'lookBtn'), ('back to lobby', 'lookDone')]:
            n0 = await pg.evaluate("__mx.length")
            await pg.evaluate(f"document.getElementById('{sel}').click()"); await pg.wait_for_timeout(6000)
            print(step, json.dumps(await pg.evaluate(f"__mx.slice({n0})"), default=str))
        log = await pg.evaluate("__mx"); print('errors', errs, [e for e in log if e['k'] == 'err'])
        # check: each new start's offset vs where the previous song was at that moment, both as distance into their loops
        st = [e for e in log if e['k'] == 'start' and (abs(e['dur'] - 43.82) < 0.05 or abs(e['dur'] - 38.39) < 0.05)]  # (the two songs, not the sound sheets' ambient loops)
        for prev, nxt in zip(st, st[1:]):
            pos = prev['off'] + (nxt['when'] - prev['when']); L = prev['le'] - prev['ls']
            if pos > prev['le']: pos = prev['ls'] + (pos - prev['ls']) % L
            want = nxt['ls'] + (pos - prev['ls']) % (nxt['le'] - nxt['ls'])
            print('handover %.2fs-long -> %.2fs-long: previous at %.4f s (%.4f into its loop), next starts at %.4f s (%.4f into its loop): error %.2f ms' % (prev['dur'], nxt['dur'], pos, pos - prev['ls'], nxt['off'], nxt['off'] - nxt['ls'], (nxt['off'] - want) * 1000))
        await b.close()
asyncio.run(main())
