# one map's basins and their start scores, and a top-down picture of the floor with the basins and the chosen starts
import asyncio, sys, json
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
PAGE = sys.argv[1]; STAGE = sys.argv[2]; SEED = int(sys.argv[3]); MODE = sys.argv[4] if len(sys.argv) > 4 else 'duel'
JS = r"""([stage, seed, mode]) => { const T = __T; window.__noLoop = true; T.mode = mode; T.applyMode(); T.setStage(stage === 'island' || stage === 'blank' ? stage : 'season');
  T.genWorld(seed, { themes: [stage] }); T.mapUsed = false;
  const A = T.ARENA, N = 160, grid = [];
  for (let j = 0; j < N; j++) { const row = []; for (let i = 0; i < N; i++) { const x = -A + (i + 0.5) / N * 2 * A, z = -A + (j + 0.5) / N * 2 * A, g = T.surfaceUnder(x, z, 9); row.push(g === -Infinity ? -1 : T.blockedAt(x, z, Math.max(0, g)) ? -2 : g); } grid.push(row); }
  const got = T.introBasins(), chosen = [...got.values()];
  const pots = T.pots.filter(p => T.potUp(p)).map(p => { const R = p.room || {}; return { x: p.x, z: p.z, y: p.y, yaw: T.basinLeap(p), score: R.score, run: R.run, fan: R.fan, open: R.open, edge: R.edge, chosen: chosen.indexOf(p) }; });
  return { A, N, grid, pots }; }"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width': 360, 'height': 640})
        await pg.goto('file://' + SP + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP', polling=200, timeout=300000); await pg.wait_for_timeout(500)
        r = await pg.evaluate(JS, [STAGE, SEED, MODE])
        for q in sorted(r['pots'], key=lambda q: -(q['score'] or 0)): print({k: (round(v, 2) if isinstance(v, float) else v) for k, v in q.items()})
        N, A = r['N'], r['A']; S = 4; im = Image.new('RGB', (N * S, N * S)); dr = ImageDraw.Draw(im)
        for j, row in enumerate(r['grid']):
            for i, v in enumerate(row):
                c = (20, 40, 90) if v == -1 else (90, 60, 40) if v == -2 else (int(200 - 40 * min(v, 3)), int(190 - 30 * min(v, 3)), 150)
                dr.rectangle((i * S, j * S, i * S + S - 1, j * S + S - 1), fill=c)
        import math
        for q in r['pots']:
            x = (q['x'] + A) / (2 * A) * N * S; y = (q['z'] + A) / (2 * A) * N * S
            col = (255, 40, 40) if q['chosen'] == 0 else (40, 120, 255) if q['chosen'] >= 1 else (255, 255, 255)
            dr.ellipse((x - 7, y - 7, x + 7, y + 7), outline=col, width=3)
            ex = x + math.sin(q['yaw']) * 30; ey = y + math.cos(q['yaw']) * 30; dr.line((x, y, ex, ey), fill=col, width=3)
            dr.text((x + 9, y - 6), '%.0f' % (q['score'] or 0), fill=(0, 0, 0))
        im.save(SP + 'rx/spawnmap_%s_%d.png' % (STAGE, SEED)); print('saved')
        await b.close()
asyncio.run(main())
