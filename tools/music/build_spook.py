"""The locker's Halloween cut, rebuilt on the lobby song's own clock (v2: from the full recording, exact cycle length).
1. Beat clocks: both songs' beats, tracked and then sharpened to the sample on a fine onset curve. The lobby song speeds up a
   little across its loop (a smooth curve, pinned to exactly 68 beats a loop); the Halloween recording holds one tempo.
2. The bars: the lobby loop's start is 16 beats into the old Halloween loop (bass line, melody and drums all agree).
3. The Halloween cycle (68 beats) is taken from the full recording at its exact length, with one 100 ms crossfade where it
   comes round, and Rubber Band's R3 engine stretches it beat by beat onto the lobby song's timeline.
4. The result's loop is exactly as long as the lobby loop, so the two swap at any moment and carry on from the same spot."""
import sys, subprocess, numpy as np, json
D = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/music2/'
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/'
sys.path.insert(0, D)
import rb, soundfile as sf
REFINE = len(sys.argv) > 1 and sys.argv[1] == 'refine'; OUT = sys.argv[2] if len(sys.argv) > 2 else 'spook2'
SR, SRA = 48000, 22050; SHIFT = 16.0; PRE = 1.0; POST = 0.6; XF = 0.05; XJ = 0.1
M = dict(a=6.928, b=43.72223); OLD = dict(a=7.32, b=46.21, src0=43.27)
def dec(p, sr, ch):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-ac', str(ch), '-ar', str(sr), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.float32); return a.reshape(-1, ch).T.copy() if ch > 1 else a.copy()
def fine_onset(x, hop=64, nfft=1024):
    w = np.hanning(nfft).astype(np.float32); n = 1 + (len(x) - nfft) // hop; L = np.empty((n, nfft // 2 + 1), np.float32)
    for i0 in range(0, n, 4096):
        i1 = min(n, i0 + 4096); idx = np.arange(nfft)[None, :] + hop * np.arange(i0, i1)[:, None]; L[i0:i1] = np.log1p(100 * np.abs(np.fft.rfft(x[idx] * w, axis=1)))
    d = np.diff(L, axis=0); d[d < 0] = 0; e = np.concatenate([[0], d.sum(1)]); fps = SRA / hop
    return e, fps, (nfft / 2) / SRA   # (time of frame i = i/fps + centre offset)
def refine(bt, e, fps, cen, win=0.02):
    out = []
    for t in bt:
        c = (t - cen) * fps; lo, hi = int(max(1, c - win * fps)), int(min(len(e) - 2, c + win * fps)); k = lo + int(np.argmax(e[lo:hi + 1]))
        y0, y1, y2 = e[k - 1], e[k], e[k + 1]; den = y0 - 2 * y1 + y2; dk = 0.5 * (y0 - y2) / den if den < 0 else 0
        out.append((k + dk) / fps + cen)
    return np.array(out)
