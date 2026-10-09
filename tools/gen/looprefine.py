# refine a loop length: onset envelopes first (10 ms), then the waveform itself (to the sample), then score candidate seam points
import sys, numpy as np, warnings, json
from scipy.io import wavfile
from scipy import signal
warnings.filterwarnings('ignore')
path, L0, a0, a1 = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])  # rough loop length, range to search the loop start in
period, off, fps = map(float, open('music_src/grid.txt').read().split())
sr, a = wavfile.read(path); a = a.astype(np.float64) / 32768.0; m = a.mean(1); N = len(m)
flux = np.load('music_src/flux.npy')
# 1) loop length from the onset envelopes over the whole overlap
best = None
for L in np.arange(L0 - 0.3, L0 + 0.3, 0.002):
    k = int(round(L * fps)); x = flux[int(a0 * fps):len(flux) - k - 50]; y = flux[int(a0 * fps) + k:len(flux) - 50]
    n = min(len(x), len(y)); c = np.dot(x[:n], y[:n]) / (np.linalg.norm(x[:n]) * np.linalg.norm(y[:n]) + 1e-9)
    if best is None or c > best[0]: best = (c, L)
print('onset match', round(best[0], 3), 'at loop length', round(best[1], 4), 's')
L1 = best[1]
# 2) to the sample, on the low end (steadier) over several windows, the median of the best lags
b, aa = signal.butter(4, 1800 / (sr / 2)); lo = signal.filtfilt(b, aa, m)
lags = []
for st in np.arange(a0, min(a1 + 6, (N / sr) - L1 - 1.5), 0.75):
    i0 = int(st * sr); W = int(0.6 * sr); x = lo[i0:i0 + W]; base = int(round((st + L1) * sr)); R = int(0.012 * sr)
    seg = lo[base - R:base + R + W]; cc = signal.correlate(seg, x, 'valid'); nrm = np.sqrt(np.convolve(seg ** 2, np.ones(W), 'valid')) * np.linalg.norm(x) + 1e-12; cc = cc / nrm
    j = int(np.argmax(cc)); lags.append((base - R + j - i0, cc[j], st))
good = [l for l in lags if l[1] > 0.6]
print('windows', len(lags), 'good', len(good), 'lags (samples) of good:', sorted(set(l[0] for l in good))[:12], '...')
Ls = int(np.median([l[0] for l in good])) if good else int(round(L1 * sr))
print('loop length', Ls, 'samples =', round(Ls / sr, 5), 's  (', round(Ls / sr / period, 3), 'beats )')
# 3) score each candidate seam: how alike the audio is for a beat either side of A and A+L (full band), plus the onset nearby
cands = []
for st in np.arange(a0, a1, 0.01):
    i = int(st * sr); W = int(0.25 * sr)
    x = m[i - W:i + W]; y = m[i - W + Ls:i + W + Ls]
    c = np.dot(x, y) / (np.linalg.norm(x) * np.linalg.norm(y) + 1e-12)
    e = np.sqrt((x ** 2).mean())
    cands.append((c, st, e))
cands.sort(reverse=True)
for c, st, e in cands[:12]: bp = (st - off) / period; print(f'A {st:7.3f}s  match {c:.4f}  beat {bp:6.2f}  level {20*np.log10(e+1e-9):6.1f} dB')
json.dump({'Ls': Ls, 'sr': sr, 'cands': [(c, st) for c, st, e in cands[:40]]}, open('music_src/loopcands.json', 'w'))
