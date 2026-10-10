#!/usr/bin/env python3
"""The tally's names and numbers each keep their own column (left, middle, right), so in a duel, with the middle one hidden, the rival's score sits at the right edge instead of sliding into the middle. On top of ui99_patch."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui99_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep("blobContact(); updateOrb(dt); updateShots(dt); if (tut) tutStep(dt);", "blobContact(); updateOrb(dt); updateShots(dt); if (tut) tutStep(dt); else if (tut2) tut2Step(dt);")
# the weather's own banners stay quiet while the coach explains it
s_wx0 = s.index('function updateWeather(dt) {'); s_wx1 = s.index('\nfunction stepBlob', s_wx0)
wx = s[s_wx0:s_wx1]; assert wx.count('banner(') == 4, wx.count('banner(')
s = s[:s_wx0] + wx.replace('banner(', 'wxBanner(') + s[s_wx1:]
rep("function hint(id, text, dur) { if (tut ||", "function hint(id, text, dur) { if (tut || (tut2 && tutTip) ||")
rep("function setWx(ph, dur) { wxPhase = ph; wxLeft = dur; }", "function setWx(ph, dur) { wxPhase = ph; wxLeft = dur; }\nconst wxBanner = (...a) => { if (!tut2) banner(...a); };")
# the zombie eyes, found in the first real match: always priced under what you have
rep("if (t && t[w.id] >= 0) return t[w.id];", "if (t && t[w.id] >= 0) return t[w.id]; if (w.id === 'zombie' && store.zombieDeal && !BOUGHT.has('zombie')) return Math.max(1, Math.floor((store.drops || 0) * 0.7)); /* (the first find of the season: always within reach) */")
# commissions refresh every day
rep("function commState() { if (!store.comm || !store.comm.active) store.comm = { active: [], prog: {}, done: [] }; const c = store.comm;", "function commState() { if (!store.comm || !store.comm.active) store.comm = { active: [], prog: {}, done: [] }; const c = store.comm; { const day = new Date().toDateString(); if (c.day !== day) { if (c.day) { c.active = []; c.prog = {}; c.done = []; store.commSeen = 0; } c.day = day; save(); } } /* (a fresh set every day) */")
rep(".tyname.r,.tynum.r{text-align:right;justify-self:end}", ".tyname.r,.tynum.r{text-align:right;justify-self:end}\n.tyname.l,.tynum.l{grid-column:1}.tyname.m,.tynum.m{grid-column:2}.tyname.r,.tynum.r{grid-column:3} /* (fixed columns: a hidden middle does not pull the right one in) */")
open(DST, 'w').write(s)
subprocess.run(['python3', '-I', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
print('ui100 ok', n0, '->', len(s))
