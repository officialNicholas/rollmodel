#!/usr/bin/env python3
"""v208, the home screen and Settings, after Brawl Stars:
- the character says nothing on the home screen (no speech bubbles)
- the name and rank box top left goes; your dabs take its place, big (a gold coin over a dark tab), still the way into the Paint Shop
- a floating power bar over your character: your rank on a shield, your paint filling toward the next rank (a star), your name on tape;
  tap it for your stats (wins, matches, win rate, best coverage; the wins and best plates leave the home screen) and to change your name
- Friends on the right, and a spot either side of your character for a friend to join your lobby: both say coming soon
- Settings and the sound go into a menu that slides open from the right (room for more)
- Settings itself: switches that slide between their two settings (sound effects and music apart now), the screen, the visuals, help,
  play with friends (soon), the terms, the privacy note and the credits; the moving paint behind it stays"""
import re, subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui135_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
css = open(S + '/tools/assets/home208.css').read(); js = open(S + '/tools/assets/home208.js').read()
assert '</style>' not in css and '</script>' not in js

# ---- art ----
DAB = 'M10 5.2c.9 0 1.3 1.1 2 1.5 1 .5 2.2-.3 2.6.7.4 1-.9 1.6-.9 2.6s1.2 1.6.7 2.5c-.5.9-1.6.2-2.5.6-.8.4-1 1.7-1.9 1.7s-1.1-1.3-2-1.7c-.9-.4-2 .3-2.5-.6s.7-1.5.7-2.5-1.3-1.6-.9-2.6c.4-1 1.6-.2 2.6-.7.7-.4 1.1-1.5 2.1-1.5z'
COIN = ('<svg viewBox="0 0 40 40"><circle cx="20" cy="20" r="18.6" fill="#F2C14E" stroke="#171320" stroke-width="2.6"/><circle cx="20" cy="20" r="14.4" fill="#C98E22"/>'
        '<circle cx="20" cy="20.6" r="12.8" fill="#EDB43F"/><path class="dabk" transform="scale(2)" d="' + DAB + '" stroke="#171320" stroke-width=".85"/>'
        '<path d="M8.6 14.2a13 13 0 0 1 7.6-6.6" fill="none" stroke="#FFF1BF" stroke-width="2.2" stroke-linecap="round" opacity=".85"/></svg>')
def face(col, gill, kind):
    # a little axolotl peeking: its frills, a round head, a shine; its eyes and mouth by kind
    g = ''.join(f'<path d="{d}" stroke="#171320" stroke-width="5.4" stroke-linecap="round"/>' for d in ('M9.5 17 4.5 12.5', 'M8.5 21.5 2.5 20.5', 'M9.5 26 4.5 28.5', 'M30.5 17l5-4.5', 'M31.5 21.5l6-1', 'M30.5 26l5 2.5'))
    g += ''.join(f'<path d="{d}" stroke="{gill}" stroke-width="3" stroke-linecap="round"/>' for d in ('M9.5 17 4.5 12.5', 'M8.5 21.5 2.5 20.5', 'M9.5 26 4.5 28.5', 'M30.5 17l5-4.5', 'M31.5 21.5l6-1', 'M30.5 26l5 2.5'))
    head = f'<ellipse cx="20" cy="23.5" rx="13" ry="11.2" fill="{col}" stroke="#171320" stroke-width="2.3"/><ellipse cx="15" cy="17.6" rx="4.6" ry="2.2" fill="#fff" opacity=".42"/>'
    if kind == 'yay':
        fx = ('<ellipse cx="15.2" cy="22.6" rx="1.9" ry="2.4" fill="#171320"/><ellipse cx="24.8" cy="22.6" rx="1.9" ry="2.4" fill="#171320"/><circle cx="14.6" cy="21.8" r=".7" fill="#fff"/><circle cx="24.2" cy="21.8" r=".7" fill="#fff"/>'
              '<path d="M16.6 27.2q3.4 4.4 6.8 0z" fill="#5A0C1E" stroke="#171320" stroke-width="1.3" stroke-linejoin="round"/>')
    elif kind == 'happy':
        fx = ('<path d="M12.8 23.4q2.4-2.8 4.8 0M22.4 23.4q2.4-2.8 4.8 0" fill="none" stroke="#171320" stroke-width="2" stroke-linecap="round"/>'
              '<path d="M16.8 27.2q3.2 2.6 6.4 0" fill="none" stroke="#171320" stroke-width="1.8" stroke-linecap="round"/>')
    else:
        fx = ('<ellipse cx="15.2" cy="22.8" rx="1.8" ry="2.3" fill="#171320"/><ellipse cx="24.8" cy="22.8" rx="1.8" ry="2.3" fill="#171320"/><circle cx="14.6" cy="22" r=".7" fill="#fff"/><circle cx="24.2" cy="22" r=".7" fill="#fff"/>'
              '<path d="M17 27.4q3 2.2 6 0" fill="none" stroke="#171320" stroke-width="1.8" stroke-linecap="round"/>')
    blush = '<ellipse cx="11.4" cy="26.4" rx="2.2" ry="1.2" fill="#FF8FB1" opacity=".75"/><ellipse cx="28.6" cy="26.4" rx="2.2" ry="1.2" fill="#FF8FB1" opacity=".75"/>'
    return f'<svg viewBox="0 0 40 40"><g fill="none">{g}</g>{head}{blush}{fx}</svg>'