# ---- the lobby song's clock (stream: intro + loop, then the loop twice more, as the beats were tracked on)
xm = dec('/home/claude/music/menu.mp3', SRA, 1); ia, ib = int(round(M['a'] * SRA)), int(round(M['b'] * SRA))
st = np.concatenate([xm[:ib], xm[ia:ib], xm[ia:ib]]); e, fps, cen = fine_onset(st)
btm = np.load(D + 'menu_bt2.npy'); btm = refine(btm, e, fps, cen) if REFINE else btm
Lm = M['b'] - M['a']; s0m = M['b']
k = np.arange(len(btm)); b0 = np.interp(s0m, btm, k); sel = (btm >= s0m - 0.05) & (btm < s0m + Lm - 0.05); u = k[sel] - b0; tau = btm[sel] - s0m
A = np.stack([u * (68 - u) * u ** p for p in range(3)], 1); cm = np.linalg.lstsq(A, tau - Lm * u / 68, rcond=None)[0]
fm = lambda v: Lm * v / 68 + v * (68 - v) * sum(cm[p] * v ** p for p in range(3))
res = tau - fm(u); print('lobby clock: %d beats, resid rms %.1f ms max %.1f ms; %.2f -> %.2f bpm across the loop' % (len(u), np.sqrt((res ** 2).mean()) * 1e3, np.abs(res).max() * 1e3, 60 / (fm(1) - fm(0)), 60 / (fm(68) - fm(67))))
def Tm(v): v = np.asarray(v, float); n = np.floor(v / 68); return s0m + n * Lm + fm(v - n * 68)
# ---- the Halloween recording's clock: one tempo over the whole recording
xs = dec(S + 'spooky/source.wav', SRA, 1); e2, fps2, cen2 = fine_onset(xs)
bts = np.load(D + 'src_bt.npy'); bts = refine(bts, e2, fps2, cen2) if REFINE else bts; bts = bts[(bts > 3) & (bts < 90)]
kk = np.arange(len(bts)); Ps, t0s = np.linalg.lstsq(np.stack([kk, np.ones_like(kk)], 1), bts, rcond=None)[0]; r2 = bts - (t0s + kk * Ps)
print('halloween clock: %d beats, %.3f bpm, resid rms %.1f ms max %.1f ms' % (len(bts), 60 / Ps, np.sqrt((r2 ** 2).mean()) * 1e3, np.abs(r2).max() * 1e3))
for q in range(0, len(r2) - 20, 20): print('   resid beats %3d-%3d: mean %+.1f ms' % (q, q + 20, r2[q:q + 20].mean() * 1e3))
v0 = OLD['src0'] + OLD['a']; C = 68 * Ps   # old loop start = loop-relative beat 0; one cycle = 68 beats
print('cycle %.5f s (the old loop was %.5f s: %.1f ms long)' % (C, OLD['b'] - OLD['a'], (OLD['b'] - OLD['a'] - C) * 1e3))
# ---- the Halloween cycle as a seamless stream at 48 kHz, from the full recording
src = dec(S + 'spooky/source.wav', SR, 2); i0 = int(round(v0 * SR)); iJ = int(round((v0 + C) * SR)); nJ = int(XJ * SR)
a1, a2 = src[:, iJ:iJ + nJ], src[:, i0:i0 + nJ]; corr = float((a1 * a2).sum() / np.sqrt((a1 ** 2).sum() * (a2 ** 2).sum()))
need = int((Tm(80) - Tm(-8)) * SR * 1.2) + SR * 10
r = (np.arange(nJ) / nJ).astype(np.float32)
strm = np.concatenate([src[:, :iJ], a1 * np.cos(r * np.pi / 2) + a2 * np.sin(r * np.pi / 2), src[:, i0 + nJ:i0 + nJ + need]], axis=1)  # (equal power: the recording's ending and the cycle's start don't correlate)
print('junction: the recording at the cycle end vs its start, correlation %.3f (equal-power 100 ms crossfade)' % corr)
sv = lambda v: (v0 + v * Ps) * SR     # loop-relative Halloween beat -> stream sample (one straight line through the junction)
# ---- the stretch: a key frame on every beat
uu = np.arange(-6, 77); tm = Tm(uu); ks = sv(uu + SHIFT)
assert ks[-1] < strm.shape[1] - SR, (ks[-1], strm.shape)
in0 = int(round(ks[0])); x = strm[:, in0:int(round(ks[-1]))]
kin = np.round(ks - in0).astype(int); kout = np.round((tm - tm[0]) * SR).astype(int); ratio = kout[-1] / kin[-1]
print('stretch: %.2f s -> %.2f s, mean ratio %.5f (tempo x%.4f)' % (kin[-1] / SR, kout[-1] / SR, ratio, 1 / ratio))
y, eng = rb.stretch(x, SR, ratio, kin[1:-1], kout[1:-1], finer=True)
print('R%d out %d (map end %d)' % (eng, y.shape[1], kout[-1]))
# ---- cut on the lobby song's timeline: PRE s before the loop, the loop, POST s after
LEAD = 0.006  # the Halloween cut's snares and hats sit ~12 ms behind its kick compared with the lobby song: split the difference
j0 = int(round((s0m - PRE - tm[0] + LEAD) * SR)); nL = int(round(Lm * SR)); nP = int(round(PRE * SR)); nQ = int(round(POST * SR))
out = y[:, j0:j0 + nP + nL + nQ].copy(); nx = int(XF * SR); rr = (np.arange(nx) / nx).astype(np.float32)
cont = y[:, j0 + nP + nL:j0 + nP + nL + nx]; head = out[:, nP:nP + nx].copy(); out[:, nP:nP + nx] = cont * (1 - rr) + head * rr
print('loop seam: step %.4f (it was %.4f before the 50 ms fade)' % (float(np.abs(out[:, nP + nL - 1] - out[:, nP]).max()), float(np.abs(y[:, j0 + nP + nL - 1] - y[:, j0 + nP]).max())))
print('new file: %.4f s, loop a=%.6f b=%.6f' % (out.shape[1] / SR, nP / SR, (nP + nL) / SR))
sf.write(D + OUT + '.wav', out.T, SR, subtype='FLOAT')
old = dec('/home/claude/music/spook.mp3', SR, 2)
rms = lambda a: float(np.sqrt((a ** 2).mean()))
ro, rn = rms(old[:, int(OLD['a'] * SR):int(OLD['b'] * SR)]), rms(out[:, nP:nP + nL])
print('rms old loop %.4f new loop %.4f -> k %.3f keeps the level (was 0.795); peak %.3f' % (ro, rn, 0.795 * ro / rn, float(np.abs(out).max())))
json.dump(dict(a=nP / SR, b=(nP + nL) / SR, k=round(0.795 * ro / rn, 3)), open(D + OUT + '.json', 'w'))
