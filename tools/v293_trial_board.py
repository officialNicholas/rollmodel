"""v293: Time trial becomes a weekly leaderboard, one per canvas.

- Every canvas keeps its own board for the week (Monday 00:00 UTC to the next, the same moment for everyone once boards go online).
  For now the board is you against yourself: your best runs this week on that canvas, ranked, the top three in gold, silver and bronze.
  When the week turns the boards clear (last week's best is kept to show beside the new one).
- The board opens from the canvas picker in Time trial (a strip under the pictures: your best and place this week on the canvas in the
  middle, and when the week turns). The board itself is a taped sheet of notebook paper: the canvas on a plaque you can flip through,
  tabs for You, Friends and Global, and the countdown to the new week.
- Friends and Global are there, locked until online play, each with its prizes for the week's top three: Global 350, 200 and 100 dabs,
  Friends 100, 60 and 30 (a friends board needs three friends or more to count).
- A Time trial is now against the week: the HUD bar fills toward this week's best on this canvas, and the results say where the run
  placed (a "Best this week" tag, its place, and the week's top three under the stats, this run marked).
- The Time trial card on the events page says "Weekly leaderboard"."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

LOCK = '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="10.5" width="14" height="10" rx="2.4" fill="currentColor"/><path d="M8.2 10.5V8a3.8 3.8 0 0 1 7.6 0v2.5" fill="none" stroke="currentColor" stroke-width="2.4"/></svg>'
CHEV = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 5.5 15.5 12 9 18.5" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>'
CHEVL = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5.5 8.5 12 15 18.5" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>'
CLOCK = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="8.6" fill="none" stroke="currentColor" stroke-width="2.4"/><path d="M12 7.4V12l3.2 2" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/></svg>'
CUP = ('<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M9 5h14v6.5a7 7 0 0 1-14 0z" fill="#FFD84A" stroke="#171320" stroke-width="2.4" stroke-linejoin="round"/>'
       '<path d="M9 8H5.5a4 4 0 0 0 4.6 5M23 8h3.5a4 4 0 0 1-4.6 5" fill="none" stroke="#171320" stroke-width="2.4" stroke-linecap="round"/>'
       '<path d="M16 18.5v4.5M11 27.5h10l-1.5-4.5h-7z" fill="#E3A12C" stroke="#171320" stroke-width="2.4" stroke-linejoin="round"/><path d="M12.4 8.2v3" stroke="#fff" stroke-width="2" stroke-linecap="round" opacity=".8"/></svg>')
DAB = ('<svg class="ttdab" viewBox="0 0 40 40" aria-hidden="true"><circle cx="20" cy="20" r="18.6" fill="#F2C14E" stroke="#171320" stroke-width="2.6"/><circle cx="20" cy="20" r="14.4" fill="#C98E22"/><circle cx="20" cy="20.6" r="12.8" fill="#EDB43F"/>'
       '<path class="dabk" transform="scale(2)" d="M10 5.2c.9 0 1.3 1.1 2 1.5 1 .5 2.2-.3 2.6.7.4 1-.9 1.6-.9 2.6s1.2 1.6.7 2.5c-.5.9-1.6.2-2.5.6-.8.4-1 1.7-1.9 1.7s-1.1-1.3-2-1.7c-.9-.4-2 .3-2.5-.6s.7-1.5.7-2.5-1.3-1.6-.9-2.6c.4-1 1.6-.2 2.6-.7.7-.4 1.1-1.5 2.1-1.5z" stroke="#171320" stroke-width=".85"/>'
       '<path d="M8.6 14.2a13 13 0 0 1 7.6-6.6" fill="none" stroke="#FFF1BF" stroke-width="2.2" stroke-linecap="round" opacity=".85"/></svg>')

HTML = ('  <div class="modal ttm" id="ttModal" hidden><div class="ttcard" role="dialog" aria-modal="true" aria-labelledby="ttTitle">\n'
        '    <button class="ttx" id="ttX" type="button" aria-label="Close"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.5 6.5l11 11M17.5 6.5l-11 11" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"/></svg></button>\n'
        '    <div class="tthd"><small id="ttWeek">This week</small><h3 id="ttTitle">Leaderboard</h3></div>\n'
        '    <div class="ttstage"><button class="ttarr" id="ttPrev" type="button" aria-label="Previous canvas">' + CHEVL + '</button><b class="ttplq" id="ttStage" aria-live="polite">Blank Canvas</b><button class="ttarr" id="ttNext" type="button" aria-label="Next canvas">' + CHEV + '</button></div>\n'
        '    <div class="tttabs" role="tablist" aria-label="Whose times"><button type="button" role="tab" data-tt="you" aria-selected="true">You</button><button type="button" role="tab" data-tt="friends" aria-selected="false">Friends' + LOCK + '</button><button type="button" role="tab" data-tt="global" aria-selected="false">Global' + LOCK + '</button></div>\n'
        '    <div class="ttbody" id="ttBody" role="tabpanel"></div>\n'
        '    <p class="ttfoot">' + CLOCK + '<span>New week in <b id="ttLeft">7d</b></span></p>\n'
        '  </div></div>\n')

STRIP = ('<button class="ttstrip" id="ttStrip" type="button" hidden><span class="ttsi" aria-hidden="true">' + CUP + '</span><span class="ttst"><b id="ttStripB">This week</b><small id="ttStripS"></small><small class="ttsw">' + CLOCK + '<span id="ttStripW"></span></small></span>'
         '<span class="ttsgo">Leaderboard' + CHEV + '</span></button>')

JS = r"""
// ---------- (v293) Time trial: a leaderboard a week, one for each canvas. For now it's you against yourself; Friends and Global come with
// online play, each paying its top three every week ----------
const TT_WK = 7 * 864e5, TT_KEEP = 30, TT_SHOW = 10, TT_PRIZE = { global: [350, 200, 100], friends: [100, 60, 30] }, TT_FRIENDS_MIN = 3;
// the week: from Monday 00:00 UTC (one moment for everyone, so the online boards turn together)
const ttWeek = (t = Date.now()) => { const d = new Date(t); return Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate()) - ((d.getUTCDay() + 6) % 7) * 864e5; };
function ttLeft() { const ms = Math.max(0, ttWeek() + TT_WK - Date.now()), m = Math.floor(ms / 6e4), h = Math.floor(m / 60), d = Math.floor(h / 24); return d ? d + 'd ' + (h % 24) + 'h' : h ? h + 'h ' + (m % 60) + 'm' : Math.max(1, m) + 'm'; }
function ttOf() {
  const w = ttWeek(); let o = store.tt; if (!o || typeof o !== 'object' || !o.b) o = store.tt = { wk: w, b: {}, n: {} };
  if (o.wk !== w) { const best = {}; for (const k in o.b) if (o.b[k] && o.b[k][0]) best[k] = o.b[k][0].p; o.prev = o.wk === w - TT_WK ? { wk: o.wk, best } : null; o.wk = w; o.b = {}; o.n = {}; }
  return o;
}
const ttRuns = sid => ttOf().b[sid] || [], ttBest = sid => { const L = ttRuns(sid); return L.length ? L[0].p : 0; };
// a finished run on the board: where it placed among this week's runs on the canvas
function ttAdd(sid, p) {
  const o = ttOf(), L = o.b[sid] || (o.b[sid] = []), run = { p, t: Date.now() }; L.push(run); L.sort((a, b) => b.p - a.p || a.t - b.t);
  const rank = L.indexOf(run) + 1; if (L.length > TT_KEEP) L.length = TT_KEEP; o.n[sid] = (o.n[sid] || 0) + 1; return { rank, runs: o.n[sid], t: run.t };
}
const TT_STAGES = VOTE_STAGES.filter(s => STAGE_THEMES[s] && THEME_BY[STAGE_THEMES[s][0]]);
const ttName = sid => THEME_BY[sid] ? THEME_BY[sid].label : sid;
const ttSid = () => STAGE_THEMES[stageSel] ? STAGE_THEMES[stageSel][0] : TT_STAGES.includes(TH.id) ? TH.id : TT_STAGES[0];
const ttWhen = t => { const d = new Date(t), now = new Date(), day = d.toDateString() === now.toDateString() ? 'Today' : d.toLocaleDateString([], { weekday: 'long' }); return day + ', ' + d.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' }); };
const ttOrd = n => n + (n % 100 >= 11 && n % 100 <= 13 ? 'th' : ['th', 'st', 'nd', 'rd'][n % 10] || 'th');
// the strip on the canvas picker: this week on the canvas in the middle
function ttStrip() {
  const el = $('ttStrip'); if (!el) return; const solo = mode === 'solo'; el.hidden = !solo; $('soloNote').classList.toggle('ttoff', solo); $('wDiffHd').hidden = solo; if (!solo) return;
  const sid = ttSid(), L = ttRuns(sid), n = ttOf().n[sid] || 0;
  $('ttStripB').textContent = L.length ? 'This week: ' + L[0].p + '%' : 'No run here this week';
  $('ttStripS').textContent = L.length ? 'Best of ' + n + (n === 1 ? ' run' : ' runs') + ' on ' + ttName(sid) : 'Set one on ' + ttName(sid); $('ttStripW').textContent = 'New week in ' + ttLeft();
  el.setAttribute('aria-label', 'Leaderboard for ' + ttName(sid) + '. ' + $('ttStripB').textContent + '. New week in ' + ttLeft());
}
let ttSel = null, ttTab = 'you', ttHi = 0, ttTick = 0;
function ttRender() {
  const sid = ttSel, L = ttRuns(sid).slice(0, TT_SHOW), o = ttOf();
  $('ttStage').textContent = ttName(sid); $('ttLeft').textContent = ttLeft();
  $('ttWeek').textContent = 'Week of ' + new Date(o.wk).toLocaleDateString([], { month: 'short', day: 'numeric', timeZone: 'UTC' });
  for (const b of document.querySelectorAll('.tttabs [data-tt]')) { const on = b.dataset.tt === ttTab; b.setAttribute('aria-selected', String(on)); b.classList.toggle('on', on); }
  $('ttModal').dataset.tab = ttTab; let h = '';
  if (ttTab === 'you') {
    if (!L.length) h = '<p class="ttnone"><b>No runs on this canvas yet this week.</b>Play a Time trial here to put one on the board.</p>';
    else { h = '<ol class="ttlist">'; L.forEach((r, i) => { h += '<li class="ttrow' + (i < 3 ? ' r' + (i + 1) : '') + (r.t === ttHi ? ' me' : '') + '"><b class="ttrk" aria-label="' + ttOrd(i + 1) + '">' + (i + 1) + '</b><span class="ttwho">' + escAttr(ttWhen(r.t)) + (r.t === ttHi ? '<em>Latest</em>' : '') + '</span><b class="ttpc">' + r.p + '<small>%</small></b></li>'; }); h += '</ol>'; }
    const pv = o.prev && o.prev.best[sid]; if (pv) h += '<p class="ttprev">Last week’s best here: <b>' + pv + '%</b></p>';
    h += '<p class="tttease">Soon: the top three on <b>Friends</b> and <b>Global</b> win dabs every week.</p>';
  } else {
    const P3 = TT_PRIZE[ttTab]; h = '<div class="ttlock"><span class="ttlk">' + '""" + LOCK.replace("'", "\\'") + r"""' + '</span><b>Coming with online play</b><p>' + (ttTab === 'global' ? 'Everyone’s best on ' + escAttr(ttName(sid)) + ', every week.' : 'Your friends’ best on ' + escAttr(ttName(sid)) + ', every week.') + '</p>'
      + '<ol class="ttprize" aria-label="Prizes for the week’s top three">' + P3.map((v, i) => '<li class="r' + (i + 1) + '"><i>' + ttOrd(i + 1) + '</i><b>' + v + '</b>' + '""" + DAB.replace("'", "\\'") + r"""' + '<span>dabs</span></li>').join('') + '</ol>'
      + (ttTab === 'friends' ? '<p class="ttneed">Needs ' + TT_FRIENDS_MIN + ' friends or more on the board to pay out.</p>' : '<p class="ttneed">Paid out when the week turns.</p>') + '</div>';
  }
  $('ttBody').innerHTML = h;
}
function openTT(sid, hiT) {
  ttSel = TT_STAGES.includes(sid) ? sid : ttSid(); ttTab = 'you'; ttHi = hiT || 0; const m = $('ttModal'), was = m.hidden; m.hidden = false; ttRender(); AU.ui(); buzz(6);
  if (was) { const c = m.querySelector('.ttcard'); c.style.animation = 'none'; void c.offsetWidth; c.style.animation = ''; }
  clearInterval(ttTick); ttTick = setInterval(() => { if ($('ttModal').hidden) return clearInterval(ttTick); $('ttLeft').textContent = ttLeft(); }, 30000);
  setTimeout(() => $('ttX').focus({ preventScroll: true }), 40);
}
function closeTT() { const m = $('ttModal'); if (m.hidden) return; m.hidden = true; clearInterval(ttTick); AU.ui(); const s = $('ttStrip'); if (s && !s.hidden) s.focus({ preventScroll: true }); }
$('ttStrip').addEventListener('click', () => { AU.init(); openTT(ttSid()); });
$('ttX').addEventListener('click', closeTT);
$('ttModal').addEventListener('click', e => { if (e.target === $('ttModal')) closeTT(); });
$('ttPrev').addEventListener('click', () => { const i = TT_STAGES.indexOf(ttSel); ttSel = TT_STAGES[(i - 1 + TT_STAGES.length) % TT_STAGES.length]; AU.ui(); ttRender(); kick($('ttStage'), 'bump'); });
$('ttNext').addEventListener('click', () => { const i = TT_STAGES.indexOf(ttSel); ttSel = TT_STAGES[(i + 1) % TT_STAGES.length]; AU.ui(); ttRender(); kick($('ttStage'), 'bump'); });
document.querySelector('.tttabs').addEventListener('click', e => { const b = e.target.closest('[data-tt]'); if (!b || b.dataset.tt === ttTab) return; ttTab = b.dataset.tt; AU.ui(); ttRender(); });
document.addEventListener('keydown', e => { if (e.key === 'Escape' && !$('ttModal').hidden) { e.preventDefault(); e.stopPropagation(); closeTT(); } }, true);
"""

CSS = r"""
/* (v293) Time trial: the leaderboard strip on the canvas picker */
.mworld #soloNote.ttoff{display:none}
.ttstrip{display:grid;grid-template-columns:auto minmax(0,1fr) auto;align-items:center;gap:10px;width:min(100%,420px);margin:0 auto 4px;padding:9px 12px 9px 10px;box-sizing:border-box;border:0;border-radius:3px;
  background:#FCFAF2 url(art/m_paperbg.webp) center/300px;color:var(--black);text-align:left;font:inherit;cursor:pointer;box-shadow:inset 0 0 0 1px rgba(23,19,32,.08),4px 5px 0 rgba(0,0,0,.45);rotate:-.5deg;transition:transform .14s ease}
.ttstrip:active{transform:scale(.97)}
.ttstrip .ttsi{width:34px;height:34px;display:grid;place-items:center}.ttstrip .ttsi svg{width:34px;height:34px}
.ttstrip .ttst{display:grid;gap:1px;min-width:0}
.ttstrip .ttst b{font:400 15px/1.1 var(--font-display);letter-spacing:.01em;text-transform:uppercase;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ttstrip .ttst small{font:700 11.5px/1.25 var(--font-ui);color:#5E566E;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ttstrip .ttsw{display:flex;align-items:center;gap:4px}.ttstrip .ttsw svg{width:12px;height:12px;flex:none}
.ttstrip .ttsgo{display:flex;align-items:center;gap:2px;padding:6px 6px 6px 10px;border-radius:999px;background:var(--black);color:#FFE07A;font:800 11px/1 var(--font-ui);letter-spacing:.06em;text-transform:uppercase}
.ttstrip .ttsgo svg{width:13px;height:13px}
/* the board: a taped sheet of lined notebook paper */
.ttm{z-index:30}
.ttcard{position:relative;width:min(100%,392px);max-height:min(92%,720px);display:flex;flex-direction:column;gap:10px;box-sizing:border-box;padding:22px 16px 14px 34px;border-radius:2px;color:var(--black);
  background:linear-gradient(90deg,transparent 23px,rgba(226,72,88,.6) 23px,rgba(226,72,88,.6) 25px,transparent 25px),repeating-linear-gradient(180deg,transparent 0 27px,rgba(84,140,205,.3) 27px 28px),#FCFAF2;
  background-position:0 0,0 10px,0 0;box-shadow:inset 0 0 0 1px rgba(23,19,32,.06),6px 8px 0 rgba(0,0,0,.45);rotate:-.4deg;animation:cardlift .34s cubic-bezier(.2,1.25,.35,1) both}
.ttcard::before,.ttcard::after{content:"";position:absolute;top:-10px;width:74px;height:22px;background:url(art/m_tape3.webp) center/100% 100% no-repeat;pointer-events:none;filter:drop-shadow(0 1px 0 rgba(23,19,32,.12))}
.ttcard::before{left:-16px;transform:rotate(-30deg)}.ttcard::after{right:-16px;transform:rotate(28deg)}
.ttx{position:absolute;top:8px;right:8px;width:34px;height:34px;display:grid;place-items:center;border:0;border-radius:50%;background:none;color:#6E6680;cursor:pointer}
.ttx svg{width:20px;height:20px}
.tthd{display:grid;justify-items:start;gap:3px}
.tthd small{font:800 11px/1 var(--font-ui);letter-spacing:.12em;text-transform:uppercase;color:#6E6680}
.tthd h3{position:relative;isolation:isolate;margin:0;padding:0 2px;font:400 24px/1 var(--font-display);text-transform:uppercase;letter-spacing:.01em;transform:rotate(-1deg)}
.tthd h3::after{content:"";position:absolute;left:-7px;right:-9px;bottom:-3px;height:15px;z-index:-1;background:#F2B53A;opacity:.65;-webkit-mask:url(art/m_stroke2.webp) center/100% 100% no-repeat;mask:url(art/m_stroke2.webp) center/100% 100% no-repeat}
/* the canvas: a brass plaque you flip through */
.ttstage{display:grid;grid-template-columns:36px minmax(0,1fr) 36px;align-items:center;gap:6px;margin-left:-10px}
.ttarr{width:36px;height:36px;display:grid;place-items:center;border:0;border-radius:50%;background:var(--black);color:#FFF8EA;cursor:pointer;box-shadow:2px 3px 0 rgba(0,0,0,.3)}
.ttarr svg{width:18px;height:18px}.ttarr:active{transform:scale(.92)}
.ttplq{display:block;padding:8px 10px;border-radius:4px;text-align:center;font:400 15px/1.1 var(--font-display);letter-spacing:.05em;text-transform:uppercase;color:#35240A;text-shadow:0 1px 0 rgba(255,244,210,.65);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
  background:linear-gradient(180deg,#F6E3AA 0%,#DDBB66 46%,#BF923A 54%,#DAB566 100%);box-shadow:inset 0 1px 0 rgba(255,255,255,.65),0 0 0 1.5px #5A3F12,0 4px 8px rgba(0,0,0,.25)}
/* whose times: construction-paper tabs */
.tttabs{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:6px;margin-left:-10px}
.tttabs button{--skp:#E3A12C;--skt:#2A1A04;display:flex;align-items:center;justify-content:center;gap:4px;min-height:38px;padding:6px 4px;border:0;border-radius:2px;cursor:pointer;
  background:url(art/m_cpaper_g.webp) center/180px,var(--skp);background-blend-mode:multiply;color:var(--skt);font:400 13px/1 var(--font-display);text-transform:uppercase;letter-spacing:.02em;
  box-shadow:inset 0 0 0 1px rgba(0,0,0,.08),3px 4px 0 rgba(0,0,0,.4);filter:brightness(.82) saturate(.9);scale:.95;transition:scale .18s ease,filter .18s ease,translate .18s ease}
.tttabs button[data-tt="friends"]{--skp:#3A84D4;--skt:#FFF8EA}.tttabs button[data-tt="global"]{--skp:#D33A4C;--skt:#FFF8EA}
.tttabs button.on{filter:none;scale:1;translate:0 -2px;box-shadow:inset 0 0 0 1px rgba(0,0,0,.08),5px 6px 0 rgba(0,0,0,.45)}
.tttabs button svg{width:13px;height:13px;opacity:.8}
.ttbody{min-height:min(276px,42vh);overflow:auto;margin-right:-6px;padding-right:6px;-webkit-overflow-scrolling:touch}
/* this week's runs, written on the lines */
.ttlist{list-style:none;margin:0;padding:0;display:grid}
.ttrow{display:grid;grid-template-columns:32px minmax(0,1fr) auto;align-items:center;gap:10px;min-height:42px;padding:2px 2px 2px 0;border-bottom:1px dashed rgba(84,140,205,.35)}
.ttrk{width:28px;height:28px;display:grid;place-items:center;border-radius:50%;margin-left:2px;font:400 13px/1 var(--font-display);color:#6E6680;background:rgba(23,19,32,.06)}
.ttrow.r1 .ttrk{background:radial-gradient(circle at 35% 30%,#FFF2B0,#F2C12E 55%,#B88412);color:#3A2600;box-shadow:0 0 0 2px var(--black),2px 2px 0 2px rgba(0,0,0,.25)}
.ttrow.r2 .ttrk{background:radial-gradient(circle at 35% 30%,#FFFFFF,#C9CED6 55%,#8A92A0);color:#262A33;box-shadow:0 0 0 2px var(--black),2px 2px 0 2px rgba(0,0,0,.25)}
.ttrow.r3 .ttrk{background:radial-gradient(circle at 35% 30%,#FFD9B3,#D08A4E 55%,#8E5326);color:#2E1604;box-shadow:0 0 0 2px var(--black),2px 2px 0 2px rgba(0,0,0,.25)}
.ttwho{display:flex;align-items:center;gap:7px;min-width:0;font:700 13.5px/1.2 var(--font-ui);color:var(--black);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ttwho em{flex:none;padding:3px 7px 2px;border-radius:999px;background:#E8364F;color:#fff;font:800 10px/1 var(--font-ui);font-style:normal;letter-spacing:.06em;text-transform:uppercase;rotate:-3deg}
.ttpc{font:400 22px/1 var(--font-display)}.ttpc small{font-size:13px;margin-left:1px}
.ttrow.r1 .ttpc{font-size:26px}
.ttrow.me{background:linear-gradient(90deg,rgba(255,224,122,0),rgba(255,224,122,.55) 18%,rgba(255,224,122,.55) 82%,rgba(255,224,122,0))}
.ttnone{display:grid;gap:4px;margin:6px 0;font:600 13.5px/1.45 var(--font-ui);color:#5E566E}.ttnone b{font-size:15px;color:var(--black)}
.ttprev,.tttease{margin:10px 0 0;font:600 12.5px/1.4 var(--font-ui);color:#5E566E}.ttprev b{color:var(--black)}
.tttease{font-style:italic}
/* Friends and Global: locked until online play, with the week's prizes */
.ttlock{display:grid;justify-items:center;gap:6px;padding:8px 2px 4px;text-align:center}
.ttlock .ttlk{width:46px;height:46px;display:grid;place-items:center;border-radius:50%;background:var(--black);color:#FFF8EA;rotate:-6deg;box-shadow:3px 4px 0 rgba(0,0,0,.25)}
.ttlock .ttlk svg{width:22px;height:22px}
.ttlock>b{font:400 17px/1.1 var(--font-display);text-transform:uppercase;letter-spacing:.01em}
.ttlock>p{margin:0;font:600 13px/1.4 var(--font-ui);color:#5E566E;max-width:30ch}
.ttprize{list-style:none;margin:6px 0 2px;padding:0;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;width:100%}
.ttprize li{position:relative;display:grid;justify-items:center;gap:2px;padding:12px 4px 9px;border-radius:2px;background:#FFE896;box-shadow:0 10px 10px -8px rgba(0,0,0,.5);rotate:-1.5deg}
.ttprize li:nth-child(2){rotate:1deg;background:#FFF1B8}.ttprize li:nth-child(3){rotate:-.5deg;background:#FFF6D2}
.ttprize li::before{content:"";position:absolute;top:-7px;left:50%;width:40px;height:14px;margin-left:-20px;background:url(art/m_tape3.webp) center/100% 100% no-repeat;transform:rotate(-4deg)}
.ttprize i{font:800 11px/1 var(--font-ui);font-style:normal;letter-spacing:.08em;text-transform:uppercase;color:#6E6680}
.ttprize b{font:400 26px/1 var(--font-display);color:var(--black)}
.ttprize li.r1 b{font-size:30px}
.ttprize .ttdab{width:20px;height:20px;margin:1px 0}
.ttprize span{font:800 10.5px/1 var(--font-ui);letter-spacing:.06em;text-transform:uppercase;color:#5E566E}
.ttneed{font-style:italic}
.ttfoot{display:flex;align-items:center;justify-content:center;gap:6px;margin:2px 0 0 -10px;font:700 12.5px/1 var(--font-ui);color:#5E566E}
.ttfoot svg{width:16px;height:16px}.ttfoot b{color:var(--black)}
@media (min-aspect-ratio:1/1) and (max-height:600px){.ttcard{padding-top:16px;gap:7px}.ttrow{min-height:36px}.tthd h3{font-size:20px}}
@media (prefers-reduced-motion:reduce){.ttcard{animation:none}.tttabs button{transition:none}}
"""

def apply(s):
    # the board and the strip
    s = rep(s, '  <div class="modal" id="statsModal" hidden>', HTML + '  <div class="modal" id="statsModal" hidden>')
    s = rep(s, '<p class="lhead critics" style="text-align:center;color:#B8B0C8">CPU difficulty</p><div class="seg" id="stages" role="group" aria-label="CPU difficulty"></div>\n        <p class="snote" id="soloNote" hidden></p>',
               '<p class="lhead critics" id="wDiffHd" style="text-align:center;color:#B8B0C8">CPU difficulty</p><div class="seg" id="stages" role="group" aria-label="CPU difficulty"></div>\n        <p class="snote" id="soloNote" hidden></p>' + STRIP)
    s = rep(s, '<span class="evbar"><i>Beat your best</i></span>', '<span class="evbar"><i>Weekly leaderboard</i></span>')
    # the picker keeps the strip current
    s = rep(s, "  { const sn = $('soloNote'); sn.innerHTML = mode === 'solo' ? '<b>Your canvas:</b> '",
               "  if (typeof ttStrip === 'function') ttStrip(); // (v293)\n  { const sn = $('soloNote'); sn.innerHTML = mode === 'solo' ? '<b>Your canvas:</b> '")
    s = rep(s, "function renderWorlds() {\n  const W = store.world || {};", "function renderWorlds() {\n  if (typeof ttStrip === 'function') ttStrip(); // (v293)\n  const W = store.world || {};")
    # a run counts against this week's best on its canvas
    s = rep(s, "const slot = mode === 'solo' ? 'solo' : key + diff, prev = store.bestCov[slot] || 0, newBest = ry > prev; endInfo.best = Math.max(prev, ry); endInfo.prevBest = prev;",
               "const slot = mode === 'solo' ? 'solo' : key + diff, prev = mode === 'solo' ? ttBest(TH.id) : store.bestCov[slot] || 0, newBest = ry > prev; endInfo.best = Math.max(prev, ry); endInfo.prevBest = prev;\n"
               "  if (mode === 'solo') { endInfo.sid = TH.id; endInfo.tt = ttAdd(TH.id, ry); } // (v293: on this week's board for the canvas)")
    s = rep(s, "  if (newBest) store.bestCov[slot] = ry;\n", "  if (mode === 'solo' ? ry > (store.bestCov.solo || 0) : newBest) store.bestCov[slot] = ry; // (the all-time best stays for Stats)\n")
    # the HUD bar fills toward this week's best here
    s = rep(s, "if (mode === 'solo') { const best = (store.bestCov && store.bestCov.solo) || 0, bt = best ? best + '%' : '-';",
               "if (mode === 'solo') { const best = ttBest(TH.id), bt = best ? best + '%' : '-';")
    # the results: the place this week, and the week's top three
    s = rep(s, """else if (solo) { const you = Math.round(info.you); w = { kick: info.newBest ? 'New best' : "Time's up", name: playerName(), ghost: you + '%',
    stats: vicStat(you, '%', 'Canvas painted', true) + (!info.newBest ? vicStat(info.best, '%', 'Your best', false) : info.prevBest ? vicStat('+' + (you - info.prevBest), '%', 'On your old best', false) : vicStat('1st', '', 'Canvas on record', false)) }; }""",
               """else if (solo) { const you = Math.round(info.you), tt = info.tt || { rank: 1, runs: 1 }; w = { kick: info.newBest ? 'Best this week' : "Time's up", name: playerName(), ghost: you + '%',
    stats: vicStat(you, '%', 'Canvas painted', true) + vicStat(ttOrd(tt.rank), '', 'This week', false) + (!info.newBest ? vicStat(info.best, '%', 'Week best', false) : info.prevBest ? vicStat('+' + (you - info.prevBest), '%', 'On the week best', false) : vicStat(tt.runs, '', tt.runs === 1 ? 'Run this week' : 'Runs this week', false)) }; }""")
    s = rep(s, "  $('vCards').innerHTML = solo ? '' : board.filter(",
               "  $('vCards').innerHTML = solo ? ttVicRows(info) : board.filter(")
    s = rep(s, "const vicStat = (n, unit, label, hi) =>",
               "// (v293) a Time trial's results: this week's top three on the canvas, this run marked (and this run under them if it placed lower)\n"
               "function ttVicRows(info) { if (!info.sid) return ''; const L = ttRuns(info.sid), hi = info.tt && info.tt.t, rows = L.slice(0, 3).map((r, i) => [i + 1, r]); const k = L.findIndex(r => r.t === hi); if (k >= 3) rows.push([k + 1, L[k]]);\n"
               "  return rows.map(([n, r], i) => '<div class=\"vrow' + (r.t === hi ? ' me' : '') + '\" style=\"--cc:' + colVars(P)[1] + ';animation-delay:' + (1.2 + i * 0.08).toFixed(2) + 's\"><b class=\"vr\">' + String(n).padStart(2, '0') + '</b>' + faceIcon(P, false)\n"
               "    + '<span class=\"vn\">' + escAttr(ttWhen(r.t)) + (r.t === hi ? '<em>This run</em>' : '') + '</span><b class=\"vp\">' + r.p + '<small>%</small></b></div>').join(''); }\n"
               "const vicStat = (n, unit, label, hi) =>")
    # the tally speaks of the week's best
    s = rep(s, "(info.newBest ? 'Old best' : 'Best') + '</small><span class=\"jv\">'", "(info.newBest ? 'Old best' : 'Week best') + '</small><span class=\"jv\">'")
    s = rep(s, "aria-label=\"' + (info.newBest ? 'Old best ' : 'Your best ') + best", "aria-label=\"' + (info.newBest ? 'Old best ' : 'Week best ') + best")
    s = rep(s, "<span class=\"bn\"><b>' + (info.newBest ? 'Old best' : 'Your best') + '</b>", "<span class=\"bn\"><b>' + (info.newBest ? 'Old best' : 'Week best') + '</b>")
    s = rep(s, "if (mode === 'solo') { const best = (store.bestCov && store.bestCov.solo) || 0; sn.textContent = 'Cover as much as you can in 60 seconds.' + (best ? ' Your best is ' + best + '%.' : ''); }",
               "if (mode === 'solo') sn.textContent = 'Cover as much as you can in 60 seconds. Every canvas has its own board this week.';")
    # the code, after the picker's own (VOTE_STAGES, THEME_BY and the strip's elements exist by then)
    a = "const stageArtOf = sid =>"
    assert s.count(a) == 1
    i = s.index(a); j = s.index('\n', i) + 1
    s = s[:j] + JS + s[j:]
    # the styles, after the last of the page's own
    b = "@media (prefers-reduced-motion:reduce){#mStrokes .stslot,#mStrokes .stopt{transition:none}}"
    s = rep(s, b, b + CSS.rstrip('\n'))
    return s
