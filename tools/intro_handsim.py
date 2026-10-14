"""Simulate the v263 hand-over as the game schedules it: the five stems at full layer from t0, the hit on bar line e, the sprite's impact
and pitched parts, the stems let go on the hit, the menu song from MENU_AT + (1 + e) bars. Writes a demo per e and checks the beat
across the seam (onsets in the 4 bars after the hit against the intro's grid continued)."""
import sys, numpy as np, subprocess, soundfile as sf
sys.path.insert(0, '/home/user/rollmodel/tools')
from intro_audio_an import load
SR = 44100; BEAT = 60 / 110.89; BAR = 4 * BEAT; A = 0.25; MENU_AT = 17.627; LV = 0.21; LEAD = 0.6
G = '/home/user/rollmodel/game/music/'
stems = {k: load(G + 'intro_' + k + '.mp3', SR, 2) for k in ['air', 'keys', 'low', 'tops', 'drive']}
lay = {'air': 0.55, 'keys': 1, 'low': 1, 'tops': 1, 'drive': 1}
menu = load(G + 'menu.mp3', SR, 2); spr = load(G + 'intro_sting.mp3', SR, 2)
HIT = {'imp': [0.0, 6.36429], 'dm': [6.51429, 4.8], 'am': [11.46429, 4.8], 'bb': [16.41429, 4.8], 'e': [21.36429, 4.8], 'f': [26.31429, 4.8]}
CHORD = ['dm', 'am', 'bb', 'e', 'dm', 'am', 'f', 'e']
MK = 0.923 * 0.26  # (the menu track's level: R.k * TRK_LVL.menu)
def onset(x, n=512, h=64):
    x = x.mean(1); w = np.hanning(n); fr = 1 + (len(x) - n) // h; idx = np.arange(n)[None, :] + h * np.arange(fr)[:, None]
    M = np.abs(np.fft.rfft(x[idx] * w, axis=1)); L = np.log1p(100 * M); fl = np.maximum(0, np.diff(L, axis=0)).sum(1)
    return fl - np.convolve(fl, np.ones(64) / 64, 'same'), h / SR
def sim(e, pre_bars=4):
    hb = 8 + e  # (the hit is on loop bar e of the second time round)
    hit = hb * BAR; dur = hit + 6 * BAR; n = int(dur * SR); out = np.zeros((n, 2), np.float32); t = np.arange(n) / SR
    L = BAR * 8
    for k, x in stems.items():  # the loop from t0 = 0: file position A + (t mod L)
        pos = A + (t % L); idx = np.clip((pos * SR).astype(int), 0, len(x) - 1); y = x[idx] * (lay[k] * LV)
        env = np.where(t < hit - 0.01, 1.0, np.exp(-(t - (hit - 0.01)) / 0.04)); out += y * env[:, None]
    def part(k, at):
        s0, d = HIT[k]; seg = spr[int(s0 * SR):int((s0 + d) * SR)] * (LV * 1.2); i = int(at * SR); m = min(len(seg), n - i); out[i:i + m] += seg[:m]
    part('imp', hit - BAR); part(CHORD[e], hit - LEAD)
    off = MENU_AT + (1 + e) * BAR; i = int(hit * SR); seg = menu[int(off * SR):int(off * SR) + n - i] * MK; out[i:i + len(seg)] += seg
    return out, hit, off
res = []
for e in range(8):
    out, hit, off = sim(e)
    # beat check: onsets after the hit (the menu song) folded on the intro's grid (t0 = 0)
    o, h = onset(out); tt = np.arange(len(o)) * h + 256 / SR
    sel = (tt > hit + 0.3) & (tt < hit + 4 * BAR); ph = (tt[sel] / BEAT) % 1; bins = np.zeros(80); np.add.at(bins, (ph * 80).astype(int) % 80, np.maximum(o[sel], 0))
    sel2 = (tt > hit - 4 * BAR) & (tt < hit - BAR - 0.1); ph2 = (tt[sel2] / BEAT) % 1; b2 = np.zeros(80); np.add.at(b2, (ph2 * 80).astype(int) % 80, np.maximum(o[sel2], 0))
    d = ((np.argmax(bins) - np.argmax(b2) + 40) % 80 - 40) * BEAT / 80 * 1000
    res.append((e, CHORD[e], round(off, 3), round(d, 1)))
    if e in (2, 5): sf.write(f'/tmp/hand_e{e}.wav', np.tanh(out[int((hit - 5 * BAR) * SR):] * 1.2) / 1.2, SR)
for r in res: print('bar', r[0], 'chord', r[1], 'menu offset', r[2], 's; beat after the hit vs before:', r[3], 'ms')
# a sturdier beat check: the menu after the hit against the intro's drums continued over the same time (where they would have been)
print('cross-correlation (menu after the hit vs the intro drums continued):')
L = 8 * BAR; dr = stems['drive']
for e in range(8):
    out, hit, off = sim(e); n = len(out); t = np.arange(n) / SR
    cont = dr[np.clip(((A + (t % L)) * SR).astype(int), 0, len(dr) - 1)]
    a0, a1 = int((hit + 0.5) * SR), int((hit + 4 * BAR) * SR)
    oa, h = onset(out[a0:a1]); ob, _ = onset(cont[a0 - int(0.2 * SR):a1 + int(0.2 * SR)])
    best = None
    for lag in range(-60, 61):  # in hops of 64 samples (1.45 ms), +-87 ms
        s0 = int(0.2 * SR / 64) + lag; b = ob[s0:s0 + len(oa)]; m = min(len(b), len(oa)); v = float(np.dot(oa[:m] - oa[:m].mean(), b[:m] - b[:m].mean()))
        if best is None or v > best[1]: best = (lag * 64 / SR * 1000, v)
    print('  bar', e, CHORD[e], 'lag', round(best[0], 1), 'ms')
