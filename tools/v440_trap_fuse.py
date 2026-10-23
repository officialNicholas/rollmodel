"""v440: a Paint Trap in Time trial goes off by itself. There are no rivals there to set one off, so it just sat there. Now, once dropped
in Time trial, it counts down TRAP_FUSE seconds and bursts on its own: the same burst of your paint a rival would set off (it paints the
floor, which is what counts in Time trial). The countdown shows: the trap's dome flashes white, slowly at first and faster and faster,
its light blinks with it, a tick sounds on each flash (rising as it goes), the ring under it widens and the trap swells a little in
the last moments. Matches with rivals are unchanged: there a trap still waits for someone to roll over it."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, "const TRAP_R = 0.92, TRAP_ARM = 0.6, TRAP_LIFE = 45, TRAP_MAX = 2, TRAP_STUN = 1.5, TRAP_SPLAT = SPLAT_R * 1.7;",
            "const TRAP_R = 0.92, TRAP_ARM = 0.6, TRAP_LIFE = 45, TRAP_MAX = 2, TRAP_STUN = 1.5, TRAP_SPLAT = SPLAT_R * 1.7;\n"
            "// (v440) Time trial has no rivals to set a trap off: there it goes off by itself TRAP_FUSE seconds after it's dropped, flashing white\n"
            "// faster and faster until it bursts\n"
            "const TRAP_FUSE = 3, trapFlashM = new THREE.MeshBasicMaterial({ color: 0xFFFFFF });")
    s = rep(s, "T.g.position.set(T.x, y, T.z); scene.add(T.g); trapList.push(T);",
            "T.g.position.set(T.x, y, T.z); scene.add(T.g); trapList.push(T);\n"
            "  if (mode === 'solo' && !NM) { T.fuse = TRAP_FUSE; T.domeM = T.g.children[1].material; } // (v440: Time trial: it goes off by itself)")
    s = rep(s, "    if (T.t > TRAP_LIFE) { trapPop(T, null, true); continue; }\n",
            "    if (T.t > TRAP_LIFE) { trapPop(T, null, true); continue; }\n"
            "    if (T.fuse !== undefined) { // (v440) the fuse: flashes white, slow then fast, a rising tick on each, a swell at the end, then the burst\n"
            "      T.fuse -= dt; if (T.fuse <= 0) { T.g.children[1].material = T.domeM; trapPop(T, null, false); continue; }\n"
            "      const k = 1 - T.fuse / TRAP_FUSE, per = 0.55 - 0.45 * k; T.fl = (T.fl || 0) + dt; if (T.fl >= per) T.fl -= per;\n"
            "      const on = T.fl < per * 0.45; T.g.children[1].material = on ? trapFlashM : T.domeM; u.light.material = on ? trapLightOn : trapLightOff;\n"
            "      if (on && !T.wasOn && Math.hypot(T.x - P.x, T.z - P.z) < 20 && AU.tick) { AU.at(T.x, T.z); AU.tick(Math.floor(k * 10)); }\n"
            "      T.wasOn = on; T.g.scale.setScalar(TRAP_SCALE * (1 + 0.22 * k * k * k + (on ? 0.04 : 0))); u.ring.scale.setScalar(1 + 0.6 * k + 0.07 * Math.sin(T.t * 9));\n"
            "      continue;\n"
            "    }\n")
    return s
