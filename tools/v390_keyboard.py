"""v390: the keyboard comes up over the game, and the game stays where it is (the user: the whole screen moving up, on every device,
hid the character; only the "What do we call you?" card should move up).

- In the app the page never scrolls now: WebKit used to push the whole game up to show the field being typed in. The app tells the game
  how tall the keyboard is ("nativekeyboard", window.__NATIVE.kb) and how long it takes to come up.
- In a browser the keyboard's height comes from the visual viewport, and the page is put back if the browser scrolled it.
- The intro's name card rises whole (its Back and Next with it) to sit just above the keyboard, in step with it, and settles back down when
  the keyboard goes. The scene stays where it is; the camera only eases to keep the character in the clear space above the card, as it
  does whenever a card comes or goes.
- Any other field (the account form, a friend code): the panel it's in scrolls it into view if it can, otherwise its card (or its page)
  rises just far enough to show it above the keyboard. Never the field itself off the top of the screen."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

KB_JS = r"""// ---------- (v390) the keyboard comes up over the game and the game stays where it is: only what you're typing in rises above it. In the
// app the page never scrolls (WebKit used to push the whole game up to show the field) and the app says how tall the keyboard is; in a
// browser that comes from the visual viewport. A card marked data-kblift (the intro's name card) rises whole, its buttons with it;
// anywhere else the field's own panel scrolls it into view, or its card (or its page) rises just far enough to show it
const KB = { h: 0, el: null, ink: '', x: '0px', y: '0px', lift: 0, top: -1 };
const kbField = () => { const a = document.activeElement; return a && a.matches && a.matches('input:not([type=range]):not([type=checkbox]):not([type=radio]):not([type=button]):not([type=submit]),textarea') ? a : null; };
function kbBox(a) {
  const own = a.closest('[data-kblift]') || a.closest('.modal > *'); if (own) return own;
  for (let e = a.parentElement; e && e !== document.body; e = e.parentElement) if (getComputedStyle(e).position === 'fixed') return e;
  return null;
}
function kbTop() { if (KB.top < 0) { const d = document.createElement('div'); d.style.cssText = 'position:fixed;top:0;height:env(safe-area-inset-top,0px);visibility:hidden;pointer-events:none'; document.body.appendChild(d); KB.top = d.offsetHeight || 0; d.remove(); } return Math.max(10, KB.top + 6); }
// (its own translate stays: the rise is added to it, and eases in and out with the keyboard)
function kbSet(el, y, ms) {
  const from = getComputedStyle(el).translate, to = KB.x + ' calc(' + KB.y + ' - ' + y + 'px)';
  el.style.translate = y > 0 ? to : KB.ink;
  if (ms > 0 && el.animate) try { el.animate([{ translate: from }, { translate: y > 0 ? to : KB.x + ' ' + KB.y }], { duration: ms, easing: 'cubic-bezier(.2,.8,.3,1)' }); } catch (e) {}
}
function kbFit(ms) {
  const a = KB.h > 40 ? kbField() : null, box = a ? kbBox(a) : null;
  if (KB.el && KB.el !== box) { kbSet(KB.el, 0, ms); KB.el = null; KB.lift = 0; }
  if (!box) return;
  if (KB.el !== box) { const t = getComputedStyle(box).translate.split(' '); KB.el = box; KB.ink = box.style.translate; KB.x = t[0] && t[0] !== 'none' ? t[0] : '0px'; KB.y = t[1] || '0px'; KB.lift = 0; }
  const low = innerHeight - KB.h - 12, top = kbTop(), r = a.getBoundingClientRect();
  let fTop = r.top + KB.lift, need = r.bottom + KB.lift - low; // (where the field would be without the rise)
  if (need > 0) for (let e = a.parentElement; e && e !== box; e = e.parentElement) { // a panel of its own that scrolls: there first
    const o = getComputedStyle(e).overflowY; if ((o !== 'auto' && o !== 'scroll') || e.scrollHeight <= e.clientHeight + 1) continue;
    const s0 = e.scrollTop; e.scrollTop = s0 + need; const d = e.scrollTop - s0; need -= d; fTop -= d; break;
  }
  let y = Math.max(0, need);
  if (box.hasAttribute('data-kblift')) y = Math.max(y, Math.min(box.getBoundingClientRect().bottom + KB.lift - low, fTop - top)); // (the whole card, never the field off the top)
  y = Math.max(0, Math.round(y)); if (Math.abs(y - KB.lift) < 1) return;
  KB.lift = y; kbSet(box, y, ms);
}
addEventListener('nativekeyboard', e => { const d = e.detail || {}; KB.h = Math.max(0, +d.h || 0); kbFit(d.ms > 0 ? +d.ms : 250); });
document.addEventListener('focusin', () => kbFit(220));
document.addEventListener('focusout', () => setTimeout(() => kbFit(220), 0));
addEventListener('resize', () => { KB.top = -1; kbFit(0); });
if (window.visualViewport) { const vv = window.visualViewport, vvKb = () => {
  const n = window.__NATIVE; if (n && typeof n.kb === 'number') return; // (the app says it itself)
  const h = kbField() && Math.abs(vv.scale - 1) < 0.01 ? Math.round(innerHeight - vv.height) : 0, k = h > 120 ? h : 0;
  if (k !== KB.h) { KB.h = k; kbFit(220); }
  if (k && (window.scrollY || vv.offsetTop)) try { window.scrollTo(0, 0); } catch (e) {} // (a browser scrolled the page up for the field: put it back)
}; vv.addEventListener('resize', vvKb); vv.addEventListener('scroll', vvKb); }
"""

def apply(s):
    s = rep(s, "// ---------- (v257) the first launch, out in the sun", KB_JS + "// ---------- (v257) the first launch, out in the sun")
    # the intro's name card rises whole
    s = rep(s, """'<form class="flpanel" id="flName" hidden autocomplete="off" aria-labelledby="flNameT">""",
               """'<form class="flpanel" id="flName" hidden autocomplete="off" data-kblift aria-labelledby="flNameT">""")
    # the intro frames the character in the clear part of the screen: above the card (as it rises) and clear of the keyboard too
    s = rep(s, "if (c && c.width > 0) { if (W > H * 1.05) r.x0 = c.right - sr.left + 8; else r.y1 = c.top - sr.top - 8; }\n    return free = r;",
               "if (c && c.width > 0) { if (W > H * 1.05) r.x0 = c.right - sr.left + 8; else r.y1 = c.top - sr.top - 8; }\n"
               "    if (KB.h > 40) r.y1 = Math.min(r.y1, H - KB.h - 8); // (v390: and above the keyboard)\n    return free = r;")
    return s
