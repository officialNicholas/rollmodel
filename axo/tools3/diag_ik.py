import asyncio, json, sys
from playwright.async_api import async_playwright
URL = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8811/v6/preview.html?manual'
JS = r'''() => { const A = axo.A, P = axo.P, I = A.I; axo.A.motion.speed = 1; axo.setState('crawl'); axo.step(1/60, 150); const out = [];
  const THREE_V = (v) => [+v.x.toFixed(3), +v.y.toFixed(3), +v.z.toFixed(3)];
  for (let f = 0; f < 60; f++) { axo.step(1/60, 1); const pos = P.fk('crawl', A.pose); const Fp = P.frames(A.pose); const row = { f, ph: +(((A.gait) / (2 * Math.PI)) % 1).toFixed(3) };
    for (const s of ['L', 'R']) { const th = I['thigh.' + s], sh = I['shin.' + s], ft = I['foot.' + s]; const c = A.pose.contacts['foot.' + s];
      const hip = pos[th], knee = pos[sh], ank = pos[ft]; const n = c.t.clone().sub(hip).normalize(); const pole = c.pole.clone(); const p = pole.clone().addScaledVector(n, -n.dot(pole));
      // shin's canonical Z (ventral / flexion side) and X (hinge) in world
      const qz = new (hip.constructor)(0, 0, 1).applyQuaternion(Fp[sh]); const qx = new (hip.constructor)(1, 0, 0).applyQuaternion(Fp[sh]); const tz = new (hip.constructor)(0, 0, 1).applyQuaternion(Fp[th]);
      row[s] = { knee: THREE_V(knee), ank: THREE_V(ank), tgt: THREE_V(c.t), pl: +p.length().toFixed(3), shinZ: THREE_V(qz), thighZ: THREE_V(tz), d: +c.t.distanceTo(hip).toFixed(3) }; }
    out.push(row); }
  return out; }'''
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width': 200, 'height': 200}); await pg.goto(URL); await pg.wait_for_function('window.ready')
        r = await pg.evaluate(JS)
        for row in r:
            print(row['f'], row['ph'], ' R knee', row['R']['knee'], 'tgt', row['R']['tgt'], 'pl', row['R']['pl'], 'd', row['R']['d'], 'shinZ', row['R']['shinZ'], 'thighZ', row['R']['thighZ'])
        print()
        for row in r:
            print(row['f'], row['ph'], ' L knee', row['L']['knee'], 'tgt', row['L']['tgt'], 'pl', row['L']['pl'], 'd', row['L']['d'], 'shinZ', row['L']['shinZ'], 'thighZ', row['L']['thighZ'])
        await b.close()
asyncio.run(main())
