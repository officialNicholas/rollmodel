"""v362: Ol' Bloop's plate holds still on the locker page, and the lesson's dodge takes any way out of the rival's pound.

- The plate over a control (the locker's "All yours! Now open your locker" and every tip like it) goes where it's measured to go the
  moment it comes up, then only moves to a new place once that place has held for three frames, as it slides (a scroll, the page coming
  in), when the screen changes size, or when nothing squeezes it where it's going and something squeezed it where it is. On an iPhone
  the plate on the locker page jumped between three places every frame (two of them over the tabs, one under them) and flickered.
- The lesson's dodge step still says to swipe up, but any way out of the rival's pound now passes it: a swipe, a jump, a fling with the
  slingshot, or just getting out of its way. His pound has to come down near you and miss you (two caught still passes it, as before)."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    # ---- the plate over a control: a place it holds, not one frame's measure
    s = rep(s, "  const left = clamp(cx - cw / 2, 12, Math.max(12, viewW - cw - 12)); let y = above ? roomUp - 84 : r.bottom - r0.top + 84; // (the hand's fingertip lands on the edge of the thing, not over it)\n"
               "  y = above ? Math.max(y, ph + 4) : Math.min(y, viewH - ph - 8);\n"
               "  const pos = above ? 'above' : 'below'; if (tutEl.dataset.pos !== pos) tutEl.dataset.pos = pos;\n",
               "  const left = clamp(cx - cw / 2, 12, Math.max(12, viewW - cw - 12)), y0 = above ? roomUp - 84 : r.bottom - r0.top + 84; // (the hand's fingertip lands on the edge of the thing, not over it)\n"
               "  const y = above ? Math.max(y0, ph + 4) : Math.min(y0, viewH - ph - 8), pos = above ? 'above' : 'below';\n"
               "  if (!tutHold(pos, left, y, y === y0)) return; // (v362: where it holds, not where one frame's measure puts it)\n"
               "  if (tutEl.dataset.pos !== pos) tutEl.dataset.pos = pos;\n")
    s = rep(s, "// the lesson, one step at a time: each one says what to do, waits for it (slowed down while it waits), then the next. max: real seconds before it moves on anyway\n",
               "// (v362) where the plate over a control goes, held: a new place is taken as the tip comes up or the screen changes size, as it slides (a\n"
               "// scroll, the page coming in), once it has held three frames, or when nothing squeezes it there and something squeezed it where it is.\n"
               "// A place one frame's measure gives and the next takes back never moves it (on an iPhone the locker's plate jumped between three places\n"
               "// every frame, two of them over the tabs). nat: nothing squeezed it (it's where it's meant to be, not pushed off an edge)\n"
               "function tutHold(pos, x, y, nat) {\n"
               "  const S = tutTip.hold || (tutTip.hold = { on: null, h: [], vk: '' }), c = { pos, x: +x.toFixed(0), y: +y.toFixed(0), nat }, h = S.h, on = S.on, vk = viewW + 'x' + viewH;\n"
               "  h.push(c); if (h.length > 3) h.shift();\n"
               "  const near = (a, b, d) => a.pos === b.pos && Math.abs(a.x - b.x) <= d && Math.abs(a.y - b.y) <= d;\n"
               "  if (on && near(c, on, 0)) return true;\n"
               "  const fresh = !on || S.vk !== vk || tutEl.dataset.pos !== on.pos || tutEl.style.left !== on.x + 'px' || tutEl.style.top !== on.y + 'px';\n"
               "  const held = h.length === 3 && near(h[2], h[1], 3) && near(h[1], h[0], 3);\n"
               "  const slide = h.length === 3 && h[0].pos === pos && h[1].pos === pos && ['x', 'y'].every(k => { const d1 = h[2][k] - h[1][k], d0 = h[1][k] - h[0][k]; return Math.abs(d1) <= 64 && Math.abs(d0) <= 64 && (d1 === 0 || d1 * d0 > 0); }) && !near(h[2], h[1], 0);\n"
               "  if (!(fresh || held || slide || (nat && !on.nat))) return false;\n"
               "  S.on = c; S.vk = vk; return true;\n"
               "}\n"
               "// the lesson, one step at a time: each one says what to do, waits for it (slowed down while it waits), then the next. max: real seconds before it moves on anyway\n")
    # ---- the dodge: any way out of his pound passes it (the tip still says to swipe)
    s = rep(s, "tut.rolled = false; tut.hits = 0; tut.wasKo = false;",
               "tut.rolled = false; tut.hits = 0; tut.wasKo = false; tut.escaped = false; tut.thr = false; tut.slamW = false; tut.h0 = 0;")
    s = rep(s, "      if (P.st === 'ko' && !tut.wasKo) tut.hits++; tut.wasKo = P.st === 'ko';\n",
               "      if (P.st === 'ko' && !tut.wasKo) tut.hits++; tut.wasKo = P.st === 'ko';\n"
               "      if (H.slam && !tut.slamW) tut.h0 = tut.hits; if (H.slam && H.st === 'play' && d < slamRadius(H) + PR + 6) tut.thr = true; // (v362: his pound in the air, you near it)\n"
               "      if (tut.slamW && !H.slam) { if (tut.thr && tut.hits === tut.h0 && H.st === 'play' && P.st === 'play') tut.escaped = true; tut.thr = false; } tut.slamW = !!H.slam; /* (it came down and missed you: a swipe, a jump, a fling or just getting out of its way, any of them) */\n")
    s = rep(s, "      return (tut.rolled || tut.hits >= 2) && P.st === 'play' && !H.slam; },",
               "      return (tut.rolled || tut.escaped || tut.hits >= 2) && P.st === 'play' && !H.slam; },")
    return s
