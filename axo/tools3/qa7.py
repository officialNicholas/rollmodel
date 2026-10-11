# v7 QA (successors of axo2/diag_final.py, finalcheck.py, qa_stretch.py), run on the final runtimes:
#   diag      both previews (dev ws/axo2, merged ws/axo) load and report no page or console errors
#   final     every state on the merged runtime ends in the right state / mesh; the API calls of the brief all run (Look: setIris,
#             setEyeStyle, setExpression, emoteFor, flutter, blink, setPaint, setColor, setFangs, attachEyes (no-op); Animator: jump, look)
#   stretch   CPU-skinned (dual quaternions, as the GPU) edge stretch per body region through every state, a crawl at three speeds, turning,
#             jumps and both transitions; only what is drawn counts (the swap's dither share, as the pop detector)
#   python3 -I qa7.py [BASE=http://localhost:8811]
import asyncio, json, sys, os, base64
from playwright.async_api import async_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8811'
PAGES = {'dev': BASE + '/dev/preview.html?manual', 'merged': BASE + '/merged/preview.html?manual'}
if os.environ.get('ONLYDEV'): PAGES = {'dev': os.environ.get('DEVURL', PAGES['dev'])}
STRETCH_JS = r'''(() => { const A = axo.A, MS = { stand: axo.S, crawl: axo.C }, R = POP.prep; const out = { worst: {}, bad: [], frames: 0 };
  const E = {}; for (const w in MS) { const I = R[w].I, set = new Set(), e = []; for (let t = 0; t < I.length; t += 3) for (const [a, b] of [[I[t], I[t + 1]], [I[t + 1], I[t + 2]], [I[t + 2], I[t]]]) { const k = a < b ? a * 65536 + b : b * 65536 + a; if (!set.has(k)) { set.add(k); e.push(a < b ? a : b, a < b ? b : a); } }
    const p0 = R[w].p0, L0 = new Float32Array(e.length / 2); for (let k = 0; k < L0.length; k++) { const a = e[2 * k], b = e[2 * k + 1]; L0[k] = Math.hypot(p0[a * 3] - p0[b * 3], p0[a * 3 + 1] - p0[b * 3 + 1], p0[a * 3 + 2] - p0[b * 3 + 2]); } E[w] = { e, L0 }; }
  const judge = (label) => { out.frames++; for (const w in MS) { const M = MS[w]; if (!M.mesh.visible) continue; const p = POP._skin(w), cv = POP._cover(w), { e, L0 } = E[w], reg = R[w].reg; let fmax = 0;
      for (let k = 0; k < L0.length; k++) { const a = e[2 * k], b = e[2 * k + 1]; if (L0[k] < 0.004 || cv[a] < 0.02 || cv[b] < 0.02) continue;
        const L = Math.hypot(p[a * 3] - p[b * 3], p[a * 3 + 1] - p[b * 3 + 1], p[a * 3 + 2] - p[b * 3 + 2]); if (L - L0[k] < 0.02) continue; const r = L / L0[k];
        const key = w + ':' + reg[a]; if (r > (out.worst[key] || 1)) out.worst[key] = +r.toFixed(2); if (r > fmax) fmax = r; const lk = label + '|' + w + ':' + reg[a]; if (r > ((out.byLabel = out.byLabel || {})[lk] || 1)) out.byLabel[lk] = +r.toFixed(2); }
      if (fmax > 1.8) out.bad.push([label, w, +fmax.toFixed(2)]); } };
  const run = (label, setup, steps, every) => { A.motion.turn = 0; A.motion.speed = 1; A.motion.exert = 0; setup(); for (const [fn, n] of steps) { fn(); for (let f = 0; f < n; f++) { axo.step(1 / 60, 1); if (f % every === 0) judge(label); } } };
  for (const st of ['stand', 'power', 'victory', 'pound', 'jetpack', 'crouch']) run(st, () => { axo.setState('stand'); axo.step(1 / 60, 90); }, [[() => axo.setState(st), 180], [() => A.jump(), 90]], 3);
  for (const sp of [0.5, 1, 1.5]) run('crawl x' + sp, () => { A.motion.speed = sp; axo.setState('crawl'); axo.step(1 / 60, 150); }, [[() => {}, 120]], 2);
  run('crawl turning', () => { axo.setState('crawl'); axo.step(1 / 60, 150); }, [[() => A.motion.turn = 1, 90], [() => A.motion.turn = -1, 90], [() => A.motion.turn = 0, 30], [() => A.jump(), 90]], 2);
  run('stand->crawl', () => { axo.setState('stand'); axo.step(1 / 60, 120); }, [[() => axo.setState('crawl'), 120]], 1);
  for (const st of ['stand', 'pound', 'jetpack', 'crouch']) run('crawl->' + st, () => { axo.setState('crawl'); axo.step(1 / 60, 150); }, [[() => axo.setState(st), 120]], 1);
  run('reversal', () => { axo.setState('stand'); axo.step(1 / 60, 120); }, [[() => axo.setState('crawl'), 30], [() => axo.setState('stand'), 40], [() => axo.setState('crawl'), 120]], 1);
  return JSON.stringify(out); })()'''