FACES = face('#FF6B7D', '#E3122F', 'yay') + face('#5BB6FF', '#2479D6', 'happy') + face('#B08BFF', '#7A4FE0', 'smile')
SHIELD = ('<svg viewBox="0 0 46 54"><defs><clipPath id="pbShClip"><path d="M23 2.6 43 8.6V29c0 11.4-9 18.6-20 22.6C12 47.6 3 40.4 3 29V8.6z"/></clipPath></defs>'
          '<path class="pbsh" d="M23 2.6 43 8.6V29c0 11.4-9 18.6-20 22.6C12 47.6 3 40.4 3 29V8.6z"/><rect width="46" height="20.5" fill="#F4EEE3" clip-path="url(#pbShClip)"/>'
          '<path d="M3 20.5h40" stroke="#171320" stroke-width="2.4"/><path d="M8.5 44 23 49.6 37.5 44" fill="none" stroke="rgba(0,0,0,.25)" stroke-width="3" clip-path="url(#pbShClip)"/>'
          '<path d="M23 2.6 43 8.6V29c0 11.4-9 18.6-20 22.6C12 47.6 3 40.4 3 29V8.6z" fill="none" stroke="#171320" stroke-width="3" stroke-linejoin="round"/>'
          '<path d="M8 11.4 23 7l15 4.4" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" opacity=".9"/></svg>')
STAR_D = 'M24.0 2.0 L30.4 8.5 L39.6 8.4 L39.5 17.6 L46.0 24.0 L39.5 30.4 L39.6 39.6 L30.4 39.5 L24.0 46.0 L17.6 39.5 L8.4 39.6 L8.5 30.4 L2.0 24.0 L8.5 17.6 L8.4 8.4 L17.6 8.5Z'
STAR = (f'<svg viewBox="0 0 48 48"><path d="{STAR_D}" fill="#171320" stroke="#171320" stroke-width="3" stroke-linejoin="round"/>'
        f'<path d="{STAR_D}" fill="#2A2437" stroke="#F2C14E" stroke-width="2.6" stroke-linejoin="round" transform="translate(24 24) scale(.86) translate(-24 -24)"/>'
        '<circle cx="24" cy="24" r="12.5" fill="none" stroke="rgba(242,193,78,.35)" stroke-width="1.5"/></svg>')
