(() => { const A = LAB.I.ax.A, P = A.P, nb = P.nb, prevQ = [], prevW = [], out = [], names = P.names;
  LAB.set('ramp', { v: 7, T: 9 }); LAB.step(10);
  const q = new THREE.Quaternion(), qi = new THREE.Quaternion(); let pr = null, prv = null;
  for (let f = 0; f < 540; f++) { LAB.step(1); const F = P.frames(A.pose), L = A.loco, root = A.pose.root.clone();
    const w = []; for (let i = 0; i < nb; i++) { if (prevQ[i]) { qi.copy(prevQ[i]).invert(); q.copy(F[i]).multiply(qi); const ang = 2 * Math.acos(Math.min(1, Math.abs(q.w))) * 60; w[i] = ang; } prevQ[i] = (prevQ[i] || new THREE.Quaternion()).copy(F[i]); }
    const rv = pr ? root.clone().sub(pr).multiplyScalar(60) : null; pr = root;
    if (prevW.length && w.length) for (let i = 0; i < nb; i++) { if (w[i] === undefined || prevW[i] === undefined) continue; const acc = Math.abs(w[i] - prevW[i]) * 60; out.push([acc, f, names[i], +w[i].toFixed(2), L && L.sl ? +L.sl.u.toFixed(2) : -1, L ? +(L.slK || 0).toFixed(2) : -1, +LAB.D.spd.toFixed(2)]); }
    if (rv && prv) { const ra = rv.clone().sub(prv).multiplyScalar(60).length(); out.push([ra * 3, f, 'ROOT(x3)', +rv.length().toFixed(2), L && L.sl ? +L.sl.u.toFixed(2) : -1, L ? +(L.slK || 0).toFixed(2) : -1, +LAB.D.spd.toFixed(2)]); }
    prv = rv; for (let i = 0; i < nb; i++) prevW[i] = w[i]; }
  out.sort((a, b) => b[0] - a[0]); const med = out.map(x => x[0]).sort((a, b) => a - b)[out.length >> 1];
  return 'median ' + med.toFixed(2) + '\n' + out.slice(0, 24).map(x => x.map(v => typeof v === 'number' ? +v.toFixed ? +(+v).toFixed(2) : v : v).join(' ')).join('\n'); })()
