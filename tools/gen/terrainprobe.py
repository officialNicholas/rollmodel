# how the body's drawn height and its air pose behave over real ground: the CPU brain drives you round each stage for a while at 60 fps,
# and each frame the drawn height, the simulated height, airborne or not (and airborne to the look), the leap pose and the face are
# recorded. Counts: height pops while on the ground (a big jump in drawn height in one frame), blink-short air poses, flickering faces
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_t.html'
SECS = float(sys.argv[2]) if len(sys.argv) > 2 else 25
JS = r"""([stage, secs]) => { const T = __T, P = T.P; window.__noLoop = true;
  Math.random = (() => { let s = 99; return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; })();
  T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
  T.mode = 'duel'; T.applyMode(); T.setStage(stage === 'island' || stage === 'blank' ? stage : 'season'); T.genWorld(1357, { themes: [stage] }); T.mapUsed = false; T.start(); T.setWx('clear', 999);
  T.aiReset(P); const out = []; const V = T.VP, I = V.slime;
  for (let f = 0; f < secs * 60; f++) { T.aiStep(P, 1 / 60); T.steerIn = P.steer; T.step(1 / 60); T.visuals(1 / 60, 1 / 60);
    out.push([V.root.position.y, P.y, P.air ? 1 : 0, V.vAir === undefined ? (P.air ? 1 : 0) : (V.vAir ? 1 : 0), I ? I.st.leap : 0, I ? I.st.exprB : '', P.st === 'play' ? 1 : 0, V.look.flat]); }
  return out; }"""
def runs(seq):
    out, cur, n = [], seq[0], 0
    for v in seq:
        if v == cur: n += 1
        else: out.append((cur, n)); cur, n = v, 1
    out.append((cur, n)); return out
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 200, 'height': 300}, device_scale_factor=1)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'lo', mode: 'duel', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300]))
        await pg.goto('file://' + SP + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(800)
        tot = {}
        for st in ['island', 'crypt', 'cathedral', 'manor', 'blank']:
            rows = await pg.evaluate(JS, [st, SECS])
            pops = 0; big = 0
            for i in range(1, len(rows)):
                a, b2 = rows[i - 1], rows[i]
                if a[6] and b2[6] and not a[2] and not b2[2] and a[3] == 0 and b2[3] == 0:
                    d = abs(b2[0] - a[0])
                    if d > 0.1: pops += 1
                    big = max(big, d)
            shortAir = sum(1 for v, n in runs([r[3] for r in rows]) if v == 1 and n <= 5)
            simShort = sum(1 for v, n in runs([r[2] for r in rows]) if v == 1 and n <= 5)
            leapOn = runs([1 if r[4] > 0.3 else 0 for r in rows]); shortLeap = sum(1 for v, n in leapOn if v == 1 and n <= 8)
            faces = runs([r[5] for r in rows]); shortFace = sum(1 for v, n in faces if n <= 5)
            r = { 'stage': st, 'frames': len(rows), 'groundPops>0.1': pops, 'maxGroundStep': round(big, 3), 'simAir<=5f': simShort, 'drawnAir<=5f': shortAir, 'leapPose<=8f': shortLeap, 'faceFlicker<=5f': shortFace, 'faceChanges': len(faces) }
            print(json.dumps(r))
            for k, v in r.items():
                if isinstance(v, (int, float)) and k != 'frames': tot[k] = tot.get(k, 0) + v
        print(PAGE, 'TOTAL', json.dumps(tot)); print('errors', errs[:3]); await b.close()
asyncio.run(main())
