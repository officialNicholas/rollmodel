"""v402: notifications asked for once an account is made (the user: "we need to ask for a notification earlier in the flow. maybe
after we make an account"). Until now the only ask was on a long craft, so a player who never crafted (or has dabs, which make crafts
instant) never got iOS's prompt, and a party invite couldn't reach their closed game.

- Made an account, or signed in to one: the game's own card asks, a moment after the welcome, whether to hear about party invites and
  finished crafts with the game closed. Nudge me brings up iOS's prompt; Not now leaves it for the craft card, as before.
- A player who already has an account and was never asked: the same card once, in the lobby, when nothing else is open.
- Only in the iPhone app, only while iOS hasn't been asked yet."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

JS = r"""
// (v402) notifications asked for with the account: party invites reach a closed game only once iOS has said yes
function noteOfferAc() { try {
  if (!noteApp() || NOTE.status !== 'ask' || store.noteAskedAc || !store.sbs || !store.sbs.perm || !$('noteModal').hidden) return;
  if (!lobbyOn() || lookOpen || shopOpen || lkOn() || irisBusy || document.querySelector('.modal:not([hidden])')) return;
  store.noteAskedAc = 1; save();
  $('noteTitle').textContent = 'Stay in the loop?';
  $('noteNote').innerHTML = 'Get a notification when a friend <b>invites you to a party</b> or a craft is done, even with the game closed.';
  $('noteModal').hidden = false; setTimeout(() => $('noteYes').focus({ preventScroll: true }), 30);
} catch (e) {} }
setInterval(noteOfferAc, 2500);
"""

def apply(s):
    s = rep(s, "function noteClose() { const m = $('noteModal'); if (m.hidden) return; m.hidden = true; }",
               "function noteClose() { const m = $('noteModal'); if (m.hidden) return; m.hidden = true; }" + JS)
    # the craft card keeps its own title
    s = rep(s, "  setTimeout(() => { if (state !== 'menu' || !strokesOpen()) return; $('noteNote').innerHTML = ",
               "  setTimeout(() => { if (state !== 'menu' || !strokesOpen()) return; $('noteTitle').textContent = 'Get a nudge?'; $('noteNote').innerHTML = ")
    # right after the welcome (made or signed in), once whatever comes next has had its turn
    s = rep(s, "acClose(true); frToast(html); AU.power(); acPaintAll(); if (next) setTimeout(next, 250); }",
               "acClose(true); frToast(html); AU.power(); acPaintAll(); if (next) setTimeout(next, 250); setTimeout(noteOfferAc, 1400); }")
    return s
