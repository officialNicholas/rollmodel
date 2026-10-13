"""Every CSS animation running, per game state (menu, play, burning in the sun, low paint, giant, orb pointer on the edge, basin, rain):
what it animates (anything but transform and opacity makes the page repaint each frame), whether its element can be seen at all, and
its size. usage: animaudit.py <stage>"""
import asyncio, json, os, sys
from playwright.async_api import async_playwright
STAGE = sys.argv[1] if len(sys.argv) > 1 else 'island'; PAGE = os.environ.get('PAGE', 'pc_perf.html')
UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1'
AUDIT = r"""(() => { const out = [];
  for (const a of document.getAnimations()) { if (a.playState !== 'running') continue; const t = a.effect && a.effect.target; if (!t) continue;
    const el = t.nodeType === 1 ? t : t.element || null; const pseudo = a.effect.pseudoElement || '';
    let props = new Set(); try { for (const k of a.effect.getKeyframes()) for (const p in k) if (!['offset', 'easing', 'composite', 'computedOffset'].includes(p)) props.add(p); } catch (e) {}
    const timing = a.effect.getTiming ? a.effect.getTiming() : {}; const inf = timing.iterations === Infinity;
    let vis = true, why = ''; for (let e = el; e && e.nodeType === 1; e = e.parentElement) { const cs = getComputedStyle(e); if (cs.display === 'none') { vis = false; why = 'display none'; break; } if (cs.visibility === 'hidden') { vis = false; why = 'hidden'; break; } if (+cs.opacity === 0 && !props.has('opacity')) { vis = false; why = 'opacity 0 (' + (e.id || e.className || e.tagName) + ')'; break; } }
    const r = el ? el.getBoundingClientRect() : { width: 0, height: 0 }; if (el && (r.right < 0 || r.bottom < 0 || r.left > innerWidth || r.top > innerHeight)) { vis = false; why = why || 'off screen'; }
    const name = (el ? (el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') + (typeof el.className === 'string' && el.className ? '.' + el.className.trim().split(/\s+/).join('.') : '')) : '?') + pseudo;
    const paints = [...props].filter(p => !['transform', 'opacity', 'translate', 'rotate', 'scale'].includes(p));
    out.push({ name, anim: a.animationName || a.id || '', props: [...props].join(','), paints: paints.join(','), inf, vis, why, w: Math.round(r.width), h: Math.round(r.height) }); }
  return out; })()"""
STATES = [
  ('menu (lobby)', None),
  ('play', "P.paint = 0.9;"),
  ('burning (sun)', "P.paint = 0.6; setWx('sun', 1000); P.sunGrace = 0; P.st = 'play'; P.dryT = 0; P.dry = false;"),
  ('low paint', "setWx('clear', 1000); P.paint = 0.15; P.dryT = 0; P.dry = false;"),
  ('in a basin', "setWx('clear', 1000); P.paint = 0.5; if (P.st !== 'hide') { const p = pots.find(q => potUp(q) && !q.occ); if (p) enterPot(P, p); } if (P.pot) P.pot.ink = 1;"),
  ('giant', "if (P.st === 'hide') exitPot(P); setWx('clear', 1000); P.giantT = 8; P.paint = 0.9;"),
  ('orb pointer at edge', "P.giantT = 0; if (!orb.on) orbSpawn(); orb.x = P.x - Math.sin(P.yaw) * 20; orb.z = P.z - Math.cos(P.yaw) * 20; orb.tx = orb.x; orb.tz = orb.z; orb.stay = true;"),
  ('rain', "orbReset(); setWx('rain', 1000); P.paint = 0.9;"),
  ('threat + dry', "setWx('clear', 1000); P.paint = 0; P.dry = true; P.dryT = 0.5; threat = { k: 'missile', F: H }; ['foePtr'].forEach(id => document.getElementById(id).classList.add('warn'));"),
  ('banner up', "banner('Rain!', 'Everyone speeds up');"),
]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True, user_agent=UA)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', stage:'%s', seen:{look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1}, drops: 50, runs: 9, flings: 50, tut: { ph: 'done' } })); } catch (e) {}" % STAGE)
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/' + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object"', timeout=300000)
        await pg.wait_for_timeout(2500)
        seen = {}
        for name, js in STATES:
            if js is not None:
                if await pg.evaluate("__T.state") != 'play':
                    await pg.evaluate("__T.start()"); await pg.wait_for_function("__T.state === 'play'", timeout=300000)
                    await pg.evaluate("(() => { __T.renderer.render = () => {}; __T.ev('inShadow = () => false'); window.__hold = ''; setInterval(() => { if (__hold) __T.ev(__hold); }, 100); })()")
                await pg.evaluate(f"(() => {{ window.__hold = {json.dumps(js)}; __T.ev(__hold); }})()")
                await pg.wait_for_timeout(1500)
            A = await pg.evaluate(AUDIT)
            print(f'== {name}: {len(A)} running animations')
            for a in sorted(A, key=lambda a: (not a['paints'], not a['vis'])):
                flag = ('REPAINTS ' if a['paints'] else 'compositor') + (' INVISIBLE(' + a['why'] + ')' if not a['vis'] else '')
                key = (a['name'], a['anim'])
                if key in seen and seen[key] == flag: continue
                seen[key] = flag
                print('   %-62s %-12s [%s] %s %s %dx%d' % (a['name'][:62], a['anim'][:12], a['props'][:40], 'inf' if a['inf'] else 'once', flag, a['w'], a['h']))
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
