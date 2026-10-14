#!/usr/bin/env python3
"""Put the game into the iOS app and zip the Xcode project as RollModel-iOS.zip (run from anywhere).

The app is the original Roll Model project (bundle ID studio.primeshots.rollmodel, the paint roller icon), so a build of it goes to App
Store Connect as an update of the app already there. The game goes in ios/RollModel/RollModel/Game: the page, three.js, the character
pack the page loads, art, music and sounds, plus the bundled fonts and licenses from ios/shared. The page is pointed at those fonts in
place of Google Fonts (the app runs offline), and its version line shows the app's version with the game's build number. The build
fails if anything in the page points outside the app or names a file the app doesn't have. The page also gets a fixed zoom and the
app's copy of the save (native/save.js, served by the app) ahead of the game."""
import os, re, shutil, zipfile
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
game, app, shared = os.path.join(root, 'game'), os.path.join(root, 'ios', 'RollModel'), os.path.join(root, 'ios', 'shared')
dst = os.path.join(app, 'RollModel', 'Game')
if os.path.isdir(dst): shutil.rmtree(dst)
html = open(os.path.join(game, 'index.html'), encoding='utf8').read()
used = set(re.findall(r"['\"](axo-pack[-\w]*\.txt)['\"]", html))  # (quoted, as the page loads it: a comment naming one doesn't count)
# (only the character pack the page loads goes in: older packs stay in the repo for older builds, not in the app)
# (and no local test pages: game/_*.html are probe builds, never part of the game)
skip = lambda d, names: [n for n in names if n == '.DS_Store' or (d == game and ((n.startswith('axo-pack') and n.endswith('.txt') and n not in used) or (n.startswith('_') and n.endswith('.html'))))]
shutil.copytree(game, dst, ignore=skip)
for sub in ('fonts', 'licenses'): shutil.copytree(os.path.join(shared, sub), os.path.join(dst, sub))
# the fonts from the app itself, not Google
FACES = [('Bowlby One', 400, 'bowlby-one-latin-400-normal.woff2', 'normal')] + [('Figtree', w, 'figtree-latin-%d-normal.woff2' % w, 'normal') for w in (400, 600, 700, 800, 900)]
FACES += [('Barlow Condensed', 600, 'barlow-condensed-latin-600-normal.woff2', 'normal')] + [('Barlow Condensed', w, 'barlow-condensed-latin-%d-italic.woff2' % w, 'italic') for w in (700, 800, 900)]  # (v274: the victory screen's words)
css = '<style>' + ''.join("@font-face{font-family:'%s';font-style:%s;font-weight:%d;font-display:swap;src:url(fonts/%s) format('woff2')}" % (f[0], f[3], f[1], f[2]) for f in FACES) + '</style>'
link = re.findall(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com/css2[^"]*">', html); assert len(link) == 1, link
html = html.replace(link[0], css)
for pc in ('<link rel="preconnect" href="https://fonts.googleapis.com">', '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'):
    assert html.count(pc) == 1, pc; html = html.replace(pc, '')
# (the first launch asks Google for Figtree's regular weight at boot, for its title: the app has it bundled above)
dyn = re.findall(r"try \{ const l = document\.createElement\('link'\); l\.rel = 'stylesheet'; l\.href = 'https://fonts\.googleapis\.com/[^']*'; document\.head\.appendChild\(l\); \} catch \(e\) \{\} ", html)
assert len(dyn) <= 1, dyn
for d in dyn: html = html.replace(d, '')
assert 'fonts.googleapis.com' not in html and 'fonts.gstatic.com' not in html
for n in re.findall(r'url\(fonts/([^)]+)\)', html): assert os.path.isfile(os.path.join(dst, 'fonts', n)), n
# the version line: the app's version, then the game's build
pbx = open(os.path.join(app, 'RollModel.xcodeproj', 'project.pbxproj'), encoding='utf8').read()
mv = set(re.findall(r'MARKETING_VERSION = ([\d.]+);', pbx)); assert len(mv) == 1, mv; mv = mv.pop()
ver = re.findall(r'<p class="ver">Version (\d+)</p>', html); assert len(ver) == 1, ver
html = html.replace('<p class="ver">Version %s</p>' % ver[0], '<p class="ver">Version %s (%s)</p>' % (mv, ver[0]))
# a fixed screen: no zoom (a pinch or a double tap must never scale the game)
vp = '<meta name=viewport content="width=device-width,initial-scale=1,viewport-fit=cover">'; assert html.count(vp) == 1, 'viewport'
html = html.replace(vp, '<meta name=viewport content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover">')
# the app's own copy of the save goes back in before the game reads its save (the app serves native/save.js; see SaveBridge.swift)
k = html.find('<script'); assert k > 0
html = html[:k] + '<script src="native/save.js"></script>\n' + html[k:]
# fully offline: nothing may point outside the app, and every file the game names must be in it
ext = [u for u in re.findall(r'(?:https?:)?//[\w.-]+\.[a-z]{2,}[^\s"\'<>)]*', html) if 'www.w3.org/' not in u]
assert not ext, ('points outside the app', ext[:5])
names = set(re.findall(r"['\"(]((?:music|sfx|voice|art|fonts)/[\w.-]+\.(?:mp3|webp|png|jpg|woff2))", html))
for n in names: assert os.path.isfile(os.path.join(dst, n)), ('missing in the app', n)
TRKS = re.search(r"const TRK = \{([\s\S]*?)\n  \};", html).group(1)
for key, body in re.findall(r"\n    (\w+): \{([^}]*)\}", TRKS):
    f = re.search(r"file: '(\w+)'", body); n = 'music/%s.mp3' % (f.group(1) if f else key)
    assert os.path.isfile(os.path.join(dst, n)), ('song missing in the app', n)
for n in set(re.findall(r"\.say\('(\w+)'", html)): assert os.path.isfile(os.path.join(dst, 'voice', 'say_%s.mp3' % n)), ('line missing', n)
for n in ('sfx/m.mp3', 'sfx/s.mp3'): assert os.path.isfile(os.path.join(dst, n)), n
print('offline check:', len(names), 'named files, every song, line and sheet in the app; nothing outside')
open(os.path.join(dst, 'index.html'), 'w', encoding='utf8').write(html)
for ref in re.findall(r'<script src="([^"]+)"', html): assert ref.startswith('native/') or os.path.isfile(os.path.join(dst, ref)), ref
# the zip: the project folder as RollModel/, the way the app first went out
out = os.path.join(root, 'RollModel-iOS.zip')
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    for d, dirs, files in os.walk(app):
        dirs[:] = sorted(x for x in dirs if x != 'xcuserdata')
        for f in sorted(files):
            if f == '.DS_Store': continue
            p = os.path.join(d, f); z.write(p, os.path.join('RollModel', os.path.relpath(p, app)))
print(out, os.path.getsize(out) // 1024, 'KB; app version', mv, 'game', ver[0])
