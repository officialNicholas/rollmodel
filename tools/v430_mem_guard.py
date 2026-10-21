"""v430: the game restarting mid-session (iOS closing the page when the phone runs short of memory).

- Less held during a match: the lobby song and the locker's cut of it were kept decoded through every match (about 30 MB of raw sound
  on an iPhone). They are let go when a match starts and decoded again as the results come up, ready for the lobby.
- If the page is closed under a match anyway (the app starts the game again), the next launch knows: while a match runs, the game
  stamps it every couple of seconds, and wipes the stamp when the match ends or the app is put away. A stamp still there at launch
  means the last match never ended. Then the game steps itself down a level, so it doesn't happen again: from Graphics to
  Performance, or, already in Performance, to fewer pixels and lighter music holding. A note in the lobby says what changed and that
  Settings can change Visuals back. The same goes for the restart the game makes itself when the phone takes the graphics away and
  doesn't give them back.
"""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

BOOT = r"""// (v430) the last match never ended: the page was closed under it (most likely the phone ran out of memory). Step down a level
// before the visuals are picked, so it doesn't happen again: Graphics to Performance, or Performance to fewer pixels (store.lowMem)
const MEM_DOWN = (() => { try {
  const L = JSON.parse(localStorage.getItem('rm.live') || 'null'), C = JSON.parse(localStorage.getItem('rm.crashed') || 'null');
  localStorage.removeItem('rm.live'); localStorage.removeItem('rm.crashed');
  const hit = L && Date.now() - L.t < 10 * 60000 ? L : C && Date.now() - C.t < 10 * 60000 ? C : null; if (!hit) return null;
  const was = store.gfx === 'perf' || store.gfx === 'hi' ? store.gfx : DEV_TIER >= 2 ? 'hi' : 'perf'; let did = null;
  store.memCrash = (store.memCrash || 0) + 1;
  if (was === 'hi') { store.gfx = 'perf'; did = 'gfx'; } else if (!store.lowMem) { store.lowMem = 1; did = 'px'; }
  localStorage.setItem(KEY, JSON.stringify(store)); localStorage.setItem(KEY + '.t', String(Date.now()));
  return did;
} catch (e) { return null; } })();
"""

LIVE = r"""
// (v430) while a match runs it's stamped (see MEM_DOWN at the top): a stamp left at the next launch means the page closed under it
{ const K = 'rm.live', off = () => { try { localStorage.removeItem(K); } catch (e) {} };
  setInterval(() => { if (document.hidden) return; try { if (state === 'play' || state === 'paused') localStorage.setItem(K, JSON.stringify({ t: Date.now(), m: mode, g: GFX })); else off(); } catch (e) {} }, 2000);
  document.addEventListener('visibilitychange', () => { if (document.hidden) off(); }); addEventListener('pagehide', off);
  const memToast = h => { const t = document.createElement('div'); t.className = 'frtoast memtoast'; t.setAttribute('role', 'status'); t.innerHTML = '<span>' + h + '</span>';
    document.body.appendChild(t); try { AU.pop(); } catch (e) {} setTimeout(() => t.classList.add('out'), 7500); setTimeout(() => t.remove(), 8100); };
  if (MEM_DOWN) { const say = () => { if (typeof lobbyOn === 'function' && lobbyOn() && !document.hidden) memToast((MEM_DOWN === 'gfx'
      ? 'The game ran short of memory and restarted. <b>Visuals</b> are now on <b>Performance</b> to keep that from happening. You can change it in Settings.'
      : 'The game ran short of memory and restarted. It now draws a little softer to keep that from happening.'));
    else setTimeout(say, 1000); }; setTimeout(say, 1500); } }
"""

CSS = ".frtoast.memtoast{border-radius:16px;padding:11px 16px;max-width:min(90vw,380px);text-align:center;font-weight:600;line-height:1.35}.frtoast.memtoast b{font-weight:800}"

def apply(s):
    i = s.index(".frtoast{"); s = s[:i] + CSS + s[i:]
    s = rep(s, "const GFX = store.gfx === 'perf' || store.gfx === 'hi' ? store.gfx : DEV_TIER >= 2 ? 'hi' : 'perf', HI = GFX === 'hi';",
               BOOT + "const GFX = store.gfx === 'perf' || store.gfx === 'hi' ? store.gfx : DEV_TIER >= 2 ? 'hi' : 'perf', HI = GFX === 'hi';")
    # fewer pixels after a crash already in Performance
    s = rep(s, "const PR_CAP = (HI ? [1.25, 1.35, 1.6, 2][DEV_TIER] : [1, 1.2, 1.4, 1.6][DEV_TIER]) * (NATIVE && NATIVE.lowPower ? 0.8 : 1);",
               "const PR_CAP = (HI ? [1.25, 1.35, 1.6, 2][DEV_TIER] : [1, 1.2, 1.4, 1.6][DEV_TIER]) * (NATIVE && NATIVE.lowPower ? 0.8 : 1) * (store.lowMem ? 0.85 : 1); // (v430: lowMem, after a crash)")
    s = rep(s, "const Q_PIX = 1.2e6;", "const Q_PIX = store.lowMem ? 0.85e6 : 1.2e6; // (v430: fewer after a crash in Performance)")
    # the game's own restart when the graphics don't come back counts too
    s = rep(s, "lostAt = 0; try { save(); saveSend(); } catch (e) {} location.reload(); }, 1000); }",
               "lostAt = 0; try { localStorage.setItem('rm.crashed', JSON.stringify({ t: Date.now(), why: 'gl', g: GFX })); save(); saveSend(); } catch (e) {} location.reload(); }, 1000); }")
    # music: the lobby's songs let go during a match, back as the results come up
    s = rep(s, "        if (mode === 'play') { trkDecode('win'); trkDecode('lost'); }\n",
               "        if (mode === 'play') { trkDecode('win'); trkDecode('lost'); }\n"
               "        if (mode === 'win' || mode === 'lost') trkDecode('menu'); // (v430: back for the lobby)\n")
    s = rep(s, "        if (mode === 'menu') { trkDrop('win'); trkDrop('lost'); trkDecode('spook'); } // (the locker's cut gets ready while you are in the lobby)\n",
               "        if (mode === 'menu') { trkDrop('win'); trkDrop('lost'); trkDecode('spook'); } // (the locker's cut gets ready while you are in the lobby)\n"
               "        if (mode === 'play' && key) { trkDrop('menu'); trkDrop('spook'); } // (v430: the lobby's songs wait out the match: let go once the match's own has taken over)\n")
    # after frToast exists
    s = rep(s, "function frToast(html) {", LIVE + "function frToast(html) {")
    return s
