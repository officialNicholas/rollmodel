"""v258: the sound comes back after the app has been away. An iPhone can hand the page its audio context back stuck after a trip to the
background (suspended, "interrupted", or running with no sound), and a resume doesn't always free it. So when the app says it's back
from the background (or an interruption such as a call has ended), the sound starts on a fresh context, the song carrying on from where
it was. Any wake now checks the clock is really moving; if it isn't, the app tries again by itself and any touch starts it afresh."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)
JS = r"""  // (v258) a fresh start for the sound: a new audio context in place of one the phone has left stuck (suspended, "interrupted", or
  // running with no sound, as an iPhone can after the app has been in the background). The decoded songs and sound sheets carry over;
  // the song that was playing picks up where it was, muffled again if the game is paused. awayHid: the sound has been away (hidden or
  // interrupted) and hasn't been heard to run since; stuck: a wake didn't get the clock moving, so the next touch starts afresh
  let awayHid = false, stuck = false, retry = 0, renewAt = -1e9, checkId = 0, renews = 0;
  function watch(c) { c.onstatechange = () => { if (c === ctx && c.state === 'interrupted') awayHid = true; }; }
  function renew() {
    const AC = window.AudioContext || window.webkitAudioContext; if (!AC) return false;
    if (!stuck && ctx && ctx.state === 'running' && performance.now() - renewAt < 1500) { check(); return true; } // (two signals for one return)
    const old = ctx, key = trk && trk.key, pos = trk ? trkPos() : 0, mode = lastMode;
    let c; try { c = new AC({ latencyHint: 'interactive' }); } catch (e) { return false; }
    if (timer) { clearInterval(timer); timer = 0; }
    if (old) { old.onstatechange = null; try { const p = old.close(); if (p && p.catch) p.catch(() => {}); } catch (e) {} }
    trk = null; chA = null; LP = null; stuck = false; renewAt = performance.now(); renews++;
    build(c, true); watch(c);
    const rain = mood.rain, siz = mood.sizzle; mood.sizzle = 0; if (rain) api.rain(rain); if (siz) api.sizzle(siz);
    if (key && TRK[key] && TRK[key].buf) { trkGo(key, 0, 0.5, true, pos); if (mode === 'pause' || mode === 'vs') api.music(mode); }
    else if (mode !== 'none') { lastMode = 'none'; api.music(mode); }
    if (c.state !== 'running') { try { const p = c.resume(); if (p && p.catch) p.catch(() => {}); } catch (e) {} }
    check();
    try { window.dispatchEvent(new Event('aurenew')); } catch (e) {}
    return true;
  }
  // is the sound really going? Its clock has to move. If it hasn't within a moment: in the app, try a fresh start again by itself;
  // anywhere, the next touch starts it afresh
  function check() {
    const c = ctx, id = ++checkId; if (!c) return; const t0 = c.currentTime;
    setTimeout(() => { if (id !== checkId || c !== ctx || document.hidden) return;
      if (c.state === 'running' && c.currentTime - t0 > 0.2) { stuck = false; awayHid = false; retry = 0; return; }
      stuck = true; if (retry > 0) { retry--; renew(); } }, 800);
  }
"""
def apply(s):
    s = rep(s, "  const api = {\n    // synthesize the kit and the reverbs now", JS + "  const api = {\n    // synthesize the kit and the reverbs now")
    s = rep(s, "      let c; try { c = new AC({ latencyHint: 'interactive' }); } catch (e) { return; }\n      build(c, true); sbLoad();",
               "      let c; try { c = new AC({ latencyHint: 'interactive' }); } catch (e) { return; }\n      build(c, true); watch(c); sbLoad();")
    s = rep(s, "    suspend(h) { if (!ctx) return; if (h) ctx.suspend().catch(() => {}); else api.wake(); },",
               "    suspend(h) { if (!ctx) return; if (h) { awayHid = true; ctx.suspend().catch(() => {}); } else api.wake(); },")
    # the app is back (kick): from the background or an interruption (away, or hidden since), a fresh context; else the old stop-and-start
    s = rep(s, "    wake(kick) {\n      if (!ctx) return;\n      if (ctx.state === 'closed') { ctx = null; trk = null; api.init(); return; }",
               "    wake(kick, away) {\n      if (!ctx) return;\n      if (ctx.state === 'closed') { renew(); return; }\n"
               "      if (kick && (away || awayHid)) { retry = 2; renew(); return; }\n      if (kick) retry = 1;")
    s = rep(s, "      if (kick && ctx.state === 'running') ctx.suspend().then(go, go); else go();\n      wakeArm = true;\n    },",
               "      if (kick && ctx.state === 'running') ctx.suspend().then(go, go); else go();\n      wakeArm = true; check();\n    },\n"
               "    get renews() { return renews; },")
    s = rep(s, "    touch() { if (!ctx) api.init(); else if (ctx.state !== 'running' || wakeArm) { wakeArm = false; api.wake(); } },",
               "    touch() { if (!ctx) api.init(); else if (stuck || (awayHid && ctx.state !== 'running')) { wakeArm = false; renew(); } else if (ctx.state !== 'running' || wakeArm) { wakeArm = false; api.wake(); } },")
    s = rep(s, "window.addEventListener('nativeresume', () => AU.wake(true));",
               "window.addEventListener('nativeresume', e => AU.wake(true, !!(e && e.detail && e.detail.away)));")
    return s
