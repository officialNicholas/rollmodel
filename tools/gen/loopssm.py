import sys, numpy as np, warnings
from scipy.io import wavfile
from scipy import signal
warnings.filterwarnings('ignore')
path = sys.argv[1]
period, off, fps = map(float, open('music_src/grid.txt').read().split())
sr, a = wavfile.read(path); a = a.astype(np.float64) / 32768.0; m = a.mean(1)
hop = sr // 100; nfft = 4096
f, t, Z = signal.stft(m, sr, nperseg=nfft, noverlap=nfft - hop, boundary=None, padded=False); S = np.abs(Z) ** 2
# chroma (12 pitch classes) and 24 log bands of timbre
freqs = f[1:]; midi = 69 + 12 * np.log2(freqs / 440.0); pc = np.mod(np.round(midi), 12).astype(int)
ch = np.zeros((12, S.shape[1]))
for k in range(12): ch[k] = S[1:][(pc == k) & (freqs > 60) & (freqs < 4000)].sum(0)
edges = np.geomspace(40, 14000, 25); tb = np.zeros((24, S.shape[1]))
for i in range(24): sel = (f >= edges[i]) & (f < edges[i + 1]); tb[i] = S[sel].sum(0)
tb = np.log1p(tb * 1e4)
nb = int((len(m) / sr - off) / period)
def beat_feat(F, norm=True):
    out = []
    for b in range(nb):
        i0 = int((off + b * period) * fps); i1 = int((off + (b + 1) * period) * fps); v = F[:, i0:i1].mean(1)
        out.append(v / (np.linalg.norm(v) + 1e-9) if norm else v)
    return np.array(out)
C = beat_feat(ch); T = beat_feat(tb - tb.mean(1, keepdims=True))
SS = 0.5 * (C @ C.T) + 0.5 * (T @ T.T)
print('beats', nb, 'bar', round(4 * period, 4), 's')
# how alike the song is with itself shifted by each number of bars (averaged along the diagonal)
for lagb in range(4, nb - 4, 4):
    d = np.array([SS[i, i + lagb] for i in range(nb - lagb)]); print(f'lag {lagb:3d} beats ({lagb//4:2d} bars, {lagb*period:6.2f}s): mean {d.mean():.3f}  max run', round(max(np.convolve(d, np.ones(8)/8, 'valid')), 3))
np.save('music_src/ss.npy', SS)
