"""v284: the versus screen's portraits (one fighter per row, on an upright phone) are always centred in their rows, whatever the device.
They were off on four-player matches (Showdown, 2v2): a rule meant for the side-by-side layout (the shot twice its column's width) won
over the rows' own, so each shot was framed for a box twice the row's width, rendered at a squarer shape than the row and then cropped
top and bottom: faces low and cut off, the last row showing only a halo. Now:
- the rows' shot is the row's own width in every mode;
- the shot is rendered at exactly the row's shape (nothing cropped), sized from its layout, not from where the slide-in animation has
  it at that moment;
- the head is framed in the middle of the row, across and down, in the part you can actually see: below the screen's top inset (the
  notch or an app's bar over the page) and above the title at the foot;
- when the canvas vote follows (every match but the first lesson's), the rows end where its panel will come up, so it covers none of
  them (the last row was mostly hidden behind it on shorter phones); till it slides up, the bottom band and the title fill that space.
Landscape keeps its full-length fighters until the vote; as its panel comes up (it covered all but the tops of their heads on a phone),
each head glides into the middle of what its panel still shows, across and between its name and the vote, smaller only if it
must be."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

SAFE = """// (v284) the screen's top inset (a notch, or an app's bar laid over the page), in the page's own pixels
function vsSafeTop() { const d = document.createElement('div'); d.style.cssText = 'position:fixed;left:0;top:0;width:1px;height:env(safe-area-inset-top,0px);visibility:hidden;pointer-events:none'; document.body.appendChild(d); const h = d.getBoundingClientRect().height || 0; d.remove(); return h; }
"""

ROWS = """for (const [D, el, pose] of q.list) { if (!el) continue;
      if (rows) { /* (v284) upright, one fighter per row: the shot at the row's own shape and settled size (the rows slide in and the shots
        settle from a little larger, so its layout size, not where the animation has it now), the head in the middle of what you can see
        of the row: below the screen's top inset, above the title at the foot */
        const col = el.closest('.vcol') || el.parentNode, bw = Math.max(1, el.offsetWidth || col.offsetWidth || 390), bh = Math.max(1, el.offsetHeight || col.offsetHeight || 160);
        const k = Math.min(2.2, 1400 / bw, 1200 / bh), fw = Math.max(64, Math.round(bw * k)), fh = Math.max(64, Math.round(bh * k));
        const top0 = col.getBoundingClientRect().top + el.offsetTop; let top = Math.max(top0, vsSafeTop()), bot = top0 + bh;
        if (!$('vsx').classList.contains('vvr')) for (const b of document.querySelectorAll('#vsx .vband.bot, #vsx .vstitle')) { const br = b.getBoundingClientRect(); if (br.height > 0 && br.top < bot && br.bottom > top) bot = Math.min(bot, br.top + 4); }
        const vis = Math.max(40, bot - top), foe = /\\bfoe/.test(col.className || '');
        const fr = { fd: Math.min(0.86, vis * 0.66 / bh), fx: 0.5, fy: (top + vis * 0.5 - top0) / bh, turn: foe ? 0.3 : -0.3 };
        el.replaceChildren(portraitOf(D, fw, fh, Object.assign({}, pose, { face: true, yaw: 0 }, fr))); continue; }
      const r = el.getBoundingClientRect(), fw = 720,"""

CSS = ("\n/* (v284) upright with the vote to come: the rows stop where its panel will come up (its height: the label, the reel, the tally and"
       "\n   the padding), the bottom band and the title fill the space under them till then */"
       "\n.vsx.vvr .vsrow.rows{bottom:max(20%,calc(209px + max(12px,env(safe-area-inset-bottom,0px))))}"
       "\n.vsx.vvr .vband.bot{height:calc(10% + 236px + env(safe-area-inset-bottom,0px))}"
       "\n.vsx.vvr .vstitle{bottom:calc(88px + env(safe-area-inset-bottom,0px))}\n")

FIT = """// (v284) landscape, as the vote's panel comes up: each fighter's head glides into the middle of what its panel still shows (across,
// and under its name, over the vote), smaller only if it must be; the shot knows where it put the head (el._fr: its middle, and its
// height, in the shot). Worked out from the layout, not from where the panels' entrance animations have them at that moment.
function vsVoteFit() {
  const row = $('vsRow'), vx = $('vsx'); if (row.classList.contains('rows')) return; const vtop = vx.clientHeight - $('vvote').offsetHeight;
  for (const el of row.querySelectorAll('.vbox')) { const fr = el._fr, col = el.closest('.vcol'); if (!fr || !fr.fd || !col || el.offsetParent !== col) continue;
    const hd = col.querySelector('.vhead'), cy = row.offsetTop + col.offsetTop, top = hd && hd.offsetHeight ? hd.offsetTop + hd.offsetHeight : 0, band = vtop - cy - top; if (band < 40) continue;
    el.style.animation = 'none'; el.style.transform = ''; const base = getComputedStyle(el).transform, bm = base && base !== 'none' ? new DOMMatrix(base) : null, w = el.offsetWidth, h = el.offsetHeight; if (!h) continue;
    const hy = el.offsetTop + (bm ? bm.m42 : 0) + fr.fy * h, hx = el.offsetLeft + (bm ? bm.m41 : 0) + fr.fx * w, k = Math.min(1, band * 0.8 / (fr.fd * h)), dy = top + band * 0.5 - hy, dx = col.offsetWidth / 2 - hx;
    el.style.transformOrigin = (fr.fx * 100).toFixed(2) + '% ' + (fr.fy * 100).toFixed(2) + '%'; el.style.transition = 'transform .45s cubic-bezier(.2,1.1,.35,1)';
    el.style.transform = (bm ? base + ' ' : '') + 'translate(' + dx.toFixed(1) + 'px,' + dy.toFixed(1) + 'px) scale(' + k.toFixed(3) + ')'; }
}
"""

def apply(s):
    s = rep(s, ".vsx .vsrow.quad .vcol .vbox{width:200%}", ".vsx .vsrow.quad .vcol .vbox{width:200%}\n.vsx .vsrow.rows.quad .vcol .vbox{width:auto} /* (v284: in rows the shot is the row's own width, four fighters or two) */")
    s = rep(s, ".vsrow.rows .vcol.foe3{animation-name:rowinr}", ".vsrow.rows .vcol.foe3{animation-name:rowinr}" + CSS)
    s = rep(s, "$('vsRow').classList.toggle('rows', viewH > viewW && mode !== 'solo');", "$('vsRow').classList.toggle('rows', viewH > viewW && mode !== 'solo'); $('vsx').classList.toggle('vvr', viewH > viewW && mode !== 'solo' && !window.__noVote && !tutMatchDue()); /* (v284: the vote to come) */")
    s = rep(s, "function vsSnapTick() {", SAFE + FIT + "function vsSnapTick() {")
    s = rep(s, ": portraitOf(D, 600, 720, Object.assign({}, pose, fr)); el.replaceChildren(c); } }", ": portraitOf(D, 600, 720, Object.assign({}, pose, fr)); el.replaceChildren(c); el._fr = fr; }\n    if (!rows && $('vsx').classList.contains('voting')) vsVoteFit(); } /* (v284: the vote came up before the shots were taken) */")
    s = rep(s, "box.hidden = false; $('vsx').classList.add('voting');", "box.hidden = false; $('vsx').classList.add('voting'); vsVoteFit();")
    s = rep(s, "for (const [D, el, pose] of q.list) { if (!el) continue; const r = el.getBoundingClientRect(), fw = 720,", ROWS)
    return s
