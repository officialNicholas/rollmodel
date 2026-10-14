#!/usr/bin/env python3
"""v257 intro: the first launch's adaptive music, composed on the Roll Model theme (its key, tempo, chords and main melody) and
rendered here, so the intro grows into the theme without playing the theme itself.

The theme (music/menu.mp3) is in A minor at 110.89 a minute. Its main melody, taken off the theme by ear-free pitch tracking (see
docs/intro-v257.md), runs over eight bars of Dm Am Bb E Dm Am F E. This writes five stems of one 8-bar loop on that grid, each stage of
the intro bringing in the next:
  intro_air   the barrel and the eyes: a dark shimmer, a low A drone, a clock ticking, and the melody's first notes on a music box
  intro_keys  eye colour: warm pads on the chords and the whole melody on celesta
  intro_low   eye style: a bouncing bass and harp arpeggios
  intro_tops  paint colour: shaker and hats
  intro_drive naming: drums, a tom fill, and the melody on strings an octave down
and intro_sting: a riser (one bar) into a big E major hit, the dominant that the theme's A minor resolves.
Each loop is rendered three times over (the same to the sample each time) and the middle pass kept, so reverb and ringing notes from the end carry over its start and the loop is
seamless. Usage: intro_score.py <one-shots dir (kick, shaker, riser, atmos .mp3 from Ludo.ai)> <out dir>"""
import os, sys, subprocess, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from intro_audio_an import load
SR = 44100; BPM = 110.89; BEAT = 60 / BPM; BAR = 4 * BEAT; BARS = 8; L = BARS * BAR
LS = round(L * SR) / SR  # (the loop in whole samples, so every pass lands on the same samples)
rng = np.random.default_rng(257)
mf = lambda m: 440.0 * 2 ** ((m - 69) / 12)
N = int((3 * L + 4) * SR)
def buf(): return np.zeros((N, 2), np.float32)
def put(B, t, x, pan=0.0, g=1.0):
    i = int(round(t * SR)); x = np.asarray(x, np.float32)
    if x.ndim == 1: a = np.cos((pan + 1) * np.pi / 4); b = np.sin((pan + 1) * np.pi / 4); x = np.stack([x * a * 1.414, x * b * 1.414], 1)
    n = min(len(x), N - i)
    if n > 0 and i >= 0: B[i:i + n] += x[:n] * g
def env_adsr(n, a, d, s, r, hold):
    t = np.arange(n) / SR; e = np.where(t < a, t / max(a, 1e-4), s + (1 - s) * np.exp(-(t - a) / max(d, 1e-4)))
    rel = np.clip((t - hold) / max(r, 1e-4), 0, 1); return (e * (1 - rel) ** 2).astype(np.float32)
def additive(f, dur, amp_k, tail=0.0, vib=None, det=(0.0,), kmax=60, floor=2e-3):
    n = int((dur + tail) * SR); t = np.arange(n) / SR; out = np.zeros(n, np.float32)
    ph_mod = np.zeros(n) if vib is None else vib(t)
    for dc in det:
        f0 = f * 2 ** (dc / 1200); ph0 = rng.uniform(0, 6.283)
        for k in range(1, kmax + 1):
            fk = f0 * k
            if fk > 16000: break
            a = amp_k(k, fk, t)
            if np.isscalar(a) and a < floor: continue
            out += (a * np.sin(2 * np.pi * fk * t + k * ph_mod + ph0 * k)).astype(np.float32)
    return out / len(det)
def lp(fc, fk, o=2): return 1 / np.sqrt(1 + (fk / fc) ** (2 * o))
def fft_filter(x, lo=None, hi=None):
    X = np.fft.rfft(x, axis=0); f = np.fft.rfftfreq(len(x), 1 / SR); g = np.ones_like(f)
    if lo: g *= 1 / np.sqrt(1 + (lo / np.maximum(f, 1)) ** 4)
    if hi: g *= 1 / np.sqrt(1 + (f / hi) ** 4)
    return np.fft.irfft(X * (g[:, None] if x.ndim > 1 else g), n=len(x), axis=0).astype(np.float32)
