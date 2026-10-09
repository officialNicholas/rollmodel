# World picker and Customize:
#  - no Season 2 card, no "New" ribbons, and each painting's plaque shows just the world's name
#  - tapping Halloween opens a grid of its canvases (The Crypt, The Cathedral, The Manor, or all three in turn): pick one and that's
#    what you'll play; the back button returns to the worlds
#  - your name is set in Customize now (a field at the top, with the dice for a random one); the title screen's name tag is gone
import json, re
p = '/home/claude/paint-the-canvas.html'
s = open(p).read()
TH = json.load(open('/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/gen/stage_thumbs.json'))
def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, (n, old[:120]); s = s.replace(old, new)

# --- the cards
rep('<span class="ribbon new">New</span><span class="plaque"><b class="wn">Palette Island</b><span class="wsub">Sun, sand and the sea</span><span class="wst" data-w="isl"></span></span></button>',
    '<span class="plaque"><b class="wn">Palette Island</b></span></button>')
rep('<span class="ribbon new">New</span><span class="plaque"><b class="wn">Blank Canvas</b><span class="wsub">A white world to fill</span><span class="wst" data-w="blk"></span></span></button>',
    '<span class="plaque"><b class="wn">Blank Canvas</b></span></button>')
rep('<span class="ribbon">Season 1</span><span class="plaque"><b class="wn">Halloween</b><span class="wsub">Three haunted canvases</span><span class="wst" data-w="s1"></span></span></button>',
    '<span class="ribbon">Season 1</span><span class="plaque"><b class="wn">Halloween</b></span></button>')
i = s.index('        <button class="world locked" type="button" data-s="next" aria-disabled="true">'); j = s.index('</button>', i) + len('</button>\n')
s = s[:i] + s[j:]
rep('<div class="gdots" id="gDots" aria-hidden="true"><i></i><i></i><i></i><i></i></div>',
    '<div class="gdots" id="gDots" aria-hidden="true"><i></i><i></i><i></i></div>\n      <div class="sgrid" id="seasonGrid" role="group" aria-label="Halloween canvases" hidden>'
    + ''.join('<button class="stg" type="button" data-s="%s"><span class="sfr"><img class="art" src="%s" alt="" width="440" height="302" decoding="async"><i class="wcheck" aria-hidden="true"></i></span><b>%s</b></button>' % (k, TH[k], n)
              for k, n in [('crypt', 'The Crypt'), ('cathedral', 'The Cathedral'), ('manor', 'The Manor'), ('season', 'All three')])
    + '</div>')
# --- styles
rep(".gdots{display:flex;gap:9px;padding:6px 0 4px}",
    """.gdots{display:flex;gap:9px;padding:6px 0 4px}
/* a season's canvases: a grid of small framed paintings, each with its name */
.sgrid{grid-column:1/-1;width:min(calc(100% - 32px),440px);align-self:center;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:clamp(14px,4vw,22px) clamp(12px,3.6vw,20px);padding:20px 0 8px;animation:dockin .32s cubic-bezier(.25,1.3,.45,1) both}
.stg{appearance:none;position:relative;display:grid;justify-items:center;gap:9px;padding:0;border:0;background:none;color:inherit;font:inherit;cursor:pointer;-webkit-tap-highlight-color:transparent}
.stg .sfr{position:relative;display:block;width:100%;aspect-ratio:320/220;box-sizing:border-box;padding:6px;border-radius:8px;background:linear-gradient(135deg,#FFEFB8 0,#F1C45E 20%,#B8822C 46%,#F7D47C 68%,#9C681E 100%);border:3px solid var(--line);box-shadow:0 5px 0 var(--line),0 12px 22px rgba(5,2,14,.5);transition:transform .16s cubic-bezier(.3,1.6,.5,1),box-shadow .16s}
.stg .art{display:block;width:100%;height:100%;object-fit:cover;border-radius:3px;border:2px solid var(--line);box-sizing:border-box}
.stg b{max-width:100%;box-sizing:border-box;padding:6px 12px 7px;border-radius:9px;background:linear-gradient(180deg,#FFF9EC,#EADBBF);border:3px solid var(--line);box-shadow:0 3px 0 var(--line);color:var(--outline);font:400 clamp(14px,4vw,17px)/1 var(--font-display);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.stg .wcheck{width:30px;height:30px;top:-11px;right:-11px;background-size:19px}
.stg[aria-pressed="true"] .sfr{transform:translateY(-5px);box-shadow:0 10px 0 var(--line),0 20px 30px rgba(5,2,14,.55)}
.stg[aria-pressed="true"] .wcheck{transform:scale(1)}
.stg[aria-pressed="true"] b{background:linear-gradient(180deg,#FFE7A3,#F2C24F)}
.stg:active .sfr{transform:translateY(2px)}
.stg:focus-visible .sfr{outline:3px solid var(--gold);outline-offset:5px}
.mworld.season .gallery,.mworld.season .gdots{display:none}""")
rep("  .gdots{display:none}\n", "  .gdots{display:none}\n  .sgrid{grid-template-columns:repeat(4,minmax(0,1fr));width:min(100%,780px);padding:10px 0 4px;gap:14px}\n  .stg b{font-size:14px;padding:5px 9px 6px}\n")
# --- the title screen's name tag goes (your name is in Customize)
rep(".nametag b{white-space:nowrap;", "#nameBtn{display:none}\n.nametag b{white-space:nowrap;")

