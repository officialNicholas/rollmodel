# fine seam: the loop length to the sample (waveform cross-correlation round a rough seam), then the best spot for a short crossfade
import sys, numpy as np, warnings
from scipy.io import wavfile
from scipy import signal
warnings.filterwarnings('ignore')
path, A, L = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]); span = float(sys.argv[4]) if len(sys.argv) > 4 else 0.3
sr, a = wavfile.read(path); a = a.astype(np.float64) / 32768.0; m = a.mean(1)
b, aa = signal.butter(4, [70 / (sr / 2), 5000 / (sr / 2)], 'band'); x = signal.filtfilt(b, aa, m)
R = int(0.008 * sr)
def lagAt(t, W):
    i0 = int(t * sr); w = int(W * sr); seg = x[i0:i0 + w]; base = int(round((t + L) * sr)); y = x[base - R:base + R + w]
    cc = signal.correlate(y, seg, 'valid'); nrm = np.sqrt(np.convolve(y ** 2, np.ones(w), 'valid')) * np.linalg.norm(seg) + 1e-12; cc = cc / nrm; j = int(np.argmax(cc)); return base - R + j - i0, cc[j]
for W in [0.4, 0.2, 0.1]:
    print('window', W, [ (lagAt(t, W)[0], round(lagAt(t, W)[1], 3)) for t in np.arange(A - span, A + span, 0.1)])
# with the most common lag, the short-window correlation along the seam region: where the two passes agree best sample for sample
lags = [lagAt(t, 0.2) for t in np.arange(A - span, A + span, 0.05)]; good = sorted(lags, key=lambda q: -q[1])[:5]
Ls = good[0][0]; print('loop length', Ls, 'samples', round(Ls / sr, 5), 's; best corr', round(good[0][1], 3))
w = int(0.04 * sr); best = []
for t in np.arange(A - span, A + span, 0.002):
    i = int(t * sr); p = x[i - w // 2:i + w // 2]; q = x[i - w // 2 + Ls:i + w // 2 + Ls]
    c = np.dot(p, q) / (np.linalg.norm(p) * np.linalg.norm(q) + 1e-12); e = np.sqrt((m[i - w // 2:i + w // 2] ** 2).mean()); best.append((c, t, e))
best.sort(reverse=True)
for c, t, e in best[:8]: print(f'seam {t:7.3f}s  corr {c:.3f}  level {20*np.log10(e):6.1f} dB')
