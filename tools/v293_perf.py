"""v293: a performance pass for phones, most of all in Graphics mode and in Showdown: less heat, the same look.

What a Showdown frame cost before (measured on the phone settings: four fighters, Graphics mode): about 11 ms of script a frame on a fast
desktop core, 74 draws and ~305k triangles in the main pass (57% of them the four characters), a 2048 shadow map, and the frame drawn into
a 4x multisampled HDR target at up to 2x the screen's points. Phones that hold 60 a second in the menus (where little is drawn) climbed the
quality ladder to its top (the floor mirror, the depth blur, the mid-frame see-through copy, 2x resolution on the newest iPhones) and
carried all of it into matches, stepping down only once frames were already late: hot, and then a hitch.

- A match budget on phones: in a match, the floor mirror and the mid-frame see-through copy (dear on a phone's graphics chip, hardly seen)
  stay off, and the resolution stops at 1.6x the screen's points (1.5x in Showdown, with four fighters). Menus keep everything.
- Warm phones ease off early: once the shell says the phone is warm (iOS "fair", before "serious"), a match drops the depth blur and a
  tenth of the resolution, so it doesn't get hot enough to throttle. It comes back as the phone cools.
- The scene's matrices: three.js worked out all ~2,000 objects' matrices every frame, hidden ones included. Now only what moved (or sits
  under something that moved) is worked out, and nothing under something hidden until it shows.
- Nothing is drawn behind the Strokes page (it covers the whole screen), as for the canvas picker and the events."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

MATRIX = r"""
// (v293) the scene's matrices, each frame: only what moved (or sits under something that moved) is worked out again, and nothing under
// something hidden (it's worked out the frame it shows). three.js otherwise recomputes every object's matrix every frame (~2,000 of them
// in a match, two thirds hidden: pools, other forms, other stages' pieces). Anything that builds a matrix another way (updateMatrix,
// updateWorldMatrix, a forced update) still gets a fresh one
{ const O = THREE.Object3D.prototype;
  O.updateMatrix = function () { this.matrix.compose(this.position, this.quaternion, this.scale); this.matrixWorldNeedsUpdate = true; this._trs = undefined; };
  O.updateMatrixWorld = function (force) {
    if (this.matrixAutoUpdate) {
      const p = this.position, q = this.quaternion, s = this.scale; let c = this._trs;
      if (c === undefined || c[0] !== p.x || c[1] !== p.y || c[2] !== p.z || c[3] !== q._x || c[4] !== q._y || c[5] !== q._z || c[6] !== q._w || c[7] !== s.x || c[8] !== s.y || c[9] !== s.z) {
        this.matrix.compose(p, q, s); this.matrixWorldNeedsUpdate = true; if (c === undefined) c = this._trs = new Float64Array(10);
        c[0] = p.x; c[1] = p.y; c[2] = p.z; c[3] = q._x; c[4] = q._y; c[5] = q._z; c[6] = q._w; c[7] = s.x; c[8] = s.y; c[9] = s.z;
      }
    }
    const par = this.parent;
    if (this.matrixWorldNeedsUpdate || force || par !== this._wp || (par !== null && par._wv !== this._wpv)) {
      if (this.matrixWorldAutoUpdate === true) { if (par === null) this.matrixWorld.copy(this.matrix); else this.matrixWorld.multiplyMatrices(par.matrixWorld, this.matrix); }
      this.matrixWorldNeedsUpdate = false; this._wv = (this._wv || 0) + 1; this._wp = par; this._wpv = par !== null ? par._wv : 0;
    }
    const ch = this.children;
    for (let i = 0, l = ch.length; i < l; i++) { const k = ch[i]; if (k.visible || force) k.updateMatrixWorld(force); }
  };
}
"""

def apply(s):
    # the matrices: right after the renderer is made (before anything is added to the scene)
    a = "const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' });\n"
    s = rep(s, a, a + MATRIX.lstrip('\n'))
    # the match budget and the early ease-off, applied through the ladder's own setter
    s = rep(s, """function setQ(n) {
  n = Math.max(0, Math.min(Q_LAD.length - 1, n)); qLvl = n; const q = Q_LAD[n];
  if (post) { post.mirror = q.mirror; post.dof = q.dof; post.bloom = q.bloom; post.grab = q.grab; }
  if (curPR !== q.pr) { curPR = q.pr; renderer.setPixelRatio(curPR); resize(); }""",
               """// (v293) a match's budget on a phone: no floor mirror or mid-frame copy, the resolution held at 1.6x the screen's points (1.5x with Showdown's
// four), and on a warm phone (the shell's "fair") no depth blur and a tenth less resolution, before it gets hot enough to throttle
let qInMatch = false;
const qWarm = () => !!(NATIVE && (NATIVE.thermal || 0) >= 1), qMatchPR = () => (isShow() ? 1.5 : 1.6) * (qWarm() ? 0.9 : 1);
function setQ(n) {
  n = Math.max(0, Math.min(Q_LAD.length - 1, n)); qLvl = n; const q = Q_LAD[n], inM = qInMatch = state !== 'menu', bud = inM && MOBILE;
  if (post) { post.mirror = q.mirror && !bud; post.dof = q.dof && !(bud && qWarm()); post.bloom = q.bloom; post.grab = q.grab && !bud; }
  const pr = bud ? Math.min(q.pr, Math.round(qMatchPR() * 100) / 100) : q.pr;
  if (curPR !== pr) { curPR = pr; renderer.setPixelRatio(curPR); resize(); }""")
    s = rep(s, "let n = qLvl; while (n < Q_LAD.length - 1 && !ok(Q_LAD[n])) n++; if (n !== qLvl) setQ(n); qClean = 0;",
               "let n = qLvl; while (n < Q_LAD.length - 1 && !ok(Q_LAD[n])) n++; setQ(n); qClean = 0; // (v293: always, so warming or cooling re-sets the match budget)")
    # into a match and back out: the budget follows (once, at the change)
    s = rep(s, "  tunePerf((t - last) / 1000);\n", "  tunePerf((t - last) / 1000); if ((state !== 'menu') !== qInMatch) setQ(qLvl); // (v293: a match's budget on, or off)\n")
    # the Strokes page covers the screen: nothing to draw behind it
    s = rep(s, "if (!(state === 'menu' && (menuPage === 'worlds' || menuPage === 'events'))) renderFrame();",
               "if (!(state === 'menu' && (menuPage === 'worlds' || menuPage === 'events' || menuPage === 'strokes'))) renderFrame();")
    return s
