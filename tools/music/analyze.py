"""Tempo, beat phase, key and bar alignment of the lobby song and its Halloween cut"""
import subprocess, numpy as np, sys
SR = 22050; HOP = 256; NFFT = 2048
def load(p, sr=SR):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()
def stft_mag(x):
    w = np.hanning(NFFT).astype(np.float32); n = 1 + (len(x) - NFFT) // HOP
    idx = np.arange(NFFT)[None, :] + HOP * np.arange(n)[:, None]
    return np.abs(np.fft.rfft(x[idx] * w, axis=1))
def onset_env(M):
    L = np.log1p(100 * M); d = np.diff(L, axis=0); d[d < 0] = 0; e = d.sum(1); e = np.concatenate([[0], e])
    e = e - np.convolve(e, np.ones(32) / 32, 'same'); e[e < 0] = 0; return e / (e.max() + 1e-9)
def chroma(M):
    f = np.fft.rfftfreq(NFFT, 1 / SR); C = np.zeros((M.shape[0], 12)); ok = (f > 60) & (f < 4000)
    pc = (np.round(12 * np.log2(f[ok] / 440.0)) + 69) % 12
    P = M[:, ok] ** 2
    for k in range(12): C[:, k] = P[:, pc == k].sum(1)
    return C
FPS = SR / HOP
def tempo_curve(e, lo=60, hi=180):
    ac = np.correlate(e, e, 'full')[len(e) - 1:]; best = []
    for bpm in np.arange(lo, hi, 0.05):
        lag = 60 / bpm * FPS; i = int(lag); fr = lag - i
        v = ac[i] * (1 - fr) + ac[i + 1] * fr if i + 1 < len(ac) else 0
        best.append((v, bpm))
    best.sort(reverse=True); return best[:8]
def comb_score(e, bpm, t0, t1):
    # mean onset strength on a beat grid of this tempo, best phase; returns (score, phase seconds)
    per = 60 / bpm; ph = np.arange(0, per, 0.002); sc = []
    for p in ph:
        ts = np.arange(t0 + p, t1, per); fr = np.round(ts * FPS).astype(int); fr = fr[fr < len(e)]
        sc.append(e[fr].mean())
    i = int(np.argmax(sc)); return sc[i], ph[i]
if __name__ == '__main__':
    out = {}
    for name, p, a, b in [('menu', '/home/claude/music/menu.mp3', 6.928, 43.72223), ('spook', '/home/claude/music/spook.mp3', 7.32, 46.21)]:
        x = load(p); M = stft_mag(x); e = onset_env(M); C = chroma(M)
        fa, fb = int(a * FPS), int(b * FPS)
        tc = tempo_curve(e[fa:fb])
        print(name, 'dur', len(x) / SR, 'loop', b - a, 'tempo cands', [(round(bp, 2), round(v, 1)) for v, bp in tc[:5]])
        # fine tempo by comb over the loop
        cands = sorted(set(round(bp, 1) for v, bp in tc[:3]))
        best = None
        for c in cands:
            for bpm in np.arange(c - 1.5, c + 1.5, 0.01):
                s, ph = comb_score(e, bpm, a, b) if False else (None, None)
        prof = C[fa:fb].sum(0); prof /= prof.sum()
        names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        print('  chroma profile', ' '.join(f'{names[k]}:{prof[k]:.3f}' for k in np.argsort(-prof)[:7]))
        np.save(f'/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/music2/{name}_e.npy', e)
        np.save(f'/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/music2/{name}_C.npy', C)
