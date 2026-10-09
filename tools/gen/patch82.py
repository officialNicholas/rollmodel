p='/home/claude/paint-the-canvas.html'
s=open(p).read()
a="saved: feat.map(D => ({ D, x: D.x, y: D.y, z: D.z, yaw: D.yaw, st: D.st, paint: D.paint, vis: lookRoot(D).visible })) };"
b="saved: feat.map(D => ({ D, x: D.x, y: D.y, z: D.z, yaw: D.yaw, st: D.st, paint: D.paint, power: D.power, vis: lookRoot(D).visible })) };"
assert s.count(a)==1; s=s.replace(a,b)
a="st: 'play', paint: 1, giantT: 0, slam: false, missile: false, charging: false, flatT: 0, stunT: 0, rollT: 0, immuneT: 0, air: false, vy: 0, exposed: false, dry: false, dilT: 0, spd: 0, turn: 0, squash: 0, wob: 0 });\n    lookRoot(D).visible = true; vicLayer(D, true);"
b="st: 'play', paint: 1, power: null, giantT: 0, slam: false, missile: false, charging: false, flatT: 0, stunT: 0, rollT: 0, immuneT: 0, air: false, vy: 0, exposed: false, dry: false, dilT: 0, spd: 0, turn: 0, squash: 0, wob: 0 });\n    const V = D === P ? VP : D.look.V; Object.assign(V.look, { spd: 0, lean: 0, drop: 0, flat: 1, roll: 0 }); V.flatK = 0; V.gk = 1; V.misK = 0; // its plain round self, not mid-roll or still a roller\n    lookRoot(D).visible = true; vicLayer(D, true);"
assert s.count(a)==1; s=s.replace(a,b)
a="Object.assign(D, { x: s0.x, y: s0.y, z: s0.z, yaw: s0.yaw, st: s0.st, paint: s0.paint });"
b="Object.assign(D, { x: s0.x, y: s0.y, z: s0.z, yaw: s0.yaw, st: s0.st, paint: s0.paint, power: s0.power });"
assert s.count(a)==1; s=s.replace(a,b)
open(p,'w').write(s); print('ok')
