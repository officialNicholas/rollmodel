# build a game-ready looping track from a song:
#   1) the loop length to the sample, from waveform cross-correlation round the rough seam
#   2) the best spot for the crossfade near it: where the two passes agree most closely, sample for sample
#   3) the file: the song up to the seam, a short equal-power crossfade into the early pass, then a guard stretch copied from the early pass,
#      so the loop points sit inside identical audio (a decoder shifting the timeline by a few tens of ms can't put a click in it)
#   4) the leading silence trimmed, a WAV for checking, an AAC .m4a for the game, a preview that goes round the seam twice
# usage: mkloop.py name src.wav A L [xfade_s] [search_s]
import sys, json, subprocess, numpy as np, warnings
from scipy.io import wavfile
from scipy import signal
warnings.filterwarnings('ignore')
name, path, A, L = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
X = float(sys.argv[5]) if len(sys.argv) > 5 else 0.06
SPAN = float(sys.argv[6]) if len(sys.argv) > 6 else 0.3
G = 0.2
sr, raw = wavfile.read(path); a = raw.astype(np.float64) / 32768.0; m = a.mean(1); N = len(m)
b, aa = signal.butter(4, [70 / (sr / 2), 5000 / (sr / 2)], 'band'); x = signal.filtfilt(b, aa, m)
R = int(0.010 * sr)
def lag_at(t, W):
    i0 = int(t * sr); w = int(W * sr); seg = x[i0:i0 + w]; base = int(round((t + L) * sr)); y = x[base - R:base + R + w]
    cc = signal.correlate(y, seg, 'valid'); nrm = np.sqrt(np.convolve(y ** 2, np.ones(w), 'valid')) * np.linalg.norm(seg) + 1e-12; cc = cc / nrm
    j = int(np.argmax(cc)); return base - R + j - i0, float(cc[j])
# the loop length: the lag that the most short windows round the seam agree on, weighted by how well they match
votes = {}
for t in np.arange(A - SPAN, A + SPAN, 0.025):
    lg, c = lag_at(t, 0.12)
    if c > 0.3: votes[lg] = votes.get(lg, 0) + c
    for d in (-2, -1, 1, 2): votes[lg + d] = votes.get(lg + d, 0) + c * 0.5
cands = sorted(votes, key=votes.get, reverse=True)[:8] if votes else []
cands.append(int(round(L * sr)))
# where to cross: for each likely lag, the 40 ms stretch with the best sample-for-sample agreement; keep the lag whose best spot agrees most
w = int(0.04 * sr); best = (-2, A, cands[0])
for Lc in cands:
    for t in np.arange(A - SPAN, A + SPAN, 0.002):
        i = int(t * sr); p = x[i - w // 2:i + w // 2]; q = x[i - w // 2 + Lc:i + w // 2 + Lc]
        c = np.dot(p, q) / (np.linalg.norm(p) * np.linalg.norm(q) + 1e-12)
        if c > best[0]: best = (c, t, Lc)
corr, S, Ls = best; iS = int(round(S * sr))
print(f'{name}: loop {Ls} samples ({Ls / sr:.5f} s), seam at {S:.3f} s (corr {corr:.3f})')
# the file
hx = int(X * sr / 2); g = int(G * sr)
B0 = iS + Ls  # the seam on the late pass
out = np.zeros((B0 + hx + g, 2))
out[:B0 - hx] = a[:B0 - hx]
th = np.linspace(0, np.pi / 2, 2 * hx, endpoint=False)
out[B0 - hx:B0 + hx] = a[B0 - hx:B0 + hx] * np.cos(th)[:, None] + a[iS - hx:iS + hx] * np.sin(th)[:, None]
out[B0 + hx:B0 + hx + g] = a[iS + hx:iS + hx + g]
# trim the silence before the first sound, keeping 15 ms
lead = np.where(np.abs(out).max(1) > 10 ** (-60 / 20))[0][0]; cut = max(0, lead - int(0.015 * sr))
out = out[cut:]
loopStart = (iS + hx + g // 2 - cut) / sr; loopEnd = (B0 + hx + g // 2 - cut) / sr
# a few ms of fade at the very start, so it never clicks on
f0 = int(0.005 * sr); out[:f0] *= np.linspace(0, 1, f0)[:, None]
pk = np.abs(out).max(); print(f'  file {len(out) / sr:.3f} s, loop {loopStart:.5f} -> {loopEnd:.5f} s, peak {20 * np.log10(pk):.1f} dB, trimmed {cut / sr:.3f} s')
wavfile.write(f'music_out/{name}.wav', sr, (np.clip(out, -1, 1) * 32767).astype(np.int16))
# check the seam in the finished file: the jump from loopEnd back to loopStart, spliced, must match the original audio around the seam
i1, i0 = int(round(loopEnd * sr)), int(round(loopStart * sr))
spl = np.concatenate([out[i1 - int(0.5 * sr):i1], out[i0:i0 + int(0.5 * sr)]]).mean(1)
dd = np.abs(np.diff(spl)); jump = dd[int(0.5 * sr) - 3:int(0.5 * sr) + 3].max(); typ = np.percentile(dd, 99.5)
print(f'  splice check: biggest step at the jump {jump:.5f} vs 99.5th percentile step {typ:.5f}')
# preview: the intro, round the loop twice, and on a little
pre = np.concatenate([out[:i1], out[i0:i1], out[i0:i0 + int(4 * sr)]])
wavfile.write(f'music_out/{name}_preview.wav', sr, (np.clip(pre, -1, 1) * 32767).astype(np.int16))
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', f'music_out/{name}.wav', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', f'music_out/{name}.m4a'], check=True)
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', f'music_out/{name}_preview.wav', '-b:a', '192k', f'music_out/{name}_preview.mp3'], check=True)
meta = json.load(open('music_out/loops.json')) if __import__('os').path.exists('music_out/loops.json') else {}
meta[name] = {'a': round(loopStart, 5), 'b': round(loopEnd, 5), 'len': round(len(out) / sr, 4), 'seamA': round(S - cut / sr, 3), 'seams': [round(i1 / sr, 2), round((i1 + i1 - i0) / sr, 2)], 'corr': round(corr, 3), 'rms': round(float(20 * np.log10(np.sqrt((out ** 2).mean()))), 2)}
json.dump(meta, open('music_out/loops.json', 'w'), indent=1)
print('  preview seams at', meta[name]['seams'], 's')
