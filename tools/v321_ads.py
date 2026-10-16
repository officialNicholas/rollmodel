"""v321: a rewarded ad speeds up crafting.

- On the Strokes page, Skip on a stroke being crafted now plays a rewarded ad in the app (Google AdMob, through the app's "ads"
  bridge: ios/RollModel/RollModel/AdsBridge.swift). The craft finishes, with its usual fanfare, once the ad says it was watched.
  Closing the ad early earns nothing ("Watch to the end to finish it"), and with no ad to show the craft just carries on.
- The button says so: a play mark on Skip, and under it "Watch an ad to finish it now". While the ad gets ready the mark spins.
- The lesson's Skip stays free (Ol' Bloop: "this one's on me"), and so does an app built without the ads SDK.
- While the ad plays, the game's sound is off and the bench holds still; the sound starts afresh when it closes, as after a call.
- The app is told who's playing: a player who said they're under 13 (at the account form, with no account made since) gets
  child-safe, non-personalised ads only.
- A browser has no ads to play, so there a five-second stand-in shows where the ad goes (closing it early earns nothing too).
- The Privacy Policy says what the ads collect, and gets an "Ad privacy choices" button where Google says players need one
  (some players in the EEA, the UK and Switzerland)."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

JS = r"""
// (v321) a rewarded ad speeds up crafting. In the app, Skip on a stroke being crafted plays a rewarded ad (AdsBridge.swift: Google
// AdMob) and the craft finishes once the ad says it was watched; the lesson's Skip stays free (it's on Ol' Bloop). The page asks
// through nativeSay('ads', ...) and hears back on a "nativead" event: open, reward, close, fail, and state (whether Google wants the
// "Ad privacy choices" button). A browser has no ads, so a short stand-in shows where it goes
const ADS = { mode: window.__ADS ? (window.__ADS.sdk ? 'app' : 'none') : 'web', id: null, open: false, earned: false, hold: false, t: 0, ct: 0, si: 0, privacy: false, sent: '' };
const AD_PLAY = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="10.5" fill="currentColor"/><path d="M9.8 7.7v8.6l6.9-4.3z" fill="#FFE896"/></svg>';
const adKid = () => !!store.acYoung && !(store.sbs && store.sbs.acct); // (said they're under 13 at the account form, and no account since)
const adFree = () => ADS.mode === 'none' || !!(store.tut && store.tut.strokes === 'on' && ((store.strokes || {}).craft || {}).id === 'giant');
// the app is told who's playing (again if that changes), and when an ad may be wanted soon (a stroke on the bench), so one's ready
function adHello(warm) { if (ADS.mode !== 'app') return; const kid = adKid(), k = String(kid); if (!warm && ADS.sent === k) return; ADS.sent = k; nativeSay('ads', { init: true, kid, warm: !!warm }); }
function adWarm() { const d = store.strokes; if (d && d.craft && !adFree()) adHello(true); }
// Skip on the bench: free in the lesson; otherwise the ad, and the craft's done when it's been watched
function craftSkipAsk() {
  const d = strokesOf(); if (!d.craft) return;
  if (adFree()) return craftSkip();
  if (ADS.id) return; // (one at a time)
  ADS.id = d.craft.id; ADS.earned = false; ADS.open = false; AU.ui(); buzz(6); sgSkipPaint();
  clearTimeout(ADS.t); ADS.t = setTimeout(() => adFail('slow'), 45000); // (the app answers well before this: it's in case it never does)
  if (ADS.mode === 'app') nativeSay('ads', { show: 'craft', kid: adKid() }); else adStandIn();
}
window.addEventListener('nativead', e => adOn((e && e.detail) || {}));
function adOn(m) {
  if (m.e === 'state') { ADS.privacy = !!m.privacy; return adPrivPaint(); }
  if (m.p && m.p !== 'craft') return;
  if (m.e === 'open') { clearTimeout(ADS.t); ADS.open = ADS.hold = true; if (!ADS.id) { const d = store.strokes; ADS.id = d && d.craft ? d.craft.id : null; } if (ADS.mode === 'app') AU.suspend(true); else AU.muted(true); return; }
  if (m.e === 'reward') return adReward();
  if (m.e === 'close') return adClose(!!m.earned);
  if (m.e === 'fail') return adFail(m.why);
}
// the reward: the craft's done now (kept, in case the app is closed mid-ad), and shown off when the ad closes
function adReward() {
  if (!ADS.id) return; ADS.earned = true; const d = store.strokes;
  if (d && d.craft && d.craft.id === ADS.id) { d.craft.end = Math.min(d.craft.end, Date.now()); save(); }
  if (!ADS.open && !ADS.ct) adPayoff();
}
// closed: a beat for the sound to come back (and for a reward that comes just after the close), then the craft's shown off, or not
function adClose(earned) {
  ADS.open = false; clearTimeout(ADS.t); if (ADS.mode !== 'app') applyMix(); // (in the app, its "nativeresume" brings the sound back)
  if (earned) ADS.earned = true;
  clearTimeout(ADS.ct); ADS.ct = setTimeout(() => { ADS.ct = 0; if (ADS.earned) return adPayoff(); adDone(); stToast('Watch to the end to finish it'); }, 420);
}
function adPayoff() { const id = ADS.id; adDone(); const d = strokesOf(); if (id && d.craft && d.craft.id === id) craftSkip(); else if (strokesOpen()) renderStrokes(); }
function adFail(why) {
  if (!ADS.id && !ADS.open) return;
  const was = ADS.open; adDone(); if (was) { if (ADS.mode === 'app') AU.wake(true, true); else applyMix(); }
  AU.nope && AU.nope(); stToast(why === 'offline' ? 'You’re offline: connect to watch the ad' : 'No ad to show right now. Try again soon');
}
function adDone() { clearTimeout(ADS.t); clearTimeout(ADS.ct); clearInterval(ADS.si); ADS.ct = 0; ADS.id = null; ADS.open = ADS.hold = ADS.earned = false; sgSkipPaint(); }
// Skip on the bench: a play mark when it plays an ad (spinning while the ad gets ready), plain in the lesson
function sgSkipPaint() {
  const sk = $('sgSkip'); if (!sk) return; const free = adFree(), busy = !free && !!ADS.id, m = free ? 'free' : busy ? 'busy' : 'ad';
  if (sk.dataset.m === m) return; sk.dataset.m = m; sk.classList.toggle('ad', !free); sk.classList.toggle('busy', busy); sk.disabled = busy;
  sk.innerHTML = free ? 'Skip' : '<i class="sgadi" aria-hidden="true">' + (busy ? '<b class="sgspin"></b>' : AD_PLAY) + '</i><span>Skip</span>';
  sk.setAttribute('aria-label', free ? 'Skip the wait' : busy ? 'Getting the ad ready' : 'Watch an ad to finish it now');
}
// (in a browser) a stand-in for the ad: five seconds, then the reward; closed early it earns nothing, as with a real one
function adStandIn() {
  const el = $('adStand'); let left = 5; el.classList.remove('done'); $('adStN').textContent = left; $('adStW').textContent = 'Ad preview'; el.hidden = false;
  adOn({ e: 'open', p: 'craft' }); setTimeout(() => $('adStX').focus({ preventScroll: true }), 40);
  clearInterval(ADS.si); ADS.si = setInterval(() => {
    if (--left > 0) { $('adStN').textContent = left; return; }
    clearInterval(ADS.si); el.classList.add('done'); $('adStN').innerHTML = ST_CHECK; $('adStW').textContent = 'Reward earned'; adOn({ e: 'reward', p: 'craft' }); setTimeout(() => adStandOut(), 900);
  }, 1000);
}
function adStandOut() { const el = $('adStand'); if (el.hidden) return; clearInterval(ADS.si); el.hidden = true; adOn({ e: 'close', p: 'craft', earned: ADS.earned }); }
$('adStX').addEventListener('click', () => { AU.ui(); adStandOut(); });
// the Privacy Policy's "Ad privacy choices" button, where Google says the player needs one (in the app only)
function adPrivPaint() {
  const body = $('docBody'), p = $('adsP'); let b = $('adPriv'); const want = ADS.mode === 'app' && ADS.privacy && !!p;
  if (!want) { if (b) b.remove(); return; }
  if (b) return; b = document.createElement('button'); b.type = 'button'; b.className = 'frb adpriv'; b.id = 'adPriv'; b.textContent = 'Ad privacy choices';
  b.addEventListener('click', () => { AU.init(); AU.ui(); nativeSay('ads', { privacy: true }); }); p.after(b);
}
setTimeout(() => { if (strokesDue()) { adHello(false); adWarm(); } }, 5000); // (once the game's up: the app checks with Google, and readies an ad if one may be wanted)
"""

CSS = r"""
/* (v321) Skip on the bench plays a rewarded ad: a play mark on it, spinning while the ad gets ready */
#mStrokes.sgp .sgskip.ad{display:inline-flex;align-items:center;gap:6px;padding:0 16px 2px 12px}
#mStrokes.sgp .sgskip .sgadi{display:grid;place-items:center;width:18px;height:18px;flex:none}
#mStrokes.sgp .sgskip .sgadi svg{width:18px;height:18px;display:block}
#mStrokes.sgp .sgskip.busy{cursor:default}
#mStrokes.sgp .sgskip.busy span{opacity:.55}
#mStrokes.sgp .sgskip .sgspin{width:14px;height:14px;border-radius:50%;border:2.5px solid currentColor;border-right-color:transparent;animation:sgspin .7s linear infinite}
@keyframes sgspin{to{transform:rotate(360deg)}}
@media (prefers-reduced-motion:reduce){#mStrokes.sgp .sgskip .sgspin{animation-duration:1.6s}}
/* (v321) in a browser, the stand-in for the ad */
.adst{position:fixed;inset:0;z-index:80;display:grid;place-items:center;padding:24px 16px;background:rgba(12,9,18,.94);color:#F4EEE3;animation:adstin .22s ease both}
.adst[hidden]{display:none}
@keyframes adstin{from{opacity:0}to{opacity:1}}
.adst .adsl{position:absolute;left:max(16px,env(safe-area-inset-left));top:max(16px,env(safe-area-inset-top));padding:5px 8px 4px;border-radius:5px;background:#F2C14E;color:#171320;font:900 11px/1 var(--font-ui);letter-spacing:.14em}
.adst .adsx{position:absolute;right:max(12px,env(safe-area-inset-right));top:max(10px,env(safe-area-inset-top));display:grid;place-items:center;width:40px;height:40px;margin:0;padding:0;border:0;border-radius:50%;background:rgba(255,255,255,.12);color:#F4EEE3;cursor:pointer;-webkit-tap-highlight-color:transparent}
.adst .adsx svg{width:16px;height:16px}
.adst .adsc{display:flex;flex-direction:column;align-items:center;gap:14px;max-width:290px;text-align:center}
.adst .adsr{position:relative;display:grid;place-items:center;width:104px;height:104px}
.adst .adsr svg.ring{position:absolute;inset:0;width:100%;height:100%;transform:rotate(-90deg)}
.adst .adsr circle{fill:none;stroke-width:7}
.adst .adsr .bg{stroke:rgba(255,255,255,.12)}
.adst .adsr .fg{stroke:#F2C14E;stroke-linecap:round;stroke-dasharray:276.5;stroke-dashoffset:276.5}
.adst:not([hidden]) .adsr .fg{animation:adsring 5s linear forwards}
@keyframes adsring{to{stroke-dashoffset:0}}
.adst.done .adsr .fg{stroke:#5BE07E}
.adst .adsr b{display:grid;place-items:center;font:400 38px/1 var(--font-display);font-variant-numeric:tabular-nums}
.adst .adsr b svg{width:44px;height:44px;color:#5BE07E}
.adst h3{margin:0;font:400 24px/1.05 var(--font-display);letter-spacing:.01em}
.adst p{margin:0;font:700 14px/1.4 var(--font-ui);color:#CFC8DC;text-wrap:balance}
/* (v321) the Privacy Policy's button for Google's privacy choices */
#docModal .docb .adpriv{justify-self:start}
"""

HTML = ('<div class="adst" id="adStand" hidden role="dialog" aria-modal="true" aria-labelledby="adStW"><span class="adsl">AD</span>'
        '<button class="adsx" id="adStX" type="button" aria-label="Close the ad"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 5l14 14M19 5L5 19" stroke="currentColor" stroke-width="3.2" stroke-linecap="round"/></svg></button>'
        '<div class="adsc"><div class="adsr"><svg class="ring" viewBox="0 0 100 100" aria-hidden="true"><circle class="bg" cx="50" cy="50" r="44"/><circle class="fg" cx="50" cy="50" r="44"/></svg><b id="adStN">5</b></div>'
        '<h3 id="adStW">Ad preview</h3><p>In the app, a rewarded ad plays here. Watch it to the end and the stroke is done.</p></div></div>\n')

PRIV_OLD = "<h3>Who has it</h3><p>We don’t sell your information or show you ads. Supabase stores it for us, and online matches run on our game server.</p>"
PRIV_NEW = ("<h3>Who has it</h3><p>We don’t sell your information. Supabase stores it for us, and online matches run on our game server.</p>"
            "<h3>Ads</h3><p id=\"adsP\">In the iPhone app you can choose to watch an ad, for example to finish crafting a stroke right away. "
            "An ad only plays when you tap to watch one. Ads come from Google AdMob, which gets some information from your device to show "
            "an ad and count it: your IP address (which gives a rough location), the kind of device, an identifier for the device that’s "
            "only shared within our apps, and how the ad was watched. The game doesn’t ask to track you across other companies’ apps. If "
            "you told us you’re under 13, you only get ads that are fit for children, and they aren’t personalised. Where the law asks for "
            "it, Google asks for your consent before your first ad.</p>")

def apply(s):
    s = rep(s, "function craftSkip() { const d = strokesOf(); if (!d.craft) return; const id = d.craft.id; d.craft.end = Date.now(); craftTick(); AU.ui(); buzz([10, 30, 10]); renderStrokes(); stToast(stReady(id)); }\n",
               "function craftSkip() { const d = strokesOf(); if (!d.craft) return; const id = d.craft.id; d.craft.end = Date.now(); craftTick(); AU.ui(); buzz([10, 30, 10]); renderStrokes(); stToast(stReady(id)); }\n" + JS.lstrip('\n'))
    # Skip asks for the ad (the lesson's stays free); a stroke going on the bench gets one ready
    s = rep(s, "$('sgSkip').addEventListener('click', () => { AU.init(); craftSkip(); });", "$('sgSkip').addEventListener('click', () => { AU.init(); craftSkipAsk(); }); // (v321: an ad first, outside the lesson)")
    s = rep(s, "d.craft = { id, end: Date.now() + sp.craft * 60000 }; save(); AU.pop(); buzz(10); renderStrokes(); }",
               "d.craft = { id, end: Date.now() + sp.craft * 60000 }; save(); AU.pop(); buzz(10); renderStrokes(); adWarm(); }")
    s = rep(s, "closeSide(true); renderStrokes();", "closeSide(true); renderStrokes(); adWarm();")
    # the button and its line say an ad plays
    s = rep(s, "  if (cr) sgBench(o);\n", "  if (cr) sgBench(o); sgSkipPaint();\n")
    s = rep(s, "  const note = own || cr ? '' : !due ?", "  const note = own ? '' : cr ? (adFree() ? '' : 'Watch an ad to finish it now') : !due ?")
    # while the ad's up, the bench holds still (the craft's shown off when it closes), and the app's sound nudge waits for the close
    s = rep(s, "function strokesFrame() { if (!strokesOpen()) return; ", "function strokesFrame() { if (!strokesOpen() || ADS.hold) return; ")
    s = rep(s, "window.addEventListener('nativeresume', e => AU.wake(true, !!(e && e.detail && e.detail.away)));",
               "window.addEventListener('nativeresume', e => { if (ADS.open) return; AU.wake(true, !!(e && e.detail && e.detail.away)); }); /* (v321: not under an ad: the close sends its own) */")
    # an under-13 answer at the account form: the app's told at once
    s = rep(s, "store.acYoung = Date.now(); save();", "store.acYoung = Date.now(); save(); adHello(false);", 2)
    # the Privacy Policy: what the ads collect, and Google's privacy choices where needed
    s = rep(s, PRIV_OLD, PRIV_NEW)
    s = rep(s, "$('docModal').hidden = false; setTimeout(() => $('docClose').focus({ preventScroll: true }), 30); }",
               "$('docModal').hidden = false; if (k === 'priv') adPrivPaint(); setTimeout(() => $('docClose').focus({ preventScroll: true }), 30); }")
    s = rep(s, '  <div class="modal" id="docModal" hidden>', HTML + '  <div class="modal" id="docModal" hidden>')
    i = s.rfind('</style>'); s = s[:i] + CSS + s[i:]
    return s