def noise(n): return rng.standard_normal(n).astype(np.float32)
# ---- instruments ----
def pad(m, dur, v=1.0):
    e = env_adsr(int((dur + 1.2) * SR), 0.35, 0.8, 0.8, 1.0, dur)
    x = additive(mf(m), dur, lambda k, fk, t: (1 / k) * lp(1300, fk, 2), 1.2, det=(-8, 0, 7))
    return x * e * v
def strings(m, dur, v=1.0):
    e = env_adsr(int((dur + 0.6) * SR), 0.09, 0.4, 0.85, 0.45, dur)
    vib = lambda t: (0.006 * mf(m) / 5.4) * np.sin(2 * np.pi * 5.4 * t) * np.clip((t - 0.2) / 0.3, 0, 1)
    x = additive(mf(m), dur, lambda k, fk, t: (1 / k) * lp(2600, fk, 2), 0.6, vib=vib, det=(-6, 5))
    bow = fft_filter(noise(len(x)), lo=2000, hi=6000) * 0.02
    return (x + bow) * e * v
def celesta(m, v=1.0):
    f = mf(m); n = int(2.6 * SR); t = np.arange(n) / SR; x = np.zeros(n, np.float32)
    for r, a, d in [(1, 1, 1.5), (2, 0.22, 0.55), (3, 0.05, 0.3), (4.16, 0.09, 0.12), (5.4, 0.03, 0.07)]:
        if f * r < 16000: x += (a * np.exp(-t / d) * np.sin(2 * np.pi * f * r * t)).astype(np.float32)
    x[:int(0.004 * SR)] *= np.linspace(0, 1, int(0.004 * SR)); clk = fft_filter(noise(int(0.006 * SR)), lo=3000) * np.linspace(1, 0, int(0.006 * SR)) * 0.15
    x[:len(clk)] += clk; return x * v
def musicbox(m, v=1.0):
    f = mf(m); n = int(2.2 * SR); t = np.arange(n) / SR; x = np.zeros(n, np.float32)
    for r, a, d in [(1, 1, 1.1), (2, 0.18, 0.4), (3.89, 0.16, 0.18), (6.1, 0.07, 0.08)]:
        if f * r < 17000: x += (a * np.exp(-t / d) * np.sin(2 * np.pi * f * r * t)).astype(np.float32)
    x[:int(0.002 * SR)] *= np.linspace(0, 1, int(0.002 * SR)); return x * v
def harp(m, v=1.0):
    return additive(mf(m), 0, lambda k, fk, t: (1 / k ** 1.3) * np.exp(-t * (1.6 + 0.9 * k)) * lp(5000, fk), 1.6, kmax=14) * v
def bass(m, dur, v=1.0):
    f = mf(m); n = int((dur + 0.12) * SR); t = np.arange(n) / SR
    e = np.minimum(1, t / 0.006) * np.exp(-t / (dur * 0.9 + 0.05)) * np.clip((dur + 0.1 - t) / 0.1, 0, 1)
    x = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) + 0.12 * np.sin(6 * np.pi * f * t) + 0.05 * np.sin(8 * np.pi * f * t)
    return (np.tanh(1.6 * x * e) / np.tanh(1.6)).astype(np.float32) * v
def drone(m, dur, v=1.0):
    e = env_adsr(int((dur + 1.5) * SR), 1.2, 1, 1, 1.5, dur)
    return additive(mf(m), dur, lambda k, fk, t: (1 / k ** 1.5) * lp(700, fk, 2), 1.5, det=(-5, 4)) * e * v
def kick_syn():
    n = int(0.45 * SR); t = np.arange(n) / SR; f = 46 + 110 * np.exp(-t / 0.035); ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) * np.exp(-t / 0.22) + fft_filter(noise(n), lo=1500) * np.exp(-t / 0.004) * 0.3).astype(np.float32)
def snare_syn():
    n = int(0.35 * SR); t = np.arange(n) / SR
    body = np.sin(2 * np.pi * 185 * t) * np.exp(-t / 0.05) * 0.6; nz = fft_filter(noise(n), lo=1200, hi=9000) * np.exp(-t / 0.11)
    return (body + nz * 0.9).astype(np.float32)
