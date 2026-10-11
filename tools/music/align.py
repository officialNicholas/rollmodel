"""Which beat of the Halloween cut lines up with which beat of the lobby song: both loops resampled onto a beat-phase grid
and cross-correlated round the loop, by onsets (rhythm) and by chroma (harmony)"""
import numpy as np, sys
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/music2')
from analyze import FPS
D = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/music2/'
G = 48  # grid points per beat
def beat_map(bt):
    # time -> fractional beat index, piecewise linear through the tracked beats
    k = np.arange(len(bt)); return lambda t: np.interp(t, bt, k, left=np.nan, right=np.nan), lambda b: np.interp(b, k, bt)
res = {}
for name, a, b in [('menu', 6.928, 43.72223), ('spook', 7.32, 46.21)]:
    e = np.load(D + name + '_e.npy'); C = np.load(D + name + '_C.npy'); bt = np.load(D + name + '_bt.npy')
    t2b, b2t = beat_map(bt); ba, bb = t2b(a), t2b(b)
    grid_b = ba + np.arange(int(68 * G)) / G           # 68 beats from the loop start, in this song's own beats
    ts = b2t(grid_b); fr = ts * FPS
    env = np.interp(fr, np.arange(len(e)), e)
    Cg = np.stack([np.interp(fr, np.arange(len(C)), C[:, k]) for k in range(12)], 1)
    Cg = Cg / (np.linalg.norm(Cg, axis=1, keepdims=True) + 1e-9)
    res[name] = dict(env=env, C=Cg, ba=ba, bb=bb, bt=bt)
    print(name, 'loop start at beat', round(float(ba), 3), 'end at beat', round(float(bb), 3), 'len', round(float(bb - ba), 3))
m, s = res['menu'], res['spook']
N = len(m['env'])
# circular cross-correlation: spook shifted by k grid steps vs menu
def xc(x, y): X = np.fft.rfft(x - x.mean()); Y = np.fft.rfft(y - y.mean()); return np.fft.irfft(np.conj(X) * Y, n=len(x))
on = xc(m['env'], s['env']); on /= on.max()
ch = sum(xc(m['C'][:, k], s['C'][:, k]) for k in range(12)); ch /= ch.max()
both = on / np.abs(on).max() + ch / np.abs(ch).max()
for nm, v in [('onset', on), ('chroma', ch), ('both', both)]:
    top = np.argsort(-v)[:6]
    print(nm, 'best shifts (beats):', [(round(((k + N // 2) % N - N // 2) / G, 3), round(float(v[k]), 3)) for k in top])
