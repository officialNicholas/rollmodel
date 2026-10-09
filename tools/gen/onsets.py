# precise attack times in a window: high-passed energy in 2 ms steps, its rises
import sys, numpy as np, warnings
from scipy.io import wavfile
from scipy import signal
warnings.filterwarnings('ignore')
path = sys.argv[1]; wins = [tuple(map(float, w.split(':'))) for w in sys.argv[2:]]
sr, a = wavfile.read(path); a = a.astype(np.float64) / 32768.0; m = a.mean(1)
bands = {'lo': signal.butter(4, [40 / (sr / 2), 160 / (sr / 2)], 'band'), 'hi': signal.butter(4, 3000 / (sr / 2), 'high')}
for t0, t1 in wins:
    seg = m[int(t0 * sr):int(t1 * sr)]; out = []
    for nm, (b, aa) in bands.items():
        x = signal.filtfilt(b, aa, seg); h = int(0.002 * sr); e = np.array([np.sqrt((x[i:i + h * 2] ** 2).mean()) for i in range(0, len(x) - 2 * h, h)]); d = np.diff(20 * np.log10(e + 1e-7))
        pk, _ = signal.find_peaks(d, height=4, distance=40); out.append((nm, [(round(t0 + (p + 1) * 0.002, 3), round(d[p], 1)) for p in pk]))
    print(f'[{t0}-{t1}]', out)
