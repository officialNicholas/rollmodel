"""AI vs AI matches, simulated faster than real time: the real loop is frozen (dt 0) and the probe steps the game itself (two 1/120 s
steps, then the visuals, then the trail, as a frame does), with drawing switched off. Per blob: time stuck (on the ground, not charging,
barely moving, not sheltering on purpose) and how long the stuck spells last, steering flips (hard left to hard right) per minute,
replans, pounds, flings, knock-outs by cause, coverage; per match the winner; and the planner's cost per think.
usage: aisim.py <tag> <stages comma list> <difficulties comma list> [reps]"""
import asyncio, os, json, sys, time
from playwright.async_api import async_playwright
TAG, STAGES, DIFFS = sys.argv[1], sys.argv[2].split(','), sys.argv[3].split(','); REPS = int(sys.argv[4]) if len(sys.argv) > 4 else 1
SIM = """(n => { const T = __T, M = window.__sim, dt = 1 / 60;
  for (let i = 0; i < n && T.state === 'play'; i++) {
    __pf.cur = {}; T.step(dt / 2); T.step(dt / 2); T.visuals(dt, dt); T.flushTrail(); const c = __pf.cur; __pf.cur = null;
    if (c.aiThink) { M.think.push(c.aiThink); M.fling.push(c.aiFlingPaint || 0); M.dij.push(c.dijkstra || 0); } M.t += dt;
    for (const D of T.ACTIVE) { const k = D.team, m = M.D[k] || (M.D[k] = { play: 0, moving: 0, stuck: 0, runs: [], cur: 0, flips: 0, last: 0, pounds: 0, flings: 0, wasSlam: false, wasFlung: false, wig: 0, wigT: 9, wigS: 0, hist: [], fine: [], histT: 0, drySp: [], wasDry: false, lowT: 0, refills: 0, refP: 0, wasMode: '',  wasSt: 'play', deaths: [], thinks: 0, lastTT: 0, air: 0, charging: 0, hide: 0, spin: 0, yh: [], uturn: 0, uCD: 0 });
      if (D.st === 'play') { m.play += dt;
        if (D.air) m.air += dt; else if (D.charging) m.charging += dt;
        else if (D.spd < 0.4 && !(D.ai && D.ai.atShelter) && !(D.flatT > 0) && !(D.stunT > 0) && !D.turret) { m.cur += dt; m.stuck += dt; if (m.cur > 1.5 && m.cur - dt <= 1.5 || m.cur > 4 && m.cur - dt <= 4) { const a = D.ai || {}, tn = a.tgt >= 0 ? T.NAVo.nodes[a.tgt] : null, O = T.ACTIVE.find(E => E !== D); (m.snaps || (m.snaps = [])).push({ t: +M.t.toFixed(2), cur: +m.cur.toFixed(2), x: +D.x.toFixed(2), y: +D.y.toFixed(2), z: +D.z.toFixed(2), yaw: +D.yaw.toFixed(2), spd: +D.spd.toFixed(2), steer: +(D.steer || 0).toFixed(2), turn: +(D.turn || 0).toFixed(2), mode: a.mode, tgt: a.tgt, tp: tn && [+tn.x.toFixed(2), +tn.h.toFixed(2), +tn.z.toFixed(2)], pi: a.pi, pl: a.path && a.path.length, plan: a.plan && a.plan.kind, thinkT: +(a.thinkT || 0).toFixed(2), pivotT: +(a.pivotT || 0).toFixed(2), pivotCD: +(a.pivotCD || 0).toFixed(2), paint: +D.paint.toFixed(2), held: D.held || null, oD: O ? +Math.hypot(O.x - D.x, O.z - D.z).toFixed(2) : null, st: D.st, vx: D.vx, vz: D.vz }); } }
        else { if (m.cur > 0.8) m.runs.push(+m.cur.toFixed(2)); m.cur = 0; m.moving += dt; }
        const s = D.steer || 0; if (Math.abs(s) > 0.35) { if (Math.abs(m.last) > 0.35 && Math.sign(s) !== Math.sign(m.last)) m.flips++; m.last = s; }
        if (Math.abs(D.turn || 0) > 2.2 && !D.air) m.spin += dt;
        m.wigT += dt; if (!D.air && !D.charging && D.spd > 2 && Math.abs(D.turn || 0) > 1.2) { const sg = Math.sign(D.turn); if (m.wigS && sg !== m.wigS && m.wigT < 1) m.wig++; if (sg !== m.wigS) { m.wigS = sg; } m.wigT = 0; }
        m.histT -= dt; if (m.histT <= 0) { m.histT = 0.25; const a = D.ai || {}; m.hist.push([+M.t.toFixed(2), +D.x.toFixed(1), +D.y.toFixed(1), +D.z.toFixed(1), +D.spd.toFixed(1), a.mode, +D.paint.toFixed(2), +(a.need || 0).toFixed(2), D.charging ? 1 : 0, D.air ? 1 : 0, a.plan ? a.plan.kind : null, D.dry ? 1 : 0]); if (m.hist.length > 60) m.hist.shift(); }
        if (!D.air && !D.charging && D.spd > 1.5) { m.yh.push(D.yaw); if (m.yh.length > 72) m.yh.shift(); m.uCD -= dt; if (m.yh.length >= 72 && m.uCD <= 0 && Math.abs(Math.atan2(Math.sin(D.yaw - m.yh[0]), Math.cos(D.yaw - m.yh[0]))) > 2.4) { m.uturn++; m.uCD = 1.2; m.yh.length = 0; } } else m.yh.length = 0; }
      if (D.st !== 'ko') { const a = D.ai || {}; m.fine.push([+M.t.toFixed(3), +D.x.toFixed(2), +D.y.toFixed(2), +D.z.toFixed(2), +D.yaw.toFixed(2), +D.spd.toFixed(1), +(D.vy || 0).toFixed(1), D.air ? 1 : 0, D.charging ? +D.charge.toFixed(2) : 0, a.plan ? a.plan.kind + ':' + (+a.plan.c).toFixed(2) + '@' + (+a.plan.yaw).toFixed(2) : null, a.flight || null, D.flung ? 1 : 0, D.dashDir || 0, D.airSling ? 1 : 0, a.mode, D.st, D.rollT > 0 ? 1 : 0, +(D.kx || 0).toFixed(1), +(D.kz || 0).toFixed(1), +(D.steer || 0).toFixed(2), D.giantT > 0 ? 1 : 0, D.slam ? 1 : 0]); if (m.fine.length > 150) m.fine.shift(); }
      if (D.st === 'ko' && m.wasSt !== 'ko' && D.reason !== 'pound' && D.reason !== 'crush') m.deaths.push({ t: +M.t.toFixed(2), why: D.reason, hist: m.hist.slice(), fine: m.fine.slice() }); m.wasSt = D.st;
      if (D.st === 'hide') m.hide += dt;
      if (D.st === 'play' && D.paint < 0.06) m.lowT += dt;
      if (D.dry && !m.wasDry) m.drySp.push([+M.t.toFixed(1), T.wxPhase, D.ai ? D.ai.mode : null]); m.wasDry = !!D.dry;
      if (D.ai && D.ai.mode === 'refill' && m.wasMode !== 'refill') { m.refills++; m.refP += D.paint; } if (D.ai) m.wasMode = D.ai.mode;
      if (D.slam && !m.wasSlam) m.pounds++; m.wasSlam = !!D.slam; if (D.flung && !m.wasFlung) m.flings++; m.wasFlung = !!D.flung;
      if (D.ai) { if (D.ai.thinkT > m.lastTT + 0.05) m.thinks++; m.lastTT = D.ai.thinkT; } } }
  return [T.state, M.t]; })"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 430, 'height': 754})
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{look:1}, runs: 9, flings: 99, tut: { ph: 'done' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/' + os.environ.get('PAGE', 'pc_perf.html'), timeout=300000)
        for i in range(200):
            if await pg.evaluate("typeof __T === 'object' && !!window.__pf"): break
            await pg.wait_for_timeout(2500)
        await pg.evaluate("(() => { __T.renderer.render = () => {}; })()")
        out = []
        for rep in range(REPS):
            for st in STAGES:
                for df in DIFFS:
                    await pg.evaluate(f"(() => {{ window.__noStep = false; __T.setStage('{st}'); __T.setDiff('{df}'); __T.setAI('{df}'); }})()")
                    await pg.evaluate("__T.start()")
                    t0 = time.time()
                    while time.time() - t0 < 240:
                        s = await pg.evaluate("__T.state")
                        if s == 'play': break
                        await pg.wait_for_timeout(500)
                    await pg.evaluate(f"(() => {{ window.__noStep = true; window.__perfAI(); __T.setAI('{df}'); window.__sim = {{ t: 0, D: {{}}, think: [], fling: [], dij: [] }}; }})()")
                    while True:
                        r = await pg.evaluate(SIM + "(600)")
                        if r[0] != 'play': break
                    res = await pg.evaluate("(() => ({ M: __sim, th: __T.TH.id, diff: __T.diff, blobs: __T.ACTIVE.map(D => ({ team: D.team, cov: +__T.teamCov(D.team).toFixed(1), outs: D.outs, why: D.outWhy, kos: D.kos })) }))()")
                    out.append(res); M = res['M']; th = sorted(M['think']); q = lambda a, f: a[min(len(a) - 1, int(f * len(a)))] if a else 0
                    fl = sorted(M['fling']); dj = sorted(M['dij'])
                    print(f"== {st}/{df}: {M['t']:.0f}s sim, think calls {len(th)} mean {sum(th)/max(1,len(th)):.2f}ms p95 {q(th,.95):.2f} max {th[-1] if th else 0:.2f} | of which fling search mean {sum(fl)/max(1,len(fl)):.2f} max {fl[-1] if fl else 0:.2f}, dijkstra mean {sum(dj)/max(1,len(dj)):.2f}")
                    for bl in res['blobs']:
                        m = M['D'][str(bl['team'])]; pl = max(1e-6, m['play'])
                        for sn in m.get('snaps', []): print('      STUCK', json.dumps(sn))
                        for dd in m.get('deaths', []): print('      DEATH', dd['t'], dd['why'], json.dumps(dd['hist']))
                        print(f"   team {bl['team']}: cov {bl['cov']}%  stuck {100*m['stuck']/pl:.1f}% (spells>0.8s {len(m['runs'])}, longest {max(m['runs'] or [0])}s)  flips/min {60*m['flips']/max(1e-6,m['moving']):.1f}  U-turns/min {60*m['uturn']/max(1e-6,m['moving']):.1f}  wiggles/min {60*m['wig']/max(1e-6,m['moving']):.1f}  spin {m['spin']:.1f}s  air {100*m['air']/pl:.0f}%  charging {100*m['charging']/pl:.0f}%  hide {m['hide']:.0f}s  thinks/min {60*m['thinks']/pl:.0f}  pounds {m['pounds']} flings {m['flings']}  outs {bl['outs']} {bl['why']} kos {bl['kos']}")
                    await pg.evaluate("window.__noStep = false")
                    for i in range(40):
                        if await pg.evaluate("__T.state === 'dead' || __T.state === 'menu'"): break
                        await pg.wait_for_timeout(500)
                    await pg.evaluate("(() => { try { __T.toMenu(); } catch (e) {} })()"); await pg.wait_for_timeout(3000)
        json.dump(out, open(f'/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/aisim_{TAG}.json', 'w'))
        print('errors', errs[:5])
        await b.close()
asyncio.run(main())
