import asyncio, json, sys
PAGE = sys.argv[1]
sys.argv = ['x', PAGE, 'none', 'dbg']
exec(open('tools/anim252.py').read().split("SCN = {")[0])
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx, pg, errs = await boot(b, SAVE)
        for act in ['bounce', 'doze', 'sneeze', 'wave', 'shake', 'proud', 'blep', 'peek']:
            await pg.evaluate(f"window.__idleForce = '{act}'")
            for i in range(30):
                st = await pg.evaluate("__T.ev(`JSON.stringify([idle.act, +idle.u.toFixed(2), +idle.t.toFixed(2), state, menuPage, !!lookIntro, !!vic, menuReact, !!lkDip, AXOC.S.ready, IDLE_ACTS.length, idle.face])`)")
                if json.loads(st)[0] == act: break
                await pg.wait_for_timeout(400)
            print(act, st)
            await pg.wait_for_timeout(1500)
        print('errors', errs[:5]); await b.close()
asyncio.run(main())
