"""What matches pay: the CPU brain drives your blob too (so you win about half), N matches in a mode, and the dabs each one paid.
usage: shpay.py page.html mode n [diff]"""
import asyncio, sys, json
from playwright.async_api import async_playwright
PAGE, MODE, N = sys.argv[1], sys.argv[2], int(sys.argv[3]); DIFF = sys.argv[4] if len(sys.argv) > 4 else 'medium'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/opt/pw-browsers/chromium', args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 640, 'height': 360})
        await ctx.route('**/*supabase.co/**', lambda r: r.abort()); await ctx.route('**/*fly.dev/**', lambda r: r.abort())
        await ctx.add_init_script("window.__tut = true; window.__skipIntro = true; window.__noReveal = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'land', name:'Dusk', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1,items:1}, runs: 20, xp: 5000, tut: { ph: 'done' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = lambda x: pg.evaluate('__T.ev(%s)' % json.dumps(x))
        await pg.goto('http://localhost:8765/' + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object"', timeout=300000, polling=1000); await pg.wait_for_timeout(4000)
        out = []
        for i in range(N):
            await ev("mode = %s; diff = %s; beginMatch(); 0" % (json.dumps(MODE), json.dumps(DIFF)))
            await pg.wait_for_function("__T.ev('state') === 'play'", timeout=120000, polling=500)
            await ev("aiReset(P); P.cpu = true; 0")
            t = 0
            while await ev("state") == 'play' and t < 900:
                await pg.wait_for_timeout(5000); t += 5
            await pg.wait_for_timeout(1500)
            r = await ev("JSON.stringify({ win: endInfo.win, drops: endInfo.drops, you: Math.round(endInfo.you), cpu: Math.round(endInfo.cpu), kos: endInfo.kos, best: endInfo.newBest, place: P.place, t: Math.round(runT) })")
            print(i, r, 'wall', t, flush=True); out.append(json.loads(r))
            await ev("toMenu(); 0"); await pg.wait_for_timeout(3000)
        print('mean drops', sum(o['drops'] for o in out) / len(out), 'errors', errs[:3]); await b.close()
asyncio.run(main())
