import sys, numpy as np, warnings
from scipy.io import wavfile
from scipy import signal
warnings.filterwarnings('ignore')
path = sys.argv[1]; wins = [tuple(map(float, w.split(':'))) for w in sys.argv[2:]]
sr, a = wavfile.read(path); a = a.astype(np.float64) / 32768.0; m = a.mean(1)
hop = int(0.002 * sr); nfft = 2048
for t0, t1 in wins:
    seg = m[int((t0 - 0.05) * sr):int((t1 + 0.05) * sr)]
    f, t, Z = signal.stft(seg, sr, nperseg=nfft, noverlap=nfft - hop, boundary=None, padded=False); S = np.log1p(np.abs(Z) * 50)
    edges = np.geomspace(50, 16000, 13); E = np.array([S[(f >= edges[i]) & (f < edges[i + 1])].mean(0) for i in range(12) if ((f >= edges[i]) & (f < edges[i + 1])).any()])
    fl = np.maximum(0, np.diff(E, axis=1)); lo = fl[:3].sum(0); allb = fl.sum(0)
    tt = t0 - 0.05 + (np.arange(len(allb)) * hop + nfft / 2) / sr
    pk, pr = signal.find_peaks(allb, prominence=np.percentile(allb, 90) * 0.6, distance=25)
    print(f'[{t0}-{t1}]', [(round(tt[p], 3), round(allb[p], 2), round(lo[p], 2)) for p in pk if t0 <= tt[p] <= t1])
