# how big a change the loop's jump makes, next to the changes the song makes by itself at those two spots (and on average)
import sys, json, numpy as np, warnings
from scipy.io import wavfile
from scipy import signal
warnings.filterwarnings('ignore')
name = sys.argv[1]; meta = json.load(open('music_out/loops.json'))[name]
def feats(path):
    sr, a = wavfile.read(path); m = a.astype(np.float64).mean(1) / 32768.0
    hop = sr // 50; f, t, Z = signal.stft(m, sr, nperseg=4096, noverlap=4096 - hop, boundary=None, padded=False); S = np.abs(Z) ** 2
    freqs = f[1:]; midi = 69 + 12 * np.log2(np.maximum(freqs, 1) / 440.0); pc = np.mod(np.round(midi), 12).astype(int)
    ch = np.array([S[1:][(pc == k) & (freqs > 60) & (freqs < 4000)].sum(0) for k in range(12)]); ch /= ch.sum(0, keepdims=True) + 1e-9
    edges = np.geomspace(40, 15000, 21); tb = np.array([S[(f >= edges[i]) & (f < edges[i + 1])].sum(0) for i in range(20)]); tb = np.log10(tb + 1e-9)
    return sr, np.vstack([ch * 4, tb * 0.5]), 50.0
def change(F, fps, tsec, w=1.0):
    i = int(tsec * fps); k = int(w * fps); x = F[:, i - k:i].mean(1); y = F[:, i:i + k].mean(1); return float(np.linalg.norm(x - y))
_, Fp, fps = feats(f'music_out/{name}_preview.wav'); _, Fo, _ = feats(f'music_out/{name}.wav')
seam = meta['seams'][0]; dA = change(Fo, fps, meta['hits'][0]); dB = change(Fo, fps, meta['hits'][1]); dS = change(Fp, fps, seam)
typ = [change(Fo, fps, t) for t in np.arange(3, meta['len'] - 3, 0.37)]
print(f'{name}: jump {dS:.3f}  vs the song at A {dA:.3f}, at B {dB:.3f}; anywhere: median {np.median(typ):.3f}, 90th {np.percentile(typ, 90):.3f}, max {max(typ):.3f}')
