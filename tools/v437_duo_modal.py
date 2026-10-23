"""v437: iPhone Duo's cover screen (the side column), pop-ups over a page.
- A pop-up over a page (the account sheet over Friends, the time trial board, online, the party picker, the inbox) owns the column:
  only its close button sits there. The page's own Back goes back to its place on the page, under the pop-up's dimmed, blurred
  backdrop like everything else on it, and comes back to the column when the pop-up closes. (Before, both sat in the column, the
  page's Back sharp above the blur, and a tap on it left the pop-up open.)
- The close buttons that sit in the column (the account sheet, the time trial board, online, the party picker, the inbox, a stroke's
  Info) are the side menu's chunky slate key, like the dab store's: a white X on dark, plain to see. They were a thin grey X meant for
  the cream card, nearly invisible on the dark column.
- The column follows a pop-up opening or closing at once, not up to a quarter of a second later."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

CSS = r"""
/* (v437) close buttons in the cover screen's column: the chunky slate key, a white X on dark */
#scolDock>:is(.ttx,.pyx,.stpx):not(#dsX){display:grid;place-items:center;width:46px;height:44px;padding:0;border:0;border-radius:9px;color:#fff;background:linear-gradient(180deg,#4A4561 0%,#353049 60%,#2A2539 100%);box-shadow:0 0 0 2.5px #171320,inset 0 2px 0 rgba(255,255,255,.2),inset 0 -3px 0 rgba(0,0,0,.25),0 4px 0 #171320;opacity:1;transform:skewX(-5deg)!important}
#scolDock>:is(.ttx,.pyx,.stpx):not(#dsX) svg{width:22px;height:22px;color:#fff;stroke:#fff;stroke-width:3.4;filter:drop-shadow(0 1.5px 0 rgba(23,19,32,.45))}
#scolDock>:is(.ttx,.pyx,.stpx):not(#dsX) svg *{stroke:#fff}
#scolDock>:is(.ttx,.pyx,.stpx):not(#dsX):active{transform:skewX(-5deg) translateY(2px)!important}
"""

OLD = """    let n = 0;
    for (const id of IDS) {
      const b = document.getElementById(id); if (!b) continue;
      const h = home.get(id);
      if (h) { // docked: back home once its page hides (or the column goes)
        const vis = on && shown(h.parent);
        if (!vis) { h.parent.insertBefore(b, h.next && h.next.parentNode === h.parent ? h.next : null); home.delete(id); } else n++;
      } else if (on && shown(b.parentElement) && shown(b)) { home.set(id, { parent: b.parentElement, next: b.nextSibling }); dock.appendChild(b); n++; }
    }
"""
NEW = """    // (v437) only the top layer's buttons: a pop-up over a page has the column to itself, the page's Back goes home under its blur
    const mods = [...document.querySelectorAll('.modal')]; // (same level: the later one in the page draws on top)
    const layer = el => { const m = el.closest('.modal'); return m ? (parseInt(getComputedStyle(m).zIndex, 10) || 1) * 1000 + mods.indexOf(m) + 1 : 0; };
    const want = new Map(); let top = -1;
    for (const id of IDS) {
      const b = document.getElementById(id); if (!b) continue;
      const h = home.get(id), par = h ? h.parent : b.parentElement;
      if (on && par && shown(par) && (h || shown(b))) { const l = layer(par); want.set(id, l); if (l > top) top = l; }
    }
    let n = 0;
    for (const id of IDS) {
      const b = document.getElementById(id); if (!b) continue;
      const h = home.get(id), dockIt = want.has(id) && want.get(id) === top;
      if (h) { // docked: back home once its page hides, a pop-up covers it, or the column goes
        if (!dockIt) { h.parent.insertBefore(b, h.next && h.next.parentNode === h.parent ? h.next : null); home.delete(id); } else n++;
      } else if (dockIt) { home.set(id, { parent: b.parentElement, next: b.nextSibling }); dock.appendChild(b); n++; }
    }
"""

def apply(s):
    s = rep(s, OLD, NEW)
    # the column follows a pop-up opening or closing at once
    s = rep(s, "  setInterval(tick, 250); addEventListener('resize', () => setTimeout(tick, 50));",
            "  setInterval(tick, 250); addEventListener('resize', () => setTimeout(tick, 50));\n"
            "  let tq = 0; new MutationObserver(() => { const c = document.documentElement.classList; if (!tq && (c.contains('scol') || c.contains('scolL') || home.size)) tq = requestAnimationFrame(() => { tq = 0; tick(); }); }).observe(document.body, { subtree: true, attributes: true, attributeFilter: ['hidden'] }); // (v437)")
    i = s.rfind("</style>"); s = s[:i] + CSS + s[i:]
    return s
