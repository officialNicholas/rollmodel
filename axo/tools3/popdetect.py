# Pop detector runner: steps the preview at 1/60 s through the crawl cycle, idle, every state and state change and both transitions,
# and reports single-frame discontinuities (popdetect.js) per scenario and body region.
#   python3 popdetect.py [URL] [OUT.json]
import asyncio, json, sys, time, os
from playwright.async_api import async_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
URL = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/axo2/preview.html?manual'
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, 'pop_report.json')
ONLY = os.environ.get('ONLY', '')
# (label, setup js (not recorded), recorded steps: list of (js before, frames))
SCEN = [
  ('crawl cycle x1.0', "axo.A.motion.speed=1; axo.setState('crawl'); axo.step(1/60,150)", [('', 300)]),
  ('crawl cycle x0.5', "axo.A.motion.speed=0.5; axo.setState('crawl'); axo.step(1/60,150)", [('', 240)]),
  ('crawl cycle x1.5', "axo.A.motion.speed=1.5; axo.setState('crawl'); axo.step(1/60,150)", [('', 240)]),
  ('crawl turning', "axo.A.motion.speed=1; axo.setState('crawl'); axo.step(1/60,150)", [('axo.A.motion.turn=1', 120), ('axo.A.motion.turn=-1', 120), ('axo.A.motion.turn=0', 60)]),
  ('crawl start/stop', "axo.A.motion.speed=1; axo.setState('crawl'); axo.step(1/60,150)", [('axo.A.motion.speed=0', 120), ('axo.A.motion.speed=1', 120)]),
  ('stand idle', "axo.A.motion.speed=1; axo.setState('stand'); axo.step(1/60,120)", [('', 300)]),
  ('state changes', "axo.setState('stand'); axo.step(1/60,120)", [("axo.setState('power')", 150), ("axo.setState('victory')", 150), ("axo.setState('pound')", 150), ("axo.setState('jetpack')", 150), ("axo.setState('crouch')", 150), ("axo.setState('stand')", 150), ("axo.setState('pound')", 120), ("axo.setState('power')", 120), ("axo.setState('jetpack')", 120), ("axo.setState('victory')", 120), ("axo.setState('stand')", 120)]),
  ('stand -> crawl', "axo.setState('stand'); axo.step(1/60,120)", [("axo.setState('crawl')", 150)]),
  ('crawl -> stand', "axo.setState('crawl'); axo.step(1/60,150)", [("axo.setState('stand')", 150)]),
  ('crawl -> jetpack', "axo.setState('crawl'); axo.step(1/60,150)", [("axo.setState('jetpack')", 150)]),
  ('crawl -> pound', "axo.setState('crawl'); axo.step(1/60,150)", [("axo.setState('pound')", 150)]),
  ('crawl -> crouch', "axo.setState('crawl'); axo.step(1/60,150)", [("axo.setState('crouch')", 150)]),
  ('crouch -> crawl', "axo.setState('crouch'); axo.step(1/60,120)", [("axo.setState('crawl')", 150)]),
  ('pound -> crawl', "axo.setState('pound'); axo.step(1/60,120)", [("axo.setState('crawl')", 150)]),
  ('jetpack -> crawl', "axo.setState('jetpack'); axo.step(1/60,120)", [("axo.setState('crawl')", 150)]),
  ('jump crawl', "axo.setState('crawl'); axo.step(1/60,150)", [('axo.A.jump()', 90)]),
  ('jump stand', "axo.setState('stand'); axo.step(1/60,120)", [('axo.A.jump()', 90)]),
]
async def main():
    t0 = time.time(); res = []
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width': 200, 'height': 200}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto(URL, timeout=600000); await pg.wait_for_function('window.ready', timeout=600000)
        await pg.evaluate('window.POPV = { visibleOnly: %s }' % ('false' if os.environ.get('VIS', '1') == '0' else 'true'))
        await pg.add_script_tag(content=open(os.path.join(HERE, 'popdetect.js')).read())
        for label, setup, steps in SCEN:
            if ONLY and ONLY not in label: continue
            await pg.evaluate(f'axo.A.motion.turn=0; axo.A.motion.speed=1; axo.A.motion.exert=0; {setup}')
            await pg.evaluate(f'POP.reset({json.dumps(label)})')
            for js, n in steps:
                if js: await pg.evaluate(js)
                await pg.evaluate(f'POP.cont({n})')
            s = await pg.evaluate('POP.summary()'); s['series'] = await pg.evaluate('POP.rec.series'); s['events'] = await pg.evaluate('POP.rec.events.slice(0, 60000)')
            res.append(s)
            tot = s['totals']; print(f"{label:22s} frames {s['frames']:4d}  vel {tot.get('vel', 0):6d}  flip {tot.get('flip', 0):5d}  area {tot.get('area', 0):5d}  inv {tot.get('inv', 0):5d}", flush=True)
        await b.close()
    json.dump(res, open(OUT, 'w')); print('errors', errs[:3], 'time', round(time.time() - t0, 1), 's')
asyncio.run(main())
