# a song's level over time, per half second, as a text strip (and where it goes quiet at the end)
import sys, numpy as np, warnings
from scipy.io import wavfile
warnings.filterwarnings('ignore')
sr, a = wavfile.read(sys.argv[1]); a = a.astype(np.float64) / 32768.0; m = a.mean(1); N = len(m)
step = int(0.5 * sr); out = []
for i in range(0, N - step, step):
    r = np.sqrt((m[i:i + step] ** 2).mean()); out.append(20 * np.log10(r + 1e-9))
line = ''
for k, v in enumerate(out):
    if k % 10 == 0: line += f'\n{k*0.5:5.1f}s '
    line += ' ' + ('%4.0f' % v)
print(line)
tail = np.where(np.abs(m) > 10 ** (-50 / 20))[0]; print('\nlast sound above -50 dB at', round(tail[-1] / sr, 2), 's of', round(N / sr, 2))
