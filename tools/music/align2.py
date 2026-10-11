"""Alignment on seamless looped copies of both songs: beats tracked through the seam, features per band, and the score at every
beat shift round the 68-beat loop"""
import numpy as np, sys, subprocess
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/music2')
from analyze import SR, HOP, NFFT, FPS, stft_mag, chroma
from beats import track
D = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/music2/'
def load(p):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()
def band_onset(M, lo, hi):
    f = np.fft.rfftfreq(NFFT, 1 / SR); sel = (f >= lo) & (f < hi); L = np.log1p(100 * M[:, sel]); d = np.diff(L, axis=0); d[d < 0] = 0; e = np.concatenate([[0], d.sum(1)])
    e = e - np.convolve(e, np.ones(32) / 32, 'same'); e[e < 0] = 0; return e / (e.max() + 1e-9)
S = {}
for name, a, b, bpm in [('menu', 6.928, 43.72223, 110.8), ('spook', 7.32, 46.21, 105.0)]:
    x = load('/home/claude/music/' + name + '.mp3'); ia, ib = int(round(a * SR)), int(round(b * SR))
    st = np.concatenate([x[:ib], x[ia:ib], x[ia:ib]]); M = stft_mag(st)
    e = band_onset(M, 30, 11000); lo = band_onset(M, 30, 150); hi = band_onset(M, 2000, 11000); C = chroma(M)
    bt = track(e, bpm)
    L = b - a; s0 = b; s1 = b + L   # the second time round the loop, in the stream
    sel = bt[(bt >= s0 - 0.01) & (bt < s1 - 0.01)]
    print(name, 'beats in 2nd loop', len(sel), 'first', round(sel[0] - s0, 4), 's after its start; ibi', round(float(np.median(np.diff(sel))), 4))
    S[name] = dict(e=e, lo=lo, hi=hi, C=C, bt=bt, s0=s0, s1=s1, L=L)
G = 48
def grid(name, feat):
    d = S[name]; bt = d['bt']; k = np.arange(len(bt)); b0 = np.interp(d['s0'], bt, k)
    gb = b0 + np.arange(68 * G) / G; ts = np.interp(gb, k, bt); fr = ts * FPS
    v = d[feat]
    if v.ndim == 1: return np.interp(fr, np.arange(len(v)), v), b0
    Cg = np.stack([np.interp(fr, np.arange(len(v)), v[:, j]) for j in range(12)], 1); return Cg / (np.linalg.norm(Cg, axis=1, keepdims=True) + 1e-9), b0
def xc(x, y): X = np.fft.rfft(x - x.mean()); Y = np.fft.rfft(y - y.mean()); return np.fft.irfft(np.conj(X) * Y, n=len(x))
out = {}
for feat in ['e', 'lo', 'hi', 'C']:
    (mg, mb0), (sg, sb0) = grid('menu', feat), grid('spook', feat)
    r = xc(mg, sg) if mg.ndim == 1 else sum(xc(mg[:, j], sg[:, j]) for j in range(12)); r = r / r.max(); out[feat] = r
    if feat == 'e': print('loop start phase in own tracked beats: menu', round(mb0 % 1, 3), 'spook', round(sb0 % 1, 3))
N = 68 * G
print('shift(beats) ' + ' '.join(f'{f:>6}' for f in out))
for sh in [i * 0.5 for i in range(0, 136)]:
    k = int(round(sh * G)) % N; row = [out[f][k] for f in out]
    if sh % 4 == 0 or max(row[:3]) > 0.8 or row[3] > 0.85: print(f'{sh:11.1f} ' + ' '.join(f'{v:6.3f}' for v in row))
for f in out:
    k = int(np.argmax(out[f])); print(f, 'peak at', round(((k + N // 2) % N - N // 2) / G, 3) % 68)
np.save(D + 'menu_bt2.npy', S['menu']['bt']); np.save(D + 'spook_bt2.npy', S['spook']['bt'])
print('fine onset scores near 16 (loop-relative beats):')
for feat in ['e', 'hi']:
    r = out[feat]; row = []
    for sh in np.arange(15.75, 16.26, 1 / 48):
        row.append((round(sh, 3), round(float(r[int(round(sh * G)) % N]), 4)))
    best = max(row, key=lambda z: z[1]); print(' ', feat, 'local best', best, ' at 16.0:', [z for z in row if abs(z[0] - 16) < 1e-6])
    print('   ', ' '.join(f'{a:.3f}:{b:.3f}' for a, b in row[::2]))
