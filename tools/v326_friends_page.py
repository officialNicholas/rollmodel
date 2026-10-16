"""v326: Friends as a full-screen page.

The Friends pop-up (a notebook card over the blurred lobby) becomes a page of its own, in the look of the Strokes page and the locker:
- the Strokes page's lime wall, its purple Back button (top left) and its taped black banner ("Play together / Friends"); a black badge
  at the top right counts the friends online, when there are any;
- on the wall: your own hang tag (like a stroke card: hook, mottled card with your axolotl's face in your paint, lime strip with your
  name and rank), your friend code on the yellow strip with Copy and Share, and the box to add a friend;
- the locker's graph-paper sheet below (taped at the top, "My friends" in the locker's heading, a count, who's online) with duel
  invites, requests, your friends as paper tiles, the ones you're waiting on, the blocked, and the small print; it scrolls on its own;
- the other states (signing in, picking a username, getting your code, can't connect, not switched on) sit on the sheet, with your
  tag on the wall.
Sideways: the wall on the left (banner, tag, code, add), the sheet down the right. All the friends code (requests, duels, blocking,
the polling and what it keeps while you type) is as it was."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

BACK = '<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M12.6 7.4 6.2 13.6l6.4 6.2" fill="none" stroke="currentColor" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/><path d="M7.4 13.6h11.2a6.4 6.4 0 0 1 0 12.8h-4.4" fill="none" stroke="currentColor" stroke-width="3.6" stroke-linecap="round"/></svg>'

HTML_OLD = """  <div class="modal ttm" id="friendsModal" hidden><div class="ttcard frcard" role="dialog" aria-modal="true" aria-labelledby="friendsTitle">
    <button class="ttx" id="frX" type="button" aria-label="Close"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.5 6.5l11 11M17.5 6.5l-11 11" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"/></svg></button>
    <div class="tthd"><small>Play together</small><h3 id="friendsTitle">Friends</h3></div>
    <div class="frbody" id="frBody"></div>
  </div></div>
"""
HTML_NEW = """  <div class="modal ttm frpage" id="friendsModal" hidden><div class="frpg" role="dialog" aria-modal="true" aria-labelledby="friendsTitle">
    <div class="frwall" aria-hidden="true"></div>
    <div class="frtop"><button class="frback" id="frX" type="button" aria-label="Back to the lobby">""" + BACK + """<span>Back</span></button>
      <div class="frban"><small>Play together</small><h3 id="friendsTitle">Friends</h3><i class="frflag" aria-hidden="true"></i></div>
      <span class="frlive" id="frLive" hidden></span></div>
    <div class="frbody" id="frBody"></div>
  </div></div>
"""

CSS = r"""
/* ---- (v326) Friends as a page: the Strokes page's lime wall, Back and taped banner; your tag, your code and the add box on the wall;
   the locker's graph-paper sheet for invites, requests and your friends. Sideways: the wall on the left, the sheet on the right */
#friendsModal.frpage{display:block;padding:0;background:none;-webkit-backdrop-filter:none;backdrop-filter:none;animation:frpgin .2s ease-out}
@keyframes frpgin{from{opacity:0}}
#friendsModal .frpg{--lime:#CBE45A;--sel:#FFE23C;--ink0:#111014;--gx:max(14px,env(safe-area-inset-left));--gr:max(14px,env(safe-area-inset-right));--gt:max(12px,env(safe-area-inset-top));--gb:env(safe-area-inset-bottom,0px);--bk:56px;
  position:absolute;inset:0;display:flex;flex-direction:column;box-sizing:border-box;padding:var(--gt) var(--gr) 0 var(--gx);overflow:hidden;color:var(--black);text-align:left}
