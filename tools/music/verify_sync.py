"""How well a Halloween cut sits on the lobby song: the lag between their drum hits in each 4-beat window round the loop
(onsets on a 2.9 ms grid, cross-correlated within +-60 ms), plus harmony similarity at 0 and at a half beat off"""
import sys, subprocess, numpy as np
SRA = 22050
def mono(p, t0=None, t1=None):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-ac', '1', '-ar', str(SRA), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).copy(); return x if t0 is None else x[int(t0 * SRA):int(t1 * SRA)]
def onset(x, hop=64, nfft=1024, lo=0, hi=11025):
    w = np.hanning(nfft).astype(np.float32); n = 1 + (len(x) - nfft) // hop; f = np.fft.rfftfreq(nfft, 1 / SRA); sel = (f >= lo) & (f < hi); L = np.empty((n, sel.sum()), np.float32)
    for i0 in range(0, n, 4096):
        i1 = min(n, i0 + 4096); idx = np.arange(nfft)[None, :] + hop * np.arange(i0, i1)[:, None]; L[i0:i1] = np.log1p(100 * np.abs(np.fft.rfft(x[idx] * w, axis=1)))[:, sel]
    d = np.diff(L, axis=0); d[d < 0] = 0; e = np.concatenate([[0], d.sum(1)]); g = np.exp(-0.5 * (np.arange(-6, 7) / 2.0) ** 2); e = np.convolve(e, g / g.sum(), 'same')
    return e - np.convolve(e, np.ones(64) / 64, 'same')
def lags(m, s, beats=4, bpm=110.9, hop=64):
    fps = SRA / hop; W = int(beats * 60 / bpm * fps); R = int(0.06 * fps); out = []
    for i in range(R, min(len(m), len(s)) - W - R, W):
        a = m[i:i + W]; best = max(range(-R, R + 1), key=lambda k: float(np.dot(a, s[i + k:i + k + W])))
        out.append(best / fps * 1000)
    return np.array(out)
if __name__ == '__main__':
    path, a, b = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
    L = b - a
    m = mono('/home/claude/music/menu.mp3', 6.928, 6.928 + L); s = mono(path, a, b)
    for nm, lo, hi in [('all', 0, 11025), ('low', 30, 200), ('high', 3000, 11025)]:
        lg = lags(onset(m, lo=lo, hi=hi), onset(s, lo=lo, hi=hi))
        print('%-4s lag per 4 beats (ms, + = Halloween late): median %+.1f  mean %+.1f  sd %.1f | %s' % (nm, np.median(lg), lg.mean(), lg.std(), ' '.join('%+.0f' % v for v in lg)))
