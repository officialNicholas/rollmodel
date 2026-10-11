# phase-2 QA sheets: faces, eye styles, paint levels in both states and mid-transition, team colours, jelly (jump / land), springs (turn, speed), breathing
import asyncio, sys, time, json
from shot import *
D = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2/'
W = 420
def V(yaw, pitch, dist, ty, tx=0, tz=0, fov=30): return f'axo.view({yaw},{pitch},{dist},{ty},{tx},{tz},{fov})'
HEAD = V(0.0, 0.1, 1.7, 1.3, 0, 0.4); HEAD34 = V(0.6, 0.15, 1.7, 1.3, 0, 0.4); CHEAD = "(()=>{const p=axo.joint('crawl','head'); axo.view(0.5,0.05,1.7,p[1],p[0],p[2]+0.15,30)})()"
STAND = V(0.5, 0.15, 4.2, 0.85); CRAWL = V(0.6, 0.25, 4.6, 0.3); SIDE = V(1.57, 0.1, 4.6, 0.6)
SHEETS = {}
SHEETS['faces'] = [(f'{e}', f'axo.setState("stand"); axo.look.setEyeStyle(0); axo.look.setExpression("{e}"); axo.look.blinkK = 0; axo.look.blinkT = 9; axo.step(1/60, 20); {HEAD}') for e in ['neutral', 'happy', 'angry', 'hurt', 'glee', 'scared', 'yawn', 'dizzy', 'peek', 'leap', 'brace']] + [('blink', f'axo.look.setExpression("neutral"); axo.step(1/60, 10); axo.look.blink(); axo.step(1/60, 2); {HEAD}')]
SHEETS['eyes'] = [(f'{n} {e}', f'axo.setState("stand"); axo.look.setEyeStyle({i}); axo.look.setFangs({str(f).lower()}); axo.look.setExpression("{e}"); axo.look.blinkT = 9; axo.step(1/60, 20); {HEAD34 if i % 2 else HEAD}') for i, n in enumerate(['round', 'edgy', 'dot', 'zombie']) for e, f in (('neutral', False), ('happy', True), ('angry', True))]
SHEETS['facecrawl'] = [(f'crawl {e}', f'axo.setState("crawl"); axo.look.setEyeStyle(0); axo.look.setFangs(false); axo.look.setExpression("{e}"); axo.look.blinkT = 9; axo.step(1/60, 40); {CHEAD}') for e in ['neutral', 'happy', 'scared', 'glee']] + [(f'crawl look {y}', f'axo.setLook({y}, -10); axo.step(1/60, 30); {CHEAD}') for y in (50, -50)] + [('crawl top', f'axo.setLook(0,0); axo.step(1/60, 20); {V(0.3, 1.2, 1.8, 0.4, 0, 0.5)}')]
SHEETS['paint'] = [(f'{st} paint {lv}', f'axo.setState("{st}"); axo.look.setPaint({lv}); axo.step(1/60, 70); {STAND if st == "stand" else CRAWL}') for st in ('stand', 'crawl') for lv in (0, 0.25, 0.5, 0.75, 1.0)]
SHEETS['paintside'] = [(f'{st} paint {lv} side', f'axo.setState("{st}"); axo.look.setPaint({lv}); axo.step(1/60, 70); {SIDE}') for st in ('stand', 'crawl') for lv in (0.3, 0.6)]
SHEETS['painttrans'] = [('crawl .55', f'axo.setState("crawl"); axo.look.setPaint(0.55); axo.step(1/60, 120); {V(0.9, 0.3, 4.4, 0.6)}')] + [(f'to stand t={t}', f'axo.setState("stand"); axo.step(1/60, {n}); {V(0.9, 0.3, 4.4, 0.6)}') for t, n in ((0.2, 12), (0.4, 12), (0.7, 18), (1.2, 30), (2.0, 48))] + [(f'to crawl t={t}', f'axo.setState("crawl"); axo.step(1/60, {n}); {V(0.9, 0.3, 4.4, 0.6)}') for t, n in ((0.25, 15), (0.5, 15), (1.0, 30), (2.0, 60))]
SHEETS['colors'] = [(f'{hex(c)}', f'axo.setState("{st}"); axo.look.setPaint(0.35); axo.look.setColor({c}); axo.step(1/60, 40); {STAND if st == "stand" else CRAWL}') for st in ('stand', 'crawl') for c in (0xff6b8a, 0xe3122f, 0xffb300, 0x3bd16f, 0x2f8cff, 0x9b5cff)] + [(f'{hex(c)} face', f'axo.setState("stand"); axo.look.setColor({c}); axo.step(1/60, 30); {HEAD34}') for c in (0xe3122f, 0x3bd16f, 0x2f8cff)]
SHEETS['jelly'] = [('before', f'axo.setState("stand"); axo.look.setPaint(0); axo.look.setColor(0xff6b8a); axo.A.motion.exert = 0; axo.step(1/60, 60); {STAND}'), ('jump 0.05', f'axo.A.jump(); axo.step(1/60, 3); {STAND}'), ('jump 0.3', f'axo.step(1/60, 15); {STAND}'), ('fall 0.6', f'axo.step(1/60, 18); {STAND}'), ('land +0.03', 'for (let i = 0; i < 60 && axo.A.inAir; i++) axo.step(1/60); axo.step(1/60, 2); ' + STAND), ('land +0.1', f'axo.step(1/60, 4); {STAND}'), ('land +0.2', f'axo.step(1/60, 6); {STAND}'), ('land +0.5', f'axo.step(1/60, 18); {STAND}'),
  ('crawl before', f'axo.setState("crawl"); axo.step(1/60, 120); {CRAWL}'), ('crawl jump', f'axo.A.jump(); axo.step(1/60, 12); {CRAWL}'), ('crawl land +0.05', 'for (let i = 0; i < 60 && axo.A.inAir; i++) axo.step(1/60); axo.step(1/60, 3); ' + CRAWL), ('crawl land +0.25', f'axo.step(1/60, 12); {CRAWL}')]