PLUS = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14M5 12h14" stroke="#171320" stroke-width="6.6" stroke-linecap="round"/><path d="M12 5v14M5 12h14" stroke="#fff" stroke-width="3.8" stroke-linecap="round"/></svg>'
GEAR = ('<svg viewBox="0 0 48 48"><path d="M27.5 4.5 29 10a15 15 0 0 1 4.4 2.5l5.5-1.6 3.5 6.1-4.1 4a15 15 0 0 1 0 5l4.1 4-3.5 6.1-5.5-1.6A15 15 0 0 1 29 38l-1.5 5.5h-7L19 38a15 15 0 0 1-4.4-2.5l-5.5 1.6-3.5-6.1 4.1-4a15 15 0 0 1 0-5l-4.1-4 3.5-6.1 5.5 1.6A15 15 0 0 1 19 10l1.5-5.5z" '
        'fill="#fff" stroke="#171320" stroke-width="3" stroke-linejoin="round"/><circle cx="24" cy="24" r="6.2" fill="#5B5580" stroke="#171320" stroke-width="3"/><path d="M14 16a12 12 0 0 1 8-5" fill="none" stroke="#C9C2E4" stroke-width="2.4" stroke-linecap="round"/></svg>')
SND_ON = ('<svg viewBox="0 0 48 48"><path d="M7 18h8l11-9v30l-11-9H7z" fill="#fff" stroke="#171320" stroke-width="3" stroke-linejoin="round"/>'
          '<path d="M32 17a9 9 0 0 1 0 14M36.5 12.5a15 15 0 0 1 0 23" fill="none" stroke="#171320" stroke-width="6.5" stroke-linecap="round"/>'
          '<path d="M32 17a9 9 0 0 1 0 14M36.5 12.5a15 15 0 0 1 0 23" fill="none" stroke="#46E07A" stroke-width="3.2" stroke-linecap="round"/></svg>')
SND_OFF = ('<svg viewBox="0 0 48 48"><path d="M7 18h8l11-9v30l-11-9H7z" fill="#fff" stroke="#171320" stroke-width="3" stroke-linejoin="round"/>'
           '<path d="M32 18l10 12M42 18 32 30" fill="none" stroke="#171320" stroke-width="7" stroke-linecap="round"/>'
           '<path d="M32 18l10 12M42 18 32 30" fill="none" stroke="#FF5A57" stroke-width="3.6" stroke-linecap="round"/></svg>')
BACK = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 4.5 7.5 12l7.5 7.5" fill="none" stroke="#fff" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'

# ---- the styles ----
rep(".comms{display:grid;gap:10px}", ".comms{display:grid;gap:10px}\n" + css)
rep(".ltop{grid-area:top;display:flex;align-items:center;gap:8px;padding-right:54px;", ".ltop{grid-area:top;display:flex;align-items:center;gap:8px;padding-right:0;")

# ---- the speech bubbles: never on the home screen ----
rep("function sayTick(rdt) { if (!(state === 'menu' && menuPage === 'home' && !lookOpen && $('orient').hidden) || onboarding()) { if (!heroSay.hidden) heroSay.hidden = true; sayT = Math.min(sayT, 1.2); return; } sayT -= rdt; if (sayT <= 0) sayRandom(); }",
    "function sayTick(rdt) { if (!heroSay.hidden) heroSay.hidden = true; } // (v208: the character keeps its thoughts to itself on the home screen)")
rep("menuReact = 0.7; AU.pop(); if (!onboarding()) sayRandom(); if (Math.random() < 0.6)", "menuReact = 0.7; AU.pop(); if (Math.random() < 0.6)")

