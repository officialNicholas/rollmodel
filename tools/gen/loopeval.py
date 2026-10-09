# how identical the audio really is round a loop's two ends: the waveform, aligned to the sample, over a bar before to two after,
# in three bands (lows, mids, highs) - usage: loopeval.py song.wav bar A:B [A:B ...]
import sys, numpy as np, warnings
from scipy.io import wavfile
from scipy import signal
warnings.filterwarnings('ignore')
path, bar = sys.argv[1], float(sys.argv[2])
sr, a = wavfile.read(path); a = a.astype(np.float64) / 32768.0; m = a.mean(1)
bands = {'low': signal.butter(4, 250 / (sr / 2), 'low'), 'mid': signal.butter(4, [250 / (sr / 2), 2500 / (sr / 2)], 'band'), 'high': signal.butter(4, 2500 / (sr / 2), 'high')}
X = {k: signal.filtfilt(b, aa, m) for k, (b, aa) in bands.items()}
for pr in sys.argv[3:]:
    A, B = map(float, pr.split(':'))
    i0, j0, w0, w1, R = int((A - bar) * sr), int((B - bar) * sr), 0, int(3 * bar * sr), int(0.03 * sr)
    out = []
    for k in ('low', 'mid', 'high'):
        x = X[k][i0:i0 + w1]; y = X[k][j0 - R:j0 + w1 + R]
        cc = signal.correlate(y, x, 'valid'); nrm = np.sqrt(np.convolve(y ** 2, np.ones(len(x)), 'valid')) * np.linalg.norm(x) + 1e-12; cc = cc / nrm
        j = int(np.argmax(cc)); out.append((k, round(float(cc[j]), 3), j - R))
    # and the same right at the seam, a quarter bar either side, mids
    x = X['mid'][int((A - bar / 4) * sr):int((A + bar / 4) * sr)]; lag = out[1][2]; y = X['mid'][int((B - bar / 4) * sr) + lag:int((B + bar / 4) * sr) + lag]
    n = min(len(x), len(y)); near = float(np.dot(x[:n], y[:n]) / (np.linalg.norm(x[:n]) * np.linalg.norm(y[:n]) + 1e-12))
    print(f'A {A:7.3f} B {B:7.3f} L {B - A:6.3f}:', ' '.join(f'{k} {c:.3f} (lag {l:+d})' for k, c, l in out), f' seam-mid {near:.3f}')