SHEETS['springs'] = [('crawl speed 0.2', f'axo.setState("crawl"); axo.A.motion.speed = 0.2; axo.A.motion.turn = 0; axo.step(1/60, 150); {V(0.0, 1.35, 5.0, 0.0)}'), ('speed 1.0', f'axo.A.motion.speed = 1; axo.step(1/60, 120); {V(0.0, 1.35, 5.0, 0.0)}'), ('speed 1.5', f'axo.A.motion.speed = 1.5; axo.step(1/60, 120); {V(0.0, 1.35, 5.0, 0.0)}'),
  ('turn left 0.3s', f'axo.A.motion.speed = 1; axo.A.motion.turn = 1; axo.step(1/60, 18); {V(0.0, 1.35, 5.0, 0.0)}'), ('turn left 1s', f'axo.step(1/60, 42); {V(0.0, 1.35, 5.0, 0.0)}'), ('turn right 0.5s', f'axo.A.motion.turn = -1; axo.step(1/60, 30); {V(0.0, 1.35, 5.0, 0.0)}'), ('straight +0.3', f'axo.A.motion.turn = 0; axo.step(1/60, 18); {V(0.0, 1.35, 5.0, 0.0)}'), ('straight +1.5 (settled)', f'axo.step(1/60, 72); {V(0.0, 1.35, 5.0, 0.0)}'),
  ('gills turn L', f'axo.A.motion.turn = 1; axo.step(1/60, 20); {CHEAD}'), ('gills turn R', f'axo.A.motion.turn = -1; axo.step(1/60, 24); {CHEAD}'), ('gills settle', f'axo.A.motion.turn = 0; axo.step(1/60, 60); {CHEAD}'), ('stand tail idle', f'axo.setState("stand"); axo.step(1/60, 120); {V(2.4, 0.3, 4.2, 0.8)}')]
SHEETS['breath'] = [(f'{lab} ph {k}', f'axo.setState("stand"); axo.A.motion.exert = {ex}; axo.step(1/60, {60 if k == 0 else 0}); axo.A.breathPh = {ph}; axo.A.breath = 0.5 + 0.5 * Math.sin({ph}); axo.A.jelly(1/60); {V(0.9, 0.1, 2.4, 0.9)}') for lab, ex in (('calm', 0), ('exerted', 1)) for k, ph in enumerate((-1.5708, 1.5708))] + [(f'crawl breath {k}', f'axo.setState("crawl"); axo.A.motion.exert = 1; axo.step(1/60, 60); axo.A.breathPh = {ph}; axo.A.breath = 0.5 + 0.5 * Math.sin({ph}); axo.A.jelly(1/60); {V(1.57, 0.05, 2.8, 0.3)}') for k, ph in enumerate((-1.5708, 1.5708))]
async def main(which):
    async with async_playwright() as p:
        b, pg, errs = await open_page(p, 'http://localhost:8765/axo2/preview.html?manual', W, W); await pg.evaluate(f'axo.size({W},{W})')
        for name in which:
            t0 = time.time(); cells = []
            for lab, js in SHEETS[name]:
                im = (await capture(pg, [js], 'axo.shot()'))[0]; cells.append((im, lab))
            ncol = min(6, len(cells)); grid(cells, ncol, W, W).save(D + f'v5_{name}.jpg', quality=85); print(name, 'done', round(time.time() - t0, 1), errs[:3]); errs.clear()
        await b.close()
asyncio.run(main(sys.argv[1:] or list(SHEETS)))
