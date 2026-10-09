import asyncio, json, sys
sys.path.insert(0, 'gen')
from playwright.async_api import async_playwright
src = open('gen/v20test.py').read()
PREP = src.split('PREP = r"""')[1].split('"""')[0]; HELP = src.split('HELP = r"""')[1].split('"""')[0]
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000)
        await pg.evaluate(PREP); await pg.evaluate(HELP)
        r = await pg.evaluate(r"""(() => { const T = __T, out = {}; const on = () => T.rivals.filter(r => r.on).length, vis = () => T.rivals.filter(r => r.g.visible).length;
          out.start = { on: on(), vis: vis(), spots: T.rivals.length };
          T.P.st = 'ko'; T.P.koT = 1e9; T.H.st = 'ko'; T.H.koT = 1e9;
          T.rainPuddles(); const tl = []; for (let i = 0; i < 3000; i++) { T.step(0.012); if (i % 250 === 0) tl.push(on()); }
          out.afterRain = tl;
          T.rainPuddles(); for (let i = 0; i < 700; i++) T.step(0.012); out.rain2 = on(); T.rainPuddles(); for (let i = 0; i < 700; i++) T.step(0.012); out.rain3cap = on();
          T.dryPuddles(); for (let i = 0; i < 300; i++) T.step(0.012); out.afterSun = { on: on(), vis: vis() };
          return out; })()""")
        print('lifecycle', json.dumps(r))
        # weather-driven: a full match of weather, how many puddles at a time
        r = await pg.evaluate(r"""(() => { const T = __T; const hist = {}; let maxOn = 0, secsWith = 0;
          T.start(); T.P.st = 'ko'; T.P.koT = 1e9; T.H.st = 'ko'; T.H.koT = 1e9;
          for (let i = 0; i < 7500 && T.state === 'play'; i++) { T.step(0.012); const n = T.rivals.filter(r => r.on).length; maxOn = Math.max(maxOn, n); if (n) secsWith += 0.012; }
          return { maxOn, secsWith: +secsWith.toFixed(1) }; })()""")
        print('match', r)
        # dilution: rolling through a puddle, paint counts half and looks faint
        await pg.evaluate("__flat()")
        r = await pg.evaluate(r"""(() => { const T = __T, P = T.P, H = T.H; T.start(); T.setWx('clear', 999); __flat(); H.st = 'ko'; H.koT = 1e9; const out = {};
          const n = __open(9); __place(P, n.x - 8, n.z, 0, Math.PI / 2); P.spd = 5.4; const c0 = T.teamCov(0);
          for (let i = 0; i < 120; i++) { T.step(0.012); P.yaw = Math.PI / 2; } out.fullGain = +(T.teamCov(0) - c0).toFixed(3);
          __place(P, n.x - 8, n.z + 3, 0, Math.PI / 2); P.spd = 5.4; P.dilT = 99; const c1 = T.teamCov(0);
          for (let i = 0; i < 120; i++) { T.step(0.012); P.yaw = Math.PI / 2; P.dilT = 99; } out.dilGain = +(T.teamCov(0) - c1).toFixed(3);
          // diluted over your own full paint changes nothing
          __place(P, n.x - 8, n.z, 0, Math.PI / 2); P.spd = 5.4; P.dilT = 99; const c2 = T.teamCov(0);
          for (let i = 0; i < 120; i++) { T.step(0.012); P.yaw = Math.PI / 2; P.dilT = 99; } out.dilOverOwn = +(T.teamCov(0) - c2).toFixed(3);
          // full over your own diluted paint upgrades it
          __place(P, n.x - 8, n.z + 3, 0, Math.PI / 2); P.spd = 5.4; P.dilT = 0; const c3 = T.teamCov(0);
          for (let i = 0; i < 120; i++) { T.step(0.012); P.yaw = Math.PI / 2; P.dilT = 0; } out.fullOverDil = +(T.teamCov(0) - c3).toFixed(3);
          // a real puddle: roll into it
          const r = T.rivals[0]; r.x = n.x + 2; r.z = n.z - 4; r.y = 0; r.g.position.set(r.x, 0, r.z); r.on = true; r.k = 1; r.target = 1; r.life = 30; r.g.visible = true; r.g.scale.setScalar(1);
          __place(P, n.x - 2, n.z - 4, 0, Math.PI / 2); P.spd = 5.4; let hit = -1, dilEnd = -1;
          for (let i = 0; i < 500; i++) { T.step(0.012); P.yaw = Math.PI / 2; if (hit < 0 && P.dilT > 0) hit = i; if (hit >= 0 && dilEnd < 0 && P.dilT <= 0) dilEnd = i; }
          out.puddle = { hit, dilSecsAfterHit: dilEnd > 0 ? +((dilEnd - hit) * 0.012).toFixed(2) : null, spd: +P.spd.toFixed(2) };
          return out; })()""")
        print('dilution', json.dumps(r))
        print('errors', errs)
        await b.close()
asyncio.run(main())
