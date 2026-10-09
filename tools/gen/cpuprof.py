# a CPU profile (Chrome's own sampler) of game steps + visuals in a paint-heavy match, clear vs raining: self time by function
import asyncio, sys, json, collections
from playwright.async_api import async_playwright
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
GFX = sys.argv[1] if len(sys.argv) > 1 else 'hi'; STAGE = sys.argv[2] if len(sys.argv) > 2 else 'island'; SECS = float(sys.argv[3]) if len(sys.argv) > 3 else 70; PAGE = sys.argv[4] if len(sys.argv) > 4 else 'pc_t.html'
SETUP = """([stage, secs]) => { const T = __T, R = T.renderer; window.__noLoop = true;
  Math.random = (() => { let s = 777; return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; })();
  T.mode = 'trio'; T.applyMode(); T.genWorld(4242, { themes: [stage] }); T.mapUsed = false; T.setDiff('hard'); T.start();
  T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
  T.aiReset(T.P); T.setWx('clear', 999); const dt = 1 / 60, n = Math.round(secs / dt);
  for (let i = 0; i < n && T.state === 'play'; i++) { T.aiStep(T.P, dt); T.steerIn = T.P.steer; T.step(dt); if (i % 20 === 0) { T.visuals(dt * 20, dt * 20); T.flushTrail(); } T.matchLeft = 99; }
  return T.chunkN; }"""
RUN = """([n, rain]) => { const T = __T, dt = 1 / 60; T.setWx(rain ? 'rain' : 'clear', 999);
  for (let i = 0; i < n; i++) { T.aiStep(T.P, dt); T.steerIn = T.P.steer; T.step(dt); T.matchLeft = 99; T.visuals(dt, dt); T.flushTrail(); } return T.chunkN; }"""
def summarize(prof, top=28):
    nodes = {n['id']: n for n in prof['nodes']}; self_t = collections.Counter()
    dts = prof['timeDeltas']; samples = prof['samples']
    for sid, d in zip(samples, dts): n = nodes[sid]; cf = n['callFrame']; self_t[(cf['functionName'] or '(anon)') + ':' + str(cf['lineNumber'])] += d
    tot = sum(self_t.values()) or 1
    return [(k, round(v / 1000, 1), round(100 * v / tot, 1)) for k, v in self_t.most_common(top)], round(tot / 1000)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 200, 'height': 400}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};')
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: '" + GFX + "', mode: 'trio', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1} })); } catch (e) {}")
        pg = await ctx.new_page(); await pg.goto(SP + PAGE, timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
        print('paint verts', await pg.evaluate(SETUP, [STAGE, SECS]))
        cdp = await ctx.new_cdp_session(pg); await cdp.send('Profiler.enable'); await cdp.send('Profiler.setSamplingInterval', {'interval': 200})
        for rain in (False, True):
            await cdp.send('Profiler.start'); await pg.evaluate(RUN, [400, rain]); prof = (await cdp.send('Profiler.stop'))['profile']
            rows, tot = summarize(prof); print('==', 'rain' if rain else 'clear', 'total ms', tot)
            for r in rows: print('  ', r)
        await b.close()
asyncio.run(main())
