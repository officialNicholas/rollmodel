# search seam points for a loop: log-mel frames 5 ms apart; for each start A and loop length L, how alike half a second either side is
import sys, numpy as np, warnings, json
from scipy.io import wavfile
from scipy import signal
warnings.filterwarnings('ignore')
path, a0, a1, L0, L1 = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]); out = sys.argv[6]
HW = float(sys.argv[7]) if len(sys.argv) > 7 else 0.25
sr, a = wavfile.read(path); a = a.astype(np.float64) / 32768.0; m = a.mean(1)
hop = int(0.005 * sr); nfft = 2048
f, t, Z = signal.stft(m, sr, nperseg=nfft, noverlap=nfft - hop, boundary=None, padded=False); S = np.abs(Z) ** 2
# 64 mel bands
mel = lambda x: 2595 * np.log10(1 + x / 700); imel = lambda y: 700 * (10 ** (y / 2595) - 1)
edges = imel(np.linspace(mel(40), mel(15000), 66)); M = np.zeros((64, S.shape[1]))
for i in range(64):
    lo, c, hi = edges[i], edges[i + 1], edges[i + 2]; w = np.clip(np.minimum((f - lo) / (c - lo + 1e-9), (hi - f) / (hi - c + 1e-9)), 0, None); M[i] = w @ S
LM = np.log10(M + 1e-10); fps = 1 / 0.005; tt = (np.arange(LM.shape[1]) * hop + nfft / 2) / sr
idx = lambda s: int(round((s - nfft / 2 / sr) * fps))
hw = int(HW * fps); res = []
for A in np.arange(a0, a1, 0.01):
    ia = idx(A); X = LM[:, ia - hw:ia + hw]
    best = None
    for L in np.arange(L0, L1, 0.005):
        ib = idx(A + L)
        if ib + hw >= LM.shape[1]: break
        Y = LM[:, ib - hw:ib + hw]; d = np.mean((X - Y) ** 2)
        if best is None or d < best[0]: best = (d, L)
    if best: res.append((best[0], A, best[1]))
res.sort()
for d, A, L in res[:15]: print(f'A {A:7.3f}  L {L:8.4f}  B {A + L:7.3f}  dist {d:.4f}')
print('median dist', round(float(np.median([r[0] for r in res])), 4))
json.dump(res[:60], open(out, 'w'))
