#!/usr/bin/env python3
"""v263 intro: the hand-over hit, voiced on whichever chord the intro has reached. The old sting was one E major hit; the menu song now
carries on from the very bar the intro is on (bar 9 + the loop's bar), so the hit takes that bar's chord instead. One sprite,
music/intro_sting.mp3:
  imp  0.00 s: the riser (one bar), then on the hit a sub boom, a tom, a kick and a crash (no pitch, fits any bar); the hit at BAR
  dm, am, bb, e, f: the pitched part for each chord: a little run up into it, the orchestra on the chord and a celesta glissando up it;
       each segment starts LEAD seconds before the hit
The E segment with the impact is the old sting to the sample (the same notes, times and levels; one gain for every part).
Usage: intro_hit.py <one-shots dir (riser.mp3)> <out dir>"""
import os, sys, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import intro_score as I
SR, BAR = I.SR, I.BAR
LEAD, TAIL, GAP = 0.6, 4.2, 0.15  # (a pitched segment: LEAD before the hit, TAIL after it; GAP of silence between segments)
CHORDS = [('dm', 2, True), ('am', 9, True), ('bb', 10, False), ('e', 4, False), ('f', 5, False)]
def put(B, t, x, pan=0.0, g=1.0):  # (the score's own placing, bounded by this buffer rather than the score's)
    i = int(round(t * SR)); x = np.asarray(x, np.float32)
    if x.ndim == 1: a = np.cos((pan + 1) * np.pi / 4); b = np.sin((pan + 1) * np.pi / 4); x = np.stack([x * a * 1.414, x * b * 1.414], 1)
    n = min(len(x), len(B) - i)
    if n > 0 and i >= 0: B[i:i + n] += x[:n] * g
def impact(riser):
    n = int((BAR + TAIL + 3.4) * SR); X = np.zeros((n, 2), np.float32); R = BAR
    rs = riser[-int(R * SR):].copy(); rs *= np.linspace(0.2, 1, len(rs))[:, None] ** 1.5; X[:len(rs)] += rs * 0.28
    t = np.arange(int(3 * SR)) / SR; f = 34 + 40 * np.exp(-t / 0.25); boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.9); put(X, R, boom.astype(np.float32), 0, 0.9)
    put(X, R, I.tom(40) * 1.2, 0, 0.7); put(X, R, I.kick_syn(), 0, 0.8)
    I.rng = np.random.default_rng(257); crash = I.fft_filter(I.noise(int(3 * SR)), lo=3500) * np.exp(-np.arange(int(3 * SR)) / SR / 0.9); put(X, R, np.stack([crash, np.roll(crash, 300)], 1), g=0.22)
    return I.reverb(X, 3.4, 0.38)
def pitched(pc, minor, origin):
    """the pitched part of the hit on the chord with root pitch class pc; the hit at `origin` seconds into the buffer"""
    th = 3 if minor else 4; n = int((origin + TAIL + 3.4) * SR); X = np.zeros((n, 2), np.float32); R = origin
    top = 60 + ((pc - 60) % 12)  # (the run lands on the root near E4, as the E hit's did)
    for k, m in enumerate([top - 12, top - 9, top - 5, top - 2, top]): put(X, R - 0.5 + k * 0.1, I.celesta(m + 12, 0.6), -0.3 + k * 0.15, 0.12)
    r2 = 36 + ((pc - 36) % 12)
    for j, m in enumerate([r2, r2 + 7, r2 + 12, r2 + 12 + th, r2 + 19, r2 + 24, r2 + 24 + th, r2 + 31]):
        e = I.env_adsr(int(3.2 * SR), 0.012, 0.9, 0.25, 1.6, 1.4)
        x = I.additive(I.mf(m), 1.4, lambda k, fk, tt: (1 / k) * I.lp(900 + 4000 * np.exp(-tt / 0.35), fk, 2), 1.8, det=(-7, 0, 6), kmax=40) * e
        put(X, R, x, (j - 3.5) * 0.12, 0.09)
    c = 72 + ((pc - 72) % 12)
    for k, m in enumerate([c, c + th, c + 7, c + 12, c + 12 + th, c + 19, c + 24]): put(X, R + 0.04 + k * 0.07, I.celesta(m, 0.8), -0.3 + k * 0.1, 0.16)
    return I.reverb(X, 3.4, 0.38)
def fade_cut(x, dur):
    n = int(dur * SR); y = x[:n].copy(); f = int(0.5 * SR); y[-f:] *= np.linspace(1, 0, f)[:, None]; return y
if __name__ == '__main__':
    OS, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
    riser = I.load(os.path.join(OS, 'riser.mp3'), SR, 2); riser = riser / np.abs(riser).max()
    imp = impact(riser); P = {k: pitched(pc, mn, BAR) for k, pc, mn in CHORDS}
    n = min(len(imp), len(P['e'])); full_e = imp[:n] + P['e'][:n]; G = 0.92 / np.abs(full_e).max()  # (the old sting's own gain: impact and E together)
    segs = [('imp', fade_cut(imp, BAR + TAIL))] + [(k, fade_cut(P[k][int((BAR - LEAD) * SR):], LEAD + TAIL)) for k, _, _ in CHORDS]
    T, pos, parts = [], 0.0, []
    for k, s in segs:
        parts.append(s * G); T.append((k, round(pos, 5), round(len(s) / SR, 5))); pos += len(s) / SR
        parts.append(np.zeros((int(GAP * SR), 2), np.float32)); pos += GAP
    sprite = np.concatenate(parts); sprite = np.tanh(sprite * 1.02) / 1.02
    I.enc(sprite, os.path.join(out, 'intro_sting.mp3'), '96k')
    print('sprite', round(len(sprite) / SR, 3), 's; hit at BAR', round(BAR, 5), 'in imp, LEAD', LEAD, 'in each pitched segment')
    print('HIT = {' + ', '.join(f"{k}: [{p}, {d}]" for k, p, d in T) + '}')
