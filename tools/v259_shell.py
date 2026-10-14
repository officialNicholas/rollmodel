"""v259: sturdier inside the iPhone app.
- The save is also kept by the app itself, outside the web view's storage (which iOS can clear, and which can lose the last second of
  writes if the app is closed at once). Each save carries its time, so at the next start whichever copy is newer wins.
- The graphics can be taken away from the page (most often while the app is in the background). three.js asks for them back and carries
  on when they return; the paint is kept by the game, so nothing is lost. If they haven't come back a few seconds after the game is in
  view again, it starts over with progress saved, rather than sit on a frozen screen.
- When the phone is short of memory, the sound lets go of the decoded songs it isn't playing (they decode again when needed)."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)
SAVE = r"""// (v259) in the iPhone app the save is also kept by the app itself, outside the web view's storage (which iOS can clear), with the time
// it was made, so the newer copy wins at the next start (see the app's save script). A burst of saves goes over once, and at once when
// the app is put away
const NSAVE = (() => { try { return (window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.save) || null; } catch (e) { return null; } })();
let saveQ = 0, saveJ = '', saveT = 0;
const saveSend = () => { if (saveQ) { clearTimeout(saveQ); saveQ = 0; } if (!NSAVE || !saveJ) return; try { NSAVE.postMessage({ t: saveT, save: saveJ }); } catch (e) {} saveJ = ''; };
const save = () => { let j = ''; try { j = JSON.stringify(store); saveT = Date.now(); localStorage.setItem(KEY, j); localStorage.setItem(KEY + '.t', String(saveT)); } catch (e) {}
  if (NSAVE && j) { saveJ = j; if (!saveQ) saveQ = setTimeout(saveSend, 400); } };
if (NSAVE) { document.addEventListener('visibilitychange', () => { if (document.hidden) saveSend(); }); window.addEventListener('pagehide', saveSend); }"""
GL = r"""
// (v259) the phone can take the graphics away from the page (most often while the app is in the background). three.js asks for them
// back and carries on when they return (the paint is kept by the game, so nothing is lost). If they haven't come back a few seconds
// after the game is in view again, it starts over, progress saved, rather than sit on a frozen screen
{ let lostAt = 0;
  canvas.addEventListener('webglcontextlost', () => { lostAt = performance.now(); });
  canvas.addEventListener('webglcontextrestored', () => { lostAt = 0; });
  document.addEventListener('visibilitychange', () => { if (lostAt && !document.hidden) lostAt = performance.now(); });
  setInterval(() => { if (!lostAt || document.hidden || performance.now() - lostAt < 4000) return; lostAt = 0; try { save(); saveSend(); } catch (e) {} location.reload(); }, 1000); }"""
TRIM = r"""    get renews() { return renews; },
    // (v259) the phone is short of memory: let go of the songs that aren't playing or wanted next, decoded and file both (they load
    // again from the app when needed), and the curator's lines
    trim() { const keep = [trk && trk.key, trkWant]; for (const k in TRK) if (!keep.includes(k)) { trkDrop(k); if (!TRK[k].decoding && !TRK[k].fetching) TRK[k].bytes = null; } for (const k in SAY) delete SAY[k]; },"""
def apply(s):
    s = rep(s, "const save = () => { try { localStorage.setItem(KEY, JSON.stringify(store)); } catch (e) {} };", SAVE)
    s = rep(s, "const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' });",
               "const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' });" + GL)
    s = rep(s, "    get renews() { return renews; },", TRIM)
    s = rep(s, "window.addEventListener('nativeresume', e => AU.wake(true, !!(e && e.detail && e.detail.away)));",
               "window.addEventListener('nativeresume', e => AU.wake(true, !!(e && e.detail && e.detail.away))); window.addEventListener('nativememory', () => AU.trim());")
    return s
