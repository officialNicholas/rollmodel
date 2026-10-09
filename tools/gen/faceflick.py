# which faces flash up for only a few frames, and between which: the CPU brain drives you round two stages, the face sequence is run-length
# coded and each short run is printed with what came before and after (and what the blob was doing)
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_t.html'
JS = r"""([stage, secs]) => { const T = __T, P = T.P; window.__noLoop = true;
  Math.random = (() => { let s = 99; return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; })();
  T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
  T.mode = 'duel'; T.applyMode(); T.setStage(stage === 'island' || stage === 'blank' ? stage : 'season'); T.genWorld(1357, { themes: [stage] }); T.mapUsed = false; T.start(); T.setWx('clear', 999);
  T.aiReset(P); const out = []; const V = T.VP, I = V.slime;
  for (let f = 0; f < secs * 60; f++) { T.aiStep(P, 1 / 60); T.steerIn = P.steer; T.step(1 / 60); T.visuals(1 / 60, 1 / 60);
    out.push([I.st.exprB, P.st, P.air ? 1 : 0, +P.wob.toFixed(2), P.emoT > 0 ? P.emo : '', +P.paint.toFixed(2), P.charging ? 1 : 0, P.rollT > 0 ? 1 : 0, +P.vy.toFixed(1), P.slowed ? 1 : 0]); }
  return out; }"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 200, 'height': 300}, device_scale_factor=1)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'lo', mode: 'duel', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300]))
        await pg.goto('file://' + SP + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(800)
        for st in ['island', 'blank']:
            rows = await pg.evaluate(JS, [st, 25])
            runs = []; cur = rows[0][0]; s0 = 0
            for i, r in enumerate(rows):
                if r[0] != cur: runs.append((cur, s0, i)); cur = r[0]; s0 = i
            runs.append((cur, s0, len(rows)))
            for k, (f, a, z) in enumerate(runs):
                if z - a <= 5:
                    prev = runs[k - 1][0] if k else '-'; nxt = runs[k + 1][0] if k + 1 < len(runs) else '-'
                    print(st, 'frame', a, prev, '->', f, '(%d f)' % (z - a), '->', nxt, 'state', rows[a][1:])
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
