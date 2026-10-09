# the results sheet becomes a scoreboard: the verdict stamped in paint, the canvas split between the colors, a row per player
import re, sys
P = '/home/claude/paint-the-canvas.html'
src = open(P).read()

def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, (n, old[:120])
    src = src.replace(old, new)

# ---------- CSS ----------
a = src.index('.rtitle{margin:0;text-align:center;font:400 clamp(32px,9.6vw,44px)')
b = src.index('.stat>span{display:block;margin-top:6px;font:700 12px/1.15 var(--font-ui);color:var(--muted)}')
b = src.index('\n', b) + 1
old = src[a:b]
keep = []
for line in old.split('\n'):
    if line.startswith(('.ptitle', '.frame', '.placard', '.pill')):
        keep.append(line)
NEW_CSS = r'''/* results: the verdict stamped in paint, the canvas split between the colors, then a row for each player (its color, its face, its name,
   who it knocked out and how much it painted) */
#end{overflow-x:hidden}
.rhead{display:grid;justify-items:center;gap:9px;padding-top:6px}
.rtitle{position:relative;isolation:isolate;margin:0;padding:0 .16em;font:400 clamp(36px,11.2vw,52px)/1.08 var(--font-display);text-transform:uppercase;white-space:nowrap;color:var(--gold);transform:skewX(-9deg) rotate(-2.5deg);text-shadow:var(--o3),0 6px 0 var(--outline);animation:stamp .5s .06s cubic-bezier(.2,1.5,.35,1) both}
.rsplat{position:absolute;z-index:-1;left:-12%;top:-30%;width:124%;height:160%;fill:var(--ink);pointer-events:none;animation:splatin .42s cubic-bezier(.2,1.6,.4,1) both}
.rtitle.lose,.rtitle.draw{color:var(--bone)}
.rtitle.lose .rsplat{fill:var(--ink-lo)}
.rtitle.draw .rsplat{fill:#46386E}
@keyframes stamp{0%{transform:skewX(-9deg) rotate(-2.5deg) scale(1.9);opacity:0}60%{opacity:1}}
@keyframes splatin{0%{transform:scale(.15);opacity:0}}
.rhead .ptitle{margin:0}
.judge{display:grid;gap:5px}
.jnums{position:relative;height:27px}
.jnums b{position:absolute;bottom:0;font:400 25px/1 var(--font-display);color:var(--chi);text-shadow:var(--o2),0 3px 0 var(--outline);font-variant-numeric:tabular-nums;white-space:nowrap}
.jnums b small{margin-right:5px;font:800 12px/1 var(--font-ui);color:var(--muted);text-shadow:none;vertical-align:3px}
.jbar{position:relative;height:22px;border:3px solid var(--line);border-radius:10px;background:#3A2E5C;overflow:hidden;transform:skewX(-14deg);box-shadow:0 4px 0 var(--line)}
.jbar i{position:absolute;top:0;bottom:0;box-sizing:border-box;background:var(--c);box-shadow:inset 0 4px 0 rgba(255,255,255,.3),inset 0 -4px 0 rgba(0,0,0,.16);transform:scaleX(0);transform-origin:var(--o,left) center;transition:transform .95s .3s cubic-bezier(.2,.85,.25,1)}
.jbar i+i{border-left:3px solid var(--line)}
.judge.go .jbar i{transform:none}
.jbar u{position:absolute;top:0;bottom:0;width:4px;margin-left:-2px;background:var(--gold);box-shadow:0 0 0 2px var(--line)}
.board{--cols:24px 40px minmax(0,1fr) 56px 58px;--cap:30px;display:grid;gap:8px}
.board.solo{--cols:24px 40px minmax(0,1fr) 70px}
.bhead,.brow{display:grid;grid-template-columns:var(--cols);align-items:center;gap:0 6px;padding:0 12px 0 6px}
.bhead{margin-bottom:-2px;font:700 11px/1 var(--font-ui);color:var(--muted);white-space:nowrap}
.bhead span{text-align:center}
.bhead span:last-child{text-align:right}
.brow{position:relative;isolation:isolate;min-height:50px;animation:rowin .5s cubic-bezier(.2,1.2,.35,1) both;animation-delay:var(--d,0s)}
.brow::before{content:"";position:absolute;inset:0;z-index:-1;border:3px solid var(--line);border-radius:12px;background:linear-gradient(90deg,var(--c) 0 var(--cap),var(--line) var(--cap) calc(var(--cap) + 3px),#170E30 calc(var(--cap) + 3px));transform:skewX(-10deg);box-shadow:0 3px 0 var(--line)}
.brow.you::before{border-color:var(--bone);background:linear-gradient(90deg,var(--c) 0 var(--cap),var(--line) var(--cap) calc(var(--cap) + 3px),#3B2B68 calc(var(--cap) + 3px));box-shadow:0 0 0 2px var(--line),0 4px 0 1px var(--line)}
.brank{font:400 18px/1 var(--font-display);color:var(--white);text-shadow:var(--o2);text-align:center}
.bico{position:relative;display:block;width:40px;height:40px;border-radius:50%;border:2.5px solid var(--line);box-sizing:border-box;background:var(--cd)}
.bico .sface{position:absolute;inset:0;width:100%;height:100%;border-radius:50%}
.bico .crown{position:absolute;left:50%;top:-16px;width:26px;height:21px;margin-left:-13px;fill:var(--gold);stroke:var(--line);stroke-width:2.2;stroke-linejoin:round;animation:crownin .5s cubic-bezier(.3,1.7,.5,1) both;animation-delay:calc(var(--d,0s) + .35s)}
@keyframes crownin{from{transform:translateY(-10px) rotate(-20deg) scale(.4);opacity:0}}
.bname{min-width:0;display:grid;gap:4px;justify-items:start}
.bn{max-width:100%;min-width:0;display:flex;align-items:center;gap:6px}
.bn b{min-width:0;font:800 16px/1.15 var(--font-ui);color:var(--bone);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.bn i{flex:none;padding:3px 6px;border-radius:6px;background:var(--bone);color:var(--outline);font:800 10.5px/1 var(--font-ui);font-style:normal}
.medal{display:inline-flex;align-items:center;gap:4px;padding:2px 8px 2px 3px;border:2px solid var(--line);border-radius:99px;background:var(--gold);color:var(--outline);font:800 11px/1.1 var(--font-ui);font-style:normal;white-space:nowrap;animation:medalin .45s cubic-bezier(.3,1.7,.5,1) both;animation-delay:calc(var(--d,0s) + .6s)}
.medal svg{width:15px;height:15px;flex:none}
@keyframes medalin{from{opacity:0;transform:scale(.3) rotate(-10deg)}}
.bko{display:flex;align-items:center;justify-content:center;gap:4px;font:400 21px/1 var(--font-display);color:var(--bone);text-shadow:0 2px 0 var(--line);font-variant-numeric:tabular-nums}
.bko svg{width:18px;height:18px;flex:none;fill:var(--muted);stroke:var(--line);stroke-width:1.6;stroke-linejoin:round}
.bko.top svg{fill:var(--gold)}
.bpct{text-align:right;font:400 23px/1 var(--font-display);color:var(--chi);text-shadow:var(--o2),0 3px 0 var(--outline);font-variant-numeric:tabular-nums;white-space:nowrap}
.brow.best .bico{display:grid;place-items:center}
.brow.best .bico svg{width:24px;height:24px}
@keyframes rowin{from{opacity:0;transform:translateX(48px)}}
@media (max-width:374px){.board{--cols:22px 36px minmax(0,1fr) 46px 50px;--cap:28px}.bico{width:36px;height:36px}.bn b{font-size:15px}.bpct{font-size:20px}.bko{font-size:18px}.bko svg{width:15px;height:15px}.medal{font-size:10px;padding-right:6px}.bhead{font-size:10px}}
'''
new_block = NEW_CSS + '\n'.join(keep) + '\n'
src = src[:a] + new_block + src[b:]