# ---- the top bar: your dabs in place of the name box, the menu button in place of Settings ----
m = re.findall(r'\n        <button class="plate stat drops" id="dabsBtn"[^\n]*</button>', s); assert len(m) == 1; s = s.replace(m[0], '')
rep('<button class="swatch me nametag" id="nameBtn"',
    '<button class="dabs" id="dabsBtn" type="button" title="Dabs. Open the Paint Shop" aria-haspopup="dialog"><span class="dcoin" aria-hidden="true">' + COIN +
    '</span><span class="dtab"><span class="dsr">Dabs: </span><b id="statDrops">0</b><i class="dshop">Shop</i></span></button>\n        <button class="swatch me nametag" id="nameBtn"')
rep('<div class="ltools"><span class="tape exhib" id="seasonTag"><b>Season 1</b> Halloween</span>',
    '<div class="ltools"><span class="tape exhib" id="seasonTag"><b>Season 1</b> Halloween</span><button class="mbtn" id="hamBtn" type="button" aria-label="Menu" aria-expanded="false" aria-controls="sideMenu"><i></i><i></i><i></i></button>')
# ---- the right side: Friends in place of the stats ----
m = re.findall(r'\n        <div class="plate stat" title="Wins">[^\n]*</div>\n        <div class="plate stat" title="Best coverage">[^\n]*</div>', s); assert len(m) == 1
s = s.replace(m[0], '\n        <button class="friends" id="friendsBtn" type="button" aria-haspopup="dialog"><span class="ffaces" aria-hidden="true">' + FACES + '</span><b>Friends</b></button>')
# ---- the power bar, the spots beside you, the menu ----
rep('    <div class="lsay" id="heroSay" hidden><span id="heroSayTxt"></span></div>',
    '    <div class="lsay" id="heroSay" hidden><span id="heroSayTxt"></span></div>\n'
    '    <button class="pbar" id="pbar" type="button" hidden aria-haspopup="dialog"><span class="pbrank" aria-hidden="true">' + SHIELD + '<small>RANK</small><b id="pbLvl">1</b></span>'
    '<span class="pbtrack" aria-hidden="true"><canvas id="pbCanvas"></canvas><span class="pbname" id="pbName">Player</span><span class="pbxp" id="pbXp">0</span></span>'
    '<span class="pbnext" aria-hidden="true">' + STAR + '<small>NEXT</small><b id="pbNext">2</b></span></button>\n'
    '    <button class="slot" id="slotL" type="button" hidden aria-label="Bring a friend into your lobby (coming soon)">' + PLUS + '</button>'
    '<button class="slot" id="slotR" type="button" hidden aria-label="Bring a friend into your lobby (coming soon)">' + PLUS + '</button>\n'
    '    <aside class="smenu" id="sideMenu" hidden><i class="sscrim"></i><div class="spanel" role="dialog" aria-modal="true" aria-label="Menu">'
    '<button class="mbtn sx" id="smClose" type="button" aria-label="Close the menu" aria-expanded="true"><i></i><i></i><i></i></button>'
    '<button class="sitem" id="smSet" type="button" aria-haspopup="dialog"><span class="sic" aria-hidden="true">' + GEAR + '</span><span>Settings</span></button>'
    '<button class="sitem" id="smSnd" type="button" aria-pressed="true"><span class="sic" id="smSndI" aria-hidden="true">' + SND_ON + '</span><span id="smSndL">Sound on</span></button>'
    '</div></aside>')
