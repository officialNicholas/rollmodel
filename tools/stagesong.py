"""Which song a stage plays and how it loops: starts a match on the stage given and logs every long looping track that starts (its length,
loop start and end, the offset it starts from). usage: stagesong.py page stage"""
import asyncio, sys, json, functools
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
PAGE, SID = sys.argv[1], sys.argv[2]
HOOK = """(() => { window.__mx = []; const bs = AudioBufferSourceNode.prototype.start;
  AudioBufferSourceNode.prototype.start = function (when, off) { if (this.buffer && this.buffer.duration > 25) __mx.push({ dur: +this.buffer.duration.toFixed(3), loop: this.loop, ls: +this.loopStart.toFixed(5), le: +this.loopEnd.toFixed(5), off: off === undefined ? null : +(+off).toFixed(3) }); return bs.apply(this, arguments); }; })()"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__noVote = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{ jump: 1, hold: 1, steer: 1, item: 1, orb: 1 }, drops: 0, runs: 5, stage: '" + SID + "', mode: 'duel', tut: { ph: 'done', strokes: 1, comms: 1 } })); } catch (e) {}")
        await ctx.add_init_script(HOOK)
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); ev = pg.evaluate
        await pg.goto('http://localhost:8765/' + PAGE, timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000, polling=200)
        await pg.mouse.click(200, 300); await pg.wait_for_timeout(3000)
        await ev("__T.mode = 'duel'; __T.applyMode(); __T.start()"); await pg.wait_for_function("__T.state === 'play'", timeout=400000, polling=200)
        for _ in range(60):
            log = await ev("__mx")
            if any(abs(e['le'] - 59.303) < 0.01 or abs(e['le'] - 50.856) < 0.01 or abs(e['le'] - 55.376) < 0.01 for e in log): break
            await pg.wait_for_timeout(2000)
        print('theme', await ev("__T.ev('[TH.id, MUSIC_STYLE, MUSIC_TRK]')"))
        print('tracks started', json.dumps(await ev("__mx")))
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
