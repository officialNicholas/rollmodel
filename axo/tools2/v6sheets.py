# v6 QA sheets: faces (both states, same camera distance, front and 3/4), eye styles, team colours, material breakdown, paint, transitions,
# breathing / landing squash. Usage: python3 v6sheets.py [names]
import asyncio, sys, time, json
from shot import *
D = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2/'
W = 420
def V(yaw, pitch, dist, ty, tx=0, tz=0, fov=30): return f'axo.view({yaw},{pitch},{dist},{ty},{tx},{tz},{fov})'
# head-targeted cameras: the same distance and framing on both meshes (the head joint plus an offset toward the head centre)
def HV(mesh, yaw, pitch=0.08, dist=1.9, fov=30, up=-0.02, fwd=0.05): return f"(()=>{{const p=axo.hc('{mesh}'); axo.view({yaw},{pitch},{dist},p[1]+{up},p[0],p[2]+{fwd},{fov})}})()"
STAND = V(0.5, 0.15, 4.2, 0.85); CRAWL = V(0.6, 0.25, 4.6, 0.3); SIDE = V(1.57, 0.1, 4.6, 0.6); BACK = V(2.3, 0.45, 3.4, 0.2, 0.0, -0.2)
EXPRS = ['neutral', 'happy', 'angry', 'hurt', 'glee', 'scared', 'yawn', 'dizzy', 'peek', 'leap', 'brace']
SET = lambda st: f'axo.setState("{st}"); axo.A.motion.speed = 0; axo.A.motion.exert = 0; axo.look.setPaint(0); axo.look.setColor(0xff6b8a); axo.look.setEyeStyle(0); axo.look.setFangs(false); axo.look.blinkT = 99; axo.look.blinkK = 0; axo.setLook(0,0); axo.step(1/60, 90); '
SHEETS = {}
# faces: rows = stand front, stand 3/4, crawl front, crawl 3/4; columns = expressions + blink
def face_row(st, yaw):
    cells = [(f'{st} {e}', SET(st) + f'axo.look.setExpression("{e}"); axo.look.blinkT = 99; axo.step(1/60, 20); ' + HV(st, yaw)) for e in EXPRS]
    cells.append((f'{st} blink', SET(st) + 'axo.look.setExpression("neutral"); axo.step(1/60, 10); axo.look.blink(); axo.step(1/60, 2); ' + HV(st, yaw)))
    return cells
SHEETS['faces'] = face_row('stand', 0.0) + face_row('stand', 0.7) + face_row('crawl', 0.0) + face_row('crawl', 0.7)
SHEETS['facepair'] = [(f'{st} {lab}', SET(st) + f'axo.look.setExpression("neutral"); axo.step(1/60, 10); ' + HV(st, y, p, d)) for lab, y, p, d in (('front', 0.0, 0.08, 1.35), ('3/4', 0.7, 0.12, 1.35), ('side', 1.57, 0.05, 1.35), ('top', 0.3, 1.1, 1.35), ('low 3/4', -0.6, -0.2, 1.35), ('far 3/4', 0.6, 0.15, 3.0)) for st in ('stand', 'crawl')]
SHEETS['eyes'] = [(f'{st} {n} {e}' + (' fangs' if f else ''), SET(st) + f'axo.look.setEyeStyle({i}); axo.look.setFangs({str(f).lower()}); axo.look.setExpression("{e}"); axo.step(1/60, 20); ' + HV(st, 0.55 if i % 2 else 0.0))
                  for st in ('stand', 'crawl') for i, n in enumerate(['round', 'edgy', 'dot', 'zombie']) for e, f in (('neutral', False), ('happy', True), ('angry', True))]
SHEETS['look'] = [(f'{st} look {y},{p}', SET(st) + f'axo.setLook({y},{p}); axo.step(1/60, 30); ' + HV(st, 0.0)) for st in ('stand', 'crawl') for y, p in ((50, -10), (-50, -10), (0, 25), (0, -25))]
TEAM = [0xff6b8a, 0xe3122f, 0xffb300, 0x3bd16f, 0x2f8cff, 0x9b5cff, 0x22d3e6, 0xff7a1a]
SHEETS['colors'] = [(f'{st} {hex(c)}', SET(st) + f'axo.look.setPaint(0.3); axo.look.setColor({c}); axo.step(1/60, 40); ' + (STAND if st == 'stand' else CRAWL)) for st in ('stand', 'crawl') for c in TEAM] + \
                   [(f'face {hex(c)}', SET('stand') + f'axo.look.setColor({c}); axo.step(1/60, 20); ' + HV('stand', 0.6)) for c in TEAM]