def clap_syn():
    n = int(0.3 * SR); t = np.arange(n) / SR; nz = fft_filter(noise(n), lo=900, hi=4000); e = np.exp(-t / 0.09)
    for d in (0.0, 0.011, 0.022): e = e + np.where((t >= d) & (t < d + 0.008), np.exp(-(t - d) / 0.003), 0)
    return (nz * e * 0.6).astype(np.float32)
def hat_syn(open_=False):
    n = int((0.25 if open_ else 0.06) * SR); t = np.arange(n) / SR
    return (fft_filter(noise(n), lo=7000) * np.exp(-t / (0.09 if open_ else 0.014))).astype(np.float32)
def tom(m):
    n = int(0.6 * SR); t = np.arange(n) / SR; f = mf(m) * (1 + 0.35 * np.exp(-t / 0.03)); ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) * np.exp(-t / 0.28) + fft_filter(noise(n), lo=200, hi=2000) * np.exp(-t / 0.02) * 0.4).astype(np.float32)
def tick_syn(hi_):
    n = int(0.05 * SR); t = np.arange(n) / SR
    return (fft_filter(noise(n), lo=1800 if hi_ else 1200, hi=5000) * np.exp(-t / 0.006) + np.sin(2 * np.pi * (2400 if hi_ else 1800) * t) * np.exp(-t / 0.01) * 0.3).astype(np.float32)
def reverb(x, sec=2.8, wet=0.3, damp=4500, pre=0.02):
    n = int(sec * SR); t = np.arange(n) / SR; ir = np.zeros((n + int(pre * SR), 2), np.float32)
    for c in range(2):
        nz = noise(n) * np.exp(-t * 6.9 / sec); nz = fft_filter(nz, lo=180, hi=damp); ir[int(pre * SR):, c] = nz
    ir /= np.sqrt((ir ** 2).sum(0)).max()
    M = 1 << int(np.ceil(np.log2(len(x) + len(ir)))); out = np.zeros_like(x)
    for c in range(2): out[:, c] = np.fft.irfft(np.fft.rfft(x[:, c], M) * np.fft.rfft(ir[:, c], M), M)[:len(x)]
    return x + out * wet
# ---- the score ----
CH = [[50, 53, 57], [45, 48, 52], [46, 50, 53], [40, 44, 47], [50, 53, 57], [45, 48, 52], [41, 45, 48], [40, 44, 47]]  # Dm Am Bb E Dm Am F E (roots)
ROOT = [38, 33, 34, 40, 38, 33, 41, 40]
MEL = [(81, 0, 1), (77, 1, 1), (74, 2, 1), (77, 3, 1), (76, 4, 1.5), (72, 5.5, .5), (76, 6, 1), (81, 7, 1), (77, 8, 1), (74, 9, 1), (70, 10, 1), (74, 11, 1),
       (76, 12, 1), (69, 13, 1), (68, 14, 1), (71, 15, 1), (81, 16, 1), (77, 17, 1.5), (74, 18.5, .5), (84, 19, 1), (84, 20, 1.5), (83, 21.5, .5), (81, 22, 1.5), (72, 23.5, .25), (76, 23.75, .25),
       (81, 24, 1), (84, 25, 1), (83, 26, 1), (80, 27, 1), (76, 28, 2), (71, 30, .5), (72, 30.5, .5), (74, 31, .5), (76, 31.5, .5)]
def voicing(ch):  # pads around C4 to A4: the chord's tones placed in 57..69, plus the root an octave below
    pcs = sorted(set(m % 12 for m in ch)); v = []
    for pc in pcs:
        m = 57 + ((pc - 57) % 12); v.append(m)
    return sorted(v) + [ch[0] + 12 if ch[0] + 12 < 57 else ch[0]]
