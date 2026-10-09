import sys, numpy as np
from scipy.io import wavfile
from scipy import signal
def kw(x, sr):
    # BS.1770 K-weighting: high shelf then high pass (coefficients via bilinear design at sr)
    f0, G, Q = 1681.974450955533, 3.999843853973347, 0.7071752369554196
    K = np.tan(np.pi * f0 / sr); Vh = 10 ** (G / 20); Vb = Vh ** 0.4996667741545416
    a0 = 1 + K / Q + K * K
    b = [(Vh + Vb * K / Q + K * K) / a0, 2 * (K * K - Vh) / a0, (Vh - Vb * K / Q + K * K) / a0]; a = [1, 2 * (K * K - 1) / a0, (1 - K / Q + K * K) / a0]
    y = signal.lfilter(b, a, x, axis=0)
    f0, Q = 38.13547087602444, 0.5003270373238773; K = np.tan(np.pi * f0 / sr)
    b = [1, -2, 1]; a0 = 1 + K / Q + K * K; a = [1, 2 * (K * K - 1) / a0, (1 - K / Q + K * K) / a0]
    return signal.lfilter(b, a, y, axis=0)
def lufs(x, sr):
    y = kw(x, sr); blk = int(0.4 * sr); hop = int(0.1 * sr); L = []
    for i in range(0, len(y) - blk, hop):
        ms = (y[i:i + blk] ** 2).mean(axis=0).sum(); L.append(ms)
    L = np.array(L); l = -0.691 + 10 * np.log10(L + 1e-12); L = L[l > -70]
    rel = -0.691 + 10 * np.log10(L.mean()) - 10; l = -0.691 + 10 * np.log10(L + 1e-12)
    return -0.691 + 10 * np.log10(L[l > rel].mean())
def phone(x, sr):
    b, a = signal.butter(2, 320, 'highpass', fs=sr); y = signal.lfilter(b, a, x, axis=0)
    b, a = signal.butter(2, 12000, 'lowpass', fs=sr); return signal.lfilter(b, a, y, axis=0)
def bands(x, sr):
    m = x.mean(axis=1); f, P = signal.welch(m, sr, nperseg=8192)
    out = []
    for lo, hi in [(20, 80), (80, 250), (250, 800), (800, 2500), (2500, 6000), (6000, 16000)]:
        sel = (f >= lo) & (f < hi); out.append(10 * np.log10(P[sel].sum() + 1e-15))
    return out
if __name__ == '__main__':
  for fn in sys.argv[1:]:
    sr, x = wavfile.read(fn); x = x.astype(np.float64) / 32768
    b = bands(x, sr)
    print(f"{fn:22s} LUFS {lufs(x, sr):6.1f}  phone {lufs(phone(x, sr), sr):6.1f}  bands " + ' '.join(f'{v:6.1f}' for v in b))