# --- stage keys: the Halloween canvases one at a time, or all three in turn
rep("const STAGE_THEMES = { island: ['island'], blank: ['blank'] }, STAGE_KEY = { island: 'isl', blank: 'blk' };",
    "const STAGE_THEMES = { island: ['island'], blank: ['blank'], crypt: ['crypt'], cathedral: ['cathedral'], manor: ['manor'] }, STAGE_KEY = { island: 'isl', blank: 'blk', crypt: 'cry', cathedral: 'cat', manor: 'man' };\nconst inSeason = s => s === 'season' || SEASON.themes.includes(s);")
rep("let stageSel = ['island', 'blank'].includes(store.stage) ? store.stage : 'season';",
    "let stageSel = ['island', 'blank', 'crypt', 'cathedral', 'manor'].includes(store.stage) ? store.stage : 'season';")
rep("const worldKey = () => (GEN.themes && GEN.themes.length === 1 && STAGE_KEY[GEN.themes[0]]) || 's' + SEASON.n;",
    "const worldKey = () => (GEN.themes && GEN.themes.length === 1 && !SEASON.themes.includes(GEN.themes[0]) && STAGE_KEY[GEN.themes[0]]) || 's' + SEASON.n;")
# the season's card reads as picked whichever of its canvases is picked
rep("function renderGo() {\n  for (const b of worldBtns) b.setAttribute('aria-pressed', String(b.dataset.s === stageSel));",
    "function renderGo() {\n  for (const b of worldBtns) b.setAttribute('aria-pressed', String(b.dataset.s === stageSel || (b.dataset.s === 'season' && inSeason(stageSel))));\n  for (const b of $('seasonGrid').children) b.setAttribute('aria-pressed', String(b.dataset.s === stageSel));")
rep("  for (const b of $('stagePick').children) b.setAttribute('aria-pressed', String(b.dataset.s === stageSel));\n  $('shuffleBtn').hidden = false;",
    "  for (const b of $('stagePick').children) b.setAttribute('aria-pressed', String(b.dataset.s === stageSel || (b.dataset.s === 'season' && inSeason(stageSel))));\n  $('shuffleBtn').hidden = false;")
# scrolling the carousel onto Halloween keeps the canvas you picked inside it
rep("function selectWorld(s) {\n  if (s === stageSel || s === 'next' || building) return;",
    "function selectWorld(s) {\n  if (s === stageSel || s === 'next' || building || (s === 'season' && inSeason(stageSel) && !seasonOpen())) return;")
rep("gallery.addEventListener('click', e => {\n  const t = e.target.closest('.world'); if (!t) return;",
    "gallery.addEventListener('click', e => {\n  const t = e.target.closest('.world'); if (!t) return;\n  if (t.dataset.s === 'season') { centerWorld(t, true); selectWorld('season'); openSeason(); return; }")
