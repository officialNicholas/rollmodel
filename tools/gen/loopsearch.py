# the best loop in a song: every pair of beats (A early, B late) scored on how alike the music is round them (harmony, sound and
# rhythm, a bar before to two bars after), so jumping from B back to A carries on as if nothing happened
# usage: loopsearch.py song.wav grid.txt minA maxB minLoop
import sys, numpy as np, warnings
from scipy.io import wavfile
from scipy import signal
warnings.filterwarnings('ignore')
path, grid = sys.argv[1], sys.argv[2]; minA, maxB, minL = float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])
period, off, fps = map(float, open(grid).read().split())
sr, a = wavfile.read(path); a = a.astype(np.float64) / 32768.0; m = a.mean(1)
hop = sr // 100; nfft = 4096
f, t, Z = signal.stft(m, sr, nperseg=nfft, noverlap=nfft - hop, boundary=None, padded=False); S = np.abs(Z) ** 2
freqs = f[1:]; midi = 69 + 12 * np.log2(np.maximum(freqs, 1) / 440.0); pc = np.mod(np.round(midi), 12).astype(int)
ch = np.zeros((12, S.shape[1]))
for k in range(12): ch[k] = S[1:][(pc == k) & (freqs > 60) & (freqs < 4000)].sum(0)
ch = ch / (ch.sum(0, keepdims=True) + 1e-9)
edges = np.geomspace(40, 15000, 25); tb = np.zeros((24, S.shape[1]))
for i in range(24): sel = (f >= edges[i]) & (f < edges[i + 1]); tb[i] = S[sel].sum(0)
tb = np.log1p(tb * 1e4); tb = tb - tb.mean(1, keepdims=True)
L = np.log1p(tb.clip(0) * 10); flux = np.concatenate([[0], np.maximum(0, np.diff(tb, axis=1)).sum(0)])
F = np.vstack([ch * 3.0, tb * 0.25, flux[None] * 0.5])  # features x frames
nfr = F.shape[1]
W0, W1 = int(4 * period * fps), int(8 * period * fps)  # a bar before, two after
beats = off + np.arange(0, (len(m) / sr - off) / period) * period
def win(tsec):
    i = int(round(tsec * fps)); 
    if i - W0 < 0 or i + W1 >= nfr: return None
    v = F[:, i - W0:i + W1].ravel(); v = v - v.mean(); return v / (np.linalg.norm(v) + 1e-9)
V = {k: win(b) for k, b in enumerate(beats)}
res = []
for i, A in enumerate(beats):
    if A < minA or V[i] is None: continue
    for j, B in enumerate(beats):
        if B > maxB or B - A < minL or V[j] is None: continue
        res.append((float(V[i] @ V[j]), A, B, i, j))
res.sort(reverse=True)
print(f'beat {period:.5f}s  bar {4*period:.4f}s  candidates {len(res)}')
for c, A, B, i, j in res[:14]: print(f'  sim {c:.3f}  A {A:7.3f}s (beat {i:3d}, bar {i/4:5.2f})  B {B:7.3f}s (beat {j:3d})  loop {B-A:6.2f}s = {(j-i)/4:5.2f} bars')
# the longest loop among the near-best (within 0.03 of the top)
top = res[0][0]; longest = max([r for r in res if r[0] > top - 0.03], key=lambda r: r[2] - r[1])
print('  longest near-best:', f'sim {longest[0]:.3f} A {longest[1]:.3f} B {longest[2]:.3f} loop {longest[2]-longest[1]:.2f}s')
