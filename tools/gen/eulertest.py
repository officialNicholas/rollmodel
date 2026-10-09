import asyncio
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader'])
        pg = await b.new_page()
        await pg.goto('file://' + SP + 'pc_t.html', timeout=300000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=300000)
        r = await pg.evaluate("""() => { const T = __T.THREE, g = new T.Object3D(); g.rotation.set(0.6, Math.PI / 2, 0); g.updateMatrix();
          const fwd = new T.Vector3(0, 0, 1).applyMatrix4(g.matrix), up = new T.Vector3(0, 1, 0).applyMatrix4(g.matrix);
          return { fwd: fwd.toArray().map(v => +v.toFixed(3)), up: up.toArray().map(v => +v.toFixed(3)) }; }""")
        print(r); await b.close()
asyncio.run(main())
