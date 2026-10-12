#!/usr/bin/env python3
"""v240: a real wet-dog shake. Asked to shake, the axolotl twists about its own length, fast, a wave running from the head back down the
trunk to the tail, biggest at the head and the tail tip, dying out over most of a second; the body drops a touch into it. (Before, a
shake was only a flick of the gills and the tail.)"""
P = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/tools/assets/axolife.js'
s = open(P).read()
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep("Animator.prototype.pitchTurn = function (pose, i, a) {",
    """const AXY = new THREE.Vector3(0, 1, 0);
Animator.prototype.rollTurn = function (pose, i, a) { if (!a) return; const F = LQ2.copy(this.P.frames(pose)[i]).normalize(); LQ.setFromAxisAngle(AXY, a); LQ3.copy(F).invert().multiply(LQ).multiply(F); pose.q[i].multiply(LQ3).normalize(); }; // (a twist about the bone's own length)
Animator.prototype.shake = function (k) { const L = this.loco || this.initLoco(); L.shk = { t: 0, k: k === undefined ? 1 : k }; };
// the shake: a fast twist about its length, a wave from the head back to the tail tip, over most of a second
Animator.prototype.stepShake = function (out, dt) {
  const L = this.loco, K = L && L.shk; if (!K) return; K.t += dt; const T = 0.9; if (K.t >= T) { L.shk = null; return; }
  const u = K.t / T, env = Math.sin(Math.min(1, u * 4) * Math.PI / 2) * Math.pow(1 - u, 1.3) * K.k, w = 2 * Math.PI * 9.5 * K.t, I = this.I, sp = this.chain.spine, tl = this.chain.tail;
  const tw = (i, A, lag) => this.rollTurn(out, i, A * env * Math.sin(w - lag) * Math.PI / 180);
  tw(I.head, 17, 0); tw(sp[4], 11, 0.35); tw(sp[3], 8, 0.7); tw(sp[2], 5, 1.05); tw(sp[1], 3.5, 1.4); tw(sp[0], 2, 1.75);
  for (let k = 0; k < 6; k++) tw(tl[k], 6 + 1.6 * k, 2.1 + 0.5 * k);
  this.worldTurn(out, I.head, 7 * env * Math.sin(w - 0.2), 0); this.worldTurn(out, sp[4], 4 * env * Math.sin(w - 0.55), 0); // (and the head wags, so it reads from above)
  out.root.y -= 0.03 * env; // (it drops a touch into it)
};
Animator.prototype.pitchTurn = function (pose, i, a) {""")
# applied at the end of the crawl's pose, after the limbs
rep("  } else if (L.air) {\n    // touching down:", "  } else if (L.air) {\n    // touching down:")
old_end = s.find("Animator.prototype.crawl = function")
assert old_end > 0
# find the crawl function's return of the pose: it ends with a ball/curl section; hook via a wrapper instead, after the pose is built
s += """
// the shake, laid over the crawl's finished pose
{ const crawl0 = Animator.prototype.crawl;
  Animator.prototype.crawl = function (t, out, dt) { const r = crawl0.call(this, t, out, dt); this.stepShake(out, dt); return r; }; }
"""
open(P, 'w').write(s); print('shake240 ok')