# ---- the stats, friends and the pages of words ----
rep('  <div class="iris" id="iris" hidden aria-hidden="true">',
    '  <div class="modal" id="statsModal" hidden>\n    <div class="card" role="dialog" aria-modal="true" aria-labelledby="statsTitle">\n      <h2 class="ctitle" id="statsTitle">Stats</h2>\n'
    '      <div class="sthead"><b id="stName">Player</b><button id="stRename" type="button" aria-label="Change your name"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 20l1-4.6L15.6 4.8a2 2 0 0 1 2.8 0l.8.8a2 2 0 0 1 0 2.8L8.6 19 4 20z" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linejoin="round"/></svg></button></div>\n'
    '      <div class="strank"><span class="pbrank" aria-hidden="true">' + SHIELD.replace('pbShClip', 'stShClip') + '<small>RANK</small><b id="stLvl">1</b></span><span class="strt"><b id="stTitle">Unknown</b><small id="stXp"></small><span class="stbar"><i id="stFill"></i></span></span></div>\n'
    '      <div class="stgrid"><div><b id="stWins">0</b><small>Wins</small></div><div><b id="stPlayed">0</b><small>Matches</small></div><div><b id="stRate">0%</b><small>Win rate</small></div><div><b id="stBest">0%</b><small>Best coverage</small></div></div>\n'
    '      <button class="btn play sm" id="statsClose" type="button">Back to the studio</button>\n    </div>\n  </div>\n'
    '  <div class="modal" id="friendsModal" hidden>\n    <div class="card" role="dialog" aria-modal="true" aria-labelledby="friendsTitle">\n      <span class="ffaces" aria-hidden="true">' + FACES + '</span>\n'
    '      <h2 class="ctitle" id="friendsTitle">Friends</h2>\n      <p class="cnote">Coming soon. Bring your friends into your lobby, see their looks and paint against them.</p>\n'
    '      <button class="btn play sm" id="friendsClose" type="button">Got it</button>\n    </div>\n  </div>\n'
    '  <div class="modal" id="docModal" hidden>\n    <div class="card" role="dialog" aria-modal="true" aria-labelledby="docTitle">\n      <h2 class="ctitle" id="docTitle"></h2>\n      <div class="docb" id="docBody"></div>\n'
    '      <button class="btn play sm" id="docClose" type="button">Back</button>\n    </div>\n  </div>\n'
    '  <div class="iris" id="iris" hidden aria-hidden="true">')

# ---- Settings: the switches, the help, play with friends (soon), the terms, privacy and credits ----
a = s.index('      <div class="srows" id="srows">'); b = s.index('      <button class="btn play sm" id="setDone"', a)
old_rows = s[a:b]
om = re.search(r'<div class="seg duo" id="orientPick" role="group" aria-label="Screen">(.*?)</div>\n', old_rows); assert om
orient_btns = om.group(1)
def tog(id_, label, extra=''):
    return (f'<div class="seg duo tog{extra}" id="{id_}" role="group" aria-label="{label}"><button type="button" data-v="on" aria-pressed="true"><span>On</span></button>'
            f'<button type="button" data-v="off" aria-pressed="false"><span>Off</span></button></div>')
new_rows = ('      <button class="sback" id="setBack" type="button" aria-label="Back">' + BACK + '</button>\n'
            '      <div class="srows" id="srows">\n'
            '        <div class="sopt"><p class="slab">Sound effects</p>' + tog('sfxPick', 'Sound effects') + '</div>\n'
            '        <div class="sopt"><p class="slab">Music</p>' + tog('musPick', 'Music') + '</div>\n'
            '        <div class="sopt wide"><p class="slab">Screen</p><div class="seg duo tog pick" id="orientPick" role="group" aria-label="Screen">' + orient_btns + '</div></div>\n'
            '        <div class="sopt wide"><p class="slab">Visuals</p><div class="seg duo tog pick" id="gfxPick" role="group" aria-label="Visuals"><button type="button" data-g="hi" aria-pressed="false"><span>Graphics</span></button>'
            '<button type="button" data-g="perf" aria-pressed="false"><span>Performance</span></button></div><p class="gnote" id="gfxNote" aria-live="polite"></p></div>\n'
            '        <div class="sopt wide"><p class="slab">Help</p><div class="sbtns"><button class="sbtn" id="howOpen" type="button" aria-haspopup="dialog"><span>How to play</span></button>'
            '<button class="sbtn" id="tutReplay" type="button"><span>Replay tutorial</span></button></div><p class="gnote" id="lastErr"></p></div>\n'
            '        <div class="sopt wide soon"><p class="slab">Play with friends <i class="soontag">Coming soon</i></p><div class="sbtns"><button class="sbtn" type="button" disabled><span>Invite friends</span></button>'
            '<button class="sbtn" type="button" disabled><span>Link account</span></button></div></div>\n'
            '        <div class="sopt full"><div class="sbtns three"><button class="sbtn" id="tosBtn" type="button" aria-haspopup="dialog"><span>Terms of Service</span></button>'
            '<button class="sbtn" id="privBtn" type="button" aria-haspopup="dialog"><span>Privacy Policy</span></button><button class="sbtn" id="credBtn" type="button" aria-haspopup="dialog"><span>Credits</span></button></div></div>\n'
            '        <p class="sver" id="setVer"></p>\n'
            '      </div>\n')
