#!/usr/bin/env python3
"""v210: the sly eyes, a fifth eye style (in the axolotl's face shader, made by tools/mk_axo_embed.py): heavy lids in eyeshadow pink with a
thick lash line flicking out into a wing, a soft shadow above, arched brows, a pale ringed iris with a small pupil under the lid. In the
locker's eye styles and the Paint Shop (in stock, 640 dabs); CPUs wear them now and then."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui137_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
SLY_ICON = ('<ellipse cx="21" cy="15.5" rx="15.5" ry="7.5" fill="#F2A6B8" opacity=".6"/>'
            '<path d="M4.5 22.5c5-6 12-8.4 18.4-7.4 5.2.8 10 3 13.6 6.4-4 6-9.4 9.2-16.4 9.2S9 28 4.5 22.5z" fill="#fff" stroke="#171320" stroke-width="2.2" stroke-linejoin="round"/>'
            '<circle cx="20.5" cy="23.5" r="6.3" fill="#D9D6E2" stroke="#4A2A33" stroke-width="1.4"/><circle cx="20.5" cy="23.5" r="2.2" fill="#7A3B3B"/><circle cx="18.6" cy="21.8" r="1.1" fill="#fff"/>'
            '<path d="M4.5 22.5c5-6 12-8.4 18.4-7.4 5.2.8 10 3 13.6 6.4l-.6 1.4c-6.6-2.2-15-2.8-23.6-.6-3 .8-5.6 1-7.8.2z" fill="#C9808E"/>'
            '<path d="M6.5 22.4c8-2.4 18-2.6 29.4.2" fill="none" stroke="#171320" stroke-width="2.8" stroke-linecap="round"/><path d="M33.5 22l5.4-4.6" stroke="#171320" stroke-width="2.6" stroke-linecap="round"/>'
            '<path d="M8 11.5c6-4 14-5.6 20-4.4l6.5 2.6" fill="none" stroke="#8E4552" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/>')
# the style in the game's lists (the face shader takes it as 4); the slime, if it ever stands in, keeps its zombie eyes to style 3 only
rep("const EYE_STYLES = { round: 'Round', edgy: 'Squid', dot: 'Dot', zombie: 'Zombie' }, EYE_STYLE_K = { round: 0, edgy: 1, dot: 2, zombie: 3 };",
    "const EYE_STYLES = { round: 'Round', edgy: 'Squid', dot: 'Dot', sly: 'Sly', zombie: 'Zombie' }, EYE_STYLE_K = { round: 0, edgy: 1, dot: 2, zombie: 3, sly: 4 };")
rep("  float sqd = (fStyle > 0.5 && fStyle < 1.5) ? 1.0 : 0.0, zmb = fStyle > 2.5 ? 1.0 : 0.0;", "  float sqd = (fStyle > 0.5 && fStyle < 1.5) ? 1.0 : 0.0, zmb = (fStyle > 2.5 && fStyle < 3.5) ? 1.0 : 0.0;")
rep("const EXTRA = [{ id: 'zombie', name: 'Zombie eyes', slot: 'eyes', cat: 'eyes', season: 1, stage: 'halloween' }]",
    "const EXTRA = [{ id: 'zombie', name: 'Zombie eyes', slot: 'eyes', cat: 'eyes', season: 1, stage: 'halloween' }, { id: 'sly', name: 'Sly eyes', slot: 'eyes', cat: 'eyes' }]")
rep("const PRICES = { flower: 170,", "const PRICES = { sly: 640, flower: 170,")
rep("const WEAR_ICON = {\n", "const WEAR_ICON = {\n  sly: '" + SLY_ICON + "',\n")
rep("ES_ICON_T.zombie = '<svg viewBox=\"0 0 40 40\">' + WEAR_ICON.zombie + '</svg>';", "ES_ICON_T.zombie = '<svg viewBox=\"0 0 40 40\">' + WEAR_ICON.zombie + '</svg>'; ES_ICON_T.sly = '<svg viewBox=\"0 0 40 40\">' + WEAR_ICON.sly + '</svg>';")
rep("eyes: ['round', 'round', 'edgy', 'dot'][(Math.random() * 4) | 0]", "eyes: ['round', 'round', 'edgy', 'dot', 'sly'][(Math.random() * 5) | 0]")
rep('<p class="ver">Version 209</p>', '<p class="ver">Version 210</p>')
open(DST, 'w').write(s)
print('ui138 ok', n0, '->', len(s))