#friendsModal .frwall{position:absolute;inset:0;z-index:0;background:var(--lime) url(art/sg_bg.webp) 0 0/560px 560px repeat}
#friendsModal .frtop,#friendsModal .frhero,#friendsModal .frsheet{position:relative;z-index:1}
#friendsModal .frtop{flex:none;display:grid;grid-template-columns:var(--bk) minmax(0,1fr) var(--bk);align-items:center;gap:10px;min-height:var(--bk)}
#friendsModal .frback{appearance:none;display:flex;flex-direction:column;align-items:center;justify-content:center;width:var(--bk);height:var(--bk);margin:0;padding:2px 0 0;border:0;border-radius:50%;background:radial-gradient(circle at 38% 28%,#A876FF,#7B3BEA 58%,#5F22C8);color:#fff;box-shadow:0 0 0 3px var(--ink0),0 5px 0 var(--ink0);cursor:pointer;-webkit-tap-highlight-color:transparent}
#friendsModal .frback svg{width:46%;height:46%}
#friendsModal .frback span{margin-top:-1px;font:400 11px/1 var(--font-display);letter-spacing:.01em}
#friendsModal .frback:active{transform:translateY(3px);box-shadow:0 0 0 3px var(--ink0),0 2px 0 var(--ink0)}
#friendsModal .frback:focus-visible,#friendsModal .frcbtn .frb:focus-visible,#friendsModal .fradd .frb:focus-visible{outline:3px solid #fff;outline-offset:3px}
#friendsModal .frban{position:relative;justify-self:center;display:flex;flex-direction:column;align-items:flex-start;gap:3px;max-width:calc(100% - 26px);box-sizing:border-box;padding:7px 28px 8px 18px;background:var(--ink0);color:#fff;transform:skewX(-11deg);box-shadow:5px 5px 0 rgba(23,19,32,.22)}
#friendsModal .frban>small,#friendsModal .frban>h3{transform:skewX(11deg)}
#friendsModal .frban small{font:800 10px/1 var(--font-ui);letter-spacing:.16em;text-transform:uppercase;color:#5BE07E;white-space:nowrap}
#friendsModal .frban h3{margin:0;font:400 24px/1.04 var(--font-display);letter-spacing:.01em;white-space:nowrap}
#friendsModal .frban::before{content:"";position:absolute;left:-18px;top:-10px;width:58px;height:20px;background:url(art/m_tape3.webp) center/100% 100% no-repeat;transform:skewX(11deg) rotate(-24deg);filter:drop-shadow(0 1px 0 rgba(23,19,32,.18))}
#friendsModal .frflag{position:absolute;right:-19px;top:50%;width:22px;height:30px;margin-top:-15px;transform:skewX(11deg)}
#friendsModal .frflag::before{content:"";position:absolute;left:0;top:0;width:3px;height:30px;border-radius:2px;background:var(--ink0)}
#friendsModal .frflag::after{content:"";position:absolute;left:3px;top:1px;width:18px;height:14px;background:#5BE07E;clip-path:polygon(0 0,100% 50%,0 100%);animation:sgflag 2.4s ease-in-out infinite;transform-origin:0 50%}
#friendsModal .frlive{justify-self:end;display:grid;grid-template-columns:auto auto;align-items:center;justify-content:center;column-gap:5px;row-gap:3px;min-width:50px;height:50px;padding:0 7px;box-sizing:border-box;border-radius:12px;background:var(--ink0);color:#fff;font:400 16px/1 var(--font-display);box-shadow:0 3px 0 rgba(0,0,0,.3)}
#friendsModal .frlive[hidden]{display:none}
#friendsModal .frlive i{width:8px;height:8px;border-radius:50%;background:#3DD668;box-shadow:0 0 0 3px rgba(61,214,104,.28)}
#friendsModal .frlive small{grid-column:1/-1;font:800 8px/1 var(--font-ui);letter-spacing:.12em;text-transform:uppercase;color:#9FE6B0;text-align:center}
/* the wall: your tag beside your code, the add box under them */
#friendsModal .frbody{position:relative;z-index:1;display:flex;flex-direction:column;flex:1 1 auto;min-height:0;margin:0;padding:0;gap:0;overflow:visible}
#friendsModal .frhero{flex:none;display:grid;grid-template-columns:minmax(0,1fr);gap:14px;padding:16px 2px 22px}
#friendsModal .frhtop{display:flex;align-items:center;justify-content:center;gap:18px;min-width:0}
#friendsModal .frtag{position:relative;flex:none;display:flex;flex-direction:column;width:112px;padding-top:10px;transform:rotate(-2.5deg);filter:drop-shadow(3px 5px 0 rgba(23,19,32,.18))}
#friendsModal .frhook{position:absolute;left:50%;top:0;z-index:2;width:14px;height:16px;margin-left:-7px;border-radius:50% 50% 45% 45%;box-shadow:inset 0 0 0 2.6px #A9A9B2,0 1px 0 rgba(0,0,0,.4)}
#friendsModal .frtagc{position:relative;display:grid;place-items:center;aspect-ratio:1/.74;border-radius:11px 11px 3px 3px;background:#F7F1E3 url(art/sg_card.webp) 30% 20%/260% auto;box-shadow:inset 0 0 0 1.5px rgba(23,19,32,.14)}
#friendsModal .frtagc::before{content:"";position:absolute;left:50%;top:5px;width:8px;height:8px;margin-left:-4px;border-radius:50%;background:#6A6A72;box-shadow:inset 0 1.5px 0 rgba(0,0,0,.35)}
#friendsModal .frtagc .frface{width:58px;height:58px;margin-top:8px}
#friendsModal .frtagn{display:grid;justify-items:center;gap:3px;padding:5px 6px 6px;border-radius:3px 3px 11px 11px;background:#A9DC2C;box-shadow:inset 0 1.5px 0 rgba(255,255,255,.4),inset 0 -2px 0 rgba(0,0,0,.12)}
#friendsModal .frtagn b{max-width:100%;overflow:hidden;font:400 13px/1.1 var(--font-display);color:var(--ink0);white-space:nowrap;text-overflow:ellipsis}
#friendsModal .frtagn small{font:800 9px/1 var(--font-ui);letter-spacing:.12em;text-transform:uppercase;color:rgba(17,16,20,.62)}
#friendsModal .frme{display:grid;justify-items:start;gap:8px;min-width:0}
#friendsModal .frme small,#friendsModal .fradd label{color:rgba(17,16,20,.72)}
#friendsModal .frcode{margin:0;max-width:100%}
#friendsModal .frcode b{flex:none;padding:9px 12px 7px;font-size:23px;box-shadow:0 10px 10px -8px rgba(0,0,0,.45),3px 4px 0 rgba(23,19,32,.16)}
#friendsModal .frcbtn{display:flex;gap:12px;margin-top:4px;padding-left:4px}
#friendsModal .frcbtn .frb,#friendsModal .fradd .frb{min-height:0;height:36px;padding:0 15px;border-radius:9px;transform:skewX(-12deg);font:400 14px/1 var(--font-display);letter-spacing:.02em;text-transform:none;box-shadow:0 0 0 2.5px var(--ink0),0 4px 0 var(--ink0)}
#friendsModal .frcbtn .frb>span,#friendsModal .fradd .frb>span{display:inline-block;transform:skewX(12deg)}
#friendsModal .frcbtn .frb:active,#friendsModal .fradd .frb:active{transform:skewX(-12deg) translateY(3px);box-shadow:0 0 0 2.5px var(--ink0),0 1px 0 var(--ink0)}
#friendsModal .frcbtn .frcp{background:var(--sel);color:var(--ink0)}
#friendsModal .frcbtn .frb:not(.frcp){background:linear-gradient(#4A4A52,#34343B);color:#fff}
#friendsModal .frme .frnote{margin:0;padding-left:4px}
#friendsModal .fradd{display:grid;grid-template-columns:minmax(0,1fr);gap:8px;padding:0 4px}
#friendsModal .fradd>div{margin-top:0;gap:12px;align-items:center}
#friendsModal .fradd input{height:44px;border:2.5px solid var(--ink0);border-radius:10px;background:#FFFDF6;box-shadow:0 3px 0 rgba(17,16,20,.22)}
#friendsModal .fradd .frb.go{height:42px;padding:0 20px;background:#5BE07E;color:var(--ink0);font-size:16px}
#friendsModal .fradd .frnote{margin:0;min-height:0}
#friendsModal .fradd .frnote:empty{display:none}
/* the sheet: the locker's graph paper, taped at the top */
#friendsModal .frsheet{flex:1 1 auto;min-height:0;display:flex;flex-direction:column;margin:0 calc(-1 * var(--gr)) 0 calc(-1 * var(--gx));padding:22px max(16px,var(--gr)) 0 max(16px,var(--gx));border-radius:26px 26px 0 0;background:#F6F1E8 url(art/m_paperbg.webp) center/420px;box-shadow:0 -10px 30px rgba(23,19,32,.22)}
#friendsModal .frsheet::before{content:"";position:absolute;left:50%;top:-15px;width:120px;height:32px;margin-left:-60px;background:url(art/m_tape3.webp) center/100% 100% no-repeat;transform:rotate(2deg);filter:drop-shadow(0 1px 0 rgba(23,19,32,.15))}
#friendsModal .frshd{flex:none;display:flex;align-items:center;gap:10px;min-width:0;padding:0 2px 12px}
#friendsModal .frsht{margin:0;font:900 26px/.95 var(--font-head);text-transform:uppercase;letter-spacing:0;color:var(--black);white-space:nowrap;transform:skewX(-6deg);text-shadow:.04em .04em 0 #FFF8EA,.08em .08em 0 var(--black)}
#friendsModal .frcnt{flex:none;font-style:normal;padding:4px 9px 3px;border-radius:999px;background:var(--ink0);color:#fff;font:400 14px/1 var(--font-display)}
#friendsModal .fron{margin-left:auto;display:flex;align-items:center;gap:7px;font:800 11.5px/1 var(--font-ui);font-style:normal;letter-spacing:.08em;text-transform:uppercase;color:#2C7A3F;white-space:nowrap}
#friendsModal .fron::before{content:"";width:8px;height:8px;border-radius:50%;background:#2E9E48;box-shadow:0 0 0 3px rgba(46,158,72,.22)}
#friendsModal .frscroll{flex:1 1 auto;min-height:0;overflow-x:hidden;overflow-y:auto;overscroll-behavior:contain;display:grid;grid-template-columns:minmax(0,1fr);align-content:start;gap:18px;padding:2px 2px calc(var(--gb) + 24px);-webkit-overflow-scrolling:touch}
#friendsModal .frscroll>*{min-width:0}
#friendsModal .frscroll h4{color:#5E566E}
#friendsModal .frlist{gap:10px;margin-top:8px}
#friendsModal .frrow{min-height:58px;padding:7px 10px;border:0;border-radius:12px;background:#FFFDF7;box-shadow:inset 0 0 0 1.5px rgba(23,19,32,.1),3px 4px 0 rgba(23,19,32,.13)}
#friendsModal .frrow.sm{min-height:48px}
#friendsModal .frmenu{padding:4px 0 4px 50px}
#friendsModal .frmsg{min-height:200px}
#friendsModal .frnone{min-height:150px;padding:8px 0 4px}
#friendsModal .frfine{padding:0 2px}
/* sideways: the wall down the left, the sheet down the right */
@media (min-aspect-ratio:1/1){
  #friendsModal .frpg{display:grid;grid-template-columns:minmax(0,46%) minmax(0,1fr);grid-template-rows:auto minmax(0,1fr);column-gap:24px}
  #friendsModal .frbody{display:contents}
  #friendsModal .frtop{grid-column:1;grid-row:1}
  #friendsModal .frhero{grid-column:1;grid-row:2;align-self:start;padding-top:14px;overflow-y:auto;max-height:100%;box-sizing:border-box}
  #friendsModal .frsheet{grid-column:2;grid-row:1 / 3;margin:8px calc(-1 * var(--gr)) 0 0;padding-left:20px;border-radius:26px 0 0 0}
}
/* a narrow phone: a smaller tag and code, so they still sit side by side */
@media (max-width:359px){#friendsModal .frhtop{gap:12px}#friendsModal .frtag{width:86px}#friendsModal .frtagc .frface{width:44px;height:44px;margin-top:6px}#friendsModal .frtagn b{font-size:11.5px}#friendsModal .frcode b{padding:8px 9px 6px;font-size:18px}#friendsModal .frcbtn{gap:9px}#friendsModal .frcbtn .frb{padding:0 12px}#friendsModal .frsht{font-size:22px}#friendsModal .frban h3{font-size:21px}}
@media (prefers-reduced-motion:reduce){#friendsModal.frpage{animation:none}#friendsModal .frflag::after{animation:none}}
"""

def apply(s):
    s = rep(s, HTML_OLD, HTML_NEW)
    i = s.rfind('</style>'); s = s[:i] + CSS + s[i:]
    # ---- frRender: your tag, code and the add box go on the wall; the rest on the sheet
    s = rep(s, "  const el = $('frBody'); if (!el) return; let h = '';", "  const el = $('frBody'); if (!el) return; let h = '', heroCode = '', heroAdd = '', above = false; // (v326: the wall's part, and the sheet's)")
    s = rep(s, """    h += '<section class="frme"><small>Your friend code</small><div class="frcode"><b>' + frCode(FR.me.code) + '</b><button class="frb" data-act="copy" type="button">Copy</button>' + (NATIVE_SHARE ? '<button class="frb" data-act="share" type="button">Share</button>' : '') + '</div></section>';""",
        """    heroCode = '<section class="frme"><small>Your friend code</small><div class="frcode"><b>' + frCode(FR.me.code) + '</b></div><div class="frcbtn"><button class="frb frcp" data-act="copy" type="button"><span>Copy</span></button>' + (NATIVE_SHARE ? '<button class="frb" data-act="share" type="button"><span>Share</span></button>' : '') + '</div>' + (FR.noteAt === 'code' && FR.note ? '<p class="frnote' + (FR.noteOk ? '' : ' bad') + '" aria-live="polite">' + frEsc(FR.note) + '</p>' : '') + '</section>';""")
    s = rep(s, """    h += '<form class="fradd" id="frAdd" autocomplete="off" novalidate><label for="frIn">Add a friend</label><div><input id="frIn" type="text" inputmode="text" autocapitalize="characters" autocorrect="off" spellcheck="false" maxlength="9" placeholder="Their friend code" value="' + frEsc(FR.typed) + '"><button class="frb go" type="submit">Add</button></div><p class="frnote' + (FR.noteOk ? '' : ' bad') + '" aria-live="polite">' + frEsc(FR.note) + '</p></form>';""",
        """    heroAdd = '<form class="fradd" id="frAdd" autocomplete="off" novalidate><label for="frIn">Add a friend</label><div><input id="frIn" type="text" inputmode="text" autocapitalize="characters" autocorrect="off" spellcheck="false" maxlength="9" placeholder="Their friend code" value="' + frEsc(FR.typed) + '"><button class="frb go" type="submit"><span>Add</span></button></div><p class="frnote' + (FR.noteOk ? '' : ' bad') + '" aria-live="polite">' + frEsc(FR.noteAt === 'code' ? '' : FR.note) + '</p></form>';""")
    s = rep(s, "    if (NET_URL) h += onInvList(); // (v306: duel invites)", "    if (NET_URL) h += onInvList(); // (v306: duel invites)\n    above = b.incoming.length > 0 || !!(NET_URL && ON.invites && ON.invites.length);")
    s = rep(s, """    h += '<section><h4>Friends <i>' + b.friends.length + '</i>' + (on ? '<em>· ' + on + ' online</em>' : '') + '</h4>' + (b.friends.length ? '<ul class="frlist">' + b.friends.map(frRow).join('') + '</ul>' : '<p class="frempty">No friends yet. Send them your code, or add theirs above.</p>') + '</section>';""",
        """    h += '<section aria-label="Your friends">' + (above && b.friends.length ? '<h4>Your friends</h4>' : '') + (b.friends.length ? '<ul class="frlist">' + b.friends.map(frRow).join('') + '</ul>' : '<div class="frmsg frnone">' + FR_FACES + '<p>No friends yet. Send them your code, or add theirs above.</p></div>') + '</section>';""")
    s = rep(s, "  if (fromPoll && h === FR.sig) return; FR.sig = h;\n  const a = document.activeElement, typing = a && a.id === 'frIn',",
        """  // (v326) the page: your tag (with your code and the add box, once you have them) on the wall, the rest on the sheet under its heading
  { const bx = FR.me && FR.box, n = bx ? bx.friends.length : -1, k = n > 0 ? bx.friends.filter(f => f.online).length : 0;
    const tag = '<div class="frtag"><i class="frhook" aria-hidden="true"></i><span class="frtagc">' + frFace(frLook()) + '</span><span class="frtagn"><b>' + frEsc(playerName()) + '</b><small>Rank ' + frRank() + '</small></span></div>';
    h = '<div class="frhero"><div class="frhtop">' + tag + heroCode + '</div>' + heroAdd + '</div><section class="frsheet" aria-labelledby="frShH"><div class="frshd"><h2 class="frsht" id="frShH">My friends</h2>' + (n >= 0 ? '<i class="frcnt">' + n + '</i>' : '') + (k ? '<em class="fron">' + k + ' online</em>' : '') + '</div><div class="frscroll">' + h + '</div></section>';
    const lv = $('frLive'); if (lv) { lv.hidden = !k; if (k) lv.innerHTML = '<i aria-hidden="true"></i><b>' + k + '</b><small>online</small>'; lv.setAttribute('aria-label', k + ' online'); } }
  if (fromPoll && h === FR.sig) return; FR.sig = h;
  const a = document.activeElement, typing = a && a.id === 'frIn',""")
    s = rep(s, "p1 = typing ? a.selectionEnd : 0, top = el.scrollTop;\n  el.innerHTML = h; el.scrollTop = top;\n  if (typing) { const i = $('frIn');",
        "p1 = typing ? a.selectionEnd : 0, top = (el.querySelector('.frscroll') || el).scrollTop;\n  el.innerHTML = h; (el.querySelector('.frscroll') || el).scrollTop = top;\n  if (typing) { const i = $('frIn');")
    # a note says where it came from: Copy's under your code, Add's under the box
    s = rep(s, "FR.note = ok ? 'Your code is copied. Send it to a friend!'", "FR.noteAt = 'code'; FR.note = ok ? 'Your code is copied. Send it to a friend!'")
    s = rep(s, "e.preventDefault(); const i = $('frIn'), code = ", "e.preventDefault(); FR.noteAt = 'add'; const i = $('frIn'), code = ")
    return s
