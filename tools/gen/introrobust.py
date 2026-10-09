# every way out of the basin, on every stage and a few maps, all the blobs at once: through Go and two seconds of play. Afterwards everyone
# must be out and playing, on the floor (not in a basin, not fallen), with nothing of the intro left on them
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
STAGES = (sys.argv[1] if len(sys.argv) > 1 else 'island,blank,crypt,cathedral,manor,studio').split(',')
MODE = sys.argv[2] if len(sys.argv) > 2 else 'duel'
JS = r"""([stage, kind, seed, mode]) => { const T = __T; window.__noLoop = true; window.__introKind = kind; T.mode = mode; T.applyMode(); T.setStage(stage === 'island' || stage === 'blank' ? stage : 'season');
  T.genWorld(seed, { themes: [stage] }); T.mapUsed = false;
  T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
  document.getElementById('menu').hidden = true; T.beginMatch();
  let minY = 9, nan = false, fellIntro = false;
  const goAt = []; for (let i = 0; i < 60 * 6; i++) { T.step(1 / 60); T.visuals(1 / 60, 1 / 60); for (const D of T.ACTIVE) if (D.st === 'hide' && T.state === 'play' && !D.__hid) { D.__hid = true; goAt.push([D === T.P ? 'P' : 'R', +(i / 60).toFixed(2)]); } for (const D of T.ACTIVE) { if (!isFinite(D.x) || !isFinite(D.y) || !isFinite(D.z)) nan = true; if (T.state === 'intro' && D.st === 'ko') fellIntro = true; } }
  const out = T.ACTIVE.map(D => ({ who: D === T.P ? 'P' : 'R', ai: !!D.ai, st: D.st, y: +D.y.toFixed(2), ground: +(T.surfaceUnder(D.x, D.z, D.y + 0.5)).toFixed(2), ip: !!D.ip, act: !!D.introAct, crawl: !!D.introCrawl, out: !!D.introOut, kind: D.introKind, pot: !!D.pot, sink: +(D === T.P ? T.VP.sink : (D.look && D.look.V ? D.look.V.sink : 0) || 0).toFixed(2) }));
  for (const D of T.ACTIVE) delete D.__hid; return { state: T.state, nan, fellIntro, out, goAt }; }"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 360, 'height': 640})
        await ctx.add_init_script("window.__skipIntro = false; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient: 'port', name: 'Nick', gfx: 'hi', mode: 'duel', color: 'red', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('file://' + SP + 'pc_t.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(500)
        bad = 0; n = 0
        for st in STAGES:
            for kind in ['climb', 'cannon', 'twister']:
                for seed in [88, 5131, 70001]:
                    r = await pg.evaluate(JS, [st, kind, seed, MODE]); n += 1
                    probs = []
                    if r['state'] != 'play': probs.append('state ' + r['state'])
                    if r['nan']: probs.append('NaN')
                    if r['fellIntro']: probs.append('fell in intro')
                    later = set(w for w, t in r['goAt'] if t > 4.0)  # (a rival hopping into a refill after Go is just playing)
                    for o in r['out']:
                        if o['who'] in later and o['ai'] and o['st'] == 'hide': continue
                        if o['st'] not in ('play',): probs.append('st ' + o['st'])
                        if o['ip'] or o['act'] or o['crawl'] or o['out'] or o['pot']: probs.append('leftover ' + json.dumps(o))
                        if o['sink'] > 0.01: probs.append('sunk ' + str(o['sink']))
                    if probs: bad += 1; print(st, kind, seed, probs[:2], r['goAt'])
        print('runs', n, 'bad', bad, 'errors', errs[:3]); await b.close()
asyncio.run(main())
