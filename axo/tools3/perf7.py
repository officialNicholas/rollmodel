# animation + look cost per character per frame (successor of axo2/perf2.py): Animator.update (pose, IK, inertialization, springs, the
# swap's two skeletons, the look / face / jelly uniforms) + the skeleton upload, per state, through both transitions and a jump.
#   python3 -I perf7.py [URL]
import asyncio, sys
from playwright.async_api import async_playwright
URL = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8811/t10/preview.html?manual'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width': 400, 'height': 400}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto(URL, timeout=600000); await pg.wait_for_function('window.ready', timeout=600000)
        r = await pg.evaluate('''() => { const A = axo.A, P = axo.P; const out = {};
          const tick = () => { A.update(1 / 60); for (const w in P.m) if (P.m[w].mesh.visible || A.mixU !== null) P.m[w].mesh.skeleton.update(); };
          const meas = (label, setup, N) => { setup(); for (let i = 0; i < 30; i++) tick(); const t0 = performance.now(); for (let i = 0; i < N; i++) tick(); out[label] = +((performance.now() - t0) / N).toFixed(3); };
          for (const st of ['stand', 'crawl', 'power', 'victory', 'pound', 'jetpack', 'crouch']) meas(st, () => { axo.setState(st); for (let i = 0; i < 150; i++) tick(); }, 1200);
          // transitions: the whole of each (fold, morph, settle), repeated
          const trans = (a, b) => { let t = 0, n = 0; for (let k = 0; k < 6; k++) { axo.setState(a); for (let i = 0; i < 120; i++) tick(); axo.setState(b); const t0 = performance.now(); for (let i = 0; i < 75; i++) tick(); t += performance.now() - t0; n += 75; } return +(t / n).toFixed(3); };
          out['stand->crawl'] = trans('stand', 'crawl'); out['crawl->stand'] = trans('crawl', 'stand');
          // the morph alone (both skeletons, both meshes)
          { let t = 0, n = 0; for (let k = 0; k < 6; k++) { axo.setState('stand'); for (let i = 0; i < 120; i++) tick(); axo.setState('crawl'); for (let i = 0; i < 14; i++) tick(); const t0 = performance.now(); for (let i = 0; i < 30; i++) tick(); t += performance.now() - t0; n += 30; } out['morph only'] = +(t / n).toFixed(3); }
          return out; }''')
        print('animation + look cost per character per frame (ms):'); [print(f'  {k:14s} {v:.3f}') for k, v in r.items()]
        print('  max', max(r.values()), 'ms; budget 0.5 ms;', 'errors:', errs[:3]); await b.close()
asyncio.run(main())
