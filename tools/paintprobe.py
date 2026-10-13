"""What the page repaints every frame outside the canvas, per HUD state: you burning in the sun, low on paint, giant, the orb pointer
on the screen edge, refilling in a basin, rain. From a trace: repaints per frame, area repainted per frame (CSS px, x DPR^2 for device
pixels) and which elements. The canvas itself isn't drawn (render stubbed), so only the page's own work shows.
usage: paintprobe.py <stage> <tag> [secs per state]"""
import asyncio, json, os, sys, collections
from playwright.async_api import async_playwright
STAGE = sys.argv[1]; TAG = sys.argv[2]; SEC = float(sys.argv[3]) if len(sys.argv) > 3 else 3
PAGE = os.environ.get('PAGE', 'pc_perf.html')
UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1'
STATES = [
  ('plain', "P.paint = 0.9; P.giantT = 0; setWx('clear', 1000);"),
  ('low paint', "P.paint = 0.15; setWx('clear', 1000);"),
  ('burning (sun)', "P.paint = 0.6; setWx('sun', 1000); hardPhase = true; P.sunGrace = 0; P.st = 'play'; P.dryT = 0; P.dry = false;"),
  ('burning + low', "P.paint = 0.12; setWx('sun', 1000); P.sunGrace = 0; P.st = 'play'; P.dryT = 0; P.dry = false;"),
  ('in a basin', "setWx('clear', 1000); P.paint = 0.5; if (P.st !== 'hide') { const p = pots.find(q => potUp(q) && !q.occ); if (p) enterPot(P, p); } if (P.pot) P.pot.ink = 1;"),
  ('giant', "setWx('clear', 1000); P.giantT = 8; P.paint = 0.9;"),
  ('orb ptr edge', "P.giantT = 0; P.paint = 0.9; if (!orb.on) orbSpawn(); orb.x = P.x - Math.sin(P.yaw) * 20; orb.z = P.z - Math.cos(P.yaw) * 20; orb.tx = orb.x; orb.tz = orb.z; orb.stay = true;"),
  ('rain', "orbReset(); setWx('rain', 1000); P.paint = 0.9;"),
]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        DPR = float(os.environ.get('DPR', 3))
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=DPR, has_touch=True, is_mobile=True, user_agent=UA)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', stage:'%s', seen:{look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1}, drops: 50, runs: 9, flings: 50, tut: { ph: 'done' } })); } catch (e) {}" % STAGE)
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/' + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object"', timeout=300000)
        await pg.evaluate("__T.start()"); await pg.wait_for_function("__T.state === 'play'", timeout=300000)
        await pg.evaluate("(() => { __T.renderer.render = () => {}; __T.ev('inShadow = () => false'); window.__hold = ''; setInterval(() => { if (__hold) __T.ev(__hold); }, 100); window.__fc = 0; (function f() { window.__fc++; requestAnimationFrame(f); })(); })()")  # (states held: the game would move on)
        cdp = await ctx.new_cdp_session(pg); await cdp.send('DOM.enable')
        events = []; done = asyncio.Event()
        cdp.on('Tracing.dataCollected', lambda e: events.extend(e['value'])); cdp.on('Tracing.tracingComplete', lambda e: done.set())
        await cdp.send('Tracing.start', {'categories': 'devtools.timeline,disabled-by-default-devtools.timeline', 'transferMode': 'ReportEvents'})
        frames = {}
        for name, js in STATES:
            await pg.evaluate(f"(() => {{ window.__hold = {json.dumps(js)}; __T.ev(__hold); }})()")
            await pg.wait_for_timeout(700)
            await pg.evaluate(f"console.timeStamp('PH:{name}'); window.__fc = 0;")
            await pg.wait_for_timeout(int(SEC * 1000))
            frames[name] = await pg.evaluate("window.__fc")
            await pg.evaluate(f"console.timeStamp('END:{name}')")
            print(name, 'classes:', await pg.evaluate("[document.getElementById('vig').className, document.getElementById('bar').className, document.getElementById('orbPtr').className]"))
        await cdp.send('Tracing.end'); await asyncio.wait_for(done.wait(), 120)
        marks = sorted([(e['ts'], e['args']['data']['message']) for e in events if e.get('name') == 'TimeStamp' and 'message' in e.get('args', {}).get('data', {})])
        spans = {}; cur = None
        for ts, msg in marks:
            if msg.startswith('PH:'): cur = (msg[3:], ts)
            elif msg.startswith('END:') and cur: spans[cur[0]] = (cur[1], ts); cur = None
        desc = {}
        async def who(nid):
            if nid in desc: return desc[nid]
            try:
                r = await cdp.send('DOM.describeNode', {'backendNodeId': nid}); n = r['node']; at = n.get('attributes', [])
                d = dict(zip(at[::2], at[1::2])); s = n.get('localName', '?') + ('#' + d['id'] if 'id' in d else '') + ('.' + '.'.join(d.get('class', '').split()) if d.get('class') else '')
            except Exception as e: s = f'node {nid}'
            desc[nid] = s; return s
        print(f'== {TAG} ({STAGE}) DPR {DPR}')
        for name, _ in STATES:
            t0, t1 = spans.get(name, (0, 0)); fr = max(1, frames.get(name, 1)); area = collections.Counter(); cnt = collections.Counter(); ms = collections.Counter()
            for e in events:
                if e.get('name') != 'Paint' or not (t0 <= e.get('ts', 0) <= t1): continue
                d = e.get('args', {}).get('data', {}); nid = d.get('nodeId'); cl = d.get('clip') or []
                a = 0
                if len(cl) >= 8: xs, ys = cl[0::2], cl[1::2]; a = (max(xs) - min(xs)) * (max(ys) - min(ys))
                k = nid or d.get('layerId') or '?'; area[k] += a; cnt[k] += 1; ms[k] += e.get('dur', 0) / 1000
            tot = sum(area.values())
            print('%-15s %4d frames | paints/frame %.2f | paint ms/frame %.3f' % (name, fr, sum(cnt.values()) / fr, sum(ms.values()) / fr))
            for k, c in cnt.most_common(6):
                nm = await who(k) if isinstance(k, int) else str(k)
                print('      %-60s x%.2f/frame  %.3f ms/frame' % (nm[:60], c / fr, ms[k] / fr))
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
