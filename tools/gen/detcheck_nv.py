# a seeded 3-way match played out the same way twice gives the same result: run on two builds to check a refactor changed nothing. Prints
# where every blob is every 100 frames (rounded) and a hash of the lot
import asyncio, sys, json, hashlib
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 160, 'height': 240}, device_scale_factor=1)
        await ctx.add_init_script("window.__noLoop = true; Math.random = (() => { let s = 99; return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; })();")
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'lo', mode: 'trio', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300]))
        await pg.goto('file://' + SP + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(800)
        out = []
        for stage in ['island', 'crypt']:
            r = await pg.evaluate("""(stage) => { const T = __T, P = T.P; window.__noLoop = true;
              T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
              Math.random = (() => { let s = 4242; return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; })();
              T.clock = 0; T.mode = 'trio'; T.applyMode(); T.setStage(stage === 'island' ? 'island' : 'season'); T.genWorld(5150, { themes: [stage] }); T.mapUsed = false; T.start(); T.setWx('clear', 999); T.aiReset(P);
              const rec = [];
              for (let i = 0; i < 1800; i++) { T.aiStep(P, 1 / 60); T.steerIn = P.steer; T.step(0.0083); T.step(0.0083); T.matchLeft = 99;
                if (i % 100 === 99) rec.push(T.ACTIVE.map(D => [D.x.toFixed(4), D.z.toFixed(4), D.y.toFixed(3), D.st, D.ai ? D.ai.mode : '-']).flat().join(',')); }
              return rec; }""", stage)
            out += r
        h = hashlib.md5('|'.join(out).encode()).hexdigest()
        print(PAGE, 'hash', h); print(out[5][:160]); print(out[-1][:160]); print('errors', errs[:3]); await b.close()
asyncio.run(main())