# the compact layout (short landscape screens)
rep('.sheet .rtitle{font-size:30px}.sheet .btn.play{min-height:50px}.sheet .ptitle{font-size:12px}.sheet .pchip{padding:7px 10px 7px 8px}.sheet .pchip b{font-size:28px}.sheet .stat{padding:6px 4px}.sheet .stat b{font-size:18px}.sheet .stat>span{margin-top:3px;font-size:11px}.sheet .row .btn{min-height:44px}',
    '.sheet .rtitle{font-size:30px}.sheet .rhead{gap:5px}.sheet .btn.play{min-height:50px}.sheet .ptitle{font-size:12px}.sheet .jnums{height:20px}.sheet .jnums b{font-size:18px}.sheet .jbar{height:16px}.sheet .board{--cols:22px 30px minmax(0,1fr) 46px 50px;--cap:27px;gap:5px}.sheet .board.solo{--cols:22px 30px minmax(0,1fr) 60px}.sheet .brow{min-height:36px}.sheet .bico{width:30px;height:30px;border-width:2px}.sheet .bico .crown{top:-12px;width:20px;height:16px;margin-left:-10px}.sheet .bn b{font-size:14px}.sheet .bpct{font-size:18px}.sheet .bko{font-size:16px}.sheet .bko svg{width:14px;height:14px}.sheet .medal{font-size:10px}.sheet .bhead{font-size:10px}.sheet .row .btn{min-height:44px}')