def score(cycle0):
    S = {k: buf() for k in ('air', 'keys', 'low', 'tops', 'drive')}
    OS = sys.argv[1]
    kick = load(os.path.join(OS, 'kick.mp3'), SR)[:int(0.5 * SR)]; kick = kick / np.abs(kick).max()
    shk = load(os.path.join(OS, 'shaker.mp3'), SR)[:int(0.35 * SR)]; shk = shk / np.abs(shk).max()
    atm = load(os.path.join(OS, 'atmos.mp3'), SR, 2); atm = atm / np.abs(atm).max()
    ks, sn, cl, hc, ho = kick_syn(), snare_syn(), clap_syn(), hat_syn(), hat_syn(True)
    global rng
    for cyc in range(3):
        T0 = cycle0 + cyc * LS; rng = np.random.default_rng(257)  # (each pass the same to the sample, so the loop's tails meet its start exactly)
        # air: the shimmer (Ludo.ai's atmosphere, overlapped with itself), a low A and E, the clock, the music box's first notes
        seg = fft_filter(atm, lo=250, hi=7000); sl = len(seg) / SR; t = 0.0
        while t < L:
            w = seg.copy(); f = int(1.2 * SR); w[:f] *= np.linspace(0, 1, f)[:, None]; w[-f:] *= np.linspace(1, 0, f)[:, None]
            put(S['air'], T0 + t, w, g=0.22); t += sl - 1.2
        put(S['air'], T0, drone(45, L - 0.5, 1), -0.2, 0.16); put(S['air'], T0, drone(52, L - 0.5, 1), 0.2, 0.1)
        for b in range(BARS * 4): put(S['air'], T0 + b * BEAT, tick_syn(b % 2 == 0), 0.35 if b % 2 else -0.35, 0.09 if b % 4 else 0.12)
        for (m, b, d) in MEL:
            if b < 4 or 16 <= b < 20: put(S['air'], T0 + b * BEAT, musicbox(m + 12), 0.25, 0.32)
        # keys: pads on the chords, the melody on celesta
        for i, ch in enumerate(CH):
            for j, m in enumerate(voicing(ch)): put(S['keys'], T0 + i * BAR, pad(m, BAR - 0.05), (j - 1.5) * 0.25, 0.085)
        for (m, b, d) in MEL: put(S['keys'], T0 + b * BEAT, celesta(m), -0.15, 0.3)
        # low: the bass bouncing root and octave, the harp running up the chord
        for i, r in enumerate(ROOT):
            for e in range(8): put(S['low'], T0 + i * BAR + e * BEAT / 2, bass(r + (12 if e % 2 else 0), BEAT / 2 * (0.85 if e % 2 else 0.95)), 0, 0.42 if e % 2 == 0 else 0.3)
            tones = sorted(set(m % 12 for m in CH[i])); arp = []
            for o in (60, 72):
                for pc in tones: arp.append(o + ((pc - o) % 12))
            arp = sorted(arp)[:6]; arp = arp + arp[::-1][1:3]
            for e, m in enumerate(arp): put(S['low'], T0 + i * BAR + e * BEAT / 2, harp(m), 0.3 - 0.08 * (e % 4), 0.11)
        # tops: shaker on the sixteenths (the off ones lighter), hats on the off-beats
        for s in range(BARS * 16):
            put(S['tops'], T0 + s * BEAT / 4 + (0.012 if s % 2 else 0), shk, 0.3, 0.45 if s % 4 == 2 else 0.25 if s % 2 else 0.35)
            if s % 4 == 2: put(S['tops'], T0 + s * BEAT / 4, ho if s % 32 == 30 else hc, -0.3, 0.5)
        # drive: kick, snare and clap, a tom fill into the top, and the melody on strings
        for b in range(BARS):
            for kb in ((0, 1.5, 2) if b % 2 == 0 else (0, 1.5, 2.75)): put(S['drive'], T0 + b * BAR + kb * BEAT, kick, 0, 0.6); put(S['drive'], T0 + b * BAR + kb * BEAT, ks, 0, 0.5)
            for sb in (1, 3):
                if b == BARS - 1 and sb == 3: continue
                put(S['drive'], T0 + b * BAR + sb * BEAT, sn, 0.05, 0.42); put(S['drive'], T0 + b * BAR + sb * BEAT, cl, -0.1, 0.3)
        for k, m in enumerate([50, 50, 47, 47, 45, 45, 43, 41]): put(S['drive'], T0 + (BARS - 1) * BAR + 3 * BEAT + k * BEAT / 8, tom(m), -0.4 + k * 0.1, 0.32)
        for (m, b, d) in MEL: put(S['drive'], T0 + b * BEAT, strings(m - 12, d * BEAT * 0.96), 0.12, 0.16)
    wet = {'air': 0.55, 'keys': 0.32, 'low': 0.16, 'tops': 0.12, 'drive': 0.16}
    for k in S: S[k] = reverb(S[k], 3.2 if k in ('air', 'keys') else 1.8, wet[k])
    return S
