#!/usr/bin/env python3
"""v267: the intro's desert wind (game/sfx/intro_wind.mp3). Ludo.ai sound effects are 10 s at most, so: two calm canyon-wind takes
(tools/ludo.py sfx ... --dur 10), their quiet starts and ends trimmed, the second's tone matched to the first's (a smooth spectral
correction within 9 dB) and its level too, then the first, the second and the first played backwards (wind reads the same either
way), each 1.6 s equal-power crossfade into the next, and the end crossfaded into the start so the loop wraps seamlessly. Its level is
then evened out over a 1.6 s window, taken round the loop, to within about 2 dB, and set to -23 dBFS RMS. The file is the loop with
0.4 s of itself either side (loop points 0.4 s to 0.4 s + the loop), so the points hold whatever start offset the decoder adds.
Usage: desert_wind.py <first.mp3> <second.mp3> <out.mp3>   (the takes used: rm-desert-b3, then rm-desert-b1)
Prompt: "Desert canyon ambience: low airy wind over sand, light sand blowing and rustling, a faint dry whistle of wind past rocks, very
calm and continuous, no music, no voices, steady volume from start to end" """
import sys, subprocess, numpy as np
SR = 44100
def load(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '2', '-ar', str(SR), '-f', 's16le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.int16).reshape(-1, 2).astype(np.float64) / 32768
rms = lambda x: np.sqrt((x ** 2).mean())
a, b, out = sys.argv[1:4]
A = load(a)[int(1.0 * SR):int(8.9 * SR)]; Bt = load(b)[int(1.0 * SR):int(8.3 * SR)]
def smooth_mag(x, n=801): X = np.abs(np.fft.rfft(x.mean(1))); return np.convolve(X, np.ones(n) / n, 'same') + 1e-12
XB = np.fft.rfft(Bt, axis=0); mA = smooth_mag(A); mA = np.interp(np.linspace(0, 1, XB.shape[0]), np.linspace(0, 1, len(mA)), mA)
g = np.clip(mA / smooth_mag(Bt) * (rms(Bt) / rms(A)), 10 ** (-9 / 20), 10 ** (9 / 20))
Bm = np.fft.irfft(XB * g[:, None], n=len(Bt), axis=0); Bm *= rms(A) / rms(Bm)
F = int(1.6 * SR); r = np.linspace(0, 1, F)[:, None]; fi, fo = np.sin(r * np.pi / 2), np.cos(r * np.pi / 2)
T = A
for s in (Bm, A[::-1]): T = np.concatenate([T[:-F], T[-F:] * fo + s[:F] * fi, s[F:]])
L = T[F:].copy(); L[-F:] = T[-F:] * fo + T[:F] * fi
n = len(L); p = (L ** 2).mean(1); W = int(1.6 * SR); ext = np.concatenate([p[-W:], p, p[:W]]); c = np.cumsum(np.concatenate([[0], ext]))
env = np.sqrt((c[W + W // 2 + np.arange(n)] - c[W // 2 + np.arange(n)]) / W) + 1e-9
L = L * ((np.exp(np.log(env).mean()) / env) ** 0.85)[:, None]; L *= 10 ** (-23 / 20) / rms(L)
PAD = int(0.4 * SR); full = np.concatenate([L[-PAD:], L, L[:PAD]])
pcm = (np.clip(full, -1, 1) * 32767).astype(np.int16).tobytes()
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 's16le', '-ar', str(SR), '-ac', '2', '-i', '-', '-c:a', 'libmp3lame', '-b:a', '96k', out], input=pcm, check=True)
print(out, 'loop %.4f s, points %.1f to %.4f s' % (n / SR, PAD / SR, (PAD + n) / SR))
