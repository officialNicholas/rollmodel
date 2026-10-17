"""v335: the ad for Skip is got ready as the Abilities page opens, and a card waits for it when it isn't ready yet.

- The app readies a rewarded ad as soon as the Abilities page opens (it used to only while a stroke was being crafted), and again once
  one's been watched, so Skip plays one at once.
- Skip tapped before the ad's loaded: a taped paper card comes up, "Getting your ad ready", with a spinner round the ad's play mark and
  Cancel. The ad plays the moment it's ready (it covers the card). While it's slow the game asks the app again (an ad that turns up
  late is kept for this), for up to 20 seconds. If the ad was ready, it just plays: the card only comes up after half a second.
- None came: the card says why (offline, too slow, or no ad to show) with Try again and Close, in place of the toast.
- Cancel tells the app to stop waiting, so the ad doesn't pop up later (AdsBridge.swift: {cancel}). Escape works as Cancel.
- In a browser the five-second stand-in plays as before."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

HTML = ('<div class="adw" id="adWait" hidden><div class="adwc" role="dialog" aria-modal="true" aria-labelledby="adWaitH" aria-describedby="adWaitP">'
        '<div class="adwi" aria-hidden="true"><svg class="adwr" viewBox="0 0 100 100"><circle class="bg" cx="50" cy="50" r="42"/><circle class="fg" cx="50" cy="50" r="42"/></svg><span class="adwp" id="adWaitI"></span><span class="adwx">!</span></div>'
        '<h3 id="adWaitH">Getting your ad ready</h3><p id="adWaitP">It starts as soon as it’s loaded.</p>'
        '<div class="adwb"><button class="adwgo" id="adWaitGo" type="button" hidden>Try again</button><button class="adwno" id="adWaitNo" type="button">Cancel</button></div></div></div>\n')

CSS = r'''
/* ---- (v335) the ad on its way: a taped paper card over the page while the ad for Skip loads (it plays the moment it's ready, over
   the card), and what went wrong if it doesn't come */
.adw{position:fixed;inset:0;z-index:70;display:grid;place-items:center;padding:24px max(16px,env(safe-area-inset-right)) 24px max(16px,env(safe-area-inset-left));background:rgba(10,7,16,.55);animation:adstin .2s ease both}
.adw[hidden]{display:none}
.adwc{position:relative;display:flex;flex-direction:column;align-items:center;gap:10px;width:min(100%,320px);box-sizing:border-box;padding:30px 22px 20px;border-radius:6px;background:#F6F1E8 url(art/m_paperbg.webp) center/420px;color:#171320;text-align:center;box-shadow:0 0 0 3px #171320,7px 8px 0 rgba(0,0,0,.45);animation:cardlift .34s cubic-bezier(.2,1.25,.35,1) both}
.adwc::before{content:"";position:absolute;left:50%;top:-12px;width:112px;height:28px;margin-left:-56px;background:url(art/m_tape3.webp) center/100% 100% no-repeat;transform:rotate(-2deg);filter:drop-shadow(0 1.5px 0 rgba(23,19,32,.16))}
.adwi{position:relative;display:grid;place-items:center;width:84px;height:84px;margin-bottom:2px}
.adwr{position:absolute;inset:0;width:100%;height:100%;animation:sgspin .9s linear infinite}
.adwr circle{fill:none;stroke-width:8}
.adwr .bg{stroke:rgba(23,19,32,.12)}
.adwr .fg{stroke:#F2C14E;stroke-linecap:round;stroke-dasharray:66 198}
.adwp{display:grid;place-items:center;width:46px;height:46px;color:#171320}
.adwp svg{display:block;width:46px;height:46px}
.adwx{display:none}
.adw.fail .adwr,.adw.fail .adwp{display:none}
.adw.fail .adwx{display:grid;place-items:center;width:56px;height:56px;border-radius:50%;background:#171320;color:#FFE23C;font:400 32px/1 var(--font-display)}
.adwc h3{margin:0;font:400 24px/1.05 var(--font-display);letter-spacing:.01em;text-wrap:balance}
.adwc p{margin:0;font:700 14px/1.4 var(--font-ui);color:#4A4258;text-wrap:balance}
.adwb{display:flex;gap:10px;margin-top:6px}
.adwb button{appearance:none;margin:0;min-width:108px;height:42px;padding:0 18px;border:0;border-radius:12px;font:400 16px/1 var(--font-display);letter-spacing:.01em;cursor:pointer;-webkit-tap-highlight-color:transparent;box-shadow:0 0 0 2.5px #171320,2px 3px 0 rgba(23,19,32,.3)}
.adwb button[hidden]{display:none}
.adwgo{background:linear-gradient(180deg,#FFE08A,#F2C14E 55%,#E0A72A);color:#2A1A04}
.adwno{background:#fff;color:#171320}
.adwb button:active{transform:translate(1px,2px);box-shadow:0 0 0 2.5px #171320,1px 1px 0 rgba(23,19,32,.3)}
@media (prefers-reduced-motion:reduce){.adw,.adwc{animation:none}.adwr{animation-duration:2.4s}}
'''

JS = r'''
// ---------- (v335) the ad on its way. The app readies an ad as the Abilities page opens (and again once one's been watched), so Skip
// plays one at once. Tapped before it's ready, a card waits for it: the ad plays the moment it loads (over the card); while it's slow
// the game asks again (one that turns up late is kept for this), up to AD_WAIT_MS; Cancel tells the app to stop waiting. If none
// comes, the card says why, with Try again ----------
const AD_WAIT_MS = 20000, ADW = { t0: 0, tries: 0, rt: 0, popT: 0 };
const AD_WHY = { offline: ['You’re offline', 'Connect to the internet to watch the ad.'], slow: ['The ad didn’t load', 'It took too long. Try again in a moment.'], noads: ['No ad right now', 'There’s no ad to show at the moment. Try again in a minute.'] };
function adWarmPage() { if (ADS.mode === 'app' && strokesDue() && !adFree()) adHello(true); }
function adWaitShow() {
  const w = $('adWait'); clearTimeout(ADW.popT); ADW.popT = 0; if (!w.hidden && !w.classList.contains('fail')) return;
  w.classList.remove('fail'); $('adWaitH').textContent = 'Getting your ad ready'; $('adWaitP').textContent = 'It starts as soon as it’s loaded.'; $('adWaitGo').hidden = true; $('adWaitNo').textContent = 'Cancel';
  const was = w.hidden; w.hidden = false; if (was) setTimeout(() => { if (!w.hidden) $('adWaitNo').focus({ preventScroll: true }); }, 40);
}
function adWaitHide() { clearTimeout(ADW.popT); clearTimeout(ADW.rt); ADW.popT = ADW.rt = 0; $('adWait').hidden = true; }
function adWaitFail(why) {
  clearTimeout(ADW.popT); clearTimeout(ADW.rt); ADW.popT = ADW.rt = 0; const w = $('adWait'), t = AD_WHY[why] || AD_WHY.noads;
  w.classList.add('fail'); $('adWaitH').textContent = t[0]; $('adWaitP').textContent = t[1]; $('adWaitGo').hidden = false; $('adWaitNo').textContent = 'Close';
  w.hidden = false; setTimeout(() => { if (!w.hidden) $('adWaitGo').focus({ preventScroll: true }); }, 40);
}
function adRetry() { ADW.rt = 0; if (!ADS.id || ADS.open) return; ADW.tries++; nativeSay('ads', { show: 'craft', kid: adKid() }); }
function adWaitCancel() {
  const fail = $('adWait').classList.contains('fail'); adWaitHide(); if (fail) return;
  if (ADS.id && !ADS.open) { nativeSay('ads', { cancel: true }); adDone(); }
}
$('adWaitI').innerHTML = AD_PLAY;
$('adWaitNo').addEventListener('click', () => { AU.init(); AU.ui(); adWaitCancel(); });
$('adWaitGo').addEventListener('click', () => { AU.init(); if (!strokesOf().craft) { AU.ui(); return adWaitHide(); } craftSkipAsk(); });
'''

def apply(s):
    s = rep(s, "the stroke is done.</p></div></div>\n", "the stroke is done.</p></div></div>\n" + HTML)
    s = rep(s, "/* (v331) the portraits, and the soft round placeholder", CSS.lstrip('\n') + "/* (v331) the portraits, and the soft round placeholder")
    # ---- readied as the page opens, and after one's been watched
    s = rep(s, "closeSide(true); renderStrokes(); adWarm();", "closeSide(true); renderStrokes(); adWarmPage(); // (v335: whenever an ad could be wanted here)")
    s = rep(s, "  clearTimeout(ADS.ct); ADS.ct = setTimeout(() => { ADS.ct = 0; if (ADS.earned) return adPayoff(); adDone(); stToast('Watch to the end to finish it'); }, 420);\n}",
               "  clearTimeout(ADS.ct); ADS.ct = setTimeout(() => { ADS.ct = 0; if (ADS.earned) adPayoff(); else { adDone(); stToast('Watch to the end to finish it'); } setTimeout(() => { if (strokesOpen()) adWarmPage(); }, 1500); }, 420); // (v335: and the next one readied)\n}")
    # ---- Skip: the card waits for an ad that isn't ready yet
    s = rep(s, "  if (ADS.id) return; // (one at a time)\n"
               "  ADS.id = d.craft.id; ADS.earned = false; ADS.open = false; AU.ui(); buzz(6); sgSkipPaint();\n"
               "  clearTimeout(ADS.t); ADS.t = setTimeout(() => adFail('slow'), 45000); // (the app answers well before this: it's in case it never does)\n"
               "  if (ADS.mode === 'app') nativeSay('ads', { show: 'craft', kid: adKid() }); else adStandIn();\n",
               "  if (ADS.id) { if (ADS.mode === 'app' && !ADS.open) adWaitShow(); return; } // (one at a time: tapped again, the wait shows)\n"
               "  ADS.id = d.craft.id; ADS.earned = false; ADS.open = false; AU.ui(); buzz(6); sgSkipPaint();\n"
               "  clearTimeout(ADS.t); ADS.t = setTimeout(() => adFail('slow', true), AD_WAIT_MS + 15000); // (the app answers well before this: it's in case it never does)\n"
               "  if (ADS.mode !== 'app') return adStandIn();\n"
               "  ADW.t0 = performance.now(); ADW.tries = 1; clearTimeout(ADW.rt); clearTimeout(ADW.popT); // (v335: an ad that's ready opens before the card would come up)\n"
               "  if (!$('adWait').hidden) adWaitShow(); else ADW.popT = setTimeout(adWaitShow, 450);\n"
               "  nativeSay('ads', { show: 'craft', kid: adKid() });\n")
    s = rep(s, "if (m.e === 'open') { clearTimeout(ADS.t);", "if (m.e === 'open') { clearTimeout(ADS.t); adWaitHide();")
    s = rep(s, "function adFail(why) {\n"
               "  if (!ADS.id && !ADS.open) return;\n"
               "  const was = ADS.open; adDone(); if (was) { if (ADS.mode === 'app') AU.wake(true, true); else applyMix(); }\n"
               "  AU.nope && AU.nope(); stToast(why === 'offline' ? 'You’re offline: connect to watch the ad' : 'No ad to show right now. Try again soon');\n"
               "}\n",
               "function adFail(why, last) {\n"
               "  if (!ADS.id && !ADS.open) return;\n"
               "  // (v335) still waiting and online: ask the app again, at once if it was only slow (a late one is kept for this), in a moment if not\n"
               "  if (!ADS.open && !last && ADS.mode === 'app' && why !== 'offline' && ADW.tries < 4 && performance.now() - ADW.t0 < AD_WAIT_MS) { adWaitShow(); clearTimeout(ADW.rt); ADW.rt = setTimeout(adRetry, why === 'slow' ? 60 : 2500); return; }\n"
               "  const was = ADS.open; adDone(); if (was) { if (ADS.mode === 'app') AU.wake(true, true); else applyMix(); }\n"
               "  AU.nope && AU.nope(); if (ADS.mode === 'app') adWaitFail(why); else stToast(why === 'offline' ? 'You’re offline: connect to watch the ad' : 'No ad to show right now. Try again soon');\n"
               "}\n" + JS.lstrip('\n'))
    # ---- keys: Escape is Cancel (or Close) while the card is up
    s = rep(s, "  if (lookOpen) { if (e.key === 'Escape') { e.preventDefault(); closeLook(); } return; }\n",
               "  if (!$('adWait').hidden) { if (e.key === 'Escape') { e.preventDefault(); AU.ui(); adWaitCancel(); } return; } // (v335)\n"
               "  if (lookOpen) { if (e.key === 'Escape') { e.preventDefault(); closeLook(); } return; }\n")
    return s
