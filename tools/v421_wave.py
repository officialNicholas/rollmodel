"""v421: the wave, redone (the user: "fix the "Wave" animation. It looks like the fingers are going in the characters face and the
waving is slightly off"). The wave (the lobby's idle mood, a tap on you in the lobby, a tap in the locker's window) put the right hand
in front of the cheek (0.2 forward of the shoulder and only 0.1 to 0.17 out to the side, inside the head's width) with the fingers
pointing up, forward and in, so they poked at the face; it wagged on the clock (this.t at 2.4 a second), so it started mid-wag, and
five or six quick wags went by in a wave of a second or two. Now:
- The arm goes up out to the side, beside the head and a touch in front of the gills, the elbow bent: the wrist 0.26 to 0.37 out from
  the shoulder (the head's cheek is about 0.4 from the middle, the shoulder 0.23), never in front of the face.
- The forearm wags side to side about the elbow on an arc, the hand following through a beat behind it and a little further (a floppy,
  friendly wave), the fingers up and tipped out, the palm to the front.
- The wag has its own clock: it starts from still once the hand is up and grows in, two wags a second, so 2 to 3 wags in a wave;
  on the way down it shrinks away as the hand comes back to the floor. The lobby's idle wave is a little shorter (2.5 -> 2.1 s) to match.
- The palm faces the front all through: a contact can now say which way its palm faces (zh, down when it doesn't say); pointed up,
  "down" gave the hand no clear way to face, so its palm turned out and in with each wag.
- The fingers point up, spread, and curl a little towards the palm (away from the head), the little finger most.
"""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    # ---- the wag's own clock: from still once the hand is up, two a second, eased in with the hand's rise and out with its fall
    s = rep(s, """  if (wv > 0.002) { out.root.x += 0.025 * wv; out.root.z -= 0.02 * wv; out.root.y += 0.012 * wv; this.pitchTurn(out, sp[3], -0.1 * wv); this.worldTurn(out, sp[2], 0, 4 * wv); }
""", """  if (wv > 0.002) { out.root.x += 0.025 * wv; out.root.z -= 0.02 * wv; out.root.y += 0.012 * wv; this.pitchTurn(out, sp[3], -0.1 * wv); this.worldTurn(out, sp[2], 0, 4 * wv); }
  // (v421) the wag's own clock: it starts from still once the hand is up (wvA, the swing either way, radians), two wags a second
  const wvA = 0.36 * smooth(clamp01((wv - 0.45) / 0.5)); if (wv > 0.45) L.wvPh = (L.wvPh || 0) + dt * 2 * Math.PI * 2.0; else if (wv < 0.002) L.wvPh = 0;
""")
    # ---- the hand: up out to the side beside the head, the forearm wagging on an arc about the elbow, the hand a beat behind
    s = rep(s, """    const slk = l.en === 'hand.R' ? slK : 0, wvk = l.en === 'hand.R' ? Math.max(wv, slk) : 0; if (wvk > 0.002) { const pk = P.fk('crawl', out), sh = pk[l.root], q = l.wq || (l.wq = new THREE.Vector3()), sw = slk > wv ? 0 : Math.sin(this.t * 2 * Math.PI * 2.4);
      if (slk > wv) q.set(sh.x + l.m * 0.05, sh.y + 0.22, sh.z + 0.13); else q.set(sh.x + l.m * (0.1 + 0.07 * sw), sh.y + 0.17 + 0.02 * Math.abs(sw), sh.z + 0.2); q.lerpVectors(tp, q, wvk); tp = q; lift = Math.max(lift, wvk); }
""", """    const slk = l.en === 'hand.R' ? slK : 0, wvk = l.en === 'hand.R' ? Math.max(wv, slk) : 0; let wdx = 0.2, wdy = 0.85, wdz = 0.5, wpk = 0; // (wd: the hand's way, up; wpk: how far its palm turns to the front)
    if (wvk > 0.002) { const pk = P.fk('crawl', out), sh = pk[l.root], q = l.wq || (l.wq = new THREE.Vector3());
      if (slk > wv) q.set(sh.x + l.m * 0.05, sh.y + 0.22, sh.z + 0.13);
      else { // (v421) the wave: the forearm (0.17 long) wags about the elbow out beside the head, tipped out 0.25; the hand follows a beat
        // behind and a little further, the fingers up (the hand's way tipped back a little: the fingers sit forward of it) and the palm to the front
        const fa = 0.25 + wvA * Math.sin(L.wvPh), ha = 0.28 + 1.15 * wvA * Math.sin(L.wvPh - 0.5);
        q.set(sh.x + l.m * (0.28 + 0.17 * Math.sin(fa)), sh.y + 0.08 + 0.17 * Math.cos(fa), sh.z + 0.06); wdx = Math.sin(ha); wdy = Math.cos(ha); wdz = -0.22; wpk = wvk; }
      q.lerpVectors(tp, q, wvk); tp = q; lift = Math.max(lift, wvk); }
""")
    s = rep(s, """LV2.set(l.m * Math.sin(a) * r * (1 - wvk) + l.m * 0.2 * wvk, -0.35 * lift * (1 - tk) * (1 - wvk) + 0.85 * wvk, Math.cos(a) * r * (1 - wvk) + 0.5 * wvk);""",
               """LV2.set(l.m * Math.sin(a) * r * (1 - wvk) + l.m * wdx * wvk, -0.35 * lift * (1 - tk) * (1 - wvk) + wdy * wvk, Math.cos(a) * r * (1 - wvk) + wdz * wvk);""")
    s = rep(s, """      out.contact(l.en, tp, LV2, LV3.set(LB.pole.x * l.m, LB.pole.y, LB.pole.z), 1); }""",
               """      out.contact(l.en, tp, LV2, LV3.set(LB.pole.x * l.m, LB.pole.y, LB.pole.z), 1, wpk > 0.002 ? (l.wz || (l.wz = new THREE.Vector3())).set(0, -1 + 0.85 * wpk, wpk) : null); }""")
    # ---- a contact's palm: which way the palm of the hand (the sole of the foot) faces, down unless a contact says otherwise (zh). Waving,
    # the hand points up, where "down" gives no clear way for the palm (it turned out and in with each wag): its palm faces the front
    s = rep(s, """  contact(name, t, fwd, pole, w = 1) { const c = this.contacts[name] || (this.contacts[name] = { t: new THREE.Vector3(), fwd: new THREE.Vector3(), pole: new THREE.Vector3(), w: 1 }); c.t.copy(t); c.fwd.copy(fwd); c.pole.copy(pole); c.w = w; return c; }""",
               """  contact(name, t, fwd, pole, w = 1, zh = null) { const c = this.contacts[name] || (this.contacts[name] = { t: new THREE.Vector3(), fwd: new THREE.Vector3(), pole: new THREE.Vector3(), w: 1 }); c.t.copy(t); c.fwd.copy(fwd); c.pole.copy(pole); c.w = w; c.zh = zh ? (c.zh || new THREE.Vector3()).copy(zh) : null; return c; }""")
    s = rep(s, """if (!a) { const c = this.contact(k, b.t, b.fwd, b.pole, b.w * t); } else { a.t.lerp(b.t, t); a.fwd.lerp(b.fwd, t); a.pole.lerp(b.pole, t); a.w += (b.w - a.w) * t; } }""",
               """if (!a) { const c = this.contact(k, b.t, b.fwd, b.pole, b.w * t, b.zh); } else { a.t.lerp(b.t, t); a.fwd.lerp(b.fwd, t); a.pole.lerp(b.pole, t); a.w += (b.w - a.w) * t;
      if (a.zh || b.zh) (a.zh || (a.zh = new THREE.Vector3(0, -1, 0))).lerp(b.zh || _v4.set(0, -1, 0), t); } }""")
    s = rep(s, "function cloneContact(c) { return { t: c.t.clone(), fwd: c.fwd.clone(), pole: c.pole.clone(), w: c.w }; }",
               "function cloneContact(c) { return { t: c.t.clone(), fwd: c.fwd.clone(), pole: c.pole.clone(), w: c.w, zh: c.zh ? c.zh.clone() : null }; }")
    s = rep(s, "P.aim(pose, e, _v.copy(c.fwd).normalize(), _v2.set(0, -1, 0), false);", "P.aim(pose, e, _v.copy(c.fwd).normalize(), c.zh ? _v2.copy(c.zh) : _v2.set(0, -1, 0), false);")
    # ---- the fingers: spread, and curled a little towards the palm (away from the head), the little finger most
    s = rep(s, """    dig.forEach((g, k) => { rot(out, g[0], (4 + lift * 16 - (air ? 8 : 0)) * ns * (1 - wvk) + 3 * sl, 0, (k - 1.5) * (5 + (air ? 5 : 0) + 12 * wvk) * l.m * ns - (k - 1.5) * 2 * l.m * sl); rot(out, g[1], (3 + l.lift * 12) * ns * (1 - wvk) + 2 * sl, 0, 0); });""",
               """    dig.forEach((g, k) => { rot(out, g[0], (4 + lift * 16 - (air ? 8 : 0)) * ns * (1 - wvk) + 3 * sl + (3 + 2 * k) * wvk, 0, (k - 1.5) * (5 + (air ? 5 : 0) + 10 * wvk) * l.m * ns - (k - 1.5) * 2 * l.m * sl); rot(out, g[1], (3 + l.lift * 12) * ns * (1 - wvk) + 2 * sl + (2 + 2 * k) * wvk, 0, 0); });""")
    # ---- the lobby's idle wave a little shorter, for 2 to 3 wags
    s = rep(s, "['blep', 2.3, 2], ['wave', 2.5, 2]];", "['blep', 2.3, 2], ['wave', 2.1, 2]];")
    return s
