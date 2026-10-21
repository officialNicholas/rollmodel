"""v434: Deep Pockets' second pocket online. Offline it held two items; online the server kept one, so a second pick-up swapped the first
out. Now the game says it knows of the second pocket (kit iv 3), the server keeps a second item for a Deep Pockets player as the game
does (a second goes in the other pocket, a third drops the older), a use says which pocket it came from, and the server's word on
what's in both pockets comes with every pick-up and use, so every phone shows the same."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, "function netKit() { return { iv: 2,", "function netKit() { return { iv: 3,") # (v434: 3, the second pocket)
    # which pocket a use came from
    s = rep(s, "function useHeld2(D) { if (!D.held2) return false; const a = D.held; D.held = D.held2; D.held2 = null; if (useHeld(D)) { D.held = a; return true; } D.held2 = D.held; D.held = a; return false; }",
               "function useHeld2(D) { if (!D.held2) return false; const a = D.held; D.held = D.held2; D.held2 = null; let ok = false; if (NM) NM.second = 1; try { ok = useHeld(D); } finally { if (NM) NM.second = 0; } if (ok) { D.held = a; return true; } D.held2 = D.held; D.held = a; return false; } // (v434: online, the use says it's the second pocket)")
    s = rep(s, "if (!echo && NMI() && netMe(D) && type !== 'boom') netAct('use', { yaw: netR(D.yaw) }, D);",
               "if (!echo && NMI() && netMe(D) && type !== 'boom') netAct('use', { yaw: netR(D.yaw), second: NM.second ? 1 : undefined }, D);")
    s = rep(s, "netAct('use', { yaw: netR(yaw), curve, tgt: tgt ? NM.slotOf.get(tgt) : undefined }, D)",
               "netAct('use', { yaw: netR(yaw), curve, tgt: tgt ? NM.slotOf.get(tgt) : undefined, second: NM.second ? 1 : undefined }, D)")
    # the server's word on both pockets
    s = rep(s, "  if (pw) collectPower(D, pw); else { D.held = PU[m.kind] ? m.kind : 'roller'; D.heldT = 0; if (D === P) { AU.pop(); buzz(12); } }\n}",
               "  if (pw) collectPower(D, pw); else { D.held = PU[m.kind] ? m.kind : 'roller'; D.heldT = 0; if (D === P) { AU.pop(); buzz(12); } }\n"
               "  if (m.h1 !== undefined || m.h2 !== undefined) { D.held = PU[m.h1] ? m.h1 : null; D.held2 = PU[m.h2] ? m.h2 : null; } // (v434: both pockets, as the server has them)\n}")
    s = rep(s, "    if (m.kind === 'trap') { const T = trapList[trapList.length - 1]; if (T && T.owner === D) { T.id = m.trap; if (Number.isFinite(m.x)) { T.x = m.x; T.z = m.z; T.g.position.set(T.x, T.y, T.z); } } }\n  });",
               "    if (m.kind === 'trap') { const T = trapList[trapList.length - 1]; if (T && T.owner === D) { T.id = m.trap; if (Number.isFinite(m.x)) { T.x = m.x; T.z = m.z; T.g.position.set(T.x, T.y, T.z); } } }\n  });\n"
               "  if (m.h1 !== undefined || m.h2 !== undefined) { D.held = PU[m.h1] ? m.h1 : null; D.held2 = PU[m.h2] ? m.h2 : null; } // (v434: what's left in its pockets)")
    return s
