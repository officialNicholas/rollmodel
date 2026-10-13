import asyncio, sys, collections
from playwright.async_api import async_playwright
UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1'
STAGE = sys.argv[1]; ROOT = sys.argv[2] if len(sys.argv) > 2 else 'aiThink'; MODE = sys.argv[3] if len(sys.argv) > 3 else 'duel'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 195, 'height': 422}, device_scale_factor=1, has_touch=True, is_mobile=True, user_agent=UA)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', stage:'%s', seen:{look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1}, drops: 50, runs: 9, flings: 50, tut: { ph: 'done' } })); } catch (e) {}" % STAGE)
        pg = await ctx.new_page()
        await pg.goto('http://localhost:8765/pc_h.html', timeout=300000); await pg.wait_for_function('typeof __T === "object"', timeout=300000)
        await pg.evaluate(f"__T.mode = '{MODE}'; __T.applyMode(); __T.start()"); await pg.wait_for_function("__T.state === 'play'", timeout=300000)
        await pg.evaluate("(() => { __T.P.cpu = true; __T.aiReset(__T.P); __T.renderer.render = () => {}; })()")
        cdp = await ctx.new_cdp_session(pg); await cdp.send('Profiler.enable'); await cdp.send('Profiler.setSamplingInterval', {'interval': 100}); await cdp.send('Profiler.start')
        await pg.wait_for_timeout(30000)
        prof = (await cdp.send('Profiler.stop'))['profile']
        nodes = {n['id']: n for n in prof['nodes']}; parent = {}
        for n in prof['nodes']:
            for c in n.get('children', []): parent[c] = n['id']
        key = lambda n: f"{n['callFrame']['functionName'] or '(anon)'}:{n['callFrame']['lineNumber'] + 1}"
        under = collections.Counter(); tot_root = 0; selfc = collections.Counter(); childc = collections.Counter()
        for sid, dt in zip(prof['samples'], prof['timeDeltas']):
            chain = []; cur = sid
            while cur is not None: chain.append(nodes[cur]); cur = parent.get(cur)
            names = [n['callFrame']['functionName'] for n in chain]
            if ROOT in names:
                tot_root += dt; selfc[key(chain[0])] += dt
                i = names.index(ROOT)
                if i > 0: childc[key(chain[i - 1])] += dt
                else: childc['(self)'] += dt
        print(f'{STAGE}: time under {ROOT} {tot_root / 1000:.0f} ms of {sum(prof["timeDeltas"]) / 1000:.0f} ms sampled')
        print(' direct children of', ROOT); [print('   %6.1f ms  %s' % (v / 1000, k)) for k, v in childc.most_common(14)]
        print(' self time under it'); [print('   %6.1f ms  %s' % (v / 1000, k)) for k, v in selfc.most_common(14)]
        await b.close()
asyncio.run(main())
