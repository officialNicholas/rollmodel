"""v272: Ol' Bloop's tips on a page (the Strokes lesson) no longer cover the page's back button. A tip with nothing to point at goes to
the page's foot instead of staying wherever the last one was (it stayed up top after the Equip step, over the back button), and the top
spot, used while the hand points at something low on the screen, sits below the page's header, his head included."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)
def apply(s):
    s = rep(s, "ct: [(viewW - tw) / 2, Math.max(8, parseFloat(getComputedStyle(stage).paddingTop) || 0) + 64] };",
            "ct: [(viewW - tw) / 2, Math.max(Math.max(8, parseFloat(getComputedStyle(stage).paddingTop) || 0) + 64, tutHeadBottom(r0) + over + 10)] }; // (v272: below the page's own header, his head and all)")
    s = rep(s, "was = tutEl.dataset.lowc, pick = was && order.includes(was) && clear(was) ? was : order.find(clear) || order[0];",
            "was = tutEl.dataset.lowc, pick = tr && was && order.includes(was) && clear(was) ? was : order.find(clear) || order[0]; // (v272: nothing pointed at, the page's foot)")
    s = rep(s, "function tutPlace() {", "// (v272) the bottom of the open page's header (its back button and title), from the stage's top: the tips keep below it\n"
            "function tutHeadBottom(r0) { let b = 0; for (const e of document.querySelectorAll('.evhead, .sback')) { if (e.offsetParent === null) continue; const r = e.getBoundingClientRect(); if (r.height > 0) b = Math.max(b, r.bottom - r0.top); } return b; }\n"
            "function tutPlace() {")
    return s
