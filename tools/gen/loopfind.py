# find the tempo and beat grid of a track, then the best bar-aligned loop
import sys, numpy as np, warnings
from scipy.io import wavfile
from scipy import signal
warnings.filterwarnings('ignore')
path = sys.argv[1]
sr, a = wavfile.read(path); a = a.astype(np.float64) / 32768.0; m = a.mean(1)
# a light onset envelope: spectral flux on a log-mel-ish spectrogram, hop 10 ms
hop = sr // 100; nfft = 2048
f, t, Z = signal.stft(m, sr, nperseg=nfft, noverlap=nfft - hop, boundary=None, padded=False)
S = np.abs(Z)
# group into 40 log-spaced bands
edges = np.geomspace(40, 12000, 41); B = np.zeros((40, S.shape[1]))
for i in range(40):
    sel = (f >= edges[i]) & (f < edges[i + 1]); B[i] = S[sel].sum(0) if sel.any() else 0
L = np.log1p(B * 100)
flux = np.maximum(0, np.diff(L, axis=1)).sum(0); flux = np.concatenate([[0], flux])
flux = flux - signal.medfilt(flux, 31); flux = np.maximum(flux, 0)
fps = sr / hop
# tempo: autocorrelation of the onset envelope, 70-180 bpm, with a gentle prior around 120
ac = np.correlate(flux, flux, 'full')[len(flux) - 1:]
lags = np.arange(len(ac)); bpm = 60 * fps / np.maximum(lags, 1)
sel = (bpm > 70) & (bpm < 180)
score = ac * np.exp(-0.5 * (np.log2(np.maximum(bpm, 1) / 120) / 0.9) ** 2)
lag = lags[sel][np.argmax(score[sel])]
# refine the lag with a parabola
y0, y1, y2 = ac[lag - 1], ac[lag], ac[lag + 1]; d = 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2) if (y0 - 2 * y1 + y2) != 0 else 0
period = (lag + d) / fps
print('tempo ~', round(60 / period, 3), 'bpm, beat', round(period, 5), 's')
# also report the top candidates
cands = sorted([(score[l], 60 * fps / l) for l in range(2, len(ac)) if sel[l] and ac[l] >= ac[l - 1] and ac[l] >= ac[l + 1]], reverse=True)[:6]
print('candidates', [(round(b, 2), round(s / score[lag], 2)) for s, b in cands])
# beat phase: the offset that lines a pulse train up best with the onsets
best = None
for off in np.arange(0, period, 0.005):
    idx = ((off + np.arange(0, len(m) / sr - off, period)) * fps).astype(int); idx = idx[idx < len(flux)]
    s = flux[idx].sum()
    if best is None or s > best[0]: best = (s, off)
off = best[1]; print('first beat at', round(off, 4), 's')
np.save('music_src/flux.npy', flux)
open('music_src/grid.txt', 'w').write(f'{period} {off} {fps}\n')