rep("function closeWorlds() {\n  if (menuPage !== 'worlds') return;",
    """// a season's canvases, in a grid in place of the carousel; the back button comes back here
const seasonOpen = () => $('mWorld').classList.contains('season');
function openSeason() {
  if (seasonOpen()) return; $('mWorld').classList.add('season'); $('seasonGrid').hidden = false; $('worldTitle').textContent = SEASON.name; $('worldBack').setAttribute('aria-label', 'Back to the worlds');
  renderGo(); setTimeout(() => { const b = [...$('seasonGrid').children].find(x => x.dataset.s === stageSel) || $('seasonGrid').firstElementChild; b && b.focus({ preventScroll: true }); }, 40);
}
function closeSeason() {
  if (!seasonOpen()) return false; $('mWorld').classList.remove('season'); $('seasonGrid').hidden = true; $('worldTitle').textContent = 'Pick a world'; $('worldBack').setAttribute('aria-label', 'Back to the title screen');
  centerWorld(worldBtns.find(b => b.dataset.s === 'season'), false); renderWorlds(); return true;
}
$('seasonGrid').addEventListener('click', e => { const t = e.target.closest('.stg'); if (!t || building) return; AU.init(); if (t.dataset.s === stageSel) { AU.ui(); return; }
  stageSel = t.dataset.s; store.stage = stageSel; save(); renderStages(); AU.pop();
  if (state === 'menu') setTimeout(() => { if (state !== 'menu' || building || stageSel !== t.dataset.s) return; freshMap(); resetRun(); decorate(); menuPose(); renderStages(); kick($('cvName'), 'bump'); }, 40); });
function closeWorlds() {
  if (menuPage !== 'worlds') return; closeSeason();""")
rep("$('worldBack').addEventListener('click', () => { AU.init(); AU.ui(); closeWorlds(); });",
    "$('worldBack').addEventListener('click', () => { AU.init(); AU.ui(); if (!closeSeason()) closeWorlds(); });")

# --- your name, in Customize
rep('    <div class="lgroup"><p class="lhead">Color <b id="lookColor">Red</b></p>',
    '    <div class="lgroup"><p class="lhead">Name</p><div class="namefield lname"><input id="lookName" type="text" size="8" maxlength="12" autocomplete="off" autocapitalize="words" autocorrect="off" spellcheck="false" enterkeyhint="done" aria-label="Your name"><button class="dice" id="lookDice" type="button" aria-label="Pick a random name"><svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3.5" y="3.5" width="17" height="17" rx="4.5" fill="none" stroke="currentColor" stroke-width="2.2"/><circle cx="8.6" cy="8.6" r="1.6"/><circle cx="15.4" cy="15.4" r="1.6"/><circle cx="12" cy="12" r="1.6"/><circle cx="15.4" cy="8.6" r="1.6"/><circle cx="8.6" cy="15.4" r="1.6"/></svg></button></div></div>\n    <div class="lgroup"><p class="lhead">Color <b id="lookColor">Red</b></p>')
rep(".lookp .swatches{padding:2px 2px 0}", ".lookp .swatches{padding:2px 2px 0}\n.lname input{height:46px;font-size:22px;border-radius:14px}\n.lname .dice{width:46px;height:46px;border-radius:14px}\n.lname .dice svg{width:22px;height:22px}")
rep("function lookPop() { menuReact = 0.7; AU.pop(); }",
    """function lookPop() { menuReact = 0.7; AU.pop(); }
// your name: typed straight into Customize (saved as you go), or a random one from the dice
const lookName = $('lookName');
function saveLookName() { const v = cleanName(lookName.value); if (v && v !== store.name) { store.name = v; save(); paintName(); } }
lookName.addEventListener('input', saveLookName);
lookName.addEventListener('change', () => { saveLookName(); lookName.value = cleanName(store.name) || ''; });
lookName.addEventListener('keydown', e => { e.stopPropagation(); if (e.key === 'Enter' || e.key === 'Escape') { e.preventDefault(); lookName.blur(); } });
$('lookDice').addEventListener('click', () => { AU.init(); AU.pop(); lookName.value = randomName(); saveLookName(); menuReact = 0.7; });""")
rep("  lookOpen = true; menu.classList.add('looking'); renderSwatches(); renderLook(); lookEl.hidden = false;",
    "  lookOpen = true; menu.classList.add('looking'); renderSwatches(); renderLook(); lookName.value = cleanName(store.name) || ''; lookName.placeholder = playerName(); lookEl.hidden = false;")
open(p, 'w').write(s)
print('ok')
