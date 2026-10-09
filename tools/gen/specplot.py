import sys, numpy as np, warnings
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy import signal
warnings.filterwarnings('ignore')
path, out = sys.argv[1], sys.argv[2]; t0 = float(sys.argv[3]) if len(sys.argv) > 3 else 0; t1 = float(sys.argv[4]) if len(sys.argv) > 4 else None
grid = open(sys.argv[5]).read().split() if len(sys.argv) > 5 else None
sr, a = wavfile.read(path); a = a.astype(np.float64) / 32768.0; m = a.mean(1)
t1 = t1 or len(m) / sr; seg = m[int(t0 * sr):int(t1 * sr)]
f, t, Z = signal.stft(seg, sr, nperseg=2048, noverlap=2048 - 240); S = 20 * np.log10(np.abs(Z) + 1e-7)
fig, ax = plt.subplots(2, 1, figsize=(22, 8), gridspec_kw={'height_ratios': [3, 1]})
ax[0].pcolormesh(t + t0, f, S, vmin=-90, vmax=-20, shading='auto', cmap='magma'); ax[0].set_yscale('symlog', linthresh=200); ax[0].set_ylim(30, 16000)
env = np.sqrt(signal.convolve(seg ** 2, np.ones(480) / 480, 'same'))[::240]; ax[1].plot(np.arange(len(env)) * 240 / sr + t0, 20 * np.log10(env + 1e-9), lw=0.6); ax[1].set_xlim(t0, t1); ax[0].set_xlim(t0, t1)
if grid:
    period, off = float(grid[0]), float(grid[1]); k = 0
    for bt in np.arange(off, t1, period):
        if bt >= t0: ax[0].axvline(bt, color='c' if k % 4 == 0 else 'w', lw=0.6 if k % 4 else 1.2, alpha=0.5)
        k += 1
ax[1].set_xticks(np.arange(np.ceil(t0), t1, 1.0)); ax[1].grid(alpha=0.3)
plt.tight_layout(); plt.savefig(out, dpi=70)
