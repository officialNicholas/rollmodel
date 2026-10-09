import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':390,'height':780}); await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{} })); } catch (e) {}")
        pg = await ctx.new_page(); await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000)
        print(await pg.evaluate("""() => { const out = {}; for (const [fov, R] of [[70, 27.4], [60, 27.4], [70, 34], [60, 34]]) { const c = new THREE.PerspectiveCamera(fov, 1, 1, 500); let x0=9,x1=-9,y0=9,y1=-9; const v = new THREE.Vector3();
          for (let k = 0; k < 48; k++) { const yw = k/48*Math.PI*2, fx = Math.sin(yw), fz = Math.cos(yw); c.position.set(-fx*31, 37, -fz*31); c.up.set(0,1,0); c.lookAt(fx*3,-12,fz*3); c.updateMatrixWorld();
            for (const [cx, cz] of [[R,R],[R,-R],[-R,R],[-R,-R]]) { v.set(cx,0,cz).project(c); x0=Math.min(x0,v.x);x1=Math.max(x1,v.x);y0=Math.min(y0,v.y);y1=Math.max(y1,v.y); } }
          out[fov+'/'+R] = {x0:+x0.toFixed(3),x1:+x1.toFixed(3),y0:+y0.toFixed(3),y1:+y1.toFixed(3), aspect:+((x1-x0)/(y1-y0)).toFixed(3), cy:+((y0+y1)/2).toFixed(3)}; } return out; }"""))
        await b.close()
asyncio.run(main())
