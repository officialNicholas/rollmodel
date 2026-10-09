# Stages: The Studio goes; The Night Garden leaves the Halloween season and becomes a map of its own
import re
p = '/home/claude/paint-the-canvas.html'
s = open(p).read()
def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, (n, old[:110]); s = s.replace(old, new)

# world cards: drop the Studio's, add the Garden's (placeholder art until its in-engine render, made after its overhaul)
i = s.index('<button class="world" type="button" data-s="standard">'); j = s.index('</button>', i) + len('</button>')
studio_card = s[i:j]; s = s[:i] + s[j:].lstrip('\n ')
k = s.index('<button class="world" type="button" data-s="season">')
season_card = s[k:s.index('</button>', k) + 9]
art = re.search(r'<img class="art" src="([^"]+)"', season_card).group(1)
garden_card = ('<button class="world" type="button" data-s="garden"><span class="frame"><img class="art" src="' + art + '" alt="" width="720" height="495" decoding="async"><i class="wcheck" aria-hidden="true"></i></span>'
               '<span class="ribbon new">New</span><span class="plaque"><b class="wn">The Night Garden</b><span class="wsub">Lamplight and hedges</span><span class="wst" data-w="gdn"></span></span></button>\n        ')
i = s.index('<button class="world" type="button" data-s="island">')
s = s[:i] + garden_card + s[i:]
rep('Four haunted canvases', 'Three haunted canvases')

rep("// the stage: one standard stage that's always here, plus the season's canvases, which come and go\nconst SEASON = { n: 1, name: 'Halloween', themes: ['crypt', 'cathedral', 'manor', 'garden'] };",
    "// the stages: maps that are always here, plus the season's canvases, which come and go\nconst SEASON = { n: 1, name: 'Halloween', themes: ['crypt', 'cathedral', 'manor'] };")
rep("const STAGE_THEMES = { island: ['island'], blank: ['blank'] }, STAGE_KEY = { island: 'isl', blank: 'blk' };",
    "const STAGE_THEMES = { garden: ['garden'], island: ['island'], blank: ['blank'] }, STAGE_KEY = { garden: 'gdn', island: 'isl', blank: 'blk' };")
rep("let stageSel = ['standard', 'island', 'blank'].includes(store.stage) ? store.stage : 'season';",
    "let stageSel = ['garden', 'island', 'blank'].includes(store.stage) ? store.stage : 'season';")
# the Studio's map data and its loader
i = s.index("// The Studio: the standard stage. Laid out once and kept as data"); j = s.index('\n', s.index('const STANDARD = ', i)) + 1
s = s[:i] + s[j:]
rep("const mapKey = () => stageSel === 'standard' ? 'std:' + (mode === 'trio' ? 'trio' : 'duel') : (STAGE_KEY[stageSel] || 'sea') + ':' + mode + ':' + (easyOn() ? 1 : 0);",
    "const mapKey = () => (STAGE_KEY[stageSel] || 'sea') + ':' + mode + ':' + (easyOn() ? 1 : 0);")
rep("$('shuffleBtn').hidden = stageSel === 'standard';", "$('shuffleBtn').hidden = false;")
rep("$('shuffleBtn').hidden = locked || stageSel === 'standard';", "$('shuffleBtn').hidden = locked;")
rep("function freshMap() { if (stageSel === 'standard') loadStandard(); else genWorld(", "function freshMap() { genWorld(")
i = s.index('function loadStandard() {'); j = s.index('\n}\n', i) + 3
s = s[:i] + s[j:]
rep("banner(GEN.std ? TH.label : 'Same canvas');", "banner('Same canvas');")
rep("const std = !!GEN.std, op = { easy: GEN.easy, avoid: GEN.avoid, themes: GEN.themes }; setTimeout(() => { if (std) loadStandard(); else genWorld(sd, op);",
    "const op = { easy: GEN.easy, avoid: GEN.avoid, themes: GEN.themes }; setTimeout(() => { genWorld(sd, op);")
rep("banner(stageSel === 'standard' ? STD_LABEL : 'New canvas');", "banner('New canvas');")
rep("const worldKey = () => GEN.std ? 'std' : (GEN.themes", "const worldKey = () => (GEN.themes")
open(p, 'w').write(s)
print('ok', 'studio card bytes', len(studio_card))