# reduced motion: the new pieces sit still
rep('.logo,.mcta,.world,.mworld,.bigplay::before,.card,.modal,.logo.paint .tcard,.pchip.win svg,#cvName.bump{animation:none}',
    '.logo,.mcta,.world,.mworld,.bigplay::before,.card,.modal,.logo.paint .tcard,#cvName.bump{animation:none}\n  .rtitle,.rsplat,.brow,.bico .crown,.medal{animation:none}\n  .jbar i{transition:none}')

# the winner's cards use the new face (in its ring)
rep('.vcard svg{width:40px;height:37px;display:block}\n', '')

# ---------- markup ----------
SPLAT = ('M30 52C22 34 44 18 70 24C80 8 112 6 126 16C140 2 176 2 188 14C204 4 240 8 246 22C270 16 296 32 286 48C304 58 290 80 266 76'
         'C258 90 224 94 210 84C196 96 156 98 146 86C130 96 92 94 86 82C62 90 30 80 38 66C16 66 12 50 30 52Z'
         'M120 86V97C120 104 130 104 130 97V86ZM176 88V94C176 100 184 100 184 94V88Z')
DROPS = '<circle cx="12" cy="30" r="6"/><circle cx="306" cy="70" r="5.5"/><circle cx="300" cy="18" r="3.5"/><circle cx="52" cy="93" r="4"/><circle cx="238" cy="95" r="3.5"/>'
a = src.index('  <section class="sheet" id="end" hidden>')
b = src.index('    <button class="btn play two" id="endBtn"', a)
src = src[:a] + '''  <section class="sheet" id="end" hidden>
    <div class="rhead">
      <h2 class="rtitle" id="endTitle"><svg class="rsplat" viewBox="0 0 320 100" preserveAspectRatio="none" aria-hidden="true"><path d="''' + SPLAT + '''"/>''' + DROPS + '''</svg><span id="endWord">Victory!</span></h2>
      <p class="ptitle"><b id="pTitle">Study in Crimson No. 1</b><span id="pMeta">Paint on canvas</span></p>
    </div>
    <div class="judge" id="judge" aria-hidden="true"><div class="jnums" id="jNums"></div><div class="jbar" id="jBar"></div></div>
    <div class="board" id="board" role="list" aria-label="Scores"></div>
''' + src[b:]

