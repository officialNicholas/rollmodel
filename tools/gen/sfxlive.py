# the game over http: the sheets download, decode and calibrate; effects and voices play through the real engine without errors
import asyncio, sys, json
from playwright.async_api import async_playwright
U = 'http://127.0.0.1:8765/pc_http.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844})
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'lo', unlockAll: 1, seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); logs = []
        pg.on('console', lambda m: logs.append(m.text[:200]) if m.type in ('error', 'warning') else None)
        reqs = []; pg.on('requestfinished', lambda r: reqs.append(r.url.split('/')[-1]) if 'sfxbank' in r.url else None)
        await pg.goto(U, timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.AU', polling=200, timeout=300000)
        await pg.wait_for_timeout(4000)
        print('before tap', await pg.evaluate('__T.AU._sbOn()'), reqs)
        await pg.evaluate('__T.AU.init()')
        for i in range(30):
            on = await pg.evaluate('__T.AU._sbOn()')
            if on['m'] and on['s']: break
            await pg.wait_for_timeout(300)
        print('after tap', on, 'state', await pg.evaluate('__T.AU.state'))
        # every effect through the wrapper, and the voice
        r = await pg.evaluate("""async () => { const A = __T.AU, out = {}; const calls = [['go'],['ui'],['nope'],['jump'],['land',0.3],['land',0.9],['splat',0.4],['splat',1],['splat',1.4],['slam'],['quake'],['burst',1],['fling',0.2],['fling',0.6],['fling',1],['whoosh'],['swish'],['rocket'],['alert'],['dash'],['brake'],['notch',1],['notch',2],['notch',3],['release'],['enter'],['glug',0.5],['pop'],['power'],['orb'],['grow'],['shrink'],['die','sun'],['die','pound'],['die','dry'],['die','x'],['fall'],['squish'],['bonk',0.2],['bonk',1],['spot'],['ready'],['lead',true],['lead',false],['danger'],['low'],['count',5],['count',2],['tick',7],['horn'],['cd',3],['sting','win'],['sting','lose'],['sting','draw'],['turret'],['shoot'],['plop'],['ball'],['boost'],['fanfare'],['thunder'],['heatWarn'],['heatOn'],['dusk'],['splashWater'],['sprinkle',1],['sink'],['rumble'],['rise'],['flip'],['flipBack']];
          for (const c of calls) { try { A[c[0]].apply(null, c.slice(1)); out[c[0]] = 'ok'; } catch (e) { out[c[0]] = String(e); } }
          for (const v of ['whee','hup','hyah','oof','waah','yay','ooh','giggle','eep','brr','hoh','ahh']) { await new Promise(r => setTimeout(r, 500)); out['vox_' + v] = A.vox(v); }
          A.chargeStart(); A.chargeSet(0.5); A.chargeSet(1); A.chargeStop(); A.roll(4, 0); A.roll(4, 1); A.roll(0, 0); A.rain(0.5); A.rain(0); A.sizzle(1); A.sizzle(0);
          return out; }""")
        bad = {k: v for k, v in r.items() if v not in ('ok', True)}
        print('calls', len(r), 'bad', bad)
        print('errors', errs[:5], 'console', [l for l in logs if 'sfx' in l.lower() or 'audio' in l.lower()][:5], 'requests', reqs)
        await b.close()
asyncio.run(main())
