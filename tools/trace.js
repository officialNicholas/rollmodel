(() => { const A = LAB.I.ax.A, P = A.P, I = A.I, rows = []; LAB.set('ramp', { v: 7, T: 9 }); LAB.step(10);
  const q = new THREE.Quaternion(), qi = new THREE.Quaternion(); let prev = null; const ti = P.idx['thigh.L'], si = P.idx['shin.L'], fi = P.idx['foot.L'];
  for (let f = 0; f < 110; f++) { LAB.step(1); const F = P.frames(A.pose), pos = P.fk('crawl', A.pose), L = A.loco, l = L.limbs.find(x => x.en === 'foot.L');
    let w = 0; if (prev) { qi.copy(prev).invert(); q.copy(F[ti]).multiply(qi); w = 2 * Math.acos(Math.min(1, Math.abs(q.w))) * 57.3; } prev = (prev || new THREE.Quaternion()).copy(F[ti]);
    const hip = pos[ti], kn = pos[si], ft = pos[fi], d = hip.distanceTo(ft), k = Math.acos(Math.max(-1, Math.min(1, kn.clone().sub(hip).normalize().dot(ft.clone().sub(kn).normalize())))) * 57.3;
    if (f >= 60) rows.push([f, l.st, (((L.ph + l.off) % 1 + 1) % 1).toFixed(2), 'w(deg/frame)', w.toFixed(1), 'tgt-hip', (l.p.clone().sub(hip).length()).toFixed(3), 'foot-hip', d.toFixed(3), 'len', l.len.toFixed(3), 'kneebend', k.toFixed(0), 'p', l.p.x.toFixed(2), l.p.y.toFixed(3), l.p.z.toFixed(2), 'ft', ft.x.toFixed(2), ft.y.toFixed(3), ft.z.toFixed(2)].join(' ')); }
  return rows.join('\n'); })()
