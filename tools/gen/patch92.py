p='/home/claude/paint-the-canvas.html'
s=open(p).read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:90]); s=s.replace(a,b)
rep("  const nx = B.x - A.x, nz = B.z - A.z, d = Math.hypot(nx, nz) || 1; A.yaw = Math.atan2(-nx / d, -nz / d) + (Math.random() - 0.5) * 0.6; A.spd *= 0.4; A.squash = Math.max(A.squash, 0.5);",
    "  // the roller doesn't bounce off: a beat of hit stop, then it carries straight on through, same heading, same speed\n  A.passT = 0.45; A.squash = Math.max(A.squash, 0.35); A.wob = Math.max(A.wob, 0.6);")
rep("  if (P.flatT > 0 || H.flatT > 0) return; // roll right over a pancake",
    "  if (P.flatT > 0 || H.flatT > 0) return; // roll right over a pancake\n  if ((P.stunT > 0 && H.passT > 0) || (H.stunT > 0 && P.passT > 0)) return; // the roller that just stunned it rolls on through")
rep("  if (D.stunT > 0) { D.stunT -= dt;", "  if (D.passT > 0) D.passT -= dt;\n  if (D.stunT > 0) { D.stunT -= dt;")
open(p,'w').write(s); print('ok')
