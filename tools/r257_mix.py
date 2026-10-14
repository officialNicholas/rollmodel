#!/usr/bin/env python3
"""v257 intro video: the frames from r257_intro.py, with the intro's music laid in as the game plays it (each layer on the beat after
its stage begins; v263's hand-over: the hit on a bar line of the loop, the riser and impact a bar before it and the hit voiced on that
bar's chord, the stems let go on the hit and the menu song carrying on from that very bar, MENU_AT + (1 + e) bars in) and the intro's
own effects.
Usage: r257_mix.py <frames dir> <out.mp4>"""
import json, os, subprocess, sys, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from intro_audio_an import load
SR = 44100; BEAT = 60 / 110.89; BAR = 4 * BEAT; LOOP = (0.25, 17.56444); LV = 0.21; MENU_AT = 17.627
# (v257_intro_au.js: the sting sprite's parts, which chord each of the loop's bars is on, how far ahead of its hit a chord's part starts)
HIT = {'imp': (0.0, 6.36429), 'dm': (6.51429, 4.8), 'am': (11.46429, 4.8), 'bb': (16.41429, 4.8), 'e': (21.36429, 4.8), 'f': (26.31429, 4.8)}; CHORD = ['dm', 'am', 'bb', 'e', 'dm', 'am', 'f', 'e']; HIT_LEAD = 0.6
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); M = os.path.join(ROOT, 'game', 'music')
FX = {'wobble': (0, 0.524), 'tip': (0.824, 0.55), 'pour': (1.673, 3.919), 'eyes': (5.893, 0.393), 'form': (6.585, 1.255), 'sparkle': (8.14, 0.8), 'tumble': (9.24, 2.326)}
d, out = sys.argv[1], sys.argv[2]; L = json.load(open(os.path.join(d, 'log.json'))); fps = L['fps']; log = L['log']
nfr = len([f for f in os.listdir(d) if f.endswith('.jpg')]); dur = nfr / fps; N = int(dur * SR)
ph = {e['ph']: e['t'] for e in log if 'ph' in e}; act = {e['act']: e['t'] for e in log if 'act' in e}
wink = ph['wink']; hit_in = next((e['hit'] for e in log if e.get('ph') == 'wink'), 2.4) or 2.4; hit = wink + hit_in
t0 = hit - int((hit - ph['sky']) / BAR) * BAR  # (the loop's clock, so the hit lands on one of its bar lines; it starts with the sky)
eb = int(round((hit - t0) / BAR)) % 8  # (which of the loop's bars the hit is on)
nb = lambda t: t0 + np.ceil((t - t0) / BEAT) * BEAT
lay_at = [t0, nb(ph['iris']), nb(ph['style']), nb(ph['paint']), nb(ph['name'])]
LAY = [[1, 0, 0, 0, 0], [0.9, 1, 0, 0, 0], [0.8, 1, 1, 0, 0], [0.7, 1, 1, 1, 0], [0.55, 1, 1, 1, 1]]
mix = np.zeros((N, 2), np.float32); t = np.arange(N) / SR
for si, k in enumerate(['air', 'keys', 'low', 'tops', 'drive']):
    x = load(os.path.join(M, f'intro_{k}.mp3'), SR, 2); a, b = int(LOOP[0] * SR), int(LOOP[1] * SR); ln = b - a
    i0 = int(t0 * SR); n = int(hit * SR) - i0; idx = a + (np.arange(n) % ln); seg = x[idx]
    # its level over time: each layer's target from its beat on, eased in (the engine's setTargetAtTime, tau a third of a beat)
    g = np.zeros(n, np.float32); cur = 0.0; tt = t[i0:i0 + n]
    targets = [(lay_at[j], LAY[j][si]) for j in range(5)]
    for j, (ta, v) in enumerate(targets):
        tb = targets[j + 1][0] if j + 1 < 5 else 1e9; m = (tt >= ta) & (tt < tb)
        if not m.any(): continue
        tau = 2.4 / 3 if (si == 0 and j == 0) else BEAT * 0.35; dt_ = tt[m] - ta; g[m] = v + (cur - v) * np.exp(-dt_ / tau); cur = float(g[m][-1])
    sw = tt >= hit - BAR; g[sw] *= 1 + 0.08 * (1 - np.exp(-(tt[sw] - (hit - BAR)) / BEAT))  # (the swell over the last bar)
    tail = int(0.04 * SR); g[-tail:] *= np.linspace(1, 0, tail)
    mix[i0:i0 + n] += seg * g[:, None] * LV
st = load(os.path.join(M, 'intro_sting.mp3'), SR, 2)
def part(k, at):
    s0, d = HIT[k]; x = st[int(s0 * SR):int((s0 + d) * SR)] * LV * 1.2; i = int(at * SR); n = min(len(x), N - i)
    if n > 0: mix[i:i + n] += x[:n]
part('imp', hit - BAR); part(CHORD[eb], hit - HIT_LEAD)
mn = load(os.path.join(M, 'menu.mp3'), SR, 2); m0 = int(hit * SR); o = int((MENU_AT + (1 + eb) * BAR) * SR); n = min(N - m0, len(mn) - o)
if n > 0: seg = mn[o:o + n] * 0.923 * 0.26; f = min(n, int(1.5 * SR)); seg[-f:] *= np.linspace(1, 0, f)[:, None]; mix[m0:m0 + n] += seg
fx = load(os.path.join(ROOT, 'game', 'sfx', 'intro_fx.mp3'), SR, 2)
def sfx(k, at, v=1.0):
    s, l = FX[k]; x = fx[int(s * SR):int((s + l) * SR)] * v * 0.5; i = int(at * SR); n = min(len(x), N - i)
    if n > 0 and i >= 0: mix[i:i + n] += x[:n]
BAR0 = 1.05  # (v257_intro.js: the drum's thumps before it rocks)
for at, v in [(0.12, 0.7), (0.62, 1.0)]: sfx('tip', ph['barrel'] + at, 0.3 * v)
b = ph['barrel'] + BAR0
for at, v in [(0.5, 0.75), (1.12, 0.85), (1.74, 1.0)]: sfx('wobble', b + at, v)
for e in log:
    if e.get('act') == 'tumble': sfx('tumble', e['t'], 0.375)
sfx('tip', b + 3.1); sfx('pour', b + 3.22, 0.9); sfx('eyes', b + 6.2); sfx('form', ph['form']); sfx('sparkle', wink + 0.2, 0.225)
mix = np.tanh(mix * 2.2) / 2.2; mix *= 0.89 / max(1e-6, np.abs(mix).max())
import soundfile as sf; wav = out + '.wav'; sf.write(wav, mix, SR)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', str(fps), '-i', os.path.join(d, 'f%05d.jpg'), '-i', wav, '-c:v', 'libx264', '-preset', 'slow', '-crf', '27', '-pix_fmt', 'yuv420p',
                '-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2', '-c:a', 'aac', '-b:a', '128k', '-shortest', '-movflags', '+faststart', out], check=True)
os.remove(wav); print(out, os.path.getsize(out), 'bytes;', round(dur, 1), 's; music clock', round(t0, 2), 'hit', round(hit, 2), 'on loop bar', eb, CHORD[eb], 'layers at', [round(x, 2) for x in lay_at])
