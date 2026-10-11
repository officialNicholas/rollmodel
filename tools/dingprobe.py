"""Every sound the main menu starts over 45 s from its first one, named from the sheet index (or the synth's pitch), during the onboarding and after it"""
import asyncio, sys, json
from playwright.async_api import async_playwright
HOOK = """(() => { const t0 = performance.now(); window.__au = []; const rec = (k, d) => __au.push([Math.round(performance.now() - t0), k, d]);
  const os = OscillatorNode.prototype.start; OscillatorNode.prototype.start = function (when) { rec('osc', [this.type, Math.round(this.frequency.value)]); return os.apply(this, arguments); };
  const bs = AudioBufferSourceNode.prototype.start; AudioBufferSourceNode.prototype.start = function (when, off, dur) { rec('buf', [this.buffer ? +this.buffer.duration.toFixed(2) : 0, off ? +(+off).toFixed(3) : 0, dur ? +(+dur).toFixed(3) : null, this.loop]); return bs.apply(this, arguments); };
})()"""
async def run(ph):
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{look:1}, drops: 50, runs: " + ('0' if ph == 'match' else '3') + ", tut: { ph: '" + ph + "' } })); } catch (e) {}")
        await ctx.add_init_script(HOOK)
        pg = await ctx.new_page()
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000)
        await pg.evaluate("(() => { const r = __T.renderer; r.render = () => {}; })(); 0")
        await pg.mouse.click(200, 300); await pg.wait_for_function('__au.length > 0', timeout=300000); await pg.wait_for_timeout(int(sys.argv[2]) * 1000 if len(sys.argv) > 2 else 45000) # (timed from the first sound: a slow boot ate the old fixed window)
        log = await pg.evaluate("__au"); src = open('/home/claude/paint-the-canvas.html').read(); a0 = src.index('/*SFXI*/') + 8; idx = json.loads(src[a0:src.index('/*SFXI_END*/')])
        def name(off, dur):
            best = None
            for k, (ch, tk, g) in idx['snd'].items():
                for t0, d in tk:
                    if abs(off - t0) < 0.12 and (dur is None or abs(dur - d) < 0.12): best = k
            return best
        print('---', ph, len(log), 'starts')
        for t, k, d in log:
            if k == 'buf': print(f'{t/1000:6.1f}s  buf len {d[0]:6.2f} off {d[1]:7.3f} dur {d[2]} loop {d[3]}  ->', name(d[1], d[2]) if d[0] > 30 and d[0] < 200 and not d[3] else ('MUSIC' if d[3] else '?'))
            else: print(f'{t/1000:6.1f}s  osc {d}')
        await b.close()
asyncio.run(run(sys.argv[1]))