# ---------- script ----------
# the slime's face icon replaces the old round blob
a = src.index("const blobSVG = c => '<svg viewBox=\"0 0 48 44\"")
b = src.index('\n', a) + 1
ICON = r'''// the slime's head and shoulders, flat, in its color, wearing what it wears: the scoreboard's faces and the winner's cards
const mixHex = (a, b, t) => { const m = s => Math.round(((a >> s) & 255) + (((b >> s) & 255) - ((a >> s) & 255)) * t); return '#' + ((m(16) << 16) | (m(8) << 8) | m(0)).toString(16).padStart(6, '0'); };
const escAttr = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);
function slimeIcon(hex, look) {
  const c = mixHex(hex, 0, 0), lo = mixHex(hex, 0x0C0620, 0.3), face = mixHex(hex, 0xFFF1E6, 0.42), O = '#0C0620', w = look || {}, hat = w.head === 'hat', halo = w.head === 'halo', fangs = w.mouth === 'fangs';
  const g = '<g transform="translate(0 ' + (hat ? 4 : halo ? 3 : 1) + ')"';
  let s = '<svg class="sface" viewBox="1 2 46 46" aria-hidden="true">' + g + ' stroke="' + O + '" stroke-width="2.3" stroke-linejoin="round" stroke-linecap="round">';
  // the body under it, the ears hanging by its face (behind the head), the head
  s += '<path d="M8.5 52C9.5 41 15 35.5 24 35.5S38.5 41 39.5 52Z" fill="' + c + '"/>';
  s += '<path d="M16 15.5C8.6 14.8 4.4 23.6 5.2 32.2C5.6 37 11.4 38.2 12.8 33.6C14 29.6 14.2 24.6 17.6 20.4Z" fill="' + lo + '"/><path d="M32 15.5C39.4 14.8 43.6 23.6 42.8 32.2C42.4 37 36.6 38.2 35.2 33.6C34 29.6 33.8 24.6 30.4 20.4Z" fill="' + lo + '"/>';
  s += '<ellipse cx="24" cy="23.4" rx="12.6" ry="11.8" fill="' + c + '"/></g>' + g + '>';
  // the face: a softer, paler patch, big eyes with a glint, a small smile, rosy cheeks, a shine on the crown
  s += '<ellipse cx="24" cy="26.6" rx="8.4" ry="6.2" fill="' + face + '" opacity=".55"/><path d="M15.6 18.4C17 15 20 13.2 23.2 13" fill="none" stroke="#fff" stroke-opacity=".7" stroke-width="2.4" stroke-linecap="round"/>';
  s += '<ellipse cx="19.9" cy="25" rx="2.55" ry="3.4" fill="#1A1030"/><ellipse cx="28.1" cy="25" rx="2.55" ry="3.4" fill="#1A1030"/><circle cx="20.8" cy="23.6" r="1" fill="#fff"/><circle cx="29" cy="23.6" r="1" fill="#fff"/>';
  s += '<path d="M22 30Q24 31.7 26 30" fill="none" stroke="#1A1030" stroke-width="1.5" stroke-linecap="round"/>';
  if (fangs) s += '<path d="M22.3 30.4l.9 2.1.9-1.9zM25.7 30.4l-.9 2.1-.9-1.9z" fill="#fff" stroke="#1A1030" stroke-width=".7" stroke-linejoin="round"/>';
  s += '<ellipse cx="15.6" cy="28.6" rx="2.2" ry="1.3" fill="#FF7FA8" opacity=".45"/><ellipse cx="32.4" cy="28.6" rx="2.2" ry="1.3" fill="#FF7FA8" opacity=".45"/>';
  if (hat) s += '<g stroke="' + O + '" stroke-width="2.1" stroke-linejoin="round"><path d="M17.6 13.4C19.6 8 22.4 2.4 29.6-.4C28 3.6 29.2 9 31 13.4Z" fill="#3B2A7A"/><path d="M9.6 14.6C15 11.2 33 11.2 38.4 14.6C33 17.4 15 17.4 9.6 14.6Z" fill="#3B2A7A"/><path d="M18.4 12C22 13 26.6 13 30.4 12" fill="none" stroke="#FF8A1F" stroke-width="1.8"/></g>';
  if (halo) s += '<ellipse cx="24" cy="6.6" rx="8.6" ry="2.7" fill="none" stroke="' + O + '" stroke-width="4.6"/><ellipse cx="24" cy="6.6" rx="8.6" ry="2.7" fill="none" stroke="#FFD86B" stroke-width="2.2"/>';
  return s + '</g></svg>';
}
const lookOf = D => D === P ? myLook : D === H ? LH.wearing : L2.wearing;
const CROWN_SVG = '<svg class="crown" viewBox="0 0 30 24" aria-hidden="true"><path d="M3.5 20.5 2 7l7.2 5.2L15 3l5.8 9.2L28 7l-1.5 13.5z"/></svg>';
const faceIcon = (D, crown) => '<span class="bico" style="--cd:' + mixHex(TEAMS[D.team].wet, 0x0C0620, 0.62) + '">' + slimeIcon(TEAMS[D.team].wet, lookOf(D)) + (crown ? CROWN_SVG : '') + '</span>';
'''
src = src[:a] + ICON + src[b:]
rep("""<b class="vrank">' + e.place + '</b>' + blobSVG(hexCss(TEAMS[e.D.team].wet)) + '<span>""", """<b class="vrank">' + e.place + '</b>' + faceIcon(e.D, false) + '<span>""")

