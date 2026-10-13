#!/usr/bin/env python3
"""v257 intro: quick analysis of an audio file (no ears needed): length, loudness over time, tempo by onset autocorrelation, key by chroma.
Usage: intro_audio_an.py file.mp3 [...]"""
import sys, subprocess, numpy as np
SR = 22050
def load(p, sr=SR, ch=1):
    raw = subprocess.run(['ffmpeg', '-v', 'quiet', '-i', p, '-ac', str(ch), '-ar', str(sr), '-f', 'f32le', '-'], capture_output=True).stdout
    a = np.frombuffer(raw, np.float32); return a.reshape(-1, ch) if ch > 1 else a
def stft_mag(x, n=2048, h=512):
    w = np.hanning(n); fr = 1 + (len(x) - n) // h
    idx = np.arange(n)[None, :] + h * np.arange(fr)[:, None]
    return np.abs(np.fft.rfft(x[idx] * w, axis=1)), h
def onset_env(x):
    M, h = stft_mag(x); L = np.log1p(100 * M); fl = np.maximum(0, np.diff(L, axis=0)).sum(1); fl -= np.convolve(fl, np.ones(16) / 16, 'same'); return np.maximum(fl, 0), h
def tempo(x, lo=70, hi=180):
    e, h = onset_env(x); fps = SR / h; e = e - e.mean(); ac = np.correlate(e, e, 'full')[len(e) - 1:]
    best = None
    for bpm in np.arange(lo, hi, 0.1):
        lag = 60 * fps / bpm; i = int(lag); f = lag - i
        if i + 1 >= len(ac): continue
        v = ac[i] * (1 - f) + ac[i + 1] * f
        if best is None or v > best[1]: best = (bpm, v)
    return best[0], e, fps
NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
MAJ = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]); MIN = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
def chroma(x):
    M, h = stft_mag(x, 8192, 2048); f = np.fft.rfftfreq(8192, 1 / SR); c = np.zeros(12); ok = (f > 55) & (f < 2000)
    pc = (np.round(12 * np.log2(f[ok] / 440)) + 9) % 12
    e = (M[:, ok] ** 2).sum(0)
    for k in range(12): c[k] = e[pc == k].sum()
    return c / c.sum()
def key(x):
    c = chroma(x); best = []
    for k in range(12):
        best.append((np.corrcoef(np.roll(MAJ, k), c)[0, 1], NAMES[k] + ' maj')); best.append((np.corrcoef(np.roll(MIN, k), c)[0, 1], NAMES[k] + ' min'))
    best.sort(reverse=True); return best[:3], c
if __name__ == '__main__':
    for p in sys.argv[1:]:
        x = load(p); d = len(x) / SR
        rms = [20 * np.log10(np.sqrt(np.mean(x[int(i * SR):int((i + 2) * SR)] ** 2)) + 1e-9) for i in np.arange(0, d - 1, 2)]
        bpm, e, fps = tempo(x); ks, c = key(x)
        print(f'{p}: {d:.1f}s peak {np.abs(x).max():.2f} tempo {bpm:.1f} key {ks[0][1]} ({ks[0][0]:.2f}) / {ks[1][1]} / {ks[2][1]}')
        print('  rms dB per 2s:', ' '.join(f'{v:.0f}' for v in rms))