def sting():
    n = int(9 * SR); X = np.zeros((n, 2), np.float32); R = BAR
    rs = load(os.path.join(sys.argv[1], 'riser.mp3'), SR, 2); rs = rs / np.abs(rs).max(); rs = rs[-int(R * SR):]
    rs *= np.linspace(0.2, 1, len(rs))[:, None] ** 1.5; X[:len(rs)] += rs * 0.28
    for k, m in enumerate([52, 55, 59, 62, 64]): put(X, R - 0.5 + k * 0.1, celesta(m + 12, 0.6), -0.3 + k * 0.15, 0.12)  # (a little run up into it)
    # the hit: a sub boom, a crack of noise, the orchestra on E major, a celesta glissando up the chord, a crash
    t = np.arange(int(3 * SR)) / SR; f = 34 + 40 * np.exp(-t / 0.25); boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.9); put(X, R, boom.astype(np.float32), 0, 0.9)
    put(X, R, tom(40) * 1.2, 0, 0.7); put(X, R, kick_syn(), 0, 0.8)
    crash = fft_filter(noise(int(3 * SR)), lo=3500) * np.exp(-np.arange(int(3 * SR)) / SR / 0.9); put(X, R, np.stack([crash, np.roll(crash, 300)], 1), g=0.22)
    for j, m in enumerate([40, 47, 52, 56, 59, 64, 68, 71]):
        e = env_adsr(int(3.2 * SR), 0.012, 0.9, 0.25, 1.6, 1.4)
        x = additive(mf(m), 1.4, lambda k, fk, tt: (1 / k) * lp(900 + 4000 * np.exp(-tt / 0.35), fk, 2), 1.8, det=(-7, 0, 6), kmax=40) * e
        put(X, R, x, (j - 3.5) * 0.12, 0.09)
    for k, m in enumerate([76, 80, 83, 88, 92, 95, 100]): put(X, R + 0.04 + k * 0.07, celesta(m, 0.8), -0.3 + k * 0.1, 0.16)
    X = reverb(X, 3.4, 0.38)
    return X
def enc(x, path, br, mono=False):
    import soundfile as sf; tmp = path + '.wav'; sf.write(tmp, x, SR)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp] + (['-ac', '1'] if mono else []) + ['-c:a', 'libmp3lame', '-b:a', br, path], check=True); os.remove(tmp)
if __name__ == '__main__':
    out = sys.argv[2]; os.makedirs(out, exist_ok=True); C0 = 0.5
    S = score(C0)
    i0, n, pre = int(round((C0 + LS) * SR)), int(round(LS * SR)), int(0.25 * SR)
    mix = sum(S.values())[i0:i0 + n]; pk = np.abs(mix).max(); G = 0.89 / pk
    print('loop', round(L, 5), 'mix peak', round(float(pk), 3), 'gain', round(float(G), 3))
    for k, x in S.items():
        y = x[i0 - pre:i0 + n + int(0.5 * SR)] * G; y = np.tanh(y * 1.1) / 1.1
        lv = 20 * np.log10(np.sqrt(np.mean(y[pre:pre + n] ** 2)) + 1e-9); print(k, 'rms', round(float(lv), 1))
        enc(y, os.path.join(out, 'intro_' + k + '.mp3'), '96k' if k in ('air', 'tops') else '112k')
    st = sting(); st = st / np.abs(st).max() * 0.92; enc(st, os.path.join(out, 'intro_sting.mp3'), '128k')
    print(f"loop a 0.25 b {0.25 + n / SR:.5f}  sting hit at {BAR:.5f}")