s = s[:a] + new_rows + s[b:]
rep("for (const b of $('soundPick').children) b.setAttribute('aria-pressed', String((b.dataset.s === 'off') === !!store.muted)); ",
    "for (const b of $('sfxPick').children) b.setAttribute('aria-pressed', String((b.dataset.v === 'off') === !!store.sfxOff)); for (const b of $('musPick').children) b.setAttribute('aria-pressed', String((b.dataset.v === 'off') === !!store.musicOff)); { const v = document.querySelector('#howModal .ver'); $('setVer').textContent = v ? v.textContent : ''; } ")
rep("$('soundPick').addEventListener('click', e => { const t = e.target.closest('button'); if (!t || (t.dataset.s === 'off') === !!store.muted) return; toggleSound(); paintSettings(); });\n", "")
rep("function closeSettings() { if (setModal.hidden) return; setModal.hidden = true; $('setBtn').focus({ preventScroll: true }); }",
    "function closeSettings() { if (setModal.hidden) return; setModal.hidden = true; $('hamBtn').focus({ preventScroll: true }); }")

# ---- the sound: effects and music on their own switches (the master mute is both off) ----
rep("let ctx = null, out, sfx, mus, musWet,", "let ctx = null, out, sfx, musGate, mus, musWet,")
rep("    sfx = ctx.createGain(); sfx.gain.value = 0.95; sfx.connect(out);", "    sfx = ctx.createGain(); sfx.gain.value = store.sfxOff ? 0 : 0.95; sfx.connect(out);")
rep("musLP.Q.value = 0.8; musLP.connect(out);", "musLP.Q.value = 0.8; musGate = ctx.createGain(); musGate.gain.value = store.musicOff ? 0 : 1; musLP.connect(musGate); musGate.connect(out);")
rep("    verb = ctx.createGain(); const vhp", "    verb = ctx.createGain(); verb.gain.value = store.sfxOff ? 0 : 1; const vhp")
rep("    echo = ctx.createGain(); const dl", "    echo = ctx.createGain(); echo.gain.value = store.sfxOff ? 0 : 1; const dl")
rep("    muted(m) { if (ctx) out.gain.setTargetAtTime(m ? 0 : 1, T(), 0.04); },",
    "    muted(m) { if (ctx) out.gain.setTargetAtTime(m ? 0 : 1, T(), 0.04); },\n"
    "    // the music and the effects apart (the effects' reverb and echo sends with them)\n"
    "    mix(mOn, sOn) { if (!ctx) return; const t = T(); musGate.gain.setTargetAtTime(mOn ? 1 : 0, t, 0.05); sfx.gain.setTargetAtTime(sOn ? 0.95 : 0, t, 0.04); verb.gain.setTargetAtTime(sOn ? 1 : 0, t, 0.04); echo.gain.setTargetAtTime(sOn ? 1 : 0, t, 0.04); out.gain.setTargetAtTime(mOn || sOn ? 1 : 0, t, 0.04); },")
