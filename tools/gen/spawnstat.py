# where the match starts: for each stage and many maps, which basins the players start in and which way they climb out, and how much
# room that leaves (the run ahead before a wall or an edge, how open it is all round, how near the nearest drop is, how far apart they are)
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_t.html'
STAGES = (sys.argv[2] if len(sys.argv) > 2 else 'island,blank,crypt,cathedral,manor,studio').split(',')
NSEED = int(sys.argv[3]) if len(sys.argv) > 3 else 12
MODE = sys.argv[4] if len(sys.argv) > 4 else 'duel'
JS = r"""([stage, nseed, mode]) => { const T = __T; window.__noLoop = true; T.mode = mode; T.applyMode(); T.setStage(stage === 'island' || stage === 'blank' ? stage : 'season');
  const out = [];
  for (let s = 0; s < nseed; s++) { const seed = 1000 + s * 7717; { let q = seed >>> 0; Math.random = () => { q = (q * 1664525 + 1013904223) >>> 0; return q / 4294967296; }; }
    T.genWorld(seed, { themes: [stage] }); T.mapUsed = false; { let q = (seed * 7 + 3) >>> 0; Math.random = () => { q = (q * 1664525 + 1013904223) >>> 0; return q / 4294967296; }; }
    const pots = T.pots.filter(p => T.potUp(p));
    const got = T.introBasins(), rows = [];
    const drop = (x, z, y) => { const g = T.surfaceUnder(x, z, y + 0.6); return g === -Infinity || Math.abs(g - y) > 0.4; };
    for (const [D, p] of got) {
      const yaw = T.basinLeap(p), run = T.openRun(p.x, p.z, p.y, yaw, 1.0, 14);
      let open = 0; for (let k = 0; k < 16; k++) if (T.openRun(p.x, p.z, p.y, k / 16 * 6.2832, 1.0, 4) >= 3) open++;
      let dd = 9; for (let r = 1.0; r <= 6 && dd === 9; r += 0.25) for (let k = 0; k < 32; k++) { const a = k / 32 * 6.2832; if (drop(p.x + Math.sin(a) * r, p.z + Math.cos(a) * r, p.y)) { dd = r; break; } }
      let fan = 9; for (const da of [-0.45, 0.45]) fan = Math.min(fan, T.openRun(p.x, p.z, p.y, yaw + da, 1.0, 14));
      rows.push({ who: D === T.P ? 'P' : 'R', x: +p.x.toFixed(1), z: +p.z.toFixed(1), y: +p.y.toFixed(2), run: +run.toFixed(1), fan: +fan.toFixed(1), open, drop: dd, kind: p.kind });
    }
    const ps = [...got.values()]; let sep = 99; for (let i = 0; i < ps.length; i++) for (let j = i + 1; j < ps.length; j++) sep = Math.min(sep, Math.hypot(ps[i].x - ps[j].x, ps[i].z - ps[j].z));
    out.push({ seed, n: pots.length, sep: +sep.toFixed(1), rows });
  }
  return out; }"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width': 360, 'height': 640}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('file://' + SP + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP', polling=200, timeout=300000); await pg.wait_for_timeout(500)
        allr = []
        for st in STAGES:
            r = await pg.evaluate(JS, [st, NSEED, MODE])
            rs = [x for m in r for x in m['rows']]
            bad = sum(1 for x in rs if x['run'] < 5); nearEdge = sum(1 for x in rs if x['drop'] < 2.5); high = sum(1 for x in rs if x['y'] > 0.1); narrow = sum(1 for x in rs if x['fan'] < 3)
            seps = sorted(m['sep'] for m in r)
            print('%-10s starts %3d  run<5: %2d  fan<3: %2d  drop<2.5: %2d  raised: %2d  run med %.1f  open med %d  sep min %.1f med %.1f' % (st, len(rs), bad, narrow, nearEdge, high, sorted(x['run'] for x in rs)[len(rs) // 2], sorted(x['open'] for x in rs)[len(rs) // 2], seps[0], seps[len(seps) // 2]))
            allr.append({ 'stage': st, 'maps': r })
        json.dump(allr, open(SP + 'rx/spawnstat_%s.json' % PAGE.replace('.html', ''), 'w'))
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
