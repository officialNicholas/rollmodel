# per bar: the hit at its first beat (high-band onset, where crashes and kicks mark sections), its loudness, and how alike
# its harmony is to the bar before (a section change shows as a dip) - usage: barmap.py song.wav grid.txt
import sys, numpy as np, warnings
from scipy.io import wavfile
from scipy import signal
warnings.filterwarnings('ignore')
path, grid = sys.argv[1], sys.argv[2]; period, off, fps = map(float, open(grid).read().split())
sr, a = wavfile.read(path); a = a.astype(np.float64) / 32768.0; m = a.mean(1)
hop = sr // 100; f, t, Z = signal.stft(m, sr, nperseg=2048, noverlap=2048 - hop, boundary=None, padded=False); S = np.abs(Z)
hi = np.log1p(S[f > 4000].sum(0) * 10); lo = np.log1p(S[(f > 30) & (f < 150)].sum(0) * 10)
fh = np.maximum(0, np.diff(hi, prepend=hi[0])); fl = np.maximum(0, np.diff(lo, prepend=lo[0]))
freqs = f[1:]; midi = 69 + 12 * np.log2(np.maximum(freqs, 1) / 440.0); pc = np.mod(np.round(midi), 12).astype(int)
P = S[1:] ** 2; ch = np.array([P[(pc == k) & (freqs > 60) & (freqs < 4000)].sum(0) for k in range(12)])
nb = int((len(m) / sr - off) / period) // 4; bars = []
for b in range(nb):
    t0 = off + b * 4 * period; i0 = int(t0 * fps); i1 = int((t0 + 4 * period) * fps)
    w = slice(max(0, i0 - 4), i0 + 5)
    c = ch[:, i0:i1].mean(1); c = c / (np.linalg.norm(c) + 1e-9)
    bars.append((b, t0, fh[w].max(), fl[w].max(), 20 * np.log10(np.sqrt((m[int(t0 * sr):int((t0 + 4 * period) * sr)] ** 2).mean()) + 1e-9), c))
line = ''
for k, (b, t0, h, l, db, c) in enumerate(bars):
    sim = float(c @ bars[k - 1][5]) if k else 1
    line += f'bar {b:3d} {t0:6.2f}s  hit hi {h:4.2f} lo {l:4.2f}  {db:5.1f} dB  harm~prev {sim:.2f}' + ('  <<' if sim < 0.8 or h > 1.2 else '') + '\n'
print(line)