# paintName no longer fills the old chip
rep("$('nameShow').textContent = store.name ? n : 'Add your name'; $('chipYouName').textContent = n; }", "$('nameShow').textContent = store.name ? n : 'Add your name'; }")

# showEnd: the scoreboard
a = src.index('function showEnd(img) {')
b = src.index('function measureOutro() {', a)
SHOW = r'''// ---------- the results: the verdict, the canvas split between the colors (counting up), and a row per player, best first ----------
const colVars = D => D === P ? ['var(--ink)', 'var(--ink-hi)'] : D === H ? ['var(--holy)', 'var(--holy-hi)'] : ['var(--wolf)', 'var(--wolf-hi)'];
const KO_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 1.8l2.3 5 5-2.3-1.7 5.3 5.2 2-5 2.4 2.2 5.1-5.3-1.8L12 22.4l-2.6-4.9-5.3 1.8 2.2-5.1-5-2.4 5.2-2-1.7-5.3 5 2.3z"/></svg>';
const MEDAL_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 1.5h4l1 5 1-5h4l-3.2 7.6" fill="#E3122F" stroke="#1A1030" stroke-width="1.6" stroke-linejoin="round"/><circle cx="12" cy="15" r="7.2" fill="#FFF4C9" stroke="#1A1030" stroke-width="1.8"/><path d="M12 10.6l1.3 2.7 3 .4-2.2 2.1.6 3-2.7-1.5-2.7 1.5.6-3-2.2-2.1 3-.4z" fill="#E8A21C"/></svg>';
const TROPHY_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 3.5h10v5.2a5 5 0 0 1-10 0zM7 5.5H4.2c0 3 1.2 4.6 3.3 5M17 5.5h2.8c0 3-1.2 4.6-3.3 5M10.2 13.4h3.6l.6 3.6h-4.8zM8 17h8v3.4H8z" fill="#FFD86B" stroke="#1A1030" stroke-width="1.6" stroke-linejoin="round"/></svg>';
const ordinal = n => n + (n % 10 === 1 && n % 100 !== 11 ? 'st' : n % 10 === 2 && n % 100 !== 12 ? 'nd' : n % 10 === 3 && n % 100 !== 13 ? 'rd' : 'th');
function showEnd(img) {
  const info = endInfo, n = store.runs || 1, w = colorOf().words, solo = info.mode === 'solo', trio = info.mode === 'trio';
  const covOf = D => Math.max(0, [info.you, info.cpu, info.cpu2][D.team] || 0);
  // the verdict
  const word = solo ? (info.newBest ? 'New best!' : 'Time!') : info.win > 0 ? 'Victory!' : info.win < 0 ? 'Defeat' : 'Draw', t = $('endTitle');
  $('endWord').textContent = word; t.className = 'rtitle' + (solo ? (info.newBest ? '' : ' lose') : info.win < 0 ? ' lose' : info.win === 0 ? ' draw' : '');
  t.setAttribute('aria-label', solo ? word : info.win > 0 ? 'Victory! You win' : info.win < 0 ? 'Defeat. ' + nameOf(info.winner) + ' wins' : 'Draw');
  paintName();
  const PT_B = ['in ' + w[0] + ' and Blue', 'in ' + w[1], 'in Two Colors', 'for One Blob', 'in Light and ' + w[2], 'in ' + w[2]];
  $('pTitle').textContent = PT_A[(n * 7) % PT_A.length] + ' ' + PT_B[(n * 3) % PT_B.length] + ', No. ' + n;
  $('pMeta').textContent = TH.label + ', ' + fmtTime(info.time);
  // the canvas between the colors: you from the left, the rivals in from the right (a solo canvas: how much of it, and where your best got to)
  let jb = '', jn = '';
  if (solo) {
    const you = covOf(P), best = info.newBest ? info.prevBest : info.best;
    jb = '<i style="--c:var(--ink);left:0;width:' + Math.min(100, you).toFixed(2) + '%"></i>' + (best && !info.newBest ? '<u style="left:' + Math.min(100, best) + '%"></u>' : '');
    jn = '<b data-to="' + Math.round(you) + '" data-a="left" style="--chi:var(--ink-hi)">0%</b>' + (best ? '<b data-a="right" style="--chi:var(--gold)"><small>' + (info.newBest ? 'Old best' : 'Best') + '</small>' + best + '%</b>' : '');
  } else {
    const order = trio ? [P, H2, H] : [P, H], tot = order.reduce((s, D) => s + covOf(D), 0); let x = 0;
    order.forEach((D, i) => {
      const sh = tot > 0 ? covOf(D) / tot * 100 : 100 / order.length, [c, hi] = colVars(D), o = i === 0 ? 'left' : i === order.length - 1 ? 'right' : 'center';
      jb += '<i style="--c:' + c + ';--o:' + o + ';left:' + x.toFixed(3) + '%;width:' + sh.toFixed(3) + '%"></i>';
      jn += '<b data-to="' + Math.round(covOf(D)) + '" data-a="' + o + '" data-x="' + (x + sh / 2).toFixed(3) + '" style="--chi:' + hi + '">0%</b>';
      x += sh;
    });
  }
  $('jBar').innerHTML = jb; $('jNums').innerHTML = jn; $('judge').classList.remove('go');
  // the board: who painted the most first; the crown on the winner; most eliminations (only if it's one player's alone)
  const ppl = (solo ? [P] : trio ? [P, H, H2] : [P, H]).map(D => ({ D, pct: Math.round(covOf(D)), kos: D.kos || 0 }));
  for (const e of ppl) e.place = 1 + ppl.filter(o => o.pct > e.pct).length;
  ppl.sort((a, b) => a.place - b.place || (b.D === info.winner) - (a.D === info.winner) || (b.D === P) - (a.D === P));
  const maxK = Math.max(0, ...ppl.map(e => e.kos)), tops = ppl.filter(e => e.kos === maxK), topK = !solo && maxK > 0 && tops.length === 1 ? tops[0].D : null;
  let h = solo ? '' : '<div class="bhead" aria-hidden="true"><span></span><span></span><span></span><span>Eliminations</span><span>Paint</span></div>';
  ppl.forEach((e, i) => {
    const D = e.D, me = D === P, [c, hi] = colVars(D), top = topK === D, nm = me ? playerName() : nameOf(D);
    const say = ordinal(e.place) + ', ' + nm + (me ? ' (you)' : '') + ', ' + e.pct + '% painted' + (solo ? '' : ', ' + e.kos + (e.kos === 1 ? ' elimination' : ' eliminations') + (top ? ', most eliminations' : ''));
    h += '<div class="brow' + (me ? ' you' : '') + '" role="listitem" aria-label="' + escAttr(say) + '" style="--c:' + c + ';--chi:' + hi + ';--d:' + (0.22 + i * 0.09).toFixed(2) + 's">'
      + '<b class="brank" aria-hidden="true">' + e.place + '</b>' + faceIcon(D, !solo && info.winner === D)
      + '<span class="bname" aria-hidden="true"><span class="bn"><b>' + escAttr(nm) + '</b>' + (me && !solo ? '<i>You</i>' : '') + '</span>' + (me && top ? '<em class="medal">' + MEDAL_SVG + 'Most eliminations</em>' : '') + '</span>'
      + (solo ? '' : '<span class="bko' + (top ? ' top' : '') + '" aria-hidden="true">' + KO_SVG + '<b>' + e.kos + '</b></span>')
      + '<b class="bpct" aria-hidden="true">' + e.pct + '%</b></div>';
  });
  if (solo) { const best = info.newBest ? info.prevBest : info.best;
    if (best) h += '<div class="brow best" role="listitem" aria-label="' + (info.newBest ? 'Old best ' : 'Your best ') + best + '%" style="--c:var(--gold);--chi:var(--gold);--d:.31s"><b class="brank" aria-hidden="true"></b><span class="bico" style="--cd:#4A3A12">' + TROPHY_SVG + '</span><span class="bname" aria-hidden="true"><span class="bn"><b>' + (info.newBest ? 'Old best' : 'Your best') + '</b></span></span><b class="bpct" aria-hidden="true">' + best + '%</b></div>'; }
  const bd = $('board'); bd.className = 'board' + (solo ? ' solo' : ''); bd.innerHTML = h;
  end.dataset.next = ''; $('replayBtn').hidden = false; $('endBtn').querySelector('small').textContent = 'New canvas';
  end.hidden = false; measureOutro(); judgeGo();
  setTimeout(() => $('endBtn').focus({ preventScroll: true }), 30);
}
// the numbers over the bar: the first at its left end, the last at its right, one in the middle over its own color (kept clear of the
// others), all counting up as the colors pour in
function judgeGo() {
  const box = $('jNums'), nums = Array.from(box.children), W = box.offsetWidth, last = nums.length - 1;
  for (const b of nums) if (b.dataset.to) b.textContent = b.dataset.to + '%';
  const ws = nums.map(b => b.offsetWidth);
  nums.forEach((b, i) => {
    const a = b.dataset.a; b.style.left = b.style.right = '';
    if (a === 'right') b.style.right = '0'; else if (a === 'center') { const lo = ws[0] + 12, hi = W - ws[last] - 12 - ws[i]; b.style.left = clamp(parseFloat(b.dataset.x) / 100 * W - ws[i] / 2, lo, Math.max(lo, hi)).toFixed(1) + 'px'; } else b.style.left = '0';
  });
  const counted = nums.filter(b => b.dataset.to);
  if (reduceMotion || window.__instant) { $('judge').classList.add('go'); return; }
  for (const b of counted) b.textContent = '0%';
  void box.offsetWidth; $('judge').classList.add('go');
  const t0 = performance.now() + 300, id = runId;
  const tick = now => { if (id !== runId || end.hidden) return; const u = clamp((now - t0) / 950, 0, 1), k = 1 - Math.pow(1 - u, 3); for (const b of counted) b.textContent = Math.round(+b.dataset.to * k) + '%'; if (u < 1) requestAnimationFrame(tick); };
  requestAnimationFrame(tick);
}
'''
src = src[:a] + SHOW + src[b:]

open(P, 'w').write(src)
print('ok')
