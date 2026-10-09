import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
EXTRACT = """(() => { const T = __T, r2 = v => typeof v === 'number' ? Math.round(v * 100) / 100 : v, arr = a => a.map(x => x.map(r2));
  return { arena: T.ARENA, sym: T.GEN.sym, arch: T.GEN.arch, holes: arr(T.HOLES), boxes: arr(T.BOXES), ramps: arr(T.RAMPS),
    clouds: T.MOVERS.filter(m => m.on).map(m => ({ x: r2(m.x), z: r2(m.z), axis: m.axis, amp: r2(m.amp), period: r2(m.period), ph: r2(m.ph) })),
    pots: arr(T.POTS), rivals: arr(T.RIVALS), powers: arr(T.POWER_SPOTS),
    start: { x: r2(T.START.x), z: r2(T.START.z), yaw: r2(T.START.yaw) }, cstart: { x: r2(T.CSTART.x), z: r2(T.CSTART.z), yaw: r2(T.CSTART.yaw) }, cstart2: { x: r2(T.CSTART2.x), z: r2(T.CSTART2.z), yaw: r2(T.CSTART2.yaw) } }; })()"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':400,'height':400}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000); await pg.wait_for_timeout(300)
        await pg.evaluate("(()=>{ const T=__T; window.__noLoop = true; T.mode = 'duel'; T.applyMode(); T.genWorld(202, { easy: true, themes: ['studio'] }); })()")
        duel = await pg.evaluate(EXTRACT)
        # the same stage at 3-way size: everything spread out by the arena ratio, items placed again for three
        trio = None
        for sd in range(1, 40):
            ok = await pg.evaluate("""([L, sd]) => { const T = __T; T.mode = 'trio'; T.applyMode(); const k = T.ARENA / L.arena, sx = r => [r[0] * k, r[1] * k, r[2] * k, r[3] * k, ...r.slice(4)];
              const SL = { sym: L.sym, theme: 'studio', holes: L.holes.map(sx), boxes: L.boxes.map(sx), ramps: L.ramps.map(sx), clouds: L.clouds.map(c => Object.assign({}, c, { x: c.x * k, z: c.z * k, amp: c.amp * k })) };
              T.applyLayout(SL); T.rebuildSamples(); T.buildNav(); return T.placeItems(SL, T.rng(sd * 977 + 5)); }""", [duel, sd])
            if ok:
                trio = await pg.evaluate(EXTRACT); trio['sym'] = duel['sym']; trio['arch'] = duel['arch']; trio['seed'] = sd; break
        print('duel', len(json.dumps(duel)), 'pots', len(duel['pots']),  '| trio', trio and len(json.dumps(trio)), trio and len(trio['pots']), trio and trio['seed'], errs[:3])
        json.dump({'duel': duel, 'trio': trio}, open('std/standard.json', 'w'), separators=(',', ':'))
        await b.close()
asyncio.run(main())