rep("function toggleSound() { store.muted = !store.muted; save(); AU.init(); AU.muted(store.muted); paintSoundBtn(); if (!store.muted) AU.ui(); }",
    "if (store.muted && store.sfxOff === undefined && store.musicOff === undefined) { store.sfxOff = true; store.musicOff = true; } // (a mute from before v208: both off)\n"
    "function toggleSound() { const off = !(store.sfxOff && store.musicOff); store.sfxOff = off; store.musicOff = off; store.muted = off; save(); AU.init(); AU.mix(!off, !off); paintSoundBtn(); if (!off) AU.ui(); }")
rep("function paintSoundBtn() { const b = $('soundBtn'); b.innerHTML = store.muted ? SOUND_OFF : SOUND_ON; b.setAttribute('aria-label', store.muted ? 'Turn sound on' : 'Turn sound off'); }",
    "function paintSoundBtn() { const off = !!store.sfxOff && !!store.musicOff, b = $('soundBtn'); b.innerHTML = off ? SOUND_OFF : SOUND_ON; b.setAttribute('aria-label', off ? 'Turn sound on' : 'Turn sound off'); }")

# ---- the home screen's own code, after Settings' ----
rep("$('setBtn').addEventListener('click', uiClick(openSettings));",
    "$('setBtn').addEventListener('click', uiClick(openSettings));\nconst SM_SND_ON = " + repr(SND_ON) + ", SM_SND_OFF = " + repr(SND_OFF) + ";\n" + js)
rep("  visuals(dt, rdt); flushTrail();\n", "  visuals(dt, rdt); flushTrail(); pbarTick(rdt);\n")
rep("  if (!heroSay.hidden) placeSay();\n", "  if (!heroSay.hidden) placeSay();\n  placePBar(); // (the power bar and the spots beside you, by the character)\n")
rep("  let wins = 0; for (const k in (store.wins || {})) wins += store.wins[k] || 0; $('statWins').textContent = wins; showDrops();\n  let best = 0; for (const k in (store.bestCov || {})) best = Math.max(best, store.bestCov[k] || 0); $('statBest').textContent = best + '%';\n",
    "  showDrops(); paintPBar();\n")
rep("function paintName() { const n = playerName(); NAMES[0] = n; $('nameShow').textContent = store.name ? n : 'Name';",
    "function paintName() { const n = playerName(); NAMES[0] = n; $('nameShow').textContent = store.name ? n : 'Name'; { const pn = $('pbName'); if (pn) pn.textContent = n; }")
# (the character's framed under the power bar)
rep("y0 = Math.max(top.bottom, lg.bottom || 0) - r.top, y1 = (bot.top || r.bottom) - r.top;",
    "y0 = Math.max(top.bottom, lg.bottom || 0) - r.top + 58, y1 = (bot.top || r.bottom) - r.top;")
# the keys: Escape closes what's open
rep("  if (!howModal.hidden) { if (k === 'Escape') { e.preventDefault(); closeHow(); } return; }",
    "  if (!howModal.hidden) { if (k === 'Escape') { e.preventDefault(); closeHow(); } return; }\n"
    "  if (!$('docModal').hidden) { if (k === 'Escape') { e.preventDefault(); closeDoc(); } return; }\n"
    "  if (!$('statsModal').hidden) { if (k === 'Escape') { e.preventDefault(); closeStats(); } return; }\n"
    "  if (!$('friendsModal').hidden) { if (k === 'Escape') { e.preventDefault(); closeFriends(); } return; }\n"
    "  if (!sideMenu.hidden) { if (k === 'Escape') { e.preventDefault(); closeSide(); } return; }")
# starting a match: the side menu shuts
rep("lobbyShadow.visible = false; heroSay.hidden = true; AI = AI_LV[diff];", "lobbyShadow.visible = false; heroSay.hidden = true; closeSide(true); AI = AI_LV[diff];")
open(DST, 'w').write(s)
print('ui136 ok', n0, '->', len(s))
