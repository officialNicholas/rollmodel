#!/usr/bin/env python3
"""v200: the first real match after the lesson is kinder and clearer. Your paint lasts longer (0.6 of the usual use, rolling and splats);
the orb comes up near you; the zombie eyes' gift box turns up a few steps ahead of you; the sun is taught in short steps and the rain in
one plain line (that half lives in tools/assets/tutorial.js and .css). After it, zombie eyes bought in the shop: Back goes to the locker
to put them on, not the lobby. The lesson’s rocket: the rival walks into your crosshair. A slingshot pro tip for players who hardly fling. The score screen’s song starts as the dabs fly up. And Ol’ Bloop has a voice: one of seven sounds, at random, each time he speaks."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui124_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
# your paint lasts longer in the first real match
rep("else D.paint -= cfg.drain * dt * (D.charging ? STILL_DRAIN : 1) * (D === P && easyOn() ? EASY_DRAIN : 1); }",
    "else D.paint -= cfg.drain * dt * (D.charging ? STILL_DRAIN : 1) * (D === P && easyOn() ? EASY_DRAIN : 1) * (D === P && tut2 ? 0.6 : 1); } /* (the first real match after the lesson: your paint lasts longer) */")
rep("if (cost > 0.005) { if (D.giantT <= 0) D.paint -= cost;", "if (cost > 0.005) { if (D.giantT <= 0) D.paint -= cost * (D === P && tut2 ? 0.6 : 1);")
# the orb comes up near you in it
rep("  for (let tries = 0; tries < 40 && !c; tries++) { const q = COF_SPOTS",
    "  if (tut2 && (P.st === 'play' || P.st === 'hide')) { let bd = 1e9; for (const q of COF_SPOTS) { if (!q || Math.max(Math.abs(q[0]), Math.abs(q[2])) >= ARENA - 4) continue; const d = Math.hypot(P.x - q[0], P.z - q[2]); if (d < 5 || ACTIVE.some(D => D !== P && D.st !== 'ko' && Math.hypot(D.x - q[0], D.z - q[2]) < 6)) continue; if (d < bd) { bd = d; c = q; } } } /* (the first real match: the orb comes up near you) */\n  for (let tries = 0; tries < 40 && !c; tries++) { const q = COF_SPOTS")
# and its gift box a few steps ahead of you
rep("if (!gift.on) { if (runT < gift.at || matchLeft < 6) return; const s = giftSpot();", "if (!gift.on) { if (runT < gift.at || matchLeft < 6) return; const s = (tut2 && tutNearSpot(6, 11)) || giftSpot();")
# the zombie eyes bought after it: Back takes you to the locker to put them on
rep("  if (state !== 'menu' || building || shopOpen) return; shopOpen = true; shopFrom", "  if (state !== 'menu' || building || shopOpen) return; shopOpen = true; shopBought.clear(); shopFrom")
rep("function openShop(from) {", "const shopBought = new Set(); // (what this visit to the shop bought)\nfunction openShop(from) {")
rep("  AU.power(); b.classList.add('got'); b.classList.remove('fresh');", "  shopBought.add(w.id); AU.power(); b.classList.add('got'); b.classList.remove('fresh');")
rep("$('shopBack').addEventListener('click', () => { AU.init(); AU.ui(); closeShop(); });",
    "$('shopBack').addEventListener('click', () => { AU.init(); AU.ui(); if (!lookOpen && shopBought.has('zombie') && store.zombieDeal && myLook.eyes !== 'zombie') { closeShop(true); lookCat = 'eyes'; openLook(); return; } closeShop(); }); // (the zombie eyes just bought after the first real match: Back goes to the locker to put them on)")
# Ol' Bloop's voice: one of the seven sounds cut from the user's take (la/sfx/bloop_N.mp3, in the sheets), never the same twice running
rep("    plop() { hiss({ k: 'p', type: 'lowpass', f: 1300, f1: 300, dur: 0.12, v: 0.16 }); tone({ f: 330 + Math.random() * 120, f1: 160, glide: 0.07, dur: 0.08, v: 0.07 }); },",
    "    plop() { hiss({ k: 'p', type: 'lowpass', f: 1300, f1: 300, dur: 0.12, v: 0.16 }); tone({ f: 330 + Math.random() * 120, f1: 160, glide: 0.07, dur: 0.08, v: 0.07 }); },\n    bloop() { fx.plop(); }, /* (Ol' Bloop talking, before the sound sheets have loaded: the plop) */")
rep("    plop() { return P_('plop'); },", "    plop() { return P_('plop'); },\n    bloop(d) { return P_('bloop', { vary: 0.02, d: d || 0 }); }, /* (Ol' Bloop talking: one of his sounds, never the same twice running) */")
# the score screen's music: the win or lose song starts as the dabs fly up to your bar (the winner screen carries on with it)
rep("  if (t >= tal.DAB1 && tal.phase === 4) { tal.phase = 5; talDabsFly(); }", "  if (t >= tal.DAB1 && tal.phase === 4) { tal.phase = 5; talDabsFly(); { const info = endInfo, won = info.mode === 'solo' ? info.newBest : info.winner === P; AU.music(won ? 'win' : 'lost'); } } /* (the song starts as the dabs fly up to your bar) */")
rep('<p class="ver">Version 199</p>', '<p class="ver">Version 200</p>')
open(DST, 'w').write(s)
print('ui125 ok', n0, '->', len(s))
