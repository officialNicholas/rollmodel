"""Ol' Bloop's voice: cut the user's take into its separate sounds (on the silences between them), each trimmed with a little lead-in
and a faded tail, mono, as la/sfx/bloop_N.mp3 for the sound sheets"""
import sys, wave, subprocess, numpy as np
src, out = sys.argv[1], sys.argv[2]
w = wave.open(src); sr = w.getframerate(); ch = w.getnchannels(); a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).reshape(-1, ch).astype(float).mean(1) / 32768
win = int(sr * 0.015); e = np.sqrt(np.convolve(a * a, np.ones(win) / win, 'same')); db = 20 * np.log10(e + 1e-9)
on = db > -46; segs = []; i = 0; n = len(a)
while i < n:
    if not on[i]: i += 1; continue
    j = i
    while j < n and (on[j] or (j < n and on[j:min(n, j + int(sr * 0.16))].any())): j += 1
    segs.append((i, j)); i = j + 1
segs = [(s0, s1) for s0, s1 in segs if (s1 - s0) / sr > 0.12]
print(len(segs), 'sounds:', [(round(s0 / sr, 2), round(s1 / sr, 2)) for s0, s1 in segs])
for k, (s0, s1) in enumerate(segs, 1):
    s0 = max(0, s0 - int(sr * 0.025)); s1 = min(n, s1 + int(sr * 0.06)); x = a[s0:s1].copy()
    f = int(sr * 0.05); x[-f:] *= np.linspace(1, 0, f) ** 2; x[:int(sr * 0.004)] *= np.linspace(0, 1, int(sr * 0.004))
    x *= 10 ** (-3 / 20) / (np.abs(x).max() + 1e-9)  # (each to the same peak; the sheet build sets the final loudness)
    pcm = (x * 32767).astype(np.int16).tobytes()
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 's16le', '-ar', str(sr), '-ac', '1', '-i', '-', '-ar', '44100', '-codec:a', 'libmp3lame', '-b:a', '128k', f'{out}/bloop_{k}.mp3'], input=pcm, check=True)
    print(f'bloop_{k}.mp3', round(len(x) / sr, 2), 's')
