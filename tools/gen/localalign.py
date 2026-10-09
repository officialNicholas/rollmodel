# line up two stretches of a track by their rhythm: multi-band onset envelopes at 2 ms, cross-correlated over a range of lags
import sys, numpy as np, warnings
from scipy.io import wavfile
from scipy import signal
warnings.filterwarnings('ignore')
path, A, B, W = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]); R = float(sys.argv[5]) if len(sys.argv) > 5 else 0.08
sr, a = wavfile.read(path); a = a.astype(np.float64) / 32768.0; m = a.mean(1)
hop = int(0.002 * sr); nfft = 2048
def env(t0, t1):
    seg = m[max(0, int(t0 * sr)):int(t1 * sr)]
    f, t, Z = signal.stft(seg, sr, nperseg=nfft, noverlap=nfft - hop, boundary=None, padded=False); S = np.log1p(np.abs(Z) * 50)
    edges = np.geomspace(50, 16000, 13); E = np.array([S[(f >= edges[i]) & (f < edges[i + 1])].mean(0) for i in range(12) if ((f >= edges[i]) & (f < edges[i + 1])).any()])
    fl = np.maximum(0, np.diff(E, axis=1)); fl = fl / (fl.std(1, keepdims=True) + 1e-9); return fl.sum(0)
ea = env(A - R, A + W + R); eb = env(B - R, B + W + R)
k = int(R / 0.002); n = min(len(ea), len(eb)) - 2 * k
best = []
for lag in range(-k, k + 1):
    x = ea[k:k + n]; y = eb[k + lag:k + lag + n]; c = np.dot(x - x.mean(), y - y.mean()) / (np.std(x) * np.std(y) * n + 1e-9); best.append((c, lag * 0.002))
best.sort(reverse=True); print('best offsets of B relative to A (s):', [(round(o, 3), round(c, 3)) for c, o in best[:6]])
