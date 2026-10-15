"""v300: no announcer on the results, a long hold always lets go, and Season Conquest on the events page (coming soon).

- The results no longer have the announcer's "Victory!" (or "Defeat", "Draw", "New best", "Time"). The sting, the music and the
  splash are unchanged.
- Holding still brakes you, as before. Letting go after a long hold now always gets you moving again. On iPhone a long press can
  swallow the finger-up event, so the game thought you were still holding the brake and you stayed put until you tapped, swiped or
  flung. The touch-end events always come, so when the last finger lifts and the brake is still on, it lets go then. A lift that
  lands on something other than the play area also counts.
- Season Conquest is on the events page as a faded card with a Coming soon tag, like Matchmaking. Tapping it says so."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

CONQ_SVG = ('<svg viewBox="0 0 64 64"><path d="M6 54c6-9 14-13 26-13s20 4 26 13z" fill="#7FD36E" stroke="#171320" stroke-width="3.2" stroke-linejoin="round"/>'
            '<path d="M14 54c3-4 8-6 12-6" fill="none" stroke="#C9F2BF" stroke-width="2.6" stroke-linecap="round"/>'
            '<path d="M31 43V8" stroke="#171320" stroke-width="4.2" stroke-linecap="round"/>'
            '<path d="M32.5 9.5c6-3 11 3 17 0 2-1 3 0 3 1.5v15c0 1.5-1 2.5-3 3.5-6 3-11-3-17 0z" fill="#FFD84A" stroke="#171320" stroke-width="3" stroke-linejoin="round"/>'
            '<path d="M38 17.5l2.2 1.6 2.4-3.4 1.9 4.6 2.6-2.2-.9 5.4h-8.2z" fill="#E3122F" stroke="#171320" stroke-width="1.8" stroke-linejoin="round"/>'
            '<circle cx="31" cy="7" r="3.4" fill="#fff" stroke="#171320" stroke-width="2.6"/>'
            '<path d="M44 46c2.5-1.4 6-.8 7.5 1.4 1.2 1.8-.4 3.6-2.8 3.6-3 0-5.6-1.6-4.7-5z" fill="#E3122F" stroke="#171320" stroke-width="2.2"/></svg>')

CARD = ('<div class="evcard soon" data-ev="conquest" style="--ec:#F2C14E"><button class="evmain" id="evConq" type="button" aria-disabled="true"><span class="evbar"><i>Coming soon</i></span>'
        '<span class="evtop"><span class="evic" aria-hidden="true">' + CONQ_SVG + '</span><span class="evtx"><b>Season Conquest</b><small>Claim the season’s canvases</small></span></span>'
        '<span class="evart" aria-hidden="true"><img id="evConqArt" alt=""></span></button><i class="evsoon">Coming soon</i></div>')

HOLD = r"""
// (v300) a long hold always lets go: iOS can swallow the finger-up of a long press, which left the brake on until the next touch. The
// touch events always come, so when the last finger lifts with the steering finger still open, that's the release. A lift that lands
// on something other than the play area counts too.
{ const lift = id => { if (steerId === null || id !== steerId) return; endPtr({ pointerId: id }); };
  for (const k of ['pointerup', 'pointercancel']) window.addEventListener(k, e => { if (e.pointerId === steerId && e.target !== canvas) { if (k === 'pointerup') lift(e.pointerId); else { touches.delete(e.pointerId); steerId = null; steerIn = 0; rangeIn = 0; if (holdCharge) cancelCharge(P); holdCharge = false; slingOff(); } } }, true);
  for (const k of ['touchend', 'touchcancel']) window.addEventListener(k, e => { if (steerId === null || (e.touches && e.touches.length)) return; const id = steerId; setTimeout(() => lift(id), 0); }, true); }
"""

def apply(s):
    # no announcer on the results
    s = rep(s, "setTimeout(() => AU.say(solo ? (info.newBest ? 'best' : 'time') : won ? 'victory' : info.winner ? 'defeat' : 'draw'), 650); AU.music(won ? 'win' : 'lost');",
               "/* (v300: no announcer line on the results) */ AU.music(won ? 'win' : 'lost');")
    # the hold's release, whatever happens to the finger-up
    a = "canvas.addEventListener('contextmenu', e => e.preventDefault());\n"
    s = rep(s, a, a + HOLD.lstrip('\n'))
    # Season Conquest, faded with Coming soon (after Time trial)
    a = '<span class="evtx"><b>Time trial</b><small>Just you, 60 seconds</small></span></span><span class="evart" aria-hidden="true"><img id="evSoloArt" alt=""></span></button></div>'
    s = rep(s, a, a + '\n        ' + CARD)
    s = rep(s, "set('evShowArt', 'manor');", "set('evShowArt', 'manor'); set('evConqArt', 'island');")
    a = "$('evMatch').addEventListener('click', () => {"
    s = rep(s, a, "$('evConq').addEventListener('click', () => { AU.init(); AU.nope(); const c = $('evConq').closest('.evcard'), old = c.querySelector('.evtoast'); if (old) old.remove(); const t = document.createElement('span'); t.className = 'evtoast'; t.textContent = 'Season Conquest is coming soon'; c.appendChild(t); setTimeout(() => t.remove(), 1700); }); // (v300)\n" + a)
    return s
