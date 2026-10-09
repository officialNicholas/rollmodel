# The trail buffer uploads only what changed. three.js keeps one pending range per attribute, so two flushes before
# a render used to drop the first slice. Merge into the pending range instead.
p = '/home/claude/paint-the-canvas.html'
s = open(p).read()
old = """function flushTrail() {
  if (teamAllDirty) { teamAllDirty = false; dirtyV = 0; }
  if (dirtyV < nV) {
    const o = dirtyV, c = nV - dirtyV;
    aPos.updateRange.offset = o * 3; aPos.updateRange.count = c * 3; aPos.needsUpdate = true;
    aEdge.updateRange.offset = o; aEdge.updateRange.count = c; aEdge.needsUpdate = true;
    aTeam.updateRange.offset = o; aTeam.updateRange.count = c; aTeam.needsUpdate = true;
    aBirth.updateRange.offset = o; aBirth.updateRange.count = c; aBirth.needsUpdate = true;
    dirtyV = nV; paintGeo.setDrawRange(0, nV);
  }
}"""
new = """// three.js uploads one range per attribute at the next render (count -1 once it has gone up), so a second flush before
// that render widens the waiting range rather than replacing it, or the first stretch of paint never reaches the screen
function upRange(a, o, c) {
  const r = a.updateRange;
  if (r.count === -1) { r.offset = o; r.count = c; } else { const e = Math.max(r.offset + r.count, o + c); r.offset = Math.min(r.offset, o); r.count = e - r.offset; }
  a.needsUpdate = true;
}
function flushTrail() {
  if (teamAllDirty) { teamAllDirty = false; dirtyV = 0; }
  if (dirtyV < nV) {
    const o = dirtyV, c = nV - dirtyV;
    upRange(aPos, o * 3, c * 3); upRange(aEdge, o, c); upRange(aTeam, o, c); upRange(aBirth, o, c);
    dirtyV = nV; paintGeo.setDrawRange(0, nV);
  }
}"""
assert s.count(old) == 1, s.count(old)
s = s.replace(old, new)
open(p, 'w').write(s)
print('ok')
