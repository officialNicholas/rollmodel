#!/usr/bin/env python3
"""The canvas vote: after the fight card, a strip of canvases to vote on; CPUs vote too; a spin lands on the winner. On top of ui7_patch."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui7_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)

CSS = '''
/* ===== the canvas vote: a strip of canvases under the fighters, everyone's splat lands on one, the spin picks ===== */
.vvote{position:absolute;left:0;right:0;bottom:0;z-index:6;box-sizing:border-box;padding:10px 10px max(12px,env(safe-area-inset-bottom));background:rgba(23,19,32,.97);box-shadow:0 -4px 0 var(--cream),0 -16px 30px rgba(0,0,0,.5);transform:translateY(110%);transition:transform .45s cubic-bezier(.2,1.2,.35,1)}
.vvote.on{transform:none}
.vvote[hidden]{display:none}
.vvh{display:flex;justify-content:space-between;align-items:baseline;gap:10px;margin:0 2px 7px;font:900 12px/1 var(--font-ui);letter-spacing:.16em;text-transform:uppercase;color:#B8B0C8}
.vvh b{font:900 16px/1 var(--font-head);font-style:italic;letter-spacing:.02em;color:#fff;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.vtimer{height:5px;margin:0 2px 10px;background:rgba(255,255,255,.12);border-radius:3px;overflow:hidden}
.vtimer i{display:block;height:100%;width:100%;background:var(--ink);transform-origin:left center}
.vvote.ticking .vtimer i{transition:transform var(--vt,3.2s) linear;transform:scaleX(0)}
.vts{display:flex;gap:8px;justify-content:center;align-items:end}
.vt{appearance:none;position:relative;flex:1;min-width:0;max-width:86px;padding:0;border:0;background:none;color:#fff;cursor:pointer;display:grid;justify-items:center;gap:5px;transition:transform .3s cubic-bezier(.3,1.5,.5,1),opacity .3s;-webkit-tap-highlight-color:transparent}
.vt img{display:block;width:100%;aspect-ratio:4/3;object-fit:cover;border:3px solid #fff;box-sizing:border-box;box-shadow:0 0 0 2px var(--black),3px 4px 0 rgba(0,0,0,.5);background:#1F0C42;transition:box-shadow .15s}
.vt small{display:block;max-width:100%;font:900 9.5px/1.1 var(--font-ui);letter-spacing:.05em;text-transform:uppercase;color:#B8B0C8;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.vt.mine img{border-color:var(--ink)}
.vt.mine small{color:#fff}
.vt .vch{position:absolute;top:-9px;right:-7px;display:flex;flex-direction:row-reverse;gap:1px;pointer-events:none}
.vt .vch i{width:20px;height:20px;background:var(--c);-webkit-mask:url(art/m_splat2.webp) center/contain no-repeat;mask:url(art/m_splat2.webp) center/contain no-repeat;filter:drop-shadow(1px 1px 0 rgba(0,0,0,.6));animation:chipin .4s cubic-bezier(.2,1.6,.4,1) both}
@keyframes chipin{from{transform:scale(2.4) rotate(-40deg);opacity:0}}
.vt.spin img{box-shadow:0 0 0 2px var(--black),0 0 0 5px var(--cream),3px 4px 0 rgba(0,0,0,.5)}
.vt.win{transform:scale(1.2) translateY(-7px);z-index:2}
.vt.win img{box-shadow:0 0 0 2px var(--black),0 0 0 5px var(--ink),0 0 26px var(--ink)}
.vt.win small{color:#fff;font-size:10.5px}
.vvote.done .vt:not(.win){opacity:.3}
.vsx.voting .vband.bot,.vsx.voting .vstitle{display:none}
.vsx.voting .vcol .vbox{transform:translate(-50%,-60%)}
@media (min-aspect-ratio:1/1){.vvote{padding:8px 14px max(8px,env(safe-area-inset-bottom))}.vvh{margin-bottom:5px}.vtimer{margin-bottom:7px}.vt{max-width:108px}.vt img{aspect-ratio:16/9}.vts{gap:10px}.vsx.voting .vcol .vbox{top:15%;width:40%;transform:translate(-50%,0)}.vsx.voting .vhead{min-height:46px}}
@media (prefers-reduced-motion:reduce){.vvote{transition:none}.vt .vch i{animation:none}}
'''
k = s.index('<div id="stage">'); j = s.rindex('</style>', 0, k); s = s[:j] + CSS + s[j:]

rep('<div class="vsrow" id="vsRow"></div><p class="vstitle" id="vsTitle"></p></section>',
    '<div class="vsrow" id="vsRow"></div><p class="vstitle" id="vsTitle"></p><div class="vvote" id="vvote" hidden><div class="vvh"><span id="vvLbl">Vote for a canvas</span><b id="vvWin"></b></div><div class="vtimer"><i></i></div><div class="vts" id="vts"></div></div></section>')

# the card: solo goes straight to the wipe; versus opens the vote, and the winning canvas is built behind the wipe if it is not the one waiting
rep("  const id = runId; setTimeout(() => { if (id !== runId && state !== 'menu') { el.hidden = true; return cb(); } slashWipe({ dur: 1.0, onPeak: () => { el.hidden = true; cb(); } }); }, 2100);\n}",
    """  const id = runId, wipe = win => slashWipe({ dur: 1.0, onPeak: () => { el.hidden = true; el.classList.remove('voting'); $('vvote').hidden = true;
    if (win && TH.id !== win) { building = true; genWorld((Math.random() * 4294967296) >>> 0, { avoid: TH.id, themes: [win] }); mapUsed = false; clearTimeout(warmQ); warmRender(); building = false; }
    cb(); } });
  if (mode === 'solo' || window.__noVote) { setTimeout(() => { if (id !== runId && state !== 'menu') { el.hidden = true; return cb(); } wipe(null); }, 2100); return; }
  setTimeout(() => { if (id !== runId && state !== 'menu') { el.hidden = true; return cb(); } openVote(id, win => { if (id !== runId && state !== 'menu') { el.hidden = true; return cb(); } wipe(win); }); }, 1000);
}
// ---------- the vote: the open canvases in a row; your splat sits on your pick (your canvas from the lobby until you tap another), the
// rivals' splats drop in after a beat, and when the clock runs out a spin walks the votes and lands on one: every vote is a ticket ----------
const VOTE_STAGES = ['island', 'blank', 'crypt', 'cathedral', 'manor'];
const stageArtOf = sid => { const b = $('stagePick').querySelector('.world[data-s="' + sid + '"] img.art') || $('seasonGrid').querySelector('.stg[data-s="' + sid + '"] img.art'); return b ? b.src : ''; };
const themeLabel = sid => (THEMES.find(t => t.id === sid) || {}).label || sid;
let voteState = null;
function openVote(id, done) {
  const box = $('vvote'), row = $('vts'), who = [P, H]; if (mode === 'trio') who.push(H2);
  const votes = new Map(); votes.set(P, VOTE_STAGES.includes(stageSel) ? stageSel : VOTE_STAGES[(Math.random() * VOTE_STAGES.length) | 0]);
  row.innerHTML = VOTE_STAGES.map(sid => '<button class="vt" type="button" data-s="' + sid + '"><span class="vch"></span><img alt="" src="' + stageArtOf(sid) + '"><small>' + escAttr(themeLabel(sid)) + '</small></button>').join('');
  $('vvLbl').textContent = 'Vote for a canvas'; $('vvWin').textContent = ''; box.classList.remove('ticking', 'done'); box.hidden = false; $('vsx').classList.add('voting');
  const draw = () => { for (const b of row.children) { const sid = b.dataset.s, chips = [...votes].filter(([, v]) => v === sid).map(([D]) => '<i style="--c:' + TEAMS[D.team].css + '"></i>').join(''); b.querySelector('.vch').innerHTML = chips; b.classList.toggle('mine', votes.get(P) === sid); } };
  draw(); const st = voteState = { id, votes, open: true, timers: [] };
  const at = (ms, fn) => st.timers.push(setTimeout(() => { if (st !== voteState || id !== runId) return; fn(); }, ms));
  row.onclick = e => { const b = e.target.closest('.vt'); if (!b || !st.open || st !== voteState) return; if (votes.get(P) !== b.dataset.s) { votes.set(P, b.dataset.s); draw(); AU.ui(); buzz(8); } };
  requestAnimationFrame(() => { box.classList.add('on'); requestAnimationFrame(() => box.classList.add('ticking')); });
  who.slice(1).forEach((D, i) => at(1300 + i * 650 + Math.random() * 500, () => { votes.set(D, VOTE_STAGES[(Math.random() * VOTE_STAGES.length) | 0]); draw(); AU.plop(); }));
  at(3300, () => {
    st.open = false; const tickets = [...votes.values()], win = tickets[(Math.random() * tickets.length) | 0], cands = VOTE_STAGES.filter(sid => tickets.includes(sid)), btn = sid => row.querySelector('[data-s="' + sid + '"]');
    $('vvLbl').textContent = 'The canvas is';
    // the spin: round the voted canvases, slowing, stopping on the winner
    const steps = []; let cur = cands.indexOf(win), total = cands.length * 2 + 2; for (let k = total; k >= 0; k--) steps.push(cands[((cur - k) % cands.length + cands.length) % cands.length]);
    let t = 0; steps.forEach((sid, k) => { const gap = 70 + Math.pow(k / steps.length, 2.2) * 260; t += gap; at(t, () => { for (const b of row.children) b.classList.toggle('spin', b.dataset.s === sid); if (k < steps.length - 1) AU.tick ? AU.tick(0) : 0; }); });
    at(t + 60, () => { for (const b of row.children) { b.classList.remove('spin'); b.classList.toggle('win', b.dataset.s === win); } box.classList.add('done'); $('vvWin').textContent = themeLabel(win); AU.pop(); buzz([14, 30, 14]); });
    at(t + 1100, () => { voteState = null; done(win); });
  });
}""")
rep('<p class="ver">Version 77</p>', '<p class="ver">Version 78</p>')
open(DST, 'w').write(s); print('ok', n0, '->', len(s))
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