FINAL_JS = r'''(() => { const out = { states: {}, api: [] }; const A = axo.A, L = axo.look;
  for (const st of ['stand', 'crawl', 'power', 'victory', 'pound', 'jetpack', 'crouch', 'crawl', 'stand']) { axo.setState(st); axo.step(1 / 60, 150); out.states[st + (out.states[st] ? '#2' : '')] = A.state + '/' + A.mesh; }
  const tryit = (name, fn) => { try { fn(); out.api.push(name + ': ok'); } catch (e) { out.api.push(name + ': ' + e.message); } };
  tryit('Look.setIris', () => { for (const k of ['brown', 'blue', 'green', 'violet', 'gold', '#ff8800']) L.setIris(k); });
  tryit('Look.setEyeStyle', () => { for (const k of ['round', 'edgy', 'dot', 'zombie', 0]) L.setEyeStyle(k); });
  tryit('Look.setExpression', () => { for (const k of ['neutral', 'happy', 'angry', 'hurt', 'glee', 'scared', 'yawn', 'dizzy', 'peek', 'leap', 'brace']) { L.setExpression(k); axo.step(1 / 60, 10); } L.setExpression('neutral'); });
  tryit('Look.emoteFor / flutter / blink', () => { L.emoteFor('glee', 0.5); L.flutter(2); L.blink(); axo.step(1 / 60, 60); });
  tryit('Look.setPaint / setColor / setFangs', () => { L.setPaint(0.5); L.setColor(0x2f8cff); L.setFangs(true); axo.step(1 / 60, 5); L.setPaint(0); L.setColor(0xff6b8a); L.setFangs(false); });
  tryit('Look.attachEyes (no-op since v7)', () => L.attachEyes());
  tryit('Animator.jump + look', () => { A.jump(); A.look.yaw = 20; A.look.pitch = -10; axo.step(1 / 60, 90); A.look.yaw = 0; A.look.pitch = 0; });
  axo.setState('stand'); axo.step(1 / 60, 150); return JSON.stringify(out); })()'''
async def main():
    res = {}
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for name, url in PAGES.items():
            pg = await b.new_page(viewport={'width': 420, 'height': 420}); errs = []
            pg.on('pageerror', lambda e, errs=errs: errs.append('pageerror: ' + str(e)[:300])); pg.on('console', lambda m, errs=errs: m.type in ('error', 'warning') and errs.append(m.type + ': ' + m.text[:300]))
            await pg.goto(url, timeout=600000); ok = True
            try: await pg.wait_for_function('window.ready', timeout=600000)
            except Exception as e: ok = False
            print(f'[diag] {name}: {"ready" if ok else "NOT READY"}; console errors / warnings: {errs[:6] or "none"}', flush=True)
            if ok and name == 'merged':
                r = json.loads(await pg.evaluate(FINAL_JS)); print('[final] states:', r['states']); print('[final] api:', '; '.join(r['api']))
                d = await pg.evaluate('axo.shot()'); open(HERE + '/out/v7_final_preview_shot.jpg', 'wb').write(base64.b64decode(d.split(',')[1]))
                print('[final] errors after the run:', errs[:6] or 'none', flush=True)
            if ok and name == 'dev':
                await pg.add_script_tag(content=open(HERE + '/popdetect.js').read())
                r = json.loads(await pg.evaluate(STRETCH_JS))
                print(f"[stretch] {r['frames']} frames judged; worst edge stretch per region (posed / rest, edges that grew by more than 2 cm, drawn only):")
                for w in ('stand', 'crawl'): print('   ', w, {k.split(':')[1]: v for k, v in sorted(r['worst'].items()) if k.startswith(w)})
                print(f"[stretch] frames with any drawn edge over 1.8x: {len(r['bad'])}", r['bad'][:10], flush=True)
                if os.environ.get('BYLABEL'):
                    import collections; g = collections.defaultdict(dict)
                    for k, v in r.get('byLabel', {}).items(): lab, reg = k.split('|'); g[lab][reg] = v
                    for lab, d in g.items(): print('     ', lab, {k: v for k, v in sorted(d.items(), key=lambda kv: -kv[1])[:6]})
            await pg.close()
        await b.close()
asyncio.run(main())