DBG = lambda k: f'axo.look.U.uDebug.value = {k}; '
SHEETS['materials'] = [(f'{st} {lab}', SET(st) + DBG(k) + (V(0.5, 0.15, 4.2, 0.85) if st == 'stand' else V(2.3, 0.45, 3.4, 0.2, 0.0, -0.2))) for st in ('stand', 'crawl') for lab, k in (('final', 0), ('roughness', 1), ('detail normal', 2), ('occlusion', 3), ('regions r=belly g=head b=thin/web', 4))] + \
                      [(f'close {lab}', SET('crawl') + DBG(k) + V(1.3, 0.35, 1.6, 0.3, 0.0, -0.1)) for lab, k in (('final', 0), ('roughness', 1), ('detail normal', 2), ('occlusion', 3), ('regions', 4))] + \
                      [(f'head {lab}', SET('stand') + DBG(k) + HV('stand', 0.6)) for lab, k in (('final', 0), ('roughness', 1), ('detail normal', 2), ('occlusion', 3), ('regions', 4))] + [('reset', DBG(0) + STAND)]
SHEETS['paint'] = [(f'{st} paint {lv}', SET(st) + f'axo.look.setPaint({lv}); axo.step(1/60, 70); ' + (STAND if st == 'stand' else CRAWL)) for st in ('stand', 'crawl') for lv in (0, 0.35, 0.7, 1.0)] + \
                  [(f'{st} paint 1.0 face', SET(st) + 'axo.look.setPaint(1.0); axo.look.setExpression("happy"); axo.step(1/60, 40); ' + HV(st, 0.5)) for st in ('stand', 'crawl')]
SHEETS['painttrans'] = [('crawl .55', SET('crawl') + f'axo.look.setPaint(0.55); axo.step(1/60, 60); {V(0.9, 0.3, 4.4, 0.6)}')] + [(f'to stand t={t}', f'axo.setState("stand"); axo.step(1/60, {n}); {V(0.9, 0.3, 4.4, 0.6)}') for t, n in ((0.2, 12), (0.3, 6), (0.35, 3), (0.4, 3), (0.5, 6), (0.7, 12), (1.2, 30), (2.0, 48))] + \
                       [(f'to crawl t={t}', f'axo.setState("crawl"); axo.step(1/60, {n}); {V(0.9, 0.3, 4.4, 0.6)}') for t, n in ((0.15, 9), (0.25, 6), (0.33, 5), (0.38, 3), (0.5, 7), (1.0, 30), (2.0, 60))]
SHEETS['breath'] = [(f'{lab} ph {k}', SET('stand') + f'axo.A.motion.exert = {ex}; axo.step(1/60, 60); axo.A.breathPh = {ph}; axo.A.breath = 0.5 + 0.5 * Math.sin({ph}); axo.A.jelly(1/60); {V(0.9, 0.1, 2.4, 0.9)}') for lab, ex in (('calm', 0), ('exerted', 1)) for k, ph in enumerate((-1.5708, 1.5708))] + \
                   [(f'crawl breath {k}', SET('crawl') + f'axo.A.motion.exert = 1; axo.step(1/60, 60); axo.A.breathPh = {ph}; axo.A.breath = 0.5 + 0.5 * Math.sin({ph}); axo.A.jelly(1/60); {V(1.57, 0.05, 2.8, 0.3)}') for k, ph in enumerate((-1.5708, 1.5708))] + \
                   [('land +0.03', SET('stand') + 'axo.A.jump(); for (let i = 0; i < 90 && axo.A.inAir; i++) axo.step(1/60); axo.step(1/60, 2); ' + STAND), ('land +0.1', f'axo.step(1/60, 4); {STAND}'), ('land +0.2', f'axo.step(1/60, 6); {STAND}'), ('land +0.5', f'axo.step(1/60, 18); {STAND}'),
                    ('crawl land +0.05', SET('crawl') + 'axo.A.motion.speed = 1; axo.A.jump(); for (let i = 0; i < 90 && axo.A.inAir; i++) axo.step(1/60); axo.step(1/60, 3); ' + CRAWL), ('crawl land +0.25', f'axo.step(1/60, 12); {CRAWL}')]
async def main(which):
    async with async_playwright() as p:
        b, pg, errs = await open_page(p, 'http://localhost:8765/axo2/preview.html?manual', W, W); await pg.evaluate(f'axo.size({W},{W})')
        print('eye probe distances', await pg.evaluate('JSON.stringify({stand: axo.look.rigs.stand.probeDist, crawl: axo.look.rigs.crawl.probeDist})'))
        for name in which:
            t0 = time.time(); cells = []
            for lab, js in SHEETS[name]:
                im = (await capture(pg, [js], 'axo.shot()'))[0]; cells.append((im, lab))
            ncol = {'faces': 12, 'facepair': 4, 'eyes': 6, 'look': 4, 'colors': 8, 'materials': 5, 'paint': 5, 'painttrans': 8, 'breath': 6}.get(name, 6)
            grid(cells, ncol, W, W).save(D + f'v6_{name}.jpg', quality=85); print(name, 'done', round(time.time() - t0, 1), errs[:3]); errs.clear()
        await b.close()
asyncio.run(main(sys.argv[1:] or list(SHEETS)))
