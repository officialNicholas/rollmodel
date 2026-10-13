#!/usr/bin/env python3
"""Put the game into the iOS app and zip the Xcode project as RollModel-iOS.zip (run from anywhere).

The app is the original Roll Model project (bundle ID studio.primeshots.rollmodel, the paint roller icon), so a build of it goes to App
Store Connect as an update of the app already there. The game goes in ios/RollModel/RollModel/Game: the page, three.js, the character
pack the page loads, art, music and sounds, plus the bundled fonts and licenses from ios/shared. The page is pointed at those fonts in
place of Google Fonts (the app runs offline), and its version line shows the app's version with the game's build number."""
import os, re, shutil, zipfile
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
game, app, shared = os.path.join(root, 'game'), os.path.join(root, 'ios', 'RollModel'), os.path.join(root, 'ios', 'shared')
dst = os.path.join(app, 'RollModel', 'Game')
if os.path.isdir(dst): shutil.rmtree(dst)
html = open(os.path.join(game, 'index.html'), encoding='utf8').read()
used = set(re.findall(r"['\"](axo-pack[-\w]*\.txt)['\"]", html))  # (quoted, as the page loads it: a comment naming one doesn't count)
# (only the character pack the page loads goes in: older packs stay in the repo for older builds, not in the app)
skip = lambda d, names: [n for n in names if n == '.DS_Store' or (d == game and n.startswith('axo-pack') and n.endswith('.txt') and n not in used)]
shutil.copytree(game, dst, ignore=skip)
for sub in ('fonts', 'licenses'): shutil.copytree(os.path.join(shared, sub), os.path.join(dst, sub))
# the fonts from the app itself, not Google
FACES = [('Bowlby One', 400, 'bowlby-one-latin-400-normal.woff2')] + [('Figtree', w, 'figtree-latin-%d-normal.woff2' % w) for w in (600, 700, 800, 900)]
css = '<style>' + ''.join("@font-face{font-family:'%s';font-style:normal;font-weight:%d;font-display:swap;src:url(fonts/%s) format('woff2')}" % f for f in FACES) + '</style>'
link = re.findall(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com/css2[^"]*">', html); assert len(link) == 1, link
html = html.replace(link[0], css)
for pc in ('<link rel="preconnect" href="https://fonts.googleapis.com">', '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'):
    assert html.count(pc) == 1, pc; html = html.replace(pc, '')
assert 'fonts.googleapis.com' not in html and 'fonts.gstatic.com' not in html
for n in re.findall(r'url\(fonts/([^)]+)\)', html): assert os.path.isfile(os.path.join(dst, 'fonts', n)), n
# the version line: the app's version, then the game's build
pbx = open(os.path.join(app, 'RollModel.xcodeproj', 'project.pbxproj'), encoding='utf8').read()
mv = set(re.findall(r'MARKETING_VERSION = ([\d.]+);', pbx)); assert len(mv) == 1, mv; mv = mv.pop()
ver = re.findall(r'<p class="ver">Version (\d+)</p>', html); assert len(ver) == 1, ver
html = html.replace('<p class="ver">Version %s</p>' % ver[0], '<p class="ver">Version %s (%s)</p>' % (mv, ver[0]))
open(os.path.join(dst, 'index.html'), 'w', encoding='utf8').write(html)
for ref in re.findall(r'<script src="([^"]+)"', html): assert os.path.isfile(os.path.join(dst, ref)), ref
# the zip: the project folder as RollModel/, the way the app first went out
out = os.path.join(root, 'RollModel-iOS.zip')
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    for d, dirs, files in os.walk(app):
        dirs[:] = sorted(x for x in dirs if x != 'xcuserdata')
        for f in sorted(files):
            if f == '.DS_Store': continue
            p = os.path.join(d, f); z.write(p, os.path.join('RollModel', os.path.relpath(p, app)))
print(out, os.path.getsize(out) // 1024, 'KB; app version', mv, 'game', ver[0])
