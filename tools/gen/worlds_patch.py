# The world select gets Palette Island and Blank Canvas; each is its own world with fresh canvases, stats and shuffle
import re, base64
p='/home/claude/paint-the-canvas.html'; s=open(p).read()
SP='/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
isl = base64.b64encode(open(SP + '/logo/island_art.webp', 'rb').read()).decode()
blk = base64.b64encode(open(SP + '/logo/blank_art.webp', 'rb').read()).decode()
def rep(a, b, n=1):
    global s
    c = s.count(a); assert c == n, (a[:100], c); s = s.replace(a, b)

card = lambda key, art, name, sub, w: ('<button class="world" type="button" data-s="' + key + '"><span class="frame"><img class="art" src="data:image/webp;base64,' + art + '" alt="" width="720" height="495" decoding="async"><i class="wcheck" aria-hidden="true"></i></span><span class="ribbon new">New</span><span class="plaque"><b class="wn">' + name + '</b><span class="wsub">' + sub + '</span><span class="wst" data-w="' + w + '"></span></span></button>\n        ')
# the new worlds sit right after the Studio
m = re.search(r'(<button class="world" type="button" data-s="standard">.*?</button>\n        )', s, re.S); assert m
s = s.replace(m.group(1), m.group(1) + card('island', isl, 'Palette Island', 'Sun, sand and the sea', 'isl') + card('blank', blk, 'Blank Canvas', 'A white world to fill', 'blk'))
rep('<div class="gdots" id="gDots" aria-hidden="true"><i></i><i></i><i></i></div>', '<div class="gdots" id="gDots" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i></div>')
rep(""".ribbon.soon{background:#6E69C8}""", """.ribbon.soon{background:#6E69C8}
.ribbon.new{background:#1FA9A0}""")
# five paintings: a carousel everywhere (on wide screens the neighbours show either side)
rep("""  .gallery{overflow:visible;justify-content:center;padding:34px 24px 10px;scroll-snap-type:none}
  .world{width:min(27vw,330px);min-width:0}
  .gdots{display:none}""", """  .gallery{padding:34px max(24px,calc(50% - 170px)) 10px}
  .world{width:min(27vw,330px);min-width:0}""")
rep("""  .gallery{grid-column:1/-1;overflow:visible;justify-content:center;padding:18px 0 4px;scroll-snap-type:none;gap:22px}""",
    """  .gallery{grid-column:1/-1;padding:18px max(12px,calc(50% - 125px)) 4px;gap:22px}""")
rep("""  .wst{flex-wrap:nowrap;gap:8px;font-size:12px}
  .gdots{display:none}""", """  .wst{flex-wrap:nowrap;gap:8px;font-size:12px}
  .gdots{display:none}
  .gallery .world{scroll-snap-align:center}""")

# stage keys: each themed world has its own canvases, map key and stats
rep("""let stageSel = store.stage === 'standard' ? 'standard' : 'season';""", """const STAGE_THEMES = { island: ['island'], blank: ['blank'] }, STAGE_KEY = { island: 'isl', blank: 'blk' };
let stageSel = ['standard', 'island', 'blank'].includes(store.stage) ? store.stage : 'season';
const stageThemes = () => STAGE_THEMES[stageSel] || SEASON.themes;""")
rep("""const mapKey = () => stageSel === 'standard' ? 'std:' + (mode === 'trio' ? 'trio' : 'duel') : 'sea:' + mode + ':' + (easyOn() ? 1 : 0);""",
    """const mapKey = () => stageSel === 'standard' ? 'std:' + (mode === 'trio' ? 'trio' : 'duel') : (STAGE_KEY[stageSel] || 'sea') + ':' + mode + ':' + (easyOn() ? 1 : 0);""")
rep("""function freshMap() { if (stageSel === 'standard') loadStandard(); else genWorld((Math.random() * 4294967296) >>> 0, { avoid: TH.id, themes: SEASON.themes }); mapUsed = false; }""",
    """function freshMap() { if (stageSel === 'standard') loadStandard(); else genWorld((Math.random() * 4294967296) >>> 0, { avoid: TH.id, themes: stageThemes() }); mapUsed = false; }""")
rep("""const worldKey = () => GEN.std ? 'std' : 's' + SEASON.n;""", """const worldKey = () => GEN.std ? 'std' : (GEN.themes && GEN.themes.length === 1 && STAGE_KEY[GEN.themes[0]]) || 's' + SEASON.n;""")
rep("""  $('shuffleBtn').hidden = stageSel !== 'season';""", """  $('shuffleBtn').hidden = stageSel === 'standard';""")
rep("""  go.querySelector('small').hidden = locked; $('shuffleBtn').hidden = locked || stageSel !== 'season';""", """  go.querySelector('small').hidden = locked; $('shuffleBtn').hidden = locked || stageSel === 'standard';""")
open(p,'w').write(s); print('worlds patch ok', len(s) // 1024, 'KB')
